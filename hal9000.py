import tkinter as tk
from tkinter import scrolledtext
from threading import Thread
import speech_recognition as sr
from elevenlabs_tts import speak_hal
from hal_brain import ask_hal

# === GUI CONFIGURATION ===
BG_COLOR = "#0a0a0a"         # Dark background
TEXT_COLOR = "#00ffcc"       # Neon cyan (HAL-like)
FONT = ("Courier", 12)

# === GUI CLASS ===
class HalGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("HAL 9000")
        self.root.configure(bg=BG_COLOR)
        self.root.geometry("800x600")

        self.create_widgets()

    def create_widgets(self):
        self.title_label = tk.Label(self.root, text="HAL 9000", fg=TEXT_COLOR, bg=BG_COLOR, font=("Courier", 20, "bold"))
        self.title_label.pack(pady=10)

        self.chat_display = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, font=FONT, fg=TEXT_COLOR, bg=BG_COLOR)
        self.chat_display.pack(expand=True, fill='both', padx=10, pady=10)
        self.chat_display.config(state='disabled')

        self.input_field = tk.Entry(self.root, font=FONT, bg=BG_COLOR, fg=TEXT_COLOR, insertbackground=TEXT_COLOR)
        self.input_field.pack(fill='x', padx=10, pady=(0, 10))
        self.input_field.bind("<Return>", lambda event: self.send_text())

        self.button_frame = tk.Frame(self.root, bg=BG_COLOR)
        self.button_frame.pack(pady=10)

        self.send_button = tk.Button(self.button_frame, text="Send", command=self.send_text, bg=TEXT_COLOR, fg=BG_COLOR, font=FONT)
        self.send_button.grid(row=0, column=0, padx=10)

        self.listen_button = tk.Button(self.button_frame, text="🎙️ Mic", command=self.listen_input, bg=TEXT_COLOR, fg=BG_COLOR, font=FONT)
        self.listen_button.grid(row=0, column=1, padx=10)

    def update_chat(self, speaker, message):
        self.chat_display.config(state='normal')
        self.chat_display.insert(tk.END, f"{speaker}: {message}\n")
        self.chat_display.config(state='disabled')
        self.chat_display.see(tk.END)

    def send_text(self):
        user_input = self.input_field.get().strip()
        if user_input == "":
            return
        self.input_field.delete(0, tk.END)
        self.update_chat("Ahad", user_input)
        Thread(target=self.process_and_respond, args=(user_input,), daemon=True).start()

    def listen_input(self):
        Thread(target=self.record_and_respond, daemon=True).start()

    def record_and_respond(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            self.update_chat("System", "Listening...")
            audio = recognizer.listen(source, phrase_time_limit=5)

        try:
            text = recognizer.recognize_google(audio)
            self.update_chat("Ahad", text)
            self.process_and_respond(text)
        except sr.UnknownValueError:
            self.update_chat("System", "Sorry, I didn't catch that.")
        except sr.RequestError:
            self.update_chat("System", "Speech recognition service unavailable.")

    def process_and_respond(self, user_input):
        response = ask_hal(user_input)
        self.update_chat("HAL 9000", response)
        speak_hal(response)


# === LAUNCH ===
if __name__ == "__main__":
    root = tk.Tk()
    app = HalGUI(root)
    root.mainloop()

