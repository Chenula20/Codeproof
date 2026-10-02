"""Student Event Management System — FastAPI application."""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from backend.database import init_db, reset_db
from backend.auth import create_user, authenticate_user, create_access_token, verify_token
from backend.events import create_event, get_events, get_event, delete_event
from backend.bookings import create_booking, get_user_bookings, cancel_booking

app = FastAPI(
    title="Student Event Management System",
    description="Demo project for CodeProof",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Pydantic Models ──────────────────────────────────────────────────

class UserRegister(BaseModel):
    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class EventCreate(BaseModel):
    title: str
    description: str = ""
    date: str
    capacity: int = 50


class BookingCreate(BaseModel):
    event_id: int
    seats: int = 1


# ── Auth Endpoints ───────────────────────────────────────────────────

@app.post("/api/auth/register")
async def register(user: UserRegister):
    """Register a new user."""
    try:
        result = create_user(user.username, user.email, user.password)
        return {"message": "User registered successfully", "user": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/auth/login")
async def login(user: UserLogin):
    """Login and get access token."""
    result = authenticate_user(user.username, user.password)
    if result is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(data={"sub": result["username"], "user_id": result["id"]})
    return {"access_token": token, "token_type": "bearer", "user": result}


# ── Events Endpoints ─────────────────────────────────────────────────

@app.get("/api/events")
async def list_events():
    """Get all events."""
    events = get_events()
    return {"events": events}


@app.get("/api/events/{event_id}")
async def retrieve_event(event_id: int):
    """Get a specific event."""
    event = get_event(event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@app.post("/api/events")
async def create_new_event(event: EventCreate):
    """Create a new event."""
    try:
        result = create_event(event.title, event.description, event.date, event.capacity)
        return {"message": "Event created", "event": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/api/events/{event_id}")
async def remove_event(event_id: int):
    """Delete an event."""
    deleted = delete_event(event_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Event not found")
    return {"message": "Event deleted"}


# ── Booking Endpoints ────────────────────────────────────────────────

@app.post("/api/bookings")
async def book_event(booking: BookingCreate, token: str = Depends(lambda: None)):
    """Create a new booking."""
    try:
        # For demo, use user_id=1 if no token provided
        user_id = 1
        if token:
            payload = verify_token(token)
            if payload:
                user_id = payload.get("user_id", 1)

        result = create_booking(user_id, booking.event_id, booking.seats)
        return {"message": "Booking created", "booking": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/bookings/{user_id}")
async def list_user_bookings(user_id: int):
    """Get all bookings for a user."""
    bookings = get_user_bookings(user_id)
    return {"bookings": bookings}


@app.delete("/api/bookings/{booking_id}")
async def cancel_user_booking(booking_id: int, user_id: int):
    """Cancel a booking."""
    cancelled = cancel_booking(booking_id, user_id)
    if not cancelled:
        raise HTTPException(status_code=404, detail="Booking not found")
    return {"message": "Booking cancelled"}


# ── Health Check ─────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "healthy"}


# ── Startup ──────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup():
    init_db()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8001, reload=True)
