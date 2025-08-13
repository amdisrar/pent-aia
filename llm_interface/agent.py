# llm_interface/agent.py

from llm_interface.ollama_client import query_ollama

def main():
    print("🔮 LLM Agent (connected to remote Ollama)\n")
    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() in {"exit", "quit"}:
                break
            response = query_ollama(user_input)
            print(f"\n🤖 LLM: {response}\n")
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()
