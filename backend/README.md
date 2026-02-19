# FastAPI Backend - College PR Event Dashboard

Simple FastAPI backend for managing events, reactions, feedback, and announcements.

## Setup

1. **Create a virtual environment:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate  # On Windows
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run the server:**
```bash
uvicorn main:app --reload
```

The API will be available at: `http://localhost:8000`

## API Documentation

Once running, visit:
- Interactive API docs: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

## Endpoints

### Events
- `POST /api/events` - Create a new event
- `GET /api/events` - List all events
- `GET /api/events/{event_id}` - Get specific event

### Reactions
- `POST /api/reactions` - Add a reaction to an event
- `GET /api/reactions/{event_id}` - Get reaction counts for an event

### Feedback
- `POST /api/feedback` - Submit anonymous feedback
- `GET /api/feedback` - Get all feedback
- `GET /api/feedback/{event_id}` - Get feedback for specific event

### Announcements
- `POST /api/announcement` - Create/update announcement
- `GET /api/announcement` - Get latest announcement

### Stats
- `GET /api/stats` - Get dashboard statistics

## Storage

Currently uses **in-memory storage** for simplicity. All data will be lost when the server restarts.

To persist data, you can later upgrade to SQLite by uncommenting the SQLAlchemy implementation.
