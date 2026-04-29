import tkinter as tk
from tkinter import ttk
from chatbot import client, thread, ASSISTANT_ID
from mood_music import generate_song_list
from spot_player import play_song_list
import json
import re
import threading
import time
import os

spinner_frames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
spinner_running = False
spinner_index = None 

bot_message_queue = []
bot_typing = False

# --------- Typing + Queue Utilities ---------

def typewriter_effect(text, tag="bot", delay=30):
    bot_message_queue.append((text, tag, delay))
    if not bot_typing:
        process_bot_queue()

def process_bot_queue():
    global bot_typing
    if not bot_message_queue:
        bot_typing = False
        return

    bot_typing = True
    text, tag, delay = bot_message_queue.pop(0)

    def insert_char(i=0):
        if i < len(text):
            chat_box.insert(tk.END, text[i], tag)
            chat_box.see(tk.END)
            chat_box.after(delay, insert_char, i + 1)
        else:
            chat_box.insert(tk.END, "\n", tag)
            chat_box.after(100, process_bot_queue)

    insert_char()

def bot_speak(message, speed="normal"):
    speeds = {"slow": 70, "normal": 30, "fast": 10, "instant": 0}
    delay = speeds.get(speed, 30)
    typewriter_effect(message, delay=delay)

def log_to_gui(output_box, message):
    output_box.insert(tk.END, message + "\n")
    output_box.yview(tk.END)

def display_json(output_box, file_path, label):
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        log_to_gui(output_box, f"\n📄 {label}:\n" + json.dumps(data, indent=2))
    except Exception as e:
        log_to_gui(output_box, f"[Error reading {file_path}]: {e}")

def clean_response(response_text):
    return re.sub(r"```(?:json)?", "", response_text).replace("```", "").strip()

def extract_json(response):
    start = response.find('{')
    return response[start:] if start != -1 else response

def start_spinner():
    def spin():
        idx = 0
        while spinner_running:
            frame = spinner_frames[idx % len(spinner_frames)]
            if spinner_index:
                chat_box.delete(spinner_index, f"{spinner_index} lineend")
                chat_box.insert(spinner_index, f"Bot: {frame}", "spinner")
            idx += 1
            time.sleep(0.1)
    threading.Thread(target=spin, daemon=True).start()

# --------- Chat and Music Logic ---------

def send_message():
    global spinner_running, spinner_index
    user_input = entry.get()
    if not user_input.strip():
        return

    entry.delete(0, tk.END)
    chat_box.insert(tk.END, f"You: {user_input}\n", "user")

    spinner_running = True
    spinner_index = chat_box.index(tk.END)
    chat_box.insert(tk.END, "Bot: ⠋\n", "spinner")
    start_spinner()

    try:
        client.beta.threads.messages.create(thread_id=thread.id, role="user", content=user_input)
        run = client.beta.threads.runs.create_and_poll(thread_id=thread.id, assistant_id=ASSISTANT_ID)
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        response_text = messages.data[0].content[0].text.value.strip()
        json_text = extract_json(clean_response(response_text))

        try:
            parsed = json.loads(json_text)
            with open("assistant_output.json", "w") as f:
                json.dump(parsed, f, indent=4)

            spinner_running = False
            if spinner_index:
                chat_box.delete(spinner_index, f"{spinner_index} lineend")

            bot_speak("Bot: Got it! Please click 'Add Music' when you're ready.", speed="normal")
            bot_speak("Bot: Or keep chatting to me if I haven't got it completely right yet", speed="fast")
            add_music_button.config(state=tk.NORMAL)

            display_json(output_box, "assistant_output.json", "assistant_output.json")

        except json.JSONDecodeError:
            spinner_running = False
            if spinner_index:
                chat_box.delete(spinner_index, f"{spinner_index} lineend")
            bot_speak(f"Bot: {response_text}", speed="fast")
            log_to_gui(output_box, "Chatbot: This is not a JSON format, Waiting for JSON Format...:")

    except Exception as e:
        spinner_running = False
        if spinner_index:
            chat_box.delete(spinner_index, f"{spinner_index} lineend")
        log_to_gui(output_box, f"[Error]: {e}")

