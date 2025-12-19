from src.validators import validate_answer

class InsuranceChatbotSession:
    def __init__(self, questions):
        self.questions = questions
        self.current_index = 0
        self.answers = {}
        self.vehicles = []
        self.current_vehicle = {}
        self.in_vehicle_flow = False
        self.attempt_counts = {}
        self.max_attempts = 3
        self.conversation_history = []
        self.user_wants_to_stop = False
        
    def should_ask_question(self, question):
        """Check if question should be asked based on conditional logic"""
        if not question.get('conditional'):
            return True
        
        cond = question['conditional']
        
        if cond.get('type') == 'vehicle_question':
            return self.in_vehicle_flow
        
        if 'field' in cond:
            field = cond['field']
            expected_values = cond['value']
            
            if question.get('vehicle_question'):
                actual_value = self.current_vehicle.get(field)
            else:
                actual_value = self.answers.get(field)
            
            if isinstance(expected_values, list):
                return actual_value in expected_values
            else:
                return actual_value == expected_values
        
        return True
    
    def get_next_question(self):
        """Get the next question that should be asked"""
        while self.current_index < len(self.questions):
            question = self.questions[self.current_index]
            
            if self.should_ask_question(question):
                return question
            else:
                self.current_index += 1
        
        return None
    
    def process_response(self, user_input):
        # Check if user wants to stop after frustration was detected
        if self.user_wants_to_stop:
            if 'stop' in user_input.lower() or 'no' in user_input.lower():
                return {
                    "done": True,
                    "message": "No problem! Feel free to come back anytime.",
                    "data": self.compile_final_data()
                }
            else:
                self.user_wants_to_stop = False
        
        current_q = self.get_next_question()
        
        if not current_q:
            return {"done": True, "message": "Survey complete!", "data": self.compile_final_data()}
        
        question_key = f"{current_q['id']}_{self.current_index}"
        if question_key not in self.attempt_counts:
            self.attempt_counts[question_key] = 0
        
        self.attempt_counts[question_key] += 1
        
        context = {**self.answers, **self.current_vehicle} if self.in_vehicle_flow else self.answers
        
        if len(self.conversation_history) > 0:
            context['recent_conversation'] = self.conversation_history[-3:]
        
        result = validate_answer(user_input, current_q, context)
        
        # Handle frustration
        if result and result.get('frustration'):
            self.user_wants_to_stop = True
            return {
                "done": False,
                "message": result['feedbackMessage']
            }
        
        self.conversation_history.append({
            "question": current_q['text'],
            "user_response": user_input,
            "result": result
        })
        
        if not result:
            return {"error": "API error, please try again"}
        
        if result['isValid'] and result['nextAction'] == 'accept':
            self.conversation_history = []
            
            if current_q['id'] == 'add_vehicle_prompt':
                if result['extractedValue'].lower() == 'yes':
                    self.in_vehicle_flow = True
                    self.current_vehicle = {}
                else:
                    self.skip_to_license_questions()
                    next_q = self.get_next_question()
                    if next_q:
                        return {
                            "done": False,
                            "message": f"{result['feedbackMessage']}\n\n{next_q['text']}"
                        }
            
            elif current_q['id'] == 'add_another_vehicle':
                self.vehicles.append(self.current_vehicle.copy())
                
                if result['extractedValue'].lower() == 'yes':
                    self.current_vehicle = {}
                    self.reset_to_vehicle_start()
                    next_q = self.get_next_question()
                    if next_q:
                        return {
                            "done": False,
                            "message": f"{result['feedbackMessage']}\n\n{next_q['text']}"
                        }
                else:
                    self.in_vehicle_flow = False
                    self.current_vehicle = {}
            
            elif current_q.get('vehicle_question'):
                self.current_vehicle[current_q['id']] = result['extractedValue']
            
            else:
                self.answers[current_q['id']] = result['extractedValue']
            
            # Only increment if we didn't already handle navigation above
            if current_q['id'] not in ['add_vehicle_prompt', 'add_another_vehicle']:
                self.current_index += 1
            elif current_q['id'] == 'add_another_vehicle' and result['extractedValue'].lower() == 'no':
                self.current_index += 1
            elif current_q['id'] == 'add_vehicle_prompt' and result['extractedValue'].lower() == 'yes':
                self.current_index += 1
            
            next_q = self.get_next_question()
            
            if next_q:
                return {
                    "done": False,
                    "message": f"{result['feedbackMessage']}\n\n{next_q['text']}"
                }
            else:
                return {
                    "done": True,
                    "message": f"{result['feedbackMessage']}\n\nThanks! Survey complete!",
                    "data": self.compile_final_data()
                }
        else:
            if self.attempt_counts[question_key] >= self.max_attempts:
                self.conversation_history = []
                self.current_index += 1
                next_q = self.get_next_question()
                
                if next_q:
                    return {
                        "done": False,
                        "message": f"Let's move on.\n\n{next_q['text']}",
                        "skipped": current_q['id']
                    }
                else:
                    return {
                        "done": True,
                        "message": "Survey complete!",
                        "data": self.compile_final_data()
                    }
            
            return {
                "done": False,
                "message": result['feedbackMessage']
            }
    
    def skip_to_license_questions(self):
        for i, q in enumerate(self.questions):
            if q['id'] == 'license_type':
                self.current_index = i
                return
    
    def reset_to_vehicle_start(self):
        for i, q in enumerate(self.questions):
            if q['id'] == 'vehicle_identifier':
                self.current_index = i
                return
    
    def compile_final_data(self):
        return {
            "personal_info": {
                "zip_code": self.answers.get('zip_code'),
                "full_name": self.answers.get('full_name'),
                "email": self.answers.get('email')
            },
            "vehicles": self.vehicles,
            "license": {
                "type": self.answers.get('license_type'),
                "status": self.answers.get('license_status')
            }
        }