import tkinter as tk
from tkinter import messagebox, scrolledtext, PhotoImage
from PIL import Image, ImageTk
import socket
import threading
import hashlib
import json
import time
import receiver
import sender


# Fonction pour hacher les mots de passe
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Interface graphique pour la connexion et l'inscription


class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CrytoChat")
        self.root.geometry("800x500")
        self.root.iconbitmap("./file_interface/logo.ico")
        self.root.resizable(width=False, height=False)
        # self.root.configure(bg='#5d6e75')
        self.bg = PhotoImage(file='./file_interface/back.png')

        # Créer un Label pour afficher l'image de fond
        self.bg_label = tk.Label(self.root, image=self.bg)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Frame pour le logo
        logo_frame = tk.Frame(root, bg='#74abdc')
        logo_frame.pack(pady=(51, 0))

        # Chargement et affichage du logo
        self.logo_image = Image.open("./file_interface/logo.png")
        self.logo_image = self.logo_image.resize((256, 158), Image.LANCZOS)
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = tk.Label(
            logo_frame, image=self.logo_photo, bg='#74abdc')
        self.logo_label.pack()

        # Frame pour le formulaire de connexion
        form_frame = tk.Frame(root, padx=20, pady=20)
        form_frame.pack(pady=20)

        self.username_label = tk.Label(root, text="Nom d'utilisateur", font=(
            'helvetica', 15, 'bold'), bg='#74abdc', fg='#cb2e30')
        self.username_label.pack()
        self.username_entry = tk.Entry(root)
        self.username_entry.pack(pady=(0, 18))

        self.password_label = tk.Label(root, text="Mot de passe", font=(
            'helvetica', '15', 'bold'), bg='#74abdc', fg='#cb2e30')
        self.password_label.pack()
        self.password_entry = tk.Entry(root, show='*')
        self.password_entry.pack(pady=(0, 24))

        button_frame = tk.Frame(root, bg='#74abdc')
        button_frame.pack()

        self.login_button = tk.Button(button_frame, text="Se connecter", font=(
            'helvetica', '10', 'bold'), command=self.login)
        self.login_button.pack(side=tk.LEFT, padx=5)

        self.register_button = tk.Button(button_frame, text="S'inscrire", font=(
            'helvetica', '10', 'bold'), command=self.register)
        self.register_button.pack(side=tk.LEFT, padx=5)

        self.root.geometry(f"{800}x{500}+{365}+{125}")

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        hashed_password = hash_password(password)
        response = self.send_request(
            "login", {"username": username, "password": hashed_password})
        if response["status"] == "success":
            messagebox.showinfo("Login", "Connexion réussie!")
            self.root.destroy()
            self.run_chat_gui(username)
        else:
            messagebox.showerror(
                "Login", "Nom d'utilisateur ou mot de passe incorrect.")

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        hashed_password = hash_password(password)
        response = self.send_request(
            "register", {"username": username, "password": hashed_password})
        if response["status"] == "success":
            messagebox.showinfo("Register", "Inscription réussie!")
        else:
            messagebox.showerror("Register", "Nom d'utilisateur déjà pris.")

    def send_request(self, action, data):
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(("127.0.0.1", 12345))
            request = {"action": action, "data": data}
            client_socket.sendall(json.dumps(request).encode())
            response = client_socket.recv(1024).decode()
            client_socket.close()
            return json.loads(response)
        except Exception as e:
            messagebox.showerror(
                "Error", f"Erreur de connexion au serveur: {e}")
            return None

    def run_chat_gui(self, username):
        chat_app = JoinChannel(username)
        chat_app.run()

# Interface graphique principale de l'application de chat


