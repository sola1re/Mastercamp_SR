import socket
import hashlib
import os
import tqdm
import tkinter as tk
from tkinter import filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD
import json

BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"
SERVER_IP = "127.0.0.1"
SERVER_PORT = 12345

# Hash


def hash_file(file_path):
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(BUFFER_SIZE), b""):
            sha256.update(byte_block)
    return sha256.hexdigest()


class SenderApp():
    def __init__(self, channel, role):
        self.channel = channel
        self.root = TkinterDnD.Tk()
        self.root.title("CrytoChat")
        self.root.geometry("400x250")
        self.root.iconbitmap("./file_interface/logo.ico")
        self.root.resizable(width=False, height=False)
        self.root.configure(bg='#74abdc')

        self.return_button = tk.Button(
            self.root, text="Retour", command=self.return_to_menu)
        self.return_button.place(x=350, y=10)

        self.button = tk.Button(self.root, text="Glisser et deposer un fichier ici ou cliquer pour selectionner",
                                width=50, height=10, relief="solid", command=self.select_file)
        self.button.pack(pady=50)

        self.button.drop_target_register(DND_FILES)
        self.button.dnd_bind('<<Drop>>', self.drop)

        self.root.geometry(f"{400}x{250}+{570}+{180}")

        self.root.mainloop()

    def send_file(self, file_path, server_host, server_port):
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        file_hash = hash_file(file_path)

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            client_socket.connect((server_host, server_port))
            metadata = f"{file_name}{SEPARATOR}{
                file_size}{SEPARATOR}{file_hash}"
            metadata = {"action": "upload_file", "data": {'file_name': file_name,
                                                          "file_size": file_size, "file_hash": file_hash, "channel": self.channel}}
            client_socket.send(json.dumps(metadata).encode())

            with open(file_path, "rb") as f:
                progress = tqdm.tqdm(range(file_size), f"Sending {
                                     file_name}", unit="B", unit_scale=True, unit_divisor=1024)
                while True:
                    bytes_read = f.read(BUFFER_SIZE)
                    if not bytes_read:
                        break
                    client_socket.sendall(bytes_read)
                    progress.update(len(bytes_read))
                progress.close()

            print(f"File {file_name} sent successfully.")

        except Exception as e:
            print(f"Error sending file {file_name}: {e}")
        finally:
            client_socket.close()

    def drop(self, event):
        file_path = event.data.strip("{}")
        self.send_file(file_path, SERVER_IP, SERVER_PORT)

    def select_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.send_file(file_path, SERVER_IP, SERVER_PORT)

    def return_to_menu(self):
        self.root.destroy()
