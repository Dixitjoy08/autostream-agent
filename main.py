"""
Main entry point - Interactive CLI
"""

from src.agent import run_agent, AgentState


def main():
    """Run the agent in interactive mode"""
    
    print("\n" + "="*70)
    print("🤖 AutoStream AI Agent - Interactive Demo (Gemini Edition)")
    print("="*70)
    print("Chat with the agent about AutoStream's pricing and features.")
    print("Type 'exit' to quit.\n")
    
    # Initialize state
    state = AgentState()
    
    # Main conversation loop
    while True:
        # Get user input
        user_input = input("You: ").strip()
        
        # Check for exit
        if user_input.lower() == "exit":
            print("\nThanks for chatting with AutoStream! 👋\n")
            break
        
        # Ignore empty input
        if not user_input:
            print("Please type something.\n")
            continue
        
        # Run agent
        state, response = run_agent(user_input, state)
        
        # Print response
        print(f"\nAgent: {response}\n")


if __name__ == "__main__":
    main()