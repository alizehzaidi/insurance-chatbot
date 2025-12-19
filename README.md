# Insurance Survey Chatbot

An intelligent conversational AI chatbot for collecting insurance information with real-time vehicle validation and live chat monitoring.

## Features

### Core Functionality
✅ **Natural Language Understanding** - OpenAI GPT-4 processes and validates user responses  
✅ **Real-time Vehicle Validation** - NHTSA API verifies VIN numbers and vehicle information  
✅ **Intelligent Question Flow** - Conditional logic adapts based on user responses  
✅ **Multiple Vehicle Support** - Users can add unlimited vehicles to their profile  
✅ **Frustration Detection** - Automatic detection with motivational quotes via ZenQuotes API  

### Technical Features
✅ **Live Database Storage** - Every message saved in real-time to SQLite database  
✅ **Chat Transcript Monitoring** - View all conversations as they happen  
✅ **Session Management** - Unique session IDs for each conversation  
✅ **API Key Validation** - Built-in security checks and error handling  
✅ **Retry Logic** - Automatic retry on API failures with exponential backoff  
✅ **Loading Indicators** - Visual feedback during processing  

## Prerequisites

- Python 3.11+ (Python 3.13 may have dependency conflicts)
- OpenAI API key (provided separately)

## Installation

### 1. Clone the Repository
```bash
cd coverix_chatbot
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv

# Activate (Mac/Linux):
source venv/bin/activate

# Activate (Windows):
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure OpenAI API Key

Create a `.env` file in the project root directory:
```bash
# .env
OPENAI_API_KEY=sk-proj-your-actual-key-here
```

⚠️ **IMPORTANT:** 
- Never commit the `.env` file to version control
- Use the `.env.example` file as a template
- The application will validate the API key on startup

### 5. Run the Application
```bash
streamlit run app.py
```

The application will automatically open in your browser at: `http://localhost:8501`

## Usage

### Main Survey Page
1. Complete the insurance survey by answering questions naturally
2. Vehicle information is validated in real-time against NHTSA database
3. Add multiple vehicles as needed
4. Every message is automatically saved to the database
5. Download completed survey data as JSON

### View Live Chats Page
1. Access via sidebar navigation
2. Monitor all conversations in real-time
3. View complete chat transcripts
4. Filter by status (in-progress/completed)
5. See collected survey data for completed sessions

## Survey Flow

The chatbot collects information in this order:

1. **Zip Code** - 5-digit US zip code
2. **Full Name** - First and last name
3. **Email Address** - Valid email format
4. **Vehicle Information** (repeatable)
   - VIN or Year/Make/Model (validated via NHTSA API)
   - Vehicle use (commuting, commercial, farming, business)
   - Blind spot warning equipped (yes/no)
   - **If commuting:**
     - Days per week used
     - One-way miles to work/school
   - **If commercial/farming/business:**
     - Annual mileage
5. **License Type** - Foreign, Personal, or Commercial
6. **License Status** - Valid or Suspended

## Project Structure
```
coverix_chatbot/
├── src/
│   ├── __init__.py           # Package initialization
│   ├── questions.py          # Survey questions and flow logic
│   ├── nhtsa_api.py          # NHTSA vehicle validation API
│   ├── frustration.py        # Frustration detection & zen quotes
│   ├── validators.py         # OpenAI validation with retry logic
│   ├── session.py            # Chat session state management
│   └── database.py           # SQLite database operations
├── pages/
│   └── view_live_chats.py    # Live chat monitoring dashboard
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── .env                      # API keys (DO NOT COMMIT)
├── .env.example              # Template for .env file
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

## Database Schema

Data is stored in `survey_data.db` with the following tables:

### `sessions`
- `session_id` (TEXT, PRIMARY KEY) - Unique session identifier
- `started_at` (TIMESTAMP) - Session start time
- `completed_at` (TIMESTAMP) - Session completion time
- `status` (TEXT) - 'in_progress', 'completed', or 'abandoned'
- `zip_code`, `full_name`, `email` - Personal information
- `license_type`, `license_status` - License information

### `messages`
- `id` (INTEGER, PRIMARY KEY)
- `session_id` (TEXT, FOREIGN KEY) - Links to sessions
- `timestamp` (TIMESTAMP) - Message timestamp
- `role` (TEXT) - 'user' or 'bot'
- `content` (TEXT) - Message content

### `vehicles`
- `id` (INTEGER, PRIMARY KEY)
- `session_id` (TEXT, FOREIGN KEY) - Links to sessions
- Vehicle details (identifier, use, blind spot warning, mileage data)

### `survey_data`
- `session_id` (TEXT, PRIMARY KEY, FOREIGN KEY)
- `completed_at` (TIMESTAMP)
- `raw_data` (TEXT) - Complete JSON of survey submission

### Query Database
```bash
# View all sessions
sqlite3 survey_data.db "SELECT * FROM sessions;"

