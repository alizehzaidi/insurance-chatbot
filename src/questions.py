questions = [
    {
        "id": "zip_code",
        "text": "What is your zip code?",
        "expectedFormat": "5-digit US zip code",
        "validationRules": "Must be exactly 5 digits",
        "retryPrompt": "Please provide a valid 5-digit zip code.",
        "conditional": None
    },
    {
        "id": "full_name",
        "text": "What is your full name?",
        "expectedFormat": "First and Last name",
        "validationRules": "Must contain at least 2-50 characters",
        "retryPrompt": "Please provide your full name (first and last).",
        "conditional": None
    },
    {
        "id": "email",
        "text": "What is your email address?",
        "expectedFormat": "valid email format (user@domain.com)",
        "validationRules": "Must be a valid email format",
        "retryPrompt": "That doesn't look like a valid email. Please provide a valid email address.",
        "conditional": None
    },
    {
        "id": "add_vehicle_prompt",
        "text": "Now let's add your vehicles. Would you like to add a vehicle? (yes/no)",
        "expectedFormat": "yes or no",
        "validationRules": "Must be yes or no",
        "retryPrompt": "Please answer yes or no.",
        "conditional": None,
        "type": "vehicle_start"
    },
    {
        "id": "vehicle_identifier",
        "text": "Please provide either the VIN number OR the Year, Make, and Model of your vehicle.",
        "expectedFormat": "VIN (17 characters) OR 'Year Make Model' (e.g., '2020 Toyota Camry')",
        "validationRules": "Either a 17-character VIN or Year (4 digits) + Make + Model",
        "retryPrompt": "Please provide either a VIN or the year, make, and model of your vehicle.",
        "conditional": {"type": "vehicle_question"},
        "vehicle_question": True
    },
    {
        "id": "vehicle_use",
        "text": "How is this vehicle used? (commuting, commercial, farming, or business)",
        "expectedFormat": "one of: commuting, commercial, farming, business",
        "validationRules": "Must be exactly one of these: commuting, commercial, farming, business",
        "retryPrompt": "Please choose one: commuting, commercial, farming, or business.",
        "conditional": {"type": "vehicle_question"},
        "vehicle_question": True
    },
    {
        "id": "blind_spot_warning",
        "text": "Is this vehicle equipped with blind spot warning? (yes/no)",
        "expectedFormat": "yes or no",
        "validationRules": "Must be yes or no",
        "retryPrompt": "Please answer yes or no.",
        "conditional": {"type": "vehicle_question"},
        "vehicle_question": True
    },
    {
        "id": "commute_days_per_week",
        "text": "How many days per week do you use this vehicle for commuting?",
        "expectedFormat": "number between 1-7",
        "validationRules": "Must be a number between 1 and 7",
        "retryPrompt": "Please provide a number between 1 and 7.",
        "conditional": {"field": "vehicle_use", "value": "commuting"},
        "vehicle_question": True
    },
    {
        "id": "commute_one_way_miles",
        "text": "How many miles is your one-way trip to work/school?",
        "expectedFormat": "number (miles)",
        "validationRules": "Must be a positive number, typically between 1-200",
        "retryPrompt": "Please provide the one-way distance in miles.",
        "conditional": {"field": "vehicle_use", "value": "commuting"},
        "vehicle_question": True
    },
    {
        "id": "annual_mileage",
        "text": "What is the annual mileage for this vehicle?",
        "expectedFormat": "number (miles per year)",
        "validationRules": "Must be a positive number, typically between 1,000-200,000",
        "retryPrompt": "Please provide the annual mileage.",
        "conditional": {"field": "vehicle_use", "value": ["commercial", "farming", "business"]},
        "vehicle_question": True
    },
    {
        "id": "add_another_vehicle",
        "text": "Would you like to add another vehicle? (yes/no)",
        "expectedFormat": "yes or no",
        "validationRules": "Must be yes or no",
        "retryPrompt": "Please answer yes or no.",
        "conditional": {"type": "vehicle_question"},
        "type": "vehicle_end",
        "vehicle_question": True
    },
    {
        "id": "license_type",
        "text": "What type of US driver's license do you have? (Foreign, Personal, or Commercial)",
        "expectedFormat": "one of: Foreign, Personal, Commercial",
        "validationRules": "Must be exactly one of these: Foreign, Personal, Commercial",
        "retryPrompt": "Please choose one: Foreign, Personal, or Commercial.",
        "conditional": None
    },
    {
        "id": "license_status",
        "text": "What is your license status? (Valid or Suspended)",
        "expectedFormat": "Valid or Suspended",
        "validationRules": "Must be either Valid or Suspended",
        "retryPrompt": "Please answer Valid or Suspended.",
        "conditional": None  
    }
]