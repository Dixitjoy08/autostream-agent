"""
Main agent implementation using LangGraph with Google Gemini API
Handles conversation flow, intent detection, lead collection, and tool execution
"""

import json
import os
from typing import Optional, List, Tuple
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage

from src.config import SYSTEM_PROMPT
from src.utils import load_knowledge_base, get_relevant_knowledge
from src.tools import mock_lead_capture

# Load environment variables
load_dotenv()

# ============================================================================
# STEP 1: Initialize LLM
# ============================================================================

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# Load knowledge base once
kb = load_knowledge_base()

# Debug: Print KB loaded
print(f"✅ KB Loaded: {len(kb['plans'])} plans found")
for plan_key, plan in kb["plans"].items():
    print(f"   - {plan['name']}: {plan['price']}")


# ============================================================================
# STEP 2: Agent State Class
# ============================================================================

class AgentState:
    """Simple state class to track conversation"""
    
    def __init__(self):
        self.messages = []  # List of (role, content) tuples
        self.user_name = None
        self.user_email = None
        self.user_platform = None
        self.lead_captured = False
    
    def add_message(self, role: str, content: str):
        """Add a message to conversation history"""
        self.messages.append((role, content))
    
    def get_last_user_message(self) -> Optional[str]:
        """Get the last user message"""
        for role, content in reversed(self.messages):
            if role == "user":
                return content
        return None
    
    def get_conversation_text(self) -> str:
        """Get conversation as formatted text"""
        text = ""
        for role, content in self.messages:
            if role == "user":
                text += f"User: {content}\n"
            else:
                text += f"Assistant: {content}\n"
        return text
    
    def dict(self):
        """Convert state to dictionary"""
        return {
            "messages": self.messages,
            "user_name": self.user_name,
            "user_email": self.user_email,
            "user_platform": self.user_platform,
            "lead_captured": self.lead_captured
        }


# ============================================================================
# STEP 3: Helper Functions
# ============================================================================

def detect_intent(user_msg: str) -> str:
    """Detect if user is greeting, asking, or showing buying intent"""
    
    user_lower = user_msg.lower()
    
    # Check for high-intent signals
    high_intent_keywords = ["want to", "ready to", "sign up", "interested in", "buy", "purchase", "get started", "try", "start", "begin"]
    if any(keyword in user_lower for keyword in high_intent_keywords):
        return "HIGH_INTENT"
    
    # Check for greeting
    greeting_keywords = ["hi", "hello", "hey", "what's up", "sup", "greetings"]
    if any(keyword in user_lower for keyword in greeting_keywords):
        return "GREETING"
    
    # Default to inquiry
    return "INQUIRY"


def extract_lead_info(user_msg: str, state: AgentState) -> dict:
    """Extract name, email, platform from user message"""
    
    updates = {}
    
    # Extract email
    if not state.user_email and "@" in user_msg:
        words = user_msg.split()
        for word in words:
            if "@" in word and "." in word:
                email = word.strip(",.!?;:()")
                if email.count("@") == 1:  # Valid email format
                    updates["user_email"] = email
                    break
    
    # Extract name
    if not state.user_name:
        lower_msg = user_msg.lower()
        
        # Pattern 1: "my name is John"
        if "my name is" in lower_msg:
            parts = user_msg.split("my name is")
            if len(parts) > 1:
                name_part = parts[1].strip().split()[0].strip(",.!?;:()")
                if len(name_part) > 1:
                    updates["user_name"] = name_part
        
        # Pattern 2: "I'm John"
        elif "i'm " in lower_msg:
            parts = user_msg.split("i'm ")
            if len(parts) > 1:
                name_part = parts[1].split()[0].strip(",.!?;:()")
                if len(name_part) > 1:
                    updates["user_name"] = name_part
        
        # Pattern 3: "call me John"
        elif "call me" in lower_msg:
            parts = user_msg.split("call me")
            if len(parts) > 1:
                name_part = parts[1].strip().split()[0].strip(",.!?;:()")
                if len(name_part) > 1:
                    updates["user_name"] = name_part
    
    # Extract platform
    if not state.user_platform:
        platforms = ["YouTube", "Instagram", "TikTok", "LinkedIn"]
        for platform in platforms:
            if platform.lower() in user_msg.lower():
                updates["user_platform"] = platform
                break
    
    return updates


