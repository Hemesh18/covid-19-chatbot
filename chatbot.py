import tkinter as tk
from tkinter import scrolledtext

class ChatbotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("COVID-19 Chatbot")
        self.root.geometry("800x600")

        # Frame
        self.frame = tk.Frame(root)
        self.frame.pack(expand=True)

        # Chat area
        self.chat_area = scrolledtext.ScrolledText(
            self.frame, wrap=tk.WORD, state='disabled',
            width=70, height=15, font=("Arial", 14),
            bg="white", fg="black"
        )
        self.chat_area.grid(row=0, column=0, columnspan=3, padx=20, pady=20)

        # Input box
        self.user_input = tk.Entry(self.frame, width=60, font=("Arial", 16))
        self.user_input.grid(row=1, column=0, padx=(20, 10), pady=10)

        # Buttons
        self.send_button = tk.Button(self.frame, text="Send",
                                     command=self.send_message)
        self.send_button.grid(row=1, column=1)

        self.start_button = tk.Button(self.frame, text="Start Chatbot",
                                      command=self.start_chatbot)
        self.start_button.grid(row=2, column=0)

        self.stop_button = tk.Button(self.frame, text="Stop Chatbot",
                                     command=self.stop_chatbot)
        self.stop_button.grid(row=2, column=1)

        self.clear_button = tk.Button(self.frame, text="Clear Chat",
                                      command=self.clear_chat)
        self.clear_button.grid(row=2, column=2)

        self.user_input.bind("<Return>", lambda event: self.send_message())

        self.user_input.config(state='disabled')
        self.send_button.config(state='disabled')

        self.display_message("Chatbot: Welcome! Ask me about COVID-19.")

    def start_chatbot(self):
        self.user_input.config(state='normal')
        self.send_button.config(state='normal')
        self.display_message("Chatbot: Chatbot started.")

    def stop_chatbot(self):
        self.user_input.config(state='disabled')
        self.send_button.config(state='disabled')
        self.display_message("Chatbot: Chatbot stopped.")

    def clear_chat(self):
        self.chat_area.config(state='normal')
        self.chat_area.delete(1.0, tk.END)
        self.chat_area.config(state='disabled')

    def send_message(self):
        user_message = self.user_input.get()
        if user_message:
            self.display_message("You: " + user_message)
            self.user_input.delete(0, tk.END)
            response = self.get_response(user_message)
            self.display_message("Chatbot: " + response)

    def display_message(self, message):
        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, message + "\n")
        self.chat_area.config(state='disabled')
        self.chat_area.yview(tk.END)

    def get_response(self, user_input):
        user_input = user_input.lower()

        if "symptom" in user_input:
            return "Common symptoms are fever, cough, and fatigue."
        elif "prevention" in user_input:
            return "Wash hands, wear mask, maintain distance."
        elif "vaccine" in user_input:
            return "Vaccines help prevent severe illness."
        else:
            return "Sorry, I didn't understand."

# Main program
if __name__ == "__main__":
    root = tk.Tk()
    app = ChatbotApp(root)
    root.mainloop()