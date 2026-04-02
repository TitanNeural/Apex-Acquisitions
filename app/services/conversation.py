"""
Conversation Manager - Core AI Receptionist Logic
Handles conversation flow, context management, and AI responses
Ready for integration with OpenAI GPT, Claude, or other LLMs
"""

from typing import Dict, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import logging
from enum import Enum

logger = logging.getLogger(__name__)

class ConversationState(str, Enum):
    """Conversation states throughout the call"""
    GREETING = "greeting"
    CAPTURING_NAME = "capturing_name"
    CAPTURING_PHONE = "capturing_phone"
    CAPTURING_VEHICLE = "capturing_vehicle"
    UNDERSTANDING_ISSUE = "understanding_issue"
    RECOMMENDING_APPOINTMENT = "recommending_appointment"
    SCHEDULING = "scheduling"
    CONFIRMATION = "confirmation"
    ENDED = "ended"

@dataclass
class ConversationResponse:
    """Response from conversation manager"""
    message: str
    next_action: str
    state: ConversationState
    requires_human_handoff: bool = False
    extracted_data: Dict = field(default_factory=dict)

@dataclass
class Conversation:
    """Conversation session details"""
    id: str
    call_id: str
    caller_phone: str
    caller_name: Optional[str] = None
    channel: str = "phone"  # phone, sms, web
    state: ConversationState = ConversationState.GREETING
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    messages: List[Dict] = field(default_factory=list)
    customer_data: Dict = field(default_factory=dict)
    
    def to_dict(self):
        return {
            "id": self.id,
            "call_id": self.call_id,
            "caller_phone": self.caller_phone,
            "caller_name": self.caller_name,
            "channel": self.channel,
            "state": self.state.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "messages": self.messages,
            "customer_data": self.customer_data
        }

