"""
Slalom Capabilities Management System API

A FastAPI application that enables Slalom consultants to register their
capabilities and manage consulting expertise across the organization.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import os
from pathlib import Path

from database import get_db, init_db, Capability, Consultant

app = FastAPI(title="Slalom Capabilities Management API",
              description="API for managing consulting capabilities and consultant expertise")

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_db()

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/capabilities")
def get_capabilities(db: Session = Depends(get_db)):
    """Get all capabilities with their consultants"""
    capabilities = db.query(Capability).all()
    
    # Format response to match the original structure
    result = {}
    for cap in capabilities:
        result[cap.name] = {
            "description": cap.description,
            "practice_area": cap.practice_area,
            "skill_levels": cap.skill_levels.split(","),
            "certifications": cap.certifications.split(","),
            "industry_verticals": cap.industry_verticals.split(","),
            "capacity": cap.capacity,
            "consultants": [c.email for c in cap.consultants]
        }
    
    return result


@app.post("/capabilities/{capability_name}/register")
def register_for_capability(capability_name: str, email: str, db: Session = Depends(get_db)):
    """Register a consultant for a capability"""
    # Validate capability exists
    capability = db.query(Capability).filter(Capability.name == capability_name).first()
    if not capability:
        raise HTTPException(status_code=404, detail="Capability not found")

    # Get or create consultant
    consultant = db.query(Consultant).filter(Consultant.email == email).first()
    if not consultant:
        consultant = Consultant(email=email)
        db.add(consultant)
        db.flush()

    # Validate consultant is not already registered
    if consultant in capability.consultants:
        raise HTTPException(
            status_code=400,
            detail="Consultant is already registered for this capability"
        )

    # Add consultant to capability
    capability.consultants.append(consultant)
    db.commit()
    
    return {"message": f"Registered {email} for {capability_name}"}


@app.delete("/capabilities/{capability_name}/unregister")
def unregister_from_capability(capability_name: str, email: str, db: Session = Depends(get_db)):
    """Unregister a consultant from a capability"""
    # Validate capability exists
    capability = db.query(Capability).filter(Capability.name == capability_name).first()
    if not capability:
        raise HTTPException(status_code=404, detail="Capability not found")

    # Get consultant
    consultant = db.query(Consultant).filter(Consultant.email == email).first()
    if not consultant or consultant not in capability.consultants:
        raise HTTPException(
            status_code=400,
            detail="Consultant is not registered for this capability"
        )

    # Remove consultant from capability
    capability.consultants.remove(consultant)
    db.commit()
    
    return {"message": f"Unregistered {email} from {capability_name}"}
