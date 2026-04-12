"""
Utility functions for loading and retrieving knowledge base information
"""

import json
import os
from typing import Dict, Any

def load_knowledge_base() -> Dict[str, Any]:
    """
    Load the knowledge base from the JSON file.
    
    Returns:
        Dictionary containing pricing, features, and policies
    """
    # Find the knowledge_base.json file
    kb_path = os.path.join(
        os.path.dirname(__file__), 
        "../data/knowledge_base.json"
    )
    
    try:
        with open(kb_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Knowledge base not found at {kb_path}")


def get_relevant_knowledge(query: str, kb: Dict[str, Any]) -> str:
    """
    Retrieve relevant knowledge based on user query using keyword matching.
    This is a simple RAG implementation.
    
    Args:
        query: User's question or message
        kb: Knowledge base dictionary
    
    Returns:
        Formatted string with relevant information
    """
    query_lower = query.lower()
    relevant_info = []
    
    # Check if user is asking about pricing
    if any(word in query_lower for word in ["price", "cost", "plan", "pay", "cheap", "expensive"]):
        relevant_info.append("## Pricing Plans\n")
        for plan_key, plan in kb["plans"].items():
            relevant_info.append(f"- {plan['name']}: {plan['price']}\n")
            relevant_info.append(f"  - Videos/month: {plan['videos_per_month']}\n")
            relevant_info.append(f"  - Resolution: {plan['resolution']}\n")
            relevant_info.append(f"  - AI Captions: {'Yes' if plan['ai_captions'] else 'No'}\n\n")
    
    # Check if user is asking about features
    if any(word in query_lower for word in ["feature", "can", "do", "support", "caption", "export", "quality"]):
        relevant_info.append("## Key Features\n")
        for feature_name, feature_desc in kb["features"].items():
            relevant_info.append(f"- {feature_name.replace('_', ' ').title()}: {feature_desc}\n")
    
    # Check if user is asking about policies
    if any(word in query_lower for word in ["refund", "trial", "cancel", "policy", "support", "guarantee"]):
        relevant_info.append("\n## Policies\n")
        for policy_name, policy_value in kb["policies"].items():
            if policy_name == "supported_platforms":
                relevant_info.append(f"- Supported Platforms: {', '.join(policy_value)}\n")
            else:
                relevant_info.append(f"- {policy_name.replace('_', ' ').title()}: {policy_value}\n")
    
    # If no specific matches, return a summary
    if not relevant_info:
        relevant_info.append("## AutoStream Overview\n")
        relevant_info.append(f"Company: {kb['company']['name']}\n")
        relevant_info.append(f"Description: {kb['company']['tagline']}\n\n")
        relevant_info.append("We offer pricing plans, multiple features, and customer-friendly policies.\n")
        relevant_info.append("Feel free to ask about pricing, features, or our policies!\n")
    
    return "".join(relevant_info)