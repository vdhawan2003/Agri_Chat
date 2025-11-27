from backend.rag_core import chat_response

print("🌱 Sustainable Agriculture Chatbot (CLI Mode)")
print("Type 'exit' to quit.\n")

while True:
    user_input = input("You: ").strip()
    if user_input.lower() in ["exit", "quit", "bye"]:
        print("🤖 Chatbot: Goodbye! 🌿")
        break

    response = chat_response(user_input)
    print(f"\n🤖 Chatbot: {response}\n")
