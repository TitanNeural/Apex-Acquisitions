"""
Conversation Manager - Core Lead Intake Logic for ApexAcquisitions
Handles conversation flow, context management, and AI responses
for real estate wholesaling lead qualification.
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
    CAPTURING_PROPERTY = "capturing_property"
    UNDERSTANDING_SITUATION = "understanding_situation"
    QUALIFYING_MOTIVATION = "qualifying_motivation"
    COLLECTING_DETAILS = "collecting_details"
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
    Manages conversation flow and lead intake interactions
    for ApexAcquisitions real estate wholesaling platform.

    This is the core engine that orchestrates:
    - Greeting and welcoming sellers
    - Capturing seller information
    - Understanding property situation and motivation
    - Qualifying leads for wholesaling deals
    - Handling conversation state transitions

    Ready to integrate with LLMs like OpenAI or Claude for natural language understanding
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
            caller_phone: Caller's phone number
            caller_name: Optional caller name (if available)
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
        Get initial greeting for lead intake

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
            f"Hi there! This is {self.receptionist_name} with ApexAcquisitions. "
            "We help property owners find solutions. What's your name?"
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
            next_action="listen",
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
        Process caller response and determine next action

        This method orchestrates the conversation flow:
        1. Extract relevant information from user input
        2. Determine current state and next state
        3. Generate appropriate AI response
        4. Update conversation context

        Args:
            call_id: Unique call identifier
            user_input: Caller's spoken or typed message
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
            "sender": "caller",
            "message": user_input,
            "input_type": input_type
        })

        # State machine: determine next state and action based on current state
        if conversation.state == ConversationState.CAPTURING_NAME:
            return self._handle_name_capture(conversation, user_input)

        elif conversation.state == ConversationState.CAPTURING_PHONE:
            return self._handle_phone_capture(conversation, user_input)

        elif conversation.state == ConversationState.CAPTURING_PROPERTY:
            return self._handle_property_capture(conversation, user_input)

        elif conversation.state == ConversationState.UNDERSTANDING_SITUATION:
            return self._handle_situation_understanding(conversation, user_input)

        elif conversation.state == ConversationState.QUALIFYING_MOTIVATION:
            return self._handle_motivation_qualifying(conversation, user_input)

        elif conversation.state == ConversationState.COLLECTING_DETAILS:
            return self._handle_detail_collection(conversation, user_input)

        else:
            logger.warning(f"Unknown state: {conversation.state}")
            return ConversationResponse(
                message="I appreciate your time. Let me have one of our acquisitions managers reach out to you directly.",
                next_action="transfer_to_human",
                state=conversation.state,
                requires_human_handoff=True
            )

    def _handle_name_capture(
        self,
        conversation: Conversation,
        user_input: str
    ) -> ConversationResponse:
        """Capture caller name"""
        # TODO: Integrate with NLP/LLM to extract name from user input
        name = user_input.strip()

        if len(name) > 2:
            conversation.customer_data["name"] = name
            conversation.state = ConversationState.CAPTURING_PHONE

            response_message = (
                f"Nice to meet you, {name}! "
                "What's the best phone number to reach you at?"
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
        """Capture caller phone number"""
        # TODO: Integrate with NLP/LLM to extract phone number
        phone = ''.join(filter(str.isdigit, user_input))

        if len(phone) >= 10:
            conversation.customer_data["phone"] = phone
            conversation.state = ConversationState.CAPTURING_PROPERTY

            response_message = (
                "Got it! Now, what's the address of the property you're looking to sell?"
            )

            logger.info(f"Captured phone: {phone}")

            return ConversationResponse(
                message=response_message,
                next_action="listen",
                state=ConversationState.CAPTURING_PROPERTY,
                extracted_data={"phone": phone}
            )
        else:
            return ConversationResponse(
                message="I didn't catch that phone number. Could you please repeat it?",
                next_action="listen",
                state=ConversationState.CAPTURING_PHONE
            )

    def _handle_property_capture(
        self,
        conversation: Conversation,
        user_input: str
    ) -> ConversationResponse:
        """Capture property address"""
        # TODO: Integrate with NLP/LLM to parse and validate address
        conversation.customer_data["property_address"] = user_input.strip()
        conversation.state = ConversationState.UNDERSTANDING_SITUATION

        response_message = (
            f"Thank you! And what's the current situation with the property? "
            "For example, is it occupied, vacant, or do you have tenants?"
        )

        logger.info(f"Captured property address: {user_input}")

        return ConversationResponse(
            message=response_message,
            next_action="listen",
            state=ConversationState.UNDERSTANDING_SITUATION,
            extracted_data={"property_address": user_input.strip()}
        )

    def _handle_situation_understanding(
        self,
        conversation: Conversation,
        user_input: str
    ) -> ConversationResponse:
        """Understand the property situation"""
        # TODO: Integrate with LLM to classify situation and distress signals
        conversation.customer_data["property_situation"] = user_input.strip()
        conversation.state = ConversationState.QUALIFYING_MOTIVATION

        response_message = (
            "I appreciate you sharing that. What's your main reason for considering selling? "
            "And do you have a timeline in mind?"
        )

        logger.info(f"Captured situation: {user_input}")

        return ConversationResponse(
            message=response_message,
            next_action="listen",
            state=ConversationState.QUALIFYING_MOTIVATION,
            extracted_data={"property_situation": user_input.strip()}
        )

    def _handle_motivation_qualifying(
        self,
        conversation: Conversation,
        user_input: str
    ) -> ConversationResponse:
        """Qualify seller motivation and timeline"""
        conversation.customer_data["motivation"] = user_input.strip()
        conversation.state = ConversationState.COLLECTING_DETAILS

        response_message = (
            "That's really helpful. Last question \u2014 do you have a price in mind, "
            "or would you like us to make you a fair cash offer?"
        )

        return ConversationResponse(
            message=response_message,
            next_action="listen",
            state=ConversationState.COLLECTING_DETAILS,
            extracted_data={"motivation": user_input.strip()}
        )

    def _handle_detail_collection(
        self,
        conversation: Conversation,
        user_input: str
    ) -> ConversationResponse:
        """Collect asking price or offer preference"""
        # TODO: Integrate with property data APIs to pull comps and estimate ARV
        conversation.customer_data["asking_price"] = user_input.strip()
        conversation.state = ConversationState.CONFIRMATION

        name = conversation.customer_data.get("name", "there")
        response_message = (
            f"Perfect, {name}! I have everything I need. One of our acquisitions "
            f"specialists will review your property details and reach out shortly "
            f"with a cash offer. Thank you for calling ApexAcquisitions!"
        )

        logger.info(f"Lead qualified: {conversation.customer_data}")

        return ConversationResponse(
            message=response_message,
            next_action="listen",
            state=ConversationState.CONFIRMATION,
            extracted_data={"asking_price": user_input.strip()}
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
