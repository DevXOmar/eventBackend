"""
Simple FastAPI backend for College PR Event Dashboard
Single-file implementation with in-memory storage
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

# Initialize FastAPI app
app = FastAPI(title="College PR Event Dashboard API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# In-Memory Storage
# ============================================
events_db = []
reactions_db = {}  # {event_id: {"🔥": count, "😮": count, ...}}
feedback_db = []
announcement_db = {
    "message": "Welcome to Event Pulse - Your hub for campus events and engagement!", 
    "created_at": datetime.now().isoformat()
}

# Auto-increment IDs
event_id_counter = 1
feedback_id_counter = 1


# ============================================
# Initialize Default Events
# ============================================
def initialize_default_events():
    """Initialize the database with default events"""
    global event_id_counter, events_db, reactions_db
    
    default_events = [
        {
            "title": "KMIT Evening Saanjh",
            "description": "An enchanting evening of music, culture, and celebration. Join us for a memorable cultural fest featuring performances, food, and fun activities.",
            "date": "2026-03-20T18:00:00"
        },
        {
            "title": "Patang Utsav",
            "description": "Celebrate the spirit of kite flying! Join us for a colorful kite festival with competitions, food stalls, and exciting prizes. Let your kites soar high!",
            "date": "2026-04-05T15:00:00"
        },
        {
            "title": "V-MUN",
            "description": "Virtual Model United Nations - A prestigious forum for debate, diplomacy, and global leadership. Participate in engaging discussions on international issues.",
            "date": "2026-04-15T09:00:00"
        }
    ]
    
    for event_data in default_events:
        event = {
            "id": event_id_counter,
            "title": event_data["title"],
            "description": event_data["description"],
            "date": event_data["date"],
            "created_at": datetime.now().isoformat()
        }
        events_db.append(event)
        
        # Initialize reactions for this event
        reactions_db[event_id_counter] = {
            "🔥": 0,
            "😮": 0,
            "👏": 0,
            "❤️": 0
        }
        
        event_id_counter += 1

# Initialize default events on startup
initialize_default_events()


# ============================================
# Pydantic Models
# ============================================

class ReactionType(str, Enum):
    FIRE = "🔥"
    WOW = "😮"
    CLAP = "👏"
    HEART = "❤️"


class EventCreate(BaseModel):
    title: str
    description: str
    date: str  # ISO format date string


class EventResponse(BaseModel):
    id: int
    title: str
    description: str
    date: str
    created_at: str


class ReactionRequest(BaseModel):
    event_id: int
    reaction: ReactionType


class ReactionResponse(BaseModel):
    event_id: int
    reactions: dict  # {"🔥": 5, "😮": 3, ...}


class FeedbackSubmit(BaseModel):
    event_id: int
    message: str
    rating: Optional[int] = None  # 1-5 stars


class FeedbackResponse(BaseModel):
    id: int
    event_id: int
    message: str
    rating: Optional[int]
    created_at: str


class AnnouncementCreate(BaseModel):
    message: str


class AnnouncementResponse(BaseModel):
    message: str
    created_at: Optional[str]


# ============================================
# Event Endpoints
# ============================================

@app.post("/api/events", response_model=EventResponse)
async def create_event(event: EventCreate):
    """Create a new event"""
    global event_id_counter
    
    new_event = {
        "id": event_id_counter,
        "title": event.title,
        "description": event.description,
        "date": event.date,
        "created_at": datetime.now().isoformat()
    }
    
    events_db.append(new_event)
    
    # Initialize reactions for this event
    reactions_db[event_id_counter] = {
        "🔥": 0,
        "😮": 0,
        "👏": 0,
        "❤️": 0
    }
    
    event_id_counter += 1
    
    return new_event


@app.get("/api/events", response_model=List[EventResponse])
async def list_events():
    """Get all events"""
    return events_db


@app.get("/api/events/{event_id}", response_model=EventResponse)
async def get_event(event_id: int):
    """Get a specific event by ID"""
    for event in events_db:
        if event["id"] == event_id:
            return event
    raise HTTPException(status_code=404, detail="Event not found")


# ============================================
# Reaction Endpoints
# ============================================

@app.post("/api/reactions", response_model=ReactionResponse)
async def add_reaction(reaction_req: ReactionRequest):
    """Increment reaction count for an event"""
    event_id = reaction_req.event_id
    
    # Check if event exists
    event_exists = any(e["id"] == event_id for e in events_db)
    if not event_exists:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Initialize reactions if not exists
    if event_id not in reactions_db:
        reactions_db[event_id] = {
            "🔥": 0,
            "😮": 0,
            "👏": 0,
            "❤️": 0
        }
    
    # Increment the reaction
    reactions_db[event_id][reaction_req.reaction.value] += 1
    
    return {
        "event_id": event_id,
        "reactions": reactions_db[event_id]
    }


@app.get("/api/reactions/{event_id}", response_model=ReactionResponse)
async def get_reactions(event_id: int):
    """Get reaction counts for an event"""
    # Check if event exists
    event_exists = any(e["id"] == event_id for e in events_db)
    if not event_exists:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Return reactions or default
    reactions = reactions_db.get(event_id, {
        "🔥": 0,
        "😮": 0,
        "👏": 0,
        "❤️": 0
    })
    
    return {
        "event_id": event_id,
        "reactions": reactions
    }


# ============================================
# Feedback Endpoints
# ============================================

@app.post("/api/feedback", response_model=FeedbackResponse)
async def submit_feedback(feedback: FeedbackSubmit):
    """Submit anonymous feedback for an event"""
    global feedback_id_counter
    
    # Check if event exists
    event_exists = any(e["id"] == feedback.event_id for e in events_db)
    if not event_exists:
        raise HTTPException(status_code=404, detail="Event not found")
    
    new_feedback = {
        "id": feedback_id_counter,
        "event_id": feedback.event_id,
        "message": feedback.message,
        "rating": feedback.rating,
        "created_at": datetime.now().isoformat()
    }
    
    feedback_db.append(new_feedback)
    feedback_id_counter += 1
    
    return new_feedback


@app.get("/api/feedback", response_model=List[FeedbackResponse])
async def list_all_feedback():
    """Get all feedback"""
    return feedback_db


@app.get("/api/feedback/{event_id}", response_model=List[FeedbackResponse])
async def list_event_feedback(event_id: int):
    """Get feedback for a specific event"""
    event_feedback = [f for f in feedback_db if f["event_id"] == event_id]
    return event_feedback


# ============================================
# Announcement Endpoints
# ============================================

@app.post("/api/announcement", response_model=AnnouncementResponse)
async def create_announcement(announcement: AnnouncementCreate):
    """Create or update announcement message"""
    announcement_db["message"] = announcement.message
    announcement_db["created_at"] = datetime.now().isoformat()
    
    return announcement_db


@app.get("/api/announcement", response_model=AnnouncementResponse)
async def get_announcement():
    """Get the latest announcement"""
    return announcement_db


# ============================================
# Health Check
# ============================================

@app.get("/")
async def root():
    """API health check"""
    return {
        "status": "ok",
        "message": "College PR Event Dashboard API",
        "endpoints": {
            "events": "/api/events",
            "reactions": "/api/reactions",
            "feedback": "/api/feedback",
            "announcement": "/api/announcement"
        }
    }


@app.get("/api/stats")
async def get_stats():
    """Get dashboard statistics"""
    return {
        "total_events": len(events_db),
        "total_feedback": len(feedback_db),
        "total_reactions": sum(
            sum(reactions.values()) 
            for reactions in reactions_db.values()
        )
    }


# ============================================
# Run with: uvicorn main:app --reload
# ============================================