class ConversationManager:
    """
    Manages conversation flow and AI receptionist interactions
    
    This is the core engine that orchestrates:
    - Greeting and welcoming customers
    - Capturing customer information
    - Understanding service needs
    - Recommending and scheduling appointments
    - Handling conversation state transitions
    
    Ready to integrate with LLMs like OpenAI for natural language understanding
    """
    
    def __init__(self):
        """Initialize conversation manager"""
        self.conversations: Dict[str, Conversation] = {}
        self.receptionist_name = "Makayla"
        
    def start_conversation(
        self,
        call_id: str,
        caller_phone: str,
        caller_name: Optional[str] = None,
        channel: str = "phone"
    ) -> Conversation:
        """
        Start a new conversation session
        
        Args:
            call_id: Unique call identifier
            caller_phone: Customer's phone number
            caller_name: Optional customer name (if available)
            channel: Communication channel (phone, sms, web)
        
        Returns:
            Conversation object
        """
        conversation_id = f"conv_{call_id}_{datetime.now().timestamp()}"
        
        conversation = Conversation(
            id=conversation_id,
            call_id=call_id,
            caller_phone=caller_phone,
            caller_name=caller_name,
            channel=channel,
            state=ConversationState.GREETING
        )
        
        self.conversations[call_id] = conversation
        logger.info(f"Started conversation: {conversation_id}")
        
        return conversation
    
    def get_greeting(self, conversation_id: str) -> ConversationResponse:
        """
        Get initial greeting from AI receptionist
        
        Returns:
            ConversationResponse with greeting message
        """
        # Lookup conversation by ID
        call_id = None
        for cid, conv in self.conversations.items():
            if conv.id == conversation_id:
                call_id = cid
                break
        
        if not call_id:
            logger.error(f"Conversation not found: {conversation_id}")
            return ConversationResponse(
                message="I'm sorry, I couldn't process your call. Please try again.",
                next_action="end_call",
                state=ConversationState.ENDED
            )
        
        conversation = self.conversations[call_id]
        conversation.state = ConversationState.CAPTURING_NAME
        
        # Greeting message from Makayla
        greeting_message = (
            f"Thank you for calling. This is {self.receptionist_name}. "
            "How can I help you today?"
        )
        
        # Add to message history
        conversation.messages.append({
            "timestamp": datetime.now().isoformat(),
            "sender": "receptionist",
            "message": greeting_message
        })
        
        logger.info(f"Greeting sent for conversation: {conversation_id}")
        
        return ConversationResponse(
            message=greeting_message,
            next_action="listen",  # Listen for customer response
            state=ConversationState.CAPTURING_NAME,
            extracted_data={}
        )
    
    def process_response(
        self,
        call_id: str,
        user_input: str,
        input_type: str = "speech"  # speech or text
    ) -> ConversationResponse:
        """
        Process customer response and determine next action
        
        This method orchestrates the conversation flow:
        1. Extract relevant information from user input
        2. Determine current state and next state
        3. Generate appropriate AI response
        4. Update conversation context
        
        Args:
            call_id: Unique call identifier
            user_input: Customer's spoken or typed message
            input_type: Type of input (speech or text)
        
        Returns:
            ConversationResponse with next message and action
        """
        if call_id not in self.conversations:
            logger.error(f"Call not found: {call_id}")
            return ConversationResponse(
                message="I'm sorry, I couldn't process that. Please try again.",
                next_action="end_call",
                state=ConversationState.ENDED
            )
        
        conversation = self.conversations[call_id]
        
        # Add user message to history
        conversation.messages.append({
            "timestamp": datetime.now().isoformat(),
            "sender": "customer",
            "message": user_input,
            "input_type": input_type
        })
        
        # State machine: determine next state and action based on current state
        if conversation.state == ConversationState.CAPTURING_NAME:
            return self._handle_name_capture(conversation, user_input)
        
        elif conversation.state == ConversationState.CAPTURING_PHONE:
            return self._handle_phone_capture(conversation, user_input)
        
        elif conversation.state == ConversationState.CAPTURING_VEHICLE:
            return self._handle_vehicle_capture(conversation, user_input)
        
        elif conversation.state == ConversationState.UNDERSTANDING_ISSUE:
            return self._handle_issue_understanding(conversation, user_input)
        
        elif conversation.state == ConversationState.RECOMMENDING_APPOINTMENT:
            return self._handle_appointment_recommendation(conversation, user_input)
        
        elif conversation.state == ConversationState.SCHEDULING:
            return self._handle_scheduling(conversation, user_input)
        
        else:
            logger.warning(f"Unknown state: {conversation.state}")
            return ConversationResponse(
                message="I'm not sure how to help with that. Let me connect you with someone.",
                next_action="transfer_to_human",
                state=conversation.state,
                requires_human_handoff=True
            )
    
    def _handle_name_capture(
        self,
        conversation: Conversation,
        user_input: str
    ) -> ConversationResponse:
        """Capture customer name"""
        # TODO: Integrate with NLP/LLM to extract name from user input
        # For now, treat entire input as potential name
        name = user_input.strip()
        
        if len(name) > 2:  # Basic validation
            conversation.customer_data["name"] = name
            conversation.state = ConversationState.CAPTURING_PHONE
            
            response_message = (
                f"Nice to meet you, {name}! "
                "May I get your phone number to keep on file?"
            )
            
            logger.info(f"Captured name: {name}")
            
            return ConversationResponse(
                message=response_message,
                next_action="listen",
                state=ConversationState.CAPTURING_PHONE,
                extracted_data={"name": name}
            )
        else:
            return ConversationResponse(
                message="I didn't quite catch that. Could you please tell me your name?",
                next_action="listen",
                state=ConversationState.CAPTURING_NAME
            )
    
    def _handle_phone_capture(
        self,
        conversation: Conversation,
        user_input: str
    ) -> ConversationResponse:
        """Capture customer phone number"""
        # TODO: Integrate with NLP/LLM to extract phone number
        # For now, extract digits from input
        phone = ''.join(filter(str.isdigit, user_input))
        
        if len(phone) >= 10:  # Basic phone validation
            conversation.customer_data["phone"] = phone
            conversation.state = ConversationState.CAPTURING_VEHICLE
            
            response_message = (
                "Great! Now, could you tell me what vehicle brings you in today? "
                "For example, the year, make, and model?"
            )
            
            logger.info(f"Captured phone: {phone}")
            
            return ConversationResponse(
                message=response_message,
                next_action="listen",
                state=ConversationState.CAPTURING_VEHICLE,
                extracted_data={"phone": phone}
            )
        else:
            return ConversationResponse(
                message="I didn't catch that phone number. Could you please repeat it?",
                next_action="listen",
                state=ConversationState.CAPTURING_PHONE
            )
    
    def _handle_vehicle_capture(
        self,
        conversation: Conversation,
        user_input: str
    ) -> ConversationResponse:
        """Capture vehicle information"""
        # TODO: Integrate with NLP/LLM to parse vehicle details
        conversation.customer_data["vehicle"] = user_input.strip()
        conversation.state = ConversationState.UNDERSTANDING_ISSUE
        
        response_message = (
            f"Thank you, a {user_input.strip()}. "
            "What seems to be the issue with your vehicle?"
        )
        
        logger.info(f"Captured vehicle: {user_input}")
        
        return ConversationResponse(
            message=response_message,
            next_action="listen",
            state=ConversationState.UNDERSTANDING_ISSUE,
            extracted_data={"vehicle": user_input.strip()}
        )
    
    def _handle_issue_understanding(
        self,
        conversation: Conversation,
        user_input: str
    ) -> ConversationResponse:
        """Understand customer's issue"""
        # TODO: Integrate with OpenAI or Claude to understand issue
        # Determine service category and urgency
        conversation.customer_data["issue"] = user_input.strip()
        conversation.state = ConversationState.RECOMMENDING_APPOINTMENT
        
        response_message = (
            "I understand. We can definitely help with that. "
            "I'd like to schedule an appointment for you. "
            "What day would work best for you?"
        )
        
        logger.info(f"Understood issue: {user_input}")
        
        return ConversationResponse(
            message=response_message,
            next_action="listen",
            state=ConversationState.RECOMMENDING_APPOINTMENT,
            extracted_data={"issue": user_input.strip()}
        )
    
    def _handle_appointment_recommendation(
        self,
        conversation: Conversation,
        user_input: str
    ) -> ConversationResponse:
        """Handle appointment recommendation and preference"""
        conversation.customer_data["preferred_date"] = user_input.strip()
        conversation.state = ConversationState.SCHEDULING
        
        response_message = (
            f"Perfect! I'll check our availability for {user_input.strip()}. "
            "What time works best for you?"
        )
        
        return ConversationResponse(
            message=response_message,
            next_action="listen",
            state=ConversationState.SCHEDULING,
            extracted_data={"preferred_date": user_input.strip()}
        )
    
    def _handle_scheduling(
        self,
        conversation: Conversation,
        user_input: str
    ) -> ConversationResponse:
        """Complete appointment scheduling"""
        # TODO: Integrate with Google Calendar, Calendly, or custom scheduling API
        conversation.customer_data["preferred_time"] = user_input.strip()
        conversation.state = ConversationState.CONFIRMATION
        
        response_message = (
            f"Excellent! I've scheduled your appointment for "
            f"{conversation.customer_data.get('preferred_date')} "
            f"at {user_input.strip()}. "
            f"We'll see you then! Is there anything else I can help with?"
        )
        
        logger.info(f"Appointment scheduled for: {conversation.customer_data}")
        
        return ConversationResponse(
            message=response_message,
            next_action="listen",
            state=ConversationState.CONFIRMATION,
            extracted_data={"preferred_time": user_input.strip()}
        )
    
    def end_conversation(self, call_id: str) -> Dict:
        """
        End conversation and save data
        
        Args:
            call_id: Unique call identifier
        
        Returns:
            Conversation summary
        """
        if call_id not in self.conversations:
            return {"status": "not_found"}
        
        conversation = self.conversations[call_id]
        conversation.state = ConversationState.ENDED
        conversation.updated_at = datetime.now()
        
        summary = {
            "call_id": call_id,
            "conversation_id": conversation.id,
            "duration": (conversation.updated_at - conversation.created_at).total_seconds(),
            "customer_data": conversation.customer_data,
            "messages_count": len(conversation.messages),
            "status": "completed"
        }
        
        logger.info(f"Conversation ended: {call_id}")
        # TODO: Save conversation data to database
        
        return summary
    
    def get_conversation_status(self, call_id: str) -> Optional[Dict]:
        """
        Get conversation status and details
        
        Args:
            call_id: Unique call identifier
        
        Returns:
            Conversation status or None if not found
        """
        if call_id not in self.conversations:
            return None
        
        conversation = self.conversations[call_id]
        return conversation.to_dict()