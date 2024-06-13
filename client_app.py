import socket
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext, simpledialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

class ClientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CryptoChat")
        self.server_ip = ""
        self.server_port = 12345
        self.client_socket = None
        self.previous_servers = ["notes"]
        self.is_notes_server = False

        self.create_widgets()
        self.configure_grid()
        self.update_server_list()

    def create_widgets(self):
        # Create main frames
        self.server_frame = ttk.Frame(self.root, padding="10")
        self.server_frame.grid(row=0, column=0, sticky="nswe")
        self.chat_frame = ttk.Frame(self.root, padding="10")
        self.chat_frame.grid(row=0, column=1, sticky="nswe")

        # Server list
        self.server_tree = ttk.Treeview(self.server_frame, columns=("server_ip"), show="headings", height=15)
        self.server_tree.heading("server_ip", text="Serveurs Précédents")
        self.server_tree.pack(fill=tk.BOTH, expand=True)
        self.server_tree.bind("<<TreeviewSelect>>", self.on_server_select)

        self.add_server_button = ttk.Button(self.server_frame, text="Ajouter Serveur", command=self.add_server_dialog)
        self.add_server_button.pack(pady=10)

        # Options frame
        self.options_frame = ttk.Frame(self.chat_frame, padding="10")
        self.options_frame.pack(fill=tk.X, pady=(0, 10))

        self.chat_button = ttk.Button(self.options_frame, text="Chat", command=self.select_chat, bootstyle="info")
        self.call_button = ttk.Button(self.options_frame, text="Appel", command=self.select_call, bootstyle="info")
        self.games_button = ttk.Button(self.options_frame, text="Jeux", command=self.select_games, bootstyle="info")
        self.file_button = ttk.Button(self.options_frame, text="Fichiers", command=self.select_file, bootstyle="info")

        # Chat area
        ttk.Label(self.chat_frame, text="Chat", bootstyle="info").pack(anchor=tk.W)
        self.chat_area = scrolledtext.ScrolledText(self.chat_frame, wrap='word', width=50, height=15)
        self.chat_area.pack(fill=tk.BOTH, expand=True)
        self.chat_area.config(state='disabled')

        ttk.Label(self.chat_frame, text="Entrez votre message:", bootstyle="info").pack(anchor=tk.W, pady=(10, 0))
        self.message_entry = ttk.Entry(self.chat_frame, width=50, bootstyle="info")
        self.message_entry.pack(fill=tk.X, pady=(0, 10))
        self.message_entry.bind("<Return>", self.send_message)

        self.send_button = ttk.Button(self.chat_frame, text="Envoyer", command=self.send_message, bootstyle="success")
        self.send_button.pack()

    def configure_grid(self):
        # Make the main window expandable
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=3)

        # Make the frames expandable
        self.server_frame.rowconfigure(0, weight=1)
        self.server_frame.columnconfigure(0, weight=1)
        self.chat_frame.rowconfigure(0, weight=1)
        self.chat_frame.columnconfigure(0, weight=1)

    def add_server_dialog(self):
        self.server_ip = simpledialog.askstring("Ajouter Serveur", "Entrez l'adresse IP du serveur:")
        if self.server_ip:
            self.previous_servers.append(self.server_ip)
            self.update_server_list()

    def update_server_list(self):
        self.server_tree.delete(*self.server_tree.get_children())
        for server in self.previous_servers:
            self.server_tree.insert("", tk.END, values=(server,))

    def on_server_select(self, event):
        selected_item = self.server_tree.selection()
        if selected_item:
            server = self.server_tree.item(selected_item, "values")[0]
            if server == "notes":
                self.is_notes_server = True
                self.chat_area.config(state='normal')
                self.chat_area.insert('end', "Connecté au serveur 'notes'\n")
                self.chat_area.config(state='disabled')
            else:
                self.is_notes_server = False
                self.server_ip = server

            self.show_options()

    def show_options(self):
        # Clear previous buttons
        for widget in self.options_frame.winfo_children():
            widget.pack_forget()

        # Add option buttons
        self.chat_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        self.call_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        self.games_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        self.file_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

    def select_chat(self):
        self.connect_to_server()
        # Add more chat specific logic if needed

    def select_call(self):
        messagebox.showinfo("Info", "Fonction Appel non implémentée")

    def select_games(self):
        messagebox.showinfo("Info", "Fonction Jeux non implémentée")
    
    def select_file(self):
        messagebox.showinfo("Info", "Dépot de fichiers non implémentée")

    def connect_to_server(self):
        if not self.server_ip:
            messagebox.showerror("Erreur", "Veuillez entrer une adresse IP du serveur.")
            return

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect((self.server_ip, self.server_port))
            self.chat_area.config(state='normal')
            self.chat_area.insert('end', f"Connecté au serveur {self.server_ip}:{self.server_port}\n")
            self.chat_area.config(state='disabled')
            self.receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
            self.receive_thread.start()
        except Exception as e:
            messagebox.showerror("Erreur", f"Échec de connexion au serveur: {e}")

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024)
                if message:
                    self.chat_area.config(state='normal')
                    self.chat_area.insert('end', f"Serveur: {message.decode()}\n")
                    self.chat_area.config(state='disabled')
                else:
                    self.chat_area.config(state='normal')
                    self.chat_area.insert('end', "Connexion au serveur perdue.\n")
                    self.chat_area.config(state='disabled')
                    self.client_socket.close()
                    break
            except Exception as e:
                self.chat_area.config(state='normal')
                self.chat_area.insert('end', f"Erreur lors de la réception des messages: {e}\n")
                self.chat_area.config(state='disabled')
                self.client_socket.close()
                break

    def send_message(self, event=None):
        message = self.message_entry.get()
        if not message:
            return

        if self.is_notes_server:
            self.chat_area.config(state='normal')
            self.chat_area.insert('end', f"Vous: {message}\n")
            self.chat_area.config(state='disabled')
            self.message_entry.delete(0, 'end')
        else:
            try:
                self.client_socket.send(message.encode())
                self.chat_area.config(state='normal')
                self.chat_area.insert('end', f"Vous: {message}\n")
                self.chat_area.config(state='disabled')
                self.message_entry.delete(0, 'end')
            except Exception as e:
                messagebox.showerror("Erreur", f"Échec de l'envoi du message: {e}")
