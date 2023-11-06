import speech_recognition as sr
import pyttsx3
import os
import openai
from dotenv import load_dotenv

load_dotenv()
OPENAI_KEY = os.getenv("OPENAI_KEY")
openai.api_key = OPENAI_KEY



def SpeakText(command):
    engine = pyttsx3.init()
    engine.say(command)
    engine.runAndWait()

r = sr.Recognizer()

def record_text():
    print("I'm listening...")
    while True:
        try:
            with sr.Microphone() as source2:
                r.adjust_for_ambient_noise(source2, duration=0.2)
                audio2 = r.listen(source2)
                MyText = r.recognize_google(audio2)
                MyText = MyText.lower()
                print("Did you say: "+MyText)
                return MyText
        except sr.RequestError as e:
            print("Could not request results; {0}".format(e))
        except sr.UnknownValueError:
            print("unknown error occured")

def generate_prompt(messages):
    return "\n".join(f"{message['role']}: {message['content']}" for message in messages)

def send_to_chatgpt(conversation):
    prompt_text = "\n".join([f'Human: {turn["content"]}\nAI:' if turn["role"] == "user" else f'AI: {turn["content"]}\nHuman:' for turn in conversation])
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt_text,
        temperature=0.5,
        max_tokens=150,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0.6,
        stop=["\nHuman:", "\nAI:"]
    )
    return response["choices"][0]["text"]

# This function manages the conversation history
def manage_conversation_history(conversation_history, max_length=2048):
    # Concatenating all the messages and responses from the conversation_history
    conversation_text = "\n".join([f'{turn["role"]}: {turn["content"]}' for turn in conversation_history])
    
    # Calculate the length of the conversation so far
    conversation_length = len(conversation_text)

    # If the conversation is too long, we need to trim it
    while conversation_length > max_length:
        # Remove the oldest messages first (they are at the start of the list)
        conversation_history.pop(0)
        # Re-calculate the conversation text and its length
        conversation_text = "\n".join([f'{turn["role"]}: {turn["content"]}' for turn in conversation_history])
        conversation_length = len(conversation_text)

    return conversation_history

# Store the conversation
conversation_history = []

#messages = []

while True:
    user_text = record_text()
    if user_text:
        # Append the user's message to the conversation history
        conversation_history.append({"role": "user", "content": user_text})

        # Manage the conversation history to avoid exceeding the token limit
        conversation_history = manage_conversation_history(conversation_history)

        # Obtain the response from ChatGPT and add it to the conversation history
        response = send_to_chatgpt(conversation_history)
        
        # If the response is not empty, add it to the conversation history and speak it out
        if response:
            conversation_history.append({"role": "ai", "content": response})
            SpeakText(response)
            print("Assistant: " + response)
        else:
            # If the response is empty, inform the user and do not add it to the conversation history
            print("Assistant did not provide a response. Please try asking something else.")