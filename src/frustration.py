import requests

def check_for_frustration(user_input):
    """
    Check if user is frustrated or wants to speak to a human
    Returns: (is_frustrated, detected_reason)
    """
    frustration_keywords = [
        'frustrated', 'angry', 'annoyed', 'upset', 'irritated',
        'speak to human', 'talk to human', 'human', 'real person',
        'agent', 'representative', 'help', 'this is not working',
        'i give up', 'forget it', 'never mind', 'this sucks',
        'terrible', 'awful', 'useless', 'stop', 'quit'
    ]
    
    user_lower = user_input.lower()
    for keyword in frustration_keywords:
        if keyword in user_lower:
            return True, keyword
    
    return False, None


def get_zen_quote():
    """
    Call the ZenQuotes API to get a quote when user is frustrated
    """
    try:
        response = requests.get("https://zenquotes.io/api/random", timeout=10)
        
        if response.status_code == 200:
            quotes = response.json()
            if quotes and len(quotes) > 0:
                quote = quotes[0]
                return f"Here's something to brighten your day:\n\n\"{quote['q']}\"\n- {quote['a']}\n\nWould you like to continue with the survey or would you prefer to stop here?"
        
        return "I understand you'd like to speak with someone. Would you like to continue with the survey or stop here?"
    
    except Exception as e:
        return "I understand you'd like to speak with someone. Would you like to continue with the survey or stop here?"