class JoinChannel:
    def __init__(self, username):
        self.username = username
        self.root = tk.Tk()
        self.root.title("CrytoChat")
        self.root.geometry("300x370")
        self.root.iconbitmap("./file_interface/logo.ico")
        self.root.resizable(width=False, height=False)
        # self.root.configure(bg='#74abdc')

        # Charger l'image de fond
        self.bg = PhotoImage(file='./file_interface/back2.png')

        # Créer un Label pour afficher l'image de fond
        self.bg_label = tk.Label(self.root, image=self.bg)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Label et Entry pour le nom du canal
        channel_label = tk.Label(self.root, text="Nom du canal :", font=(
            'helvetica', 15, 'bold'), bg='#74abdc', fg='#cb2e30')
        channel_label.pack(pady=(50, 0))
        self.channel_entry = tk.Entry(self.root)
        self.channel_entry.pack(pady=(0, 10))

        # Label et Entry pour le mot de passe du canal
        password_label = tk.Label(self.root, text="Mot de passe du canal :", font=(
            'helvetica', 15, 'bold'), bg='#74abdc', fg='#cb2e30')
        password_label.pack(pady=(20, 0))
        self.password_entry = tk.Entry(self.root, show='*')
        self.password_entry.pack(pady=(0, 40))

        # Frame pour les boutons de rejoindre et créer
        button_frame = tk.Frame(self.root, bg='#74abdc')
        button_frame.pack()

        # Boutons pour rejoindre ou créer un canal
        join_button = tk.Button(button_frame, text="Rejoindre",
                                command=self.join_channel, font=('helvetica', '10', 'bold'))
        join_button.pack(side=tk.LEFT, padx=5, pady=10)

        create_button = tk.Button(
            button_frame, text="Créer", command=self.create_channel, font=('helvetica', '10', 'bold'))
        create_button.pack(side=tk.LEFT, padx=5, pady=10)

        # Initialisation du socket et autres attributs nécessaires pour le chat
        self.socket = None
        self.channel = None

        # Centrer la fenêtre tkinter à l'écran
        self.root.geometry(f"{300}x{370}+{617}+{180}")

    def run(self):
        self.root.mainloop()

    def join_channel(self):
        channel_name = self.channel_entry.get()
        password = self.password_entry.get()
        hashed_password = hash_password(password)
        response = self.send_request("join_channel", {
                                     "channel_name": channel_name, "password": hashed_password, "username": self.username})
        if response["status"] == "success":
            messagebox.showinfo("Join Channel", f"Rejoindre le canal {
                                channel_name} avec succès!")
            self.root.destroy()
            chat_app = ChatApp(self.username, channel_name, response)
            chat_app.run()
        else:
            messagebox.showerror(
                "Error", "Nom de canal ou mot de passe incorrect.")

    def create_channel(self):
        channel_name = self.channel_entry.get()
        password = self.password_entry.get()
        hashed_password = hash_password(password)
        response = self.send_request("create_channel", {
                                     "channel_name": channel_name, "password": hashed_password, "username": self.username})
        if response["status"] == "success":
            messagebox.showinfo("Create Channel", f"Canal {
                                channel_name} créé avec succès!")
        else:
            messagebox.showerror("Error", "Ce canal existe déjà.")

    def send_request(self, action, data):
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(("127.0.0.1", 12345))
            request = {"action": action, "data": data}
            client_socket.sendall(json.dumps(request).encode())
            response = client_socket.recv(1024).decode()
            client_socket.close()
            return json.loads(response)
        except Exception as e:
            messagebox.showerror(
                "Error", f"Erreur de connexion au serveur: {e}")
            return None


