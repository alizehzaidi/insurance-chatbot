import json
import os
import time
from openai import OpenAI
from dotenv import load_dotenv
from src.frustration import check_for_frustration, get_zen_quote
from src.nhtsa_api import parse_and_validate_vehicle

# Load environment variables FIRST
load_dotenv()

# Initialize OpenAI client AFTER loading .env
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def validate_answer(user_input, question, context=None, max_retries=3):
    """
    Use OpenAI to validate user response and extract structured data
    Also checks for frustration
    Includes retry logic for API failures
    """
    
    # First check for frustration
    is_frustrated, reason = check_for_frustration(user_input)
    if is_frustrated:
        return {
            "isValid": False,
            "extractedValue": None,
            "feedbackMessage": get_zen_quote(),
            "nextAction": "frustration_detected",
            "frustration": True
        }
    
    # Special handling for vehicle_identifier - validate with NHTSA
    if question['id'] == 'vehicle_identifier':
        is_valid, message = parse_and_validate_vehicle(user_input)
        
        if is_valid:
            return {
                "isValid": True,
                "extractedValue": message,
                "feedbackMessage": f"Great! I've verified your vehicle: {message}",
                "nextAction": "accept"
            }
        else:
            return {
                "isValid": False,
                "extractedValue": None,
                "feedbackMessage": message,
                "nextAction": "reask"
            }
    
    # For all other questions, use LLM validation
    context_info = ""
    if context:
        context_info = f"\nContext from previous answers: {json.dumps(context, indent=2)}"
    
    system_prompt = f"""You are a helpful insurance survey assistant validating user responses.

Current question: "{question['text']}"
Expected format: {question['expectedFormat']}
Validation rules: {question['validationRules']}{context_info}

Your job:
1. Check if the user's response is valid and matches the expected format
2. Extract the actual answer from their response (handle natural language variations)
3. Provide helpful feedback if invalid
4. Be FLEXIBLE with natural language

Respond ONLY with valid JSON in this exact format:
{{
  "isValid": true/false,
  "extractedValue": "the extracted answer" or null if invalid,
  "feedbackMessage": "friendly message",
  "nextAction": "accept" or "reask"
}}

Examples:
- For zip code: "12345" or "I live in 12345" → {{"isValid": true, "extractedValue": "12345", "feedbackMessage": "Got it!", "nextAction": "accept"}}
- For vehicle use: "I use it to commute" → {{"isValid": true, "extractedValue": "commuting", "feedbackMessage": "Thanks!", "nextAction": "accept"}}
- For yes/no: "yeah" or "yep" → {{"isValid": true, "extractedValue": "yes", "feedbackMessage": "Great!", "nextAction": "accept"}}

Be flexible with natural language but extract structured data.
"""
    
    # Retry logic for API calls
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.2,
                max_tokens=500,
                timeout=30  # Add timeout
            )
            
            response_text = response.choices[0].message.content
            
            # Handle markdown code blocks
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(response_text)
            return result
            
        except json.JSONDecodeError as e:
            print(f"Error parsing LLM response: {e}")
            print(f"Raw response: {response_text}")
            return {
                "isValid": False,
                "extractedValue": None,
                "feedbackMessage": "Sorry, I had trouble processing that. Could you try again?",
                "nextAction": "reask"
            }
        except Exception as e:
            error_message = str(e)
            print(f"API Error (attempt {attempt + 1}/{max_retries}): {e}")
            
            # Check for authentication errors
            if "authentication" in error_message.lower() or "api key" in error_message.lower() or "401" in error_message:
                return {
                    "isValid": False,
                    "extractedValue": None,
                    "feedbackMessage": "⚠️ Authentication error. Please check your OpenAI API key in the .env file.",
                    "nextAction": "reask"
                }
            
            # Check for rate limit errors
            if "rate limit" in error_message.lower() or "429" in error_message:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff: 1s, 2s, 4s
                    continue
                return {
                    "isValid": False,
                    "extractedValue": None,
                    "feedbackMessage": "⚠️ API rate limit reached. Please wait a moment and try again.",
                    "nextAction": "reask"
                }
            
            # Retry for other errors
            if attempt < max_retries - 1:
                time.sleep(1)  # Wait 1 second before retry
                continue
            
            # Final attempt failed - return generic error
            return {
                "isValid": False,
                "extractedValue": None,
                "feedbackMessage": "I'm having trouble right now. Could you try again?",
                "nextAction": "reask"
            }