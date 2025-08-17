# Medical Secretary AI

An AI-powered medical secretary system with appointment scheduling, WhatsApp integration, and intelligent conversation management.

## Features

- **Appointment Scheduling**: AI-powered appointment booking with Google Calendar integration
- **Intent Detection**: Smart routing of user requests to appropriate agents
- **Database Management**: SQLAlchemy-based data persistence for patients, doctors, and appointments
- **LangGraph Orchestration**: Advanced conversation flow management
- **FastAPI Backend**: Modern, fast web API framework
- **WhatsApp Integration**: Meta API integration for patient communication (Phase 2)

## Technology Stack

- **Python 3.12**
- **FastAPI** - Modern web framework
- **LangGraph** - AI agent orchestration
- **SQLAlchemy** - Database ORM
- **Google Calendar API** - Calendar integration
- **UV** - Fast Python package manager

## Project Structure

```
src/
├── agents/           # AI agents (Orchestrator, Calendar, etc.)
├── tools/            # Utility tools (Database, Google Calendar)
├── models/           # Database models
├── config/           # Configuration files
├── main.py           # FastAPI application
├── database.py       # Database configuration
└── graph.py          # LangGraph definition
```

## Setup Instructions

### Prerequisites

- Python 3.12+
- UV package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd cursor-secretaria
   ```

2. **Initialize the project with UV**
   ```bash
   uv init --python 3.12
   ```

3. **Install dependencies**
   ```bash
   uv sync
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your actual credentials
   ```

5. **Create database tables**
   The database tables will be created automatically when you start the application.

### Environment Variables

Copy `env.example` to `.env` and configure:

- **Database**: SQLite by default (can be changed to PostgreSQL)
- **Google Calendar**: Service account or OAuth2 credentials
- **Meta API**: WhatsApp Business API credentials (for Phase 2)

## Running the Application

### Development Mode

```bash
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

### Core Endpoints
- `GET /` - Root endpoint
- `GET /health` - Health check
- `POST /test_agent` - Test the AI agent
- `GET /conversation_history/{thread_id}` - Get conversation history
- `DELETE /conversation/{thread_id}` - Reset conversation

### WhatsApp Integration (Phase 2)
- `GET /webhook` - Meta API webhook verification
- `POST /webhook` - Receive WhatsApp messages
- `POST /webhook_test` - Test webhook processing
- `POST /test_whatsapp` - Test WhatsApp message sending

## Testing the Agent

Use the `/test_agent` endpoint to test the AI secretary:

```bash
curl -X POST "http://localhost:8000/test_agent" \
     -H "Content-Type: application/json" \
     -d '{"message": "I need to schedule an appointment"}'
```

## WhatsApp Integration Setup

### 1. Meta Business Account Setup
1. Create a Meta Business Account
2. Set up WhatsApp Business Platform
3. Configure webhook URL: `https://your-domain.com/webhook`
4. Set webhook verify token in your `.env` file

### 2. Environment Variables
```bash
# Copy and configure these in your .env file
META_ACCESS_TOKEN=your_access_token
META_PHONE_NUMBER_ID=your_phone_number_id
META_BUSINESS_ACCOUNT_ID=your_business_account_id
META_VERIFY_TOKEN=your_webhook_verify_token
```

### 3. Testing WhatsApp Integration
```bash
# Test webhook processing
curl -X POST "http://localhost:8000/webhook_test" \
     -H "Content-Type: application/json" \
     -d '{"from": "1234567890", "message": "Hello!"}'

# Test WhatsApp sending (requires valid credentials)
curl -X POST "http://localhost:8000/test_whatsapp"
```

## Development Phases

### Phase 1: MVP Core Foundation ✅
- [x] Project initialization and dependency management
- [x] Folder structure and modularity
- [x] Database models and tools
- [x] Google Calendar integration
- [x] Basic agents (Orchestrator, Calendar)
- [x] LangGraph implementation
- [x] FastAPI setup

### Phase 2: WhatsApp Integration ✅
- ✅ Meta API integration via WhatsApp Business API
- ✅ Webhook infrastructure for receiving messages
- ✅ Notification agent for appointment reminders and confirmations
- ✅ WhatsApp message sending capabilities
- ✅ Template message support for structured notifications

### Phase 3: Enhanced Capabilities
- Clinic information agent
- Complete CRUD operations
- Error handling improvements

### Phase 4: Doctor Interface & Deployment
- Web interface for doctors
- Docker containerization
- Production deployment

## Contributing

1. Follow the project structure and coding standards
2. Use classes instead of functions (Python code style rule)
3. Always use UV for dependency management
4. Ensure Python 3.12 compatibility

## License

[Add your license here]
