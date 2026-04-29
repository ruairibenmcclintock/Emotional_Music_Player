# chatbot.py
import os
import json
from openai import OpenAI

# Initialize the OpenAI client
client = OpenAI(api_key="") #put OpenAI api key here. 

# Replace with your actual Assistant ID
ASSISTANT_ID = "asst_Yw80c47mW1zMY8BQvd1MRR5r"

# Create a persistent conversation thread
thread = client.beta.threads.create()

def get_chatbot_response(user_message: str, filename="assistant_output.json") -> str:
    """
    Sends a user message to the OpenAI Assistants API and saves the structured JSON response to a file.
    The structured JSON is NOT displayed to the user.

    Args:
        user_message (str): User input message.
        filename (str): The filename to save the structured response.

    Returns:
        str: A natural-language response from the Assistant.
    """
    try:
        # Send the user's message to the Assistant
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_message
        )

        # Run the assistant within the same thread
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=ASSISTANT_ID
        )

        # Retrieve the latest message from the assistant
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        response_text = messages.data[0].content[0].text.value.strip()

        # Attempt to parse the response as JSON
        try:
            structured_data = json.loads(response_text)
            # Save the structured response to a JSON file (without displaying it)
            with open(filename, "w") as file:
                json.dump(structured_data, file, indent=4)
        except json.JSONDecodeError:
            # If not valid JSON, return the response as a normal message
            return response_text

        return "Got it! Processing your request..."  # Generic message instead of showing JSON

    except Exception as e:
        return f"Error: {e}"

# CLI mode
if __name__ == "__main__":
    print("Chatbot: Hello! How can I assist you?")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Chatbot: Goodbye!")
            break
        print(f"Chatbot: {get_chatbot_response(user_input)}")
