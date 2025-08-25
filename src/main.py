"""
FastAPI application for the medical secretary system.
"""

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
import uvicorn
import json
import time

from src.database import get_db, db_manager
from src.graph import medical_secretary_graph
from src.tools.whatsapp_tools import WhatsAppTools
from src.tools.clinic_info_tools import ClinicInfoTools
from src.tools.database_tools import DatabaseTools

# Create FastAPI app
app = FastAPI(
    title="Medical Secretary AI",
    description="AI-powered medical secretary with appointment scheduling and WhatsApp integration",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="src/static"), name="static")


class TestAgentRequest(BaseModel):
    """Request model for testing the agent."""
    message: str
    conversation_state: Optional[Dict[str, Any]] = None


class TestAgentResponse(BaseModel):
    """Response model for testing the agent."""
    response: str
    conversation_state: Dict[str, Any]
    intent: str
    status: str


@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup."""
    # Create database tables
    db_manager.create_tables()
    print("Database tables created successfully!")


@app.get("/")
async def root():
    """Root endpoint - serve the doctor interface."""
    return FileResponse("src/static/index.html")

@app.get("/doctor")
async def doctor_interface():
    """Doctor interface endpoint."""
    return FileResponse("src/static/index.html")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/test_agent", response_model=TestAgentResponse)
async def test_agent(
    request: TestAgentRequest,
    db: Session = Depends(get_db)
):
    """
    Test the AI agent with a user message.
    
    This endpoint accepts a JSON payload with the user's message and optional
    conversation state, processes it through the LangGraph, and returns the
    chatbot's response.
    """
    try:
        # Ensure conversation_state is not None
        conversation_state = request.conversation_state or {
            "messages": [],
            "intent": "",
            "collected_params": {},
            "required_params": [],
            "status": "",
            "modification_mode": False
        }
        
        # Process the message through the LangGraph
        result = medical_secretary_graph.process_message(
            user_message=request.message,
            conversation_state=conversation_state,
            db_session=db
        )
        
        return TestAgentResponse(
            response=result["response"],
            conversation_state=result["conversation_state"],
            intent=result["intent"],
            status=result["status"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing message: {str(e)}"
        )


@app.get("/conversation_history/{thread_id}")
async def get_conversation_history(thread_id: str = "default"):
    """Get conversation history for a specific thread."""
    try:
        history = medical_secretary_graph.get_conversation_history(thread_id)
        return {"thread_id": thread_id, "history": history}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving conversation history: {str(e)}"
        )


@app.delete("/conversation/{thread_id}")
async def reset_conversation(thread_id: str = "default"):
    """Reset conversation for a specific thread."""
    try:
        medical_secretary_graph.reset_conversation(thread_id)
        return {"message": f"Conversation reset for thread {thread_id}"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error resetting conversation: {str(e)}"
        )


# Tools instances
whatsapp_tools = WhatsAppTools()
clinic_info_tools = ClinicInfoTools()


@app.get("/webhook")
async def verify_webhook(
    hub_mode: str = Query(..., alias="hub.mode"),
    hub_challenge: str = Query(..., alias="hub.challenge"),
    hub_verify_token: str = Query(..., alias="hub.verify_token")
):
    """Verify webhook for Meta API validation."""
    try:
        challenge = whatsapp_tools.verify_webhook(
            mode=hub_mode,
            token=hub_verify_token,
            challenge=hub_challenge
        )
        
        if challenge:
            return int(challenge)
        else:
            raise HTTPException(status_code=403, detail="Verification failed")
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Webhook verification error: {str(e)}"
        )


@app.post("/webhook")
async def receive_webhook(
    webhook_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Receive WhatsApp messages via webhook."""
    try:
        # Log the full webhook payload for debugging
        print(f"Webhook received: {json.dumps(webhook_data, indent=2)}")
        
        # Extract user message from webhook
        message_data = whatsapp_tools.extract_message_from_webhook(webhook_data)
        
        if not message_data:
            return {"status": "no_message"}
        
        # Import conversation state manager
        from src.tools.conversation_state_manager import ConversationStateManager
        
        # Get or create conversation state for this user
        state_manager = ConversationStateManager(db)
        conversation_state = state_manager.get_conversation_state(
            channel_id=message_data["from"],
            channel_type="whatsapp"
        )
        
        # Ensure conversation_state is not None
        if conversation_state is None:
            conversation_state = {
                "messages": [],
                "intent": "",
                "collected_params": {},
                "required_params": [],
                "status": "",
                "modification_mode": False
            }
        
        # Process the message through the LangGraph
        result = medical_secretary_graph.process_message(
            user_message=message_data["text"],
            conversation_state=conversation_state,  # Use existing or new conversation state
            db_session=db,
            channel_id=message_data["from"],
            channel_type="whatsapp"
        )
        
        # Update conversation state for next message
        if result.get("conversation_state"):
            state_manager.update_conversation_state(
                channel_id=message_data["from"],
                conversation_state=result["conversation_state"],
                channel_type="whatsapp"
            )
        
        # Send response back to user via WhatsApp
        if result["response"]:
            whatsapp_response = whatsapp_tools.send_text_message(
                to_phone_number=message_data["from"],
                message_text=result["response"]
            )
            
            if not whatsapp_response.get("success"):
                print(f"Failed to send WhatsApp response: {whatsapp_response}")
        
        return {
            "status": "processed",
            "message_id": message_data["message_id"],
            "response": result["response"]
        }
        
    except Exception as e:
        print(f"Error processing webhook: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Webhook processing error: {str(e)}"
        )