class ChatApp:
    def __init__(self, username, channel_name, response):
        self.username = username
        self.channel = channel_name
        self.port = 12345
        self.ip = "127.0.0.1"
        self.last_message_id = 0
        self.role = response['role']
        self.root = tk.Tk()
        self.root.title("CrytoChat")
        self.root.iconbitmap("./file_interface/logo.ico")
        self.root.resizable(width=False, height=False)
        self.root.geometry(f"{800}x{500}+{365}+{125}")
        # self.root.configure(bg='#74abdc')

        # Charger l'image de fond
        self.bg = PhotoImage(file='./file_interface/back.png')

        # Créer un Label pour afficher l'image de fond
        self.bg_label = tk.Label(self.root, image=self.bg)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.text_area = scrolledtext.ScrolledText(
            self.root, state=tk.DISABLED)
        self.text_area.config(state=tk.NORMAL)

        self.text_area.insert(tk.END, response["message"] + '\n')
        for msg in response["history"]:
            self.text_area.insert(
                tk.END, f"{msg['username']}:{msg['message']}\n")
            self.last_message_id += 1
        self.text_area.config(state=tk.DISABLED)
        self.text_area.pack()

        self.file_button = tk.Button(
            self.root, text="Fichier", command=self.file_button)
        self.file_button.pack()

        if self.role == 1 or self.role == 3:
            self.message_entry = tk.Entry(self.root)
            self.message_entry.pack()
            self.send_button = tk.Button(
                self.root, text="Envoyer", command=self.send_message)
            self.send_button.pack()

        self.logout_button = tk.Button(
            self.root, text="Logout", command=self.logout)
        self.logout_button.pack()

        if self.role == 1:
            self.gestion_button = tk.Button(
                self.root, text="Gerer le canal", command=self.gestion)
            self.gestion_button.pack()

        self.socket = None
        self.connect()

        self.update_thread = threading.Thread(target=self.update_messages)
        self.update_thread.start()

    def file_button(self):
        fileapp = FileApp(self.username, self.channel, self.role)
        fileapp.run()

    def run(self):
        self.root.mainloop()

    def gestion(self):
        new_window = tk.Toplevel(self.root)
        new_window.geometry("300x370")
        new_window.iconbitmap("./file_interface/logo.ico")
        new_window.resizable(width=False, height=False)
        new_window.configure(bg='#74abdc')

        channel_label = tk.Label(new_window, text="Nom de l'utilisateur :", font=(
            'helvetica', 15, 'bold'), bg='#74abdc', fg='#cb2e30')
        channel_label.pack(pady=(50, 0))
        self.channel_entry = tk.Entry(new_window)
        self.channel_entry.pack(pady=(0, 10))
        self.new_window = new_window

        # Cases à cocher pour les rôles
        self.admin_var = tk.BooleanVar()
        self.reader_var = tk.BooleanVar()
        self.editor_var = tk.BooleanVar()

        admin_check = tk.Checkbutton(new_window, text="Admin", font=(
            'helvetica', 10), variable=self.admin_var, bg='#74abdc')
        admin_check.pack()
        reader_check = tk.Checkbutton(new_window, text="Lecteur", font=(
            'helvetica', 10), variable=self.reader_var, bg='#74abdc')
        reader_check.pack()
        editor_check = tk.Checkbutton(new_window, text="Editeur", font=(
            'helvetica', 10), variable=self.editor_var, bg='#74abdc')
        editor_check.pack(pady=(0, 30))

        button_frame = tk.Frame(new_window, bg='#74abdc')
        button_frame.pack()

        # Boutons pour ajouter ou supprimer un utilisateur
        join_button = tk.Button(button_frame, text="Ajouter",
                                command=self.ajouter_users, font=('helvetica', '10', 'bold'))
        join_button.pack(side=tk.LEFT, padx=5, pady=10)
        create_button = tk.Button(button_frame, text="Supprimer",
                                  command=self.supprimer_users, font=('helvetica', '10', 'bold'))
        create_button.pack(side=tk.LEFT, padx=5, pady=10)
        return_button = tk.Button(new_window, text="Retourner",
                                  command=self.return_users, font=('helvetica', '10', 'bold'))
        return_button.pack(pady=(10, 0))

    def ajouter_users(self):
        username = self.channel_entry.get()
        roles = []
        if self.admin_var.get():
            roles = "1"
        if self.reader_var.get():
            roles = "2"
        if self.editor_var.get():
            roles = "3"

        if not username:
            messagebox.showerror(
                "Erreur", "Le nom d'utilisateur ne peut pas être vide")
            return

        # Traitement des données (exemple d'affichage des informations)
        print(f"Nom d'utilisateur : {username}")
        print(f"Rôles : {roles}")

        self.socket.sendall(json.dumps({"action": "add_users", "data": {
                            "username": username, "role": roles, 'channel': self.channel}}).encode())
        # Effacer le formulaire après soumission
        self.channel_entry.delete(0, tk.END)
        self.admin_var.set(False)
        self.reader_var.set(False)
        self.editor_var.set(False)

    def supprimer_users(self):
        username = self.channel_entry.get()
        if not username:
            messagebox.showerror(
                "Erreur", "Le nom d'utilisateur ne peut pas être vide")
            return

        self.socket.sendall(json.dumps({"action": "erase_users", "data": {
                            "username": username, "channel": self.channel}}).encode())

        print(f"Utilisateur '{username}' supprimé")
        self.channel_entry.delete(0, tk.END)

    def return_users(self):
        self.new_window.destroy()

    def connect(self):
        ip = self.ip
        port = self.port
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((ip, port))
            self.socket.sendall(json.dumps({"action": "join_channel", "data": {
                                "channel_name": self.channel, "username": self.username}}).encode())
        except Exception as e:
            messagebox.showerror("Connection Error",
                                 f"Unable to connect to server: {e}")
            self.root.destroy()

    def send_message(self):
        message = self.message_entry.get()
        if message:
            try:
                self.socket.sendall(json.dumps({"action": "send_message", "data": {
                                    "channel_name": self.channel, "message": message, "username": self.username}}).encode())
                self.message_entry.delete(0, tk.END)
            except Exception as e:
                messagebox.showerror(
                    "Send Error", f"Unable to send message: {e}")

    def update_messages(self):
        msglist = []
        while True:
            time.sleep(2)
            try:
                self.socket.sendall(json.dumps({"action": "get_new_messages", "data": {
                                    "channel_name": self.channel, "last_message_id": self.last_message_id}}).encode())
                response = self.socket.recv(1024).decode()
                new_messages = json.loads(response)

                if new_messages["status"] == "success":
                    if msglist == []:
                        for msg in new_messages["messages"]:
                            msglist.append(msg)
                    else:
                        self.text_area.config(state=tk.NORMAL)
                        for msg in new_messages["messages"]:
                            if msg not in msglist:
                                msglist.append(msg)
                                self.text_area.insert(
                                    tk.END, f"{msg['username']}:{msg['message']}\n")
                    self.text_area.config(state=tk.DISABLED)
            except Exception as e:
                break
                messagebox.showerror(
                    "Update Error", f"Unable to update messages: {e}")

    def logout(self):
        if self.socket:
            self.socket.close()
        self.root.destroy()


class FileApp():
    def __init__(self, username, channel, role):
        self.username = username
        self.channel = channel
        self.role = role
        self.root = tk.Tk()
        self.root.title("CryptoChat")
        self.root.geometry("300x200")
        self.root.iconbitmap("./file_interface/logo.ico")
        self.root.resizable(width=False, height=False)
        self.root.configure(bg='#74abdc')

        if self.role == 1:
            sender_button = tk.Button(
                self.root, text="Send File", width=20, height=2, command=self.launch_sender)
            sender_button.pack(pady=10)
        receiver_button = tk.Button(
            self.root, text="Receive Files", width=20, height=2, command=self.launch_receiver)
        receiver_button.pack(pady=10)

        exit_button = tk.Button(self.root, text="Exit",
                                width=20, height=2, command=self.exit)
        exit_button.pack(pady=10)

        root.mainloop()

    def launch_sender(self):
        send = sender.SenderApp(self.channel, self.role)
        self.root.destroy()

    def launch_receiver(self):
        receiv = receiver.ReceiverApp(self.channel, self.role)
        root.destroy()

    def exit(self):
        root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()
