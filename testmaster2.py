import tkinter as tk
from tkinter import messagebox
from tkinter import scrolledtext
import sqlite3
import socket
import threading

# Création de la base de données
def create_database():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Fonction de connexion
def login(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

# Fonction d'inscription
def register(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

# Interface graphique
class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Login")

        self.username_label = tk.Label(root, text="Nom d'utilisateur")
        self.username_label.pack()
        self.username_entry = tk.Entry(root)
        self.username_entry.pack()

        self.password_label = tk.Label(root, text="Mot de passe")
        self.password_label.pack()
        self.password_entry = tk.Entry(root, show='*')
        self.password_entry.pack()

        self.login_button = tk.Button(root, text="Login", command=self.login)
        self.login_button.pack()

        self.register_button = tk.Button(root, text="Register", command=self.register)
        self.register_button.pack()

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        user = login(username, password)
        if user:
            messagebox.showinfo("Login", "Connexion réussie!")
            self.root.destroy()
            self.run_chat_gui(user[1])  # Passer le nom d'utilisateur
        else:
            messagebox.showerror("Login", "Nom d'utilisateur ou mot de passe incorrect.")

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if register(username, password):
            messagebox.showinfo("Register", "Inscription réussie!")
        else:
            messagebox.showerror("Register", "Nom d'utilisateur déjà pris.")

    def run_chat_gui(self, username):
        chat_app = ChatApp(username)
        chat_app.run()

class ChatApp:
    def __init__(self, username):
        self.username = username
        self.root = tk.Tk()
        self.root.title("Application de Chat")
        
        self.ip_label = tk.Label(self.root, text="Adresse IP du Serveur:")
        self.ip_label.pack()
        self.ip_entry = tk.Entry(self.root)
        self.ip_entry.pack()
        
        self.port_label = tk.Label(self.root, text="Port:")
        self.port_label.pack()
        self.port_entry = tk.Entry(self.root)
        self.port_entry.pack()
        self.port_entry.insert(0, "12345")
        
        self.channel_label = tk.Label(self.root, text="Nom du canal:")
        self.channel_label.pack()
        self.channel_entry = tk.Entry(self.root)
        self.channel_entry.pack()
        
        self.text_area = scrolledtext.ScrolledText(self.root, state=tk.DISABLED)
        self.text_area.pack()
        
        self.message_entry = tk.Entry(self.root)
        self.message_entry.pack()
        
        self.send_button = tk.Button(self.root, text="Envoyer", command=self.send_message)
        self.send_button.pack()
        
        self.logout_button = tk.Button(self.root, text="Logout", command=self.logout)
        self.logout_button.pack()
        
        self.socket = None
        self.channel = None
        
    def run(self):
        self.root.mainloop()

    def connect(self):
        ip = self.ip_entry.get()
        port = int(self.port_entry.get())
        self.channel = self.channel_entry.get()
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((ip, port))
        self.socket.send(self.channel.encode())
        
        self.receive_thread = threading.Thread(target=self.receive_messages)
        self.receive_thread.start()
    
    def send_message(self):
        if self.socket is None:
            self.connect()
        
        message = self.message_entry.get()
        if message:
            self.socket.send(f"{self.username}: {message}".encode())
            self.message_entry.delete(0, tk.END)
    
    def receive_messages(self):
        while True:
            try:
                message = self.socket.recv(1024).decode()
                if message:
                    self.text_area.config(state=tk.NORMAL)
                    self.text_area.insert(tk.END, message + '\n')
                    self.text_area.config(state=tk.DISABLED)
                else:
                    break
            except:
                break

    def logout(self):
        if self.socket:
            self.socket.close()
        self.root.destroy()

if __name__ == "__main__":
    create_database()
    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()