@app.post("/webhook_test")
async def test_webhook(
    request: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Test webhook processing with simulated WhatsApp message.
    
    This endpoint accepts a JSON payload that simulates a WhatsApp message
    and processes it through the main webhook logic.
    """
    try:
        # Simulate webhook data
        webhook_data = {
            "object": "whatsapp_business_account",
            "entry": [{
                "changes": [{
                    "value": {
                        "messages": [{
                            "from": request.get("from", "1234567890"),
                            "id": "test_message_id",
                            "timestamp": str(int(time.time())),
                            "text": {"body": request.get("message", "Hello!")},
                            "type": "text"
                        }]
                    }
                }]
            }]
        }
        
        # Process through webhook logic
        result = await receive_webhook(webhook_data, db)
        
        return {
            "status": "test_completed",
            "webhook_result": result,
            "simulated_data": webhook_data
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Webhook test error: {str(e)}"
        )


@app.post("/test_whatsapp")
async def test_whatsapp_send():
    """Test WhatsApp message sending (requires valid credentials)."""
    try:
        # Test sending a simple message
        result = whatsapp_tools.send_text_message(
            to_phone_number="1234567890",
            message_text="This is a test message from the Medical Secretary AI!"
        )
        
        return {
            "status": "whatsapp_test_completed",
            "result": result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"WhatsApp test error: {str(e)}"
        )


# Clinic Information Endpoints
@app.get("/clinic/info")
async def get_clinic_info():
    """Get general clinic information."""
    try:
        return {
            "clinic_name": clinic_info_tools.get_clinic_name(),
            "address": clinic_info_tools.get_full_address(),
            "contact": clinic_info_tools.get_contact_info(),
            "hours": clinic_info_tools.get_opening_hours(),
            "services": clinic_info_tools.get_services(),
            "specialties": clinic_info_tools.get_specialties()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving clinic info: {str(e)}"
        )


@app.get("/clinic/search")
async def search_clinic_info(query: str):
    """Search clinic information."""
    try:
        results = clinic_info_tools.search_clinic_info(query)
        return {
            "query": query,
            "results": results
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error searching clinic info: {str(e)}"
        )


@app.get("/clinic/specialty/{specialty_name}")
async def get_specialty_info(specialty_name: str):
    """Get information about a specific medical specialty."""
    try:
        specialty = clinic_info_tools.get_specialty_by_name(specialty_name)
        if specialty:
            return specialty
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Specialty '{specialty_name}' not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving specialty info: {str(e)}"
        )


@app.get("/clinic/insurance/{insurance_name}")
async def check_insurance(insurance_name: str):
    """Check if a specific insurance plan is accepted."""
    try:
        is_accepted = clinic_info_tools.check_insurance_accepted(insurance_name)
        return {
            "insurance_name": insurance_name,
            "accepted": is_accepted
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error checking insurance: {str(e)}"
        )


# Enhanced Appointment Management Endpoints
@app.get("/appointments/date/{date}")
async def get_appointments_by_date(
    date: str,
    db: Session = Depends(get_db)
):
    """Get all appointments for a specific date."""
    try:
        from datetime import datetime
        appointment_date = datetime.strptime(date, "%Y-%m-%d")
        
        db_tools = DatabaseTools(db)
        appointments = db_tools.get_appointments_by_date(appointment_date)
        
        return {
            "date": date,
            "appointments": [
                {
                    "id": apt.id,
                    "patient_id": apt.patient_id,
                    "doctor_id": apt.doctor_id,
                    "datetime": apt.appointment_datetime.isoformat(),
                    "type": apt.appointment_type,
                    "status": apt.status.value
                }
                for apt in appointments
            ]
        }
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving appointments: {str(e)}"
        )


@app.get("/appointments/upcoming")
async def get_upcoming_appointments(
    days: int = 7,
    db: Session = Depends(get_db)
):
    """Get upcoming appointments within specified days."""
    try:
        db_tools = DatabaseTools(db)
        appointments = db_tools.get_upcoming_appointments(days)
        
        return {
            "days_ahead": days,
            "appointments": [
                {
                    "id": apt.id,
                    "patient_id": apt.patient_id,
                    "doctor_id": apt.doctor_id,
                    "datetime": apt.appointment_datetime.isoformat(),
                    "type": apt.appointment_type,
                    "status": apt.status.value
                }
                for apt in appointments
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving upcoming appointments: {str(e)}"
        )


@app.put("/appointments/{appointment_id}/status")
async def update_appointment_status(
    appointment_id: int,
    status: str,
    db: Session = Depends(get_db)
):
    """Update appointment status."""
    try:
        from src.models.appointment import AppointmentStatus
        
        # Validate status
        try:
            new_status = AppointmentStatus(status)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Must be one of: {[s.value for s in AppointmentStatus]}"
            )
        
        db_tools = DatabaseTools(db)
        appointment = db_tools.update_appointment_status(appointment_id, new_status)
        
        if appointment:
            return {
                "appointment_id": appointment_id,
                "new_status": status,
                "message": "Status updated successfully"
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Appointment {appointment_id} not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error updating appointment status: {str(e)}"
        )


@app.put("/appointments/{appointment_id}/datetime")
async def update_appointment_datetime(
    appointment_id: int,
    new_datetime: str,
    db: Session = Depends(get_db)
):
    """Update appointment date and time."""
    try:
        from datetime import datetime
        
        # Parse the new datetime
        try:
            parsed_datetime = datetime.fromisoformat(new_datetime.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid datetime format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"
            )
        
        db_tools = DatabaseTools(db)
        appointment = db_tools.update_appointment_datetime(appointment_id, parsed_datetime)
        
        if appointment:
            return {
                "appointment_id": appointment_id,
                "new_datetime": new_datetime,
                "message": "Appointment datetime updated successfully"
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Appointment {appointment_id} not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error updating appointment datetime: {str(e)}"
        )


@app.get("/appointments/statistics")
async def get_appointment_statistics(db: Session = Depends(get_db)):
    """Get appointment statistics."""
    try:
        db_tools = DatabaseTools(db)
        stats = db_tools.get_appointment_statistics()
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving statistics: {str(e)}"
        )


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
