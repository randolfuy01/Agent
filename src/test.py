from agent import Chat_Agent

def main():
    chatbot = Chat_Agent(index_name="personal")
    print(chatbot.index_name)
    # Initialize the Pinecone and OpenAI API
    try:
        chatbot.instantiate_api()
    except Exception as e:
        print(f"Error during API instantiation: {e}")
        return

    # Make sure the query is passed properly to the chatbot
    try:
        query = "Can you please tell me more about his internship experience?"
        response = chatbot.response(query)
        print(response)
    except Exception as e:
        print(f"Error during chatbot response generation: {e}")

if __name__ == "__main__":
    main()