def run_music_flow():
    global spinner_running, spinner_index
    try:
        if not os.path.exists("assistant_output.json"):
            bot_speak("Bot: No emotion data found yet. Please chat with me first.", speed="fast")
            return

        spinner_running = True
        spinner_index = chat_box.index(tk.END)
        chat_box.insert(tk.END, "Bot: ⠋\n", "spinner")
        start_spinner()

        generate_song_list()
        display_json(output_box, "song_list.json", "song_list.json")

        with open("song_list.json", "r") as f:
            song_data = json.load(f)

        play_song_list(output_box)

        bot_speak("🎶 Added 10 songs to your Spotify queue:", speed="normal")
        for i, song in enumerate(song_data["song_list"], 1):
            chat_box.insert(tk.END, f"{i}. {song['title']} by {song['artist']}\n", "bot")

        log_to_gui(output_box, "🚀 Spotify queue complete.")

        spinner_running = False
        if spinner_index:
            chat_box.delete(spinner_index, f"{spinner_index} lineend")

        add_music_button.config(state=tk.DISABLED)

    except Exception as e:
        spinner_running = False
        if spinner_index:
            chat_box.delete(spinner_index, f"{spinner_index} lineend")
        bot_speak(f"Bot: I can't seem to find an active device", speed="fast")
        bot_speak(f"Bot: Please make sure spotify is open and active and try clicking ''Add Music again''", speed="normal")
        log_to_gui(output_box, f"[Error while adding music]: {e}")

# --------- GUI Layout ---------

root = tk.Tk()
root.title("Emotion-Based Music Recommender")
root.geometry("1200x700")
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

# Left Side (Chat)
left_frame = ttk.Frame(root)
left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
left_frame.grid_rowconfigure(0, weight=1)
left_frame.grid_columnconfigure(0, weight=1)

chat_box = tk.Text(left_frame, wrap="word")
chat_box.grid(row=0, column=0, sticky="nsew")
chat_box.tag_config("user", foreground="red", font=("Segoe UI", 10, "bold"))
chat_box.tag_config("bot", foreground="blue", font=("Segoe UI", 10, "bold"))
chat_box.tag_config("spinner", foreground="gray", font=("Segoe UI", 10, "italic"))

# Intro Messages
bot_speak("Bot: Hello! Can you tell me how you're feeling?", speed="normal")
bot_speak("Bot: Remember! The more detailed you are, the better the results!", speed="fast")

entry = tk.Entry(left_frame)
entry.grid(row=1, column=0, sticky="ew", pady=(10, 0))
entry.bind("<Return>", lambda event: threading.Thread(target=send_message).start())

button_frame = ttk.Frame(left_frame)
button_frame.grid(row=2, column=0, sticky="ew", pady=(5, 0))
button_frame.grid_columnconfigure(0, weight=0)
button_frame.grid_columnconfigure(1, weight=1)
button_frame.grid_columnconfigure(2, weight=0)

send_button = tk.Button(button_frame, text="Send", width=12,
                        command=lambda: threading.Thread(target=send_message).start())
send_button.grid(row=0, column=0, sticky="w", padx=(0, 10))

add_music_button = tk.Button(button_frame, text="Add Music", width=20,
                             font=("Segoe UI", 10, "bold"),
                             command=lambda: threading.Thread(target=run_music_flow).start())
add_music_button.grid(row=0, column=2, sticky="e", padx=(10, 0))
add_music_button.config(state=tk.DISABLED)

# Right Side (Logs)
right_frame = ttk.Frame(root)
right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
right_frame.grid_rowconfigure(0, weight=1)
right_frame.grid_columnconfigure(0, weight=1)

output_box = tk.Text(right_frame, wrap="word")
output_box.grid(row=0, column=0, sticky="nsew")

# GPT Prompt Instructions
output_box.insert(tk.END, "GPT Prompt\n")
output_box.insert(tk.END, "You are an AI Assistant that helps users map their emotions to audio features for music selection.\n\n")
output_box.insert(tk.END, "1. Ask the user how they are feeling.\n")
output_box.insert(tk.END, "2. Ask follow-up questions until the user confirms a final emotion or set of emotions.\n")
output_box.insert(tk.END, "3. Once confirmed, identify; Final emotional state(s) from Last.fm get 10 compatible mood tags matching the emotional need, Suggested genres and weighted tags (to prioritise which ones should be queried first)\n")
output_box.insert(tk.END, "4. Return ONLY the final emotion(s) and corresponding audio features in valid, parseable JSON format — no explanations, comments, or extra text.\n")
output_box.insert(tk.END, "5. Do not wrap the JSON in quotes, markdown, or triple backticks. Just output raw JSON starting with `{`.\n")
output_box.insert(tk.END, "6. If the user types after this repeat steps 1-6 again.\n\n")
output_box.insert(tk.END, "Use this structure as your reference:\n")
output_box.insert(tk.END, "{\n")
output_box.insert(tk.END, '  "current_mood": ["..."],\n')
output_box.insert(tk.END, '  "desired_mood": ["..."],\n')
output_box.insert(tk.END, '  "recommended_tags": [\n')
output_box.insert(tk.END, '    {"tag": "...", "weight": 0.9},\n')
output_box.insert(tk.END, '    {"tag": "...", "weight": 0.7},\n')
output_box.insert(tk.END, "  ],\n")
output_box.insert(tk.END, '  "suggested_genres": ["..."]\n')
output_box.insert(tk.END, "}\n")

if __name__ == "__main__":
    root.mainloop()
