from src.agent import detect_intent
def test_intent_accuracy():
    test_cases = [
        # GREETING tests
        ("Hi there!", "GREETING"),
        ("Hello! Good morning", "GREETING"),
        ("Hey, how are you?", "GREETING"),
        ("Greetings!", "GREETING"),
        ("What's up?", "GREETING"),
        
        # INQUIRY tests
        ("What are your prices?", "INQUIRY"),
        ("Tell me more about the product", "INQUIRY"),
        ("How does this work?", "INQUIRY"),
        ("What features do you offer?", "INQUIRY"),
        ("Can you explain the service?", "INQUIRY"),
        ("What is this about?", "INQUIRY"),
        
        # HIGH_INTENT tests
        ("I want to buy now", "HIGH_INTENT"),
        ("I'm ready to purchase", "HIGH_INTENT"),
        ("I want to get started", "HIGH_INTENT"),
        ("I'm interested in signing up", "HIGH_INTENT"),
        ("How do I begin?", "HIGH_INTENT"),  # NOTE: 'begin' is a keyword
        ("I want to try this", "HIGH_INTENT"),
        ("Let me start the process", "HIGH_INTENT"),
    ]
    
    correct = 0
    wrong = []
    
    print("=" * 55)
    print(f"{'Input':<35} {'Expected':<15} {'Got':<15}")
    print("=" * 55)
    
    for user_input, expected in test_cases:
        result = detect_intent(user_input)
        status = "✅" if result == expected else "❌"
        if result == expected:
            correct += 1
        else:
            wrong.append((user_input, expected, result))
        print(f"{status} {user_input:<33} {expected:<15} {result:<15}")
    
    print("=" * 55)
    accuracy = (correct / len(test_cases)) * 100
    print(f"\n🎯 Accuracy: {correct}/{len(test_cases)} = {accuracy:.1f}%")
    
    if wrong:
        print(f"\n❌ Failed cases:")
        for inp, exp, got in wrong:
            print(f"   '{inp}' → Expected {exp}, Got {got}")

test_intent_accuracy()