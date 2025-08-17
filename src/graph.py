"""
LangGraph definition for the medical secretary system.
"""

from typing import Dict, Any, List, TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from src.agents.orchestrator_agent import OrchestratorAgent
from src.agents.calendar_agent import CalendarAgent
from src.agents.notification_agent import NotificationAgent
from src.tools.database_tools import DatabaseTools
from src.tools.google_calendar_tools import GoogleCalendarTools
from src.tools.whatsapp_tools import WhatsAppTools


class AgentState(TypedDict):
    """State class for the LangGraph."""
    messages: List[Dict[str, str]]
    intent: str
    collected_params: Dict[str, Any]
    required_params: List[str]
    status: str
    next_agent: str
    user_message: str
    response: str
    conversation_state: Dict[str, Any]
    channel_id: str  # WhatsApp phone number or other channel identifier
    channel_type: str  # "whatsapp", "web", etc.


class MedicalSecretaryGraph:
    """LangGraph implementation for the medical secretary system."""
    
    def __init__(self):
        """Initialize the medical secretary graph."""
        # Initialize tools
        self.calendar_tools = GoogleCalendarTools()
        self.whatsapp_tools = WhatsAppTools()
        
        # Initialize agents (will be set with session later)
        self.orchestrator_agent = None
        self.calendar_agent = None
        self.notification_agent = None
        
        # Create the graph
        self.graph = self._create_graph()
        self.app = self.graph.compile(checkpointer=MemorySaver())
    
    def _initialize_agents(self, db_session):
        """Initialize agents with database session."""
        if self.orchestrator_agent is None or self.calendar_agent is None or self.notification_agent is None:
            db_tools = DatabaseTools(db_session)
            self.orchestrator_agent = OrchestratorAgent(db_tools, self.calendar_tools)
            self.calendar_agent = CalendarAgent(db_tools, self.calendar_tools)
            self.notification_agent = NotificationAgent(self.whatsapp_tools, db_tools)
        
        # Create the graph
        self.graph = self._create_graph()
        self.app = self.graph.compile(checkpointer=MemorySaver())
    
    def _create_graph(self) -> StateGraph:
        """Create the LangGraph with nodes and edges."""
        # Create the state graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("orchestrator", self._orchestrator_node)
        workflow.add_node("calendar_agent", self._calendar_agent_node)
        workflow.add_node("end", self._end_node)
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "orchestrator",
            self._route_to_agent,
            {
                "calendar_agent": "calendar_agent",
                "end": "end"
            }
        )
        
        # Add edges from calendar agent
        workflow.add_edge("calendar_agent", "end")
        
        # Set entry point
        workflow.set_entry_point("orchestrator")
        
        return workflow
    
    def _orchestrator_node(self, state: AgentState) -> AgentState:
        """Orchestrator agent node."""
        # Process the user message
        result = self.orchestrator_agent.process_message(
            state["user_message"],
            state["conversation_state"]
        )
        
        # Update state
        state["response"] = result["response"]
        state["conversation_state"] = result["conversation_state"]
        state["next_agent"] = result.get("next_agent", "end")
        state["intent"] = state["conversation_state"].get("intent", "")
        state["collected_params"] = state["conversation_state"].get("collected_params", {})
        state["required_params"] = state["conversation_state"].get("required_params", [])
        state["status"] = state["conversation_state"].get("status", "")
        
        return state
    
    def _calendar_agent_node(self, state: AgentState) -> AgentState:
        """Calendar agent node."""
        # Process with calendar agent if needed
        if state["next_agent"] == "calendar_agent":
            result = self.calendar_agent.process_scheduling_request(
                state["user_message"],
                state["collected_params"],
                state["required_params"]
            )
            
            # Update state
            state["response"] = result["response"]
            state["collected_params"] = result["collected_params"]
            state["required_params"] = result["required_params"]
            state["status"] = result["status"]
            
            # Update conversation state
            state["conversation_state"]["collected_params"] = result["collected_params"]
            state["conversation_state"]["required_params"] = result["required_params"]
            state["conversation_state"]["status"] = result["status"]
        
        return state
    
    def _end_node(self, state: AgentState) -> AgentState:
        """End node - final response."""
        return state
    
    def _route_to_agent(self, state: AgentState) -> str:
        """Route to the next agent based on state."""
        next_agent = state.get("next_agent", "end")
        
        if next_agent == "calendar_agent":
            return "calendar_agent"
        else:
            return "end"
    
    def process_message(
        self,
        user_message: str,
        conversation_state: Dict[str, Any] = None,
        db_session = None,
        channel_id: str = None,
        channel_type: str = "web"
    ) -> Dict[str, Any]:
        """Process a user message through the graph."""
        # Initialize agents if needed
        if db_session:
            self._initialize_agents(db_session)
        
        # Initialize conversation state if not provided
        if conversation_state is None:
            conversation_state = {
                "messages": [],
                "intent": "",
                "collected_params": {},
                "required_params": [],
                "status": "",
                "modification_mode": False
            }
        
        # Create initial state
        initial_state = AgentState(
            messages=conversation_state.get("messages", []),
            intent=conversation_state.get("intent", ""),
            collected_params=conversation_state.get("collected_params", {}),
            required_params=conversation_state.get("required_params", []),
            status=conversation_state.get("status", ""),
            next_agent="",
            user_message=user_message,
            response="",
            conversation_state=conversation_state,
            channel_id=channel_id or "unknown",
            channel_type=channel_type
        )
        
        # Run the graph
        config = {"configurable": {"thread_id": "default"}}
        result = self.app.invoke(initial_state, config)
        
        return {
            "response": result["response"],
            "conversation_state": result["conversation_state"],
            "intent": result["intent"],
            "status": result["status"]
        }
    
    def get_conversation_history(self, thread_id: str = "default") -> List[Dict[str, Any]]:
        """Get conversation history for a thread."""
        try:
            # Get the thread from memory
            thread = self.app.get_state({"configurable": {"thread_id": thread_id}})
            if thread and "messages" in thread:
                return thread["messages"]
        except Exception as e:
            print(f"Error getting conversation history: {e}")
        
        return []
    
    def reset_conversation(self, thread_id: str = "default"):
        """Reset conversation for a thread."""
        try:
            # Clear the thread from memory
            self.app.delete_state({"configurable": {"thread_id": thread_id}})
        except Exception as e:
            print(f"Error resetting conversation: {e}")


# Global graph instance
medical_secretary_graph = MedicalSecretaryGraph()