# ============================================================================
# STEP 4: Main Agent Function
# ============================================================================

def run_agent(user_input: str, state: AgentState) -> Tuple[AgentState, str]:
    """
    Run one turn of the agent
    
    Args:
        user_input: What the user typed
        state: Current conversation state
    
    Returns:
        Tuple of (updated_state, agent_response)
    """
    
    try:
        # Add user message to history
        state.add_message("user", user_input)
        
        # Detect intent
        intent = detect_intent(user_input)
        print(f"\n[INTENT DETECTED: {intent}]")
        
        # Extract any lead info from the message
        lead_info = extract_lead_info(user_input, state)
        
        if "user_name" in lead_info:
            state.user_name = lead_info["user_name"]
            print(f"[NAME EXTRACTED: {state.user_name}]")
        
        if "user_email" in lead_info:
            state.user_email = lead_info["user_email"]
            print(f"[EMAIL EXTRACTED: {state.user_email}]")
        
        if "user_platform" in lead_info:
            state.user_platform = lead_info["user_platform"]
            print(f"[PLATFORM EXTRACTED: {state.user_platform}]")
        
        # Get relevant knowledge from KB
        kb_context = get_relevant_knowledge(user_input, kb)
        
        print(f"\n[KB CONTEXT RETRIEVED]:")
        print(kb_context)
        
        # BUILD THE COMPLETE SYSTEM PROMPT WITH KB
        system_prompt = f"""{SYSTEM_PROMPT}

================================================================================
KNOWLEDGE BASE - YOU MUST USE THIS INFORMATION TO ANSWER ALL QUESTIONS
================================================================================

{kb_context}

================================================================================
LEAD COLLECTION STATUS
================================================================================
Name: {state.user_name if state.user_name else 'Not provided yet'}
Email: {state.user_email if state.user_email else 'Not provided yet'}
Platform: {state.user_platform if state.user_platform else 'Not provided yet'}

================================================================================
YOUR INSTRUCTIONS FOR THIS RESPONSE
================================================================================
1. **PRICING**: If user asks about pricing, ALWAYS show both plans with exact prices
   - Basic Plan: $29/month
   - Pro Plan: $79/month
2. **FEATURES**: Answer using the knowledge base above
3. **POLICIES**: Use the policies from the knowledge base
4. **NEVER** say "I don't have pricing information" - you DO have it above
5. **HIGH INTENT**: If user shows buying intent, ask for missing info (one at a time)
6. **ACCURACY**: All information comes from the knowledge base - never make up details
7. **TONE**: Be friendly, helpful, and conversational
================================================================================
"""
        
        # Get conversation history
        conversation = state.get_conversation_text()
        
        # Build the prompt for Gemini
        full_prompt = f"""{system_prompt}

CONVERSATION HISTORY:
{conversation}

Now respond to the user. Remember to use the knowledge base!"""
        
        
        
        # Get response from Gemini
        response = llm.invoke([HumanMessage(content=full_prompt)])
        agent_response = response.content.strip()
        
        
        
        # Add agent response to history
        state.add_message("assistant", agent_response)
        
        # Check if we should capture lead
        # Check if we should capture lead
        if state.user_name and state.user_email and state.user_platform and not state.lead_captured:
            print(f"\n[LEAD CAPTURE TRIGGERED]")
            print(f"All information collected:")
            print(f"  Name: {state.user_name}")
            print(f"  Email: {state.user_email}")
            print(f"  Platform: {state.user_platform}")
            
            # Call the lead capture tool
            result = mock_lead_capture(state.user_name, state.user_email, state.user_platform)
            print(f"[CAPTURE RESULT] {result}")
            
            state.lead_captured = True
        
        return state, agent_response
        
    except Exception as e:
        print(f"\n❌ ERROR in run_agent:")
        print(f"{str(e)}")
        import traceback
        traceback.print_exc()
        return state, f"Error: {str(e)}"