import requests

def validate_vin_with_nhtsa(vin):
    """
    Validate VIN using NHTSA API
    Returns: (is_valid, vehicle_info_or_error_message)
    """
    try:
        url = f"https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVin/{vin}?format=json"
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            return False, "Unable to validate VIN at this time."
        
        data = response.json()
        results = data.get('Results', [])
        
        error_codes = [r for r in results if r.get('Variable') == 'Error Code']
        if error_codes and error_codes[0].get('Value') not in ['0', '']:
            error_text = [r for r in results if r.get('Variable') == 'Error Text']
            if error_text:
                return False, f"Invalid VIN: {error_text[0].get('Value', 'VIN not found')}"
            return False, "This VIN does not appear to be valid."
        
        make = next((r['Value'] for r in results if r.get('Variable') == 'Make'), None)
        model = next((r['Value'] for r in results if r.get('Variable') == 'Model'), None)
        year = next((r['Value'] for r in results if r.get('Variable') == 'Model Year'), None)
        body_type = next((r['Value'] for r in results if r.get('Variable') == 'Body Class'), None)
        
        if not make or not model or not year:
            return False, "Unable to verify this VIN. Please provide Year, Make, and Model instead."
        
        vehicle_info = f"{year} {make} {model}"
        if body_type:
            vehicle_info += f" ({body_type})"
        
        return True, vehicle_info
        
    except requests.Timeout:
        return False, "Request timed out. Please try again."
    except Exception as e:
        return False, "Unable to validate VIN at this time."


def validate_year_make_model_with_nhtsa(year, make, model=None):
    """
    Validate Year/Make/Model using NHTSA API
    Returns: (is_valid, vehicle_info_or_error_message)
    """
    try:
        url = f"https://vpic.nhtsa.dot.gov/api/vehicles/GetModelsForMakeYear/make/{make}/modelyear/{year}?format=json"
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            return False, "Unable to validate vehicle at this time."
        
        data = response.json()
        results = data.get('Results', [])
        
        if not results:
            return False, f"I couldn't find any {year} {make} vehicles. Please check the year and make and try again."
        
        if model:
            model_lower = model.lower()
            matching_models = [r for r in results if model_lower in r.get('Model_Name', '').lower()]
            
            if not matching_models:
                available_models = [r.get('Model_Name') for r in results[:5]]
                models_str = ", ".join(available_models)
                return False, f"I couldn't find a {year} {make} {model}. Did you mean one of these: {models_str}?"
            
            validated_model = matching_models[0]['Model_Name']
            return True, f"{year} {make} {validated_model}"
        else:
            return True, f"{year} {make}"
        
    except requests.Timeout:
        return False, "Request timed out. Please try again."
    except Exception as e:
        return False, "Unable to validate vehicle at this time."


def parse_and_validate_vehicle(user_input):
    """
    Parse user input and validate against NHTSA
    Returns: (is_valid, extracted_value_or_error_message)
    """
    cleaned_input = user_input.strip().replace('-', '').replace(' ', '')
    if len(cleaned_input) == 17 and cleaned_input.isalnum():
        return validate_vin_with_nhtsa(cleaned_input)
    
    parts = user_input.replace(',', ' ').split()
    parts = [p.strip() for p in parts if p.strip()]
    
    if len(parts) < 2:
        return False, "Please provide either a VIN or at least the Year and Make of your vehicle."
    
    try:
        year = int(parts[0])
        if year < 1900 or year > 2026:
            return False, f"{year} doesn't seem like a valid year. Please provide a year between 1900-2026."
    except ValueError:
        return False, "Please start with the year (e.g., '2020 Honda Civic')."
    
    make = parts[1]
    model = ' '.join(parts[2:]) if len(parts) > 2 else None
    
    return validate_year_make_model_with_nhtsa(year, make, model)