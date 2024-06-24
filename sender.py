import socket
import tqdm
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5001
BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"

def send_file(file_path):
    file_size = os.path.getsize(file_path)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"[+] Connecting to {SERVER_HOST}:{SERVER_PORT}")
    client_socket.connect((SERVER_HOST, SERVER_PORT))
    print("[+] Connected.")

    client_socket.send(f"{file_path}{SEPARATOR}{file_size}".encode())

    progress = tqdm.tqdm(range(file_size), f"Sending {file_path}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(file_path, "rb") as f:
        while True:
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                break
            client_socket.sendall(bytes_read)
            progress.update(len(bytes_read))

    client_socket.close()

def drop(event):
    file_path = event.data
    send_file(file_path)

def select_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        send_file(file_path)

root = TkinterDnD.Tk()
root.title("File Upload")
root.geometry("400x200")

button = tk.Button(root, text="Drag and drop a file here or click to select", width=50, height=10, relief="solid", command=select_file)
button.pack(pady=20)

button.drop_target_register(DND_FILES)
button.dnd_bind('<<Drop>>', drop)

root.mainloop()
