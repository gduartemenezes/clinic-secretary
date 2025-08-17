"""
FastAPI application for the medical secretary system.
"""

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
import uvicorn
import json
import time

from src.database import get_db, db_manager
from src.graph import medical_secretary_graph
from src.tools.whatsapp_tools import WhatsAppTools

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
    """Root endpoint."""
    return {
        "message": "Medical Secretary AI API",
        "version": "1.0.0",
        "status": "running"
    }


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
        # Process the message through the LangGraph
        result = medical_secretary_graph.process_message(
            user_message=request.message,
            conversation_state=request.conversation_state,
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


# WhatsApp Webhook Endpoints
whatsapp_tools = WhatsAppTools()


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
        
        # Process the message through the LangGraph
        result = medical_secretary_graph.process_message(
            user_message=message_data["text"],
            conversation_state=None,  # Start new conversation
            db_session=db,
            channel_id=message_data["from"],
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


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