# View all messages
sqlite3 survey_data.db "SELECT * FROM messages ORDER BY timestamp;"

# View completed surveys
sqlite3 survey_data.db "SELECT * FROM sessions WHERE status = 'completed';"
```

## Technologies

| Technology | Purpose |
|------------|---------|
| **OpenAI GPT-4** | Natural language processing and validation |
| **Streamlit** | Web interface and user experience |
| **SQLite** | Database storage (scalable to PostgreSQL) |
| **NHTSA API** | Vehicle information validation |
| **ZenQuotes API** | Frustration handling with motivational quotes |
| **Python 3.11+** | Core application logic |

## Features in Detail

### Natural Language Processing
- Handles varied user input (e.g., "yeah" → "yes", "I'm 25" → "25")
- Extracts structured data from conversational responses
- Provides context-aware validation

### Vehicle Validation
- Validates VIN numbers (17 characters)
- Verifies Year/Make/Model combinations against NHTSA database
- Provides suggestions for similar models if exact match not found
- Immediate feedback for invalid vehicles

### Error Handling
- Automatic retry (up to 3 attempts) for API failures
- Exponential backoff for rate limit errors
- Graceful degradation with user-friendly error messages
- API key validation on startup

### Real-time Monitoring
- Live chat transcripts updated in real-time
- Session status tracking (in-progress/completed)
- Export capabilities for completed surveys
- Full conversation history preserved

## Performance

- **Average Response Time:** 2-3 seconds (GPT-4 API)
- **Database Operations:** <100ms (SQLite)
- **Vehicle Validation:** 1-2 seconds (NHTSA API)
- **Concurrent Users:** Supported (separate sessions)

## Troubleshooting

### "OPENAI_API_KEY not found" Error
- Ensure `.env` file exists in project root
- Check that the file contains: `OPENAI_API_KEY=sk-proj-...`
- Restart the application after creating `.env`

### "Invalid OpenAI API key format" Error
- API key should start with `sk-`
- Ensure no quotes around the key in `.env`
- No spaces before or after the `=` sign

### Database Issues
- Delete `survey_data.db` to reset
- Database auto-creates on first run
- Check write permissions in project directory

### Slow Response Times
- GPT-4 API typically takes 2-3 seconds
- Check internet connection
- Consider using gpt-3.5-turbo for faster responses (less accurate)

## Development Notes

- **API Key Security:** Never commit `.env` file to version control
- **Database:** SQLite used for development; easily upgradable to PostgreSQL for production
- **Scalability:** Current architecture supports migration to cloud services (AWS, GCP, Azure)
- **Testing:** Complete a test survey to verify all features work correctly

## Future Enhancements

Potential improvements for production deployment:
- User authentication and login system
- Email notifications for completed surveys
- Admin dashboard with analytics
- Export to CSV/Excel
- Multi-language support
- Integration with CRM systems

## Support

For issues or questions, please check:
1. This README's troubleshooting section
2. Ensure all dependencies are installed
3. Verify API key is configured correctly
4. Check terminal output for error messages

---

**Built with ❤️ using OpenAI GPT-4, Streamlit, and Python**