import socket
import tqdm
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
from cryptography.fernet import Fernet

BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"

# Symmetric key
encryption_key = b'CA-US2W09BNIb_pw2Afimoey6HrU3CMh38jGNut01qg='

def encrypt_file(file_path, key):
    fernet = Fernet(key)
    with open(file_path, "rb") as file:
        file_data = file.read()
    encrypted_data = fernet.encrypt(file_data)
    encrypted_file_path = file_path + ".enc"
    with open(encrypted_file_path, "wb") as file:
        file.write(encrypted_data)
    return encrypted_file_path

def send_file(file_path, server_host, server_port):
    encrypted_file_path = encrypt_file(file_path, encryption_key)
    file_size = os.path.getsize(encrypted_file_path)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"[+] Connecting to {server_host}:{server_port}")
    client_socket.connect((server_host, server_port))
    print("[+] Connected.")

    client_socket.send(f"{os.path.basename(encrypted_file_path)}{SEPARATOR}{file_size}".encode())

    progress = tqdm.tqdm(range(file_size), f"Sending {encrypted_file_path}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(encrypted_file_path, "rb") as f:
        while True:
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                break
            client_socket.sendall(bytes_read)
            progress.update(len(bytes_read))

    client_socket.close()
    os.remove(encrypted_file_path)  # Remove the encrypted file after sending

def drop(event):
    file_path = event.data
    send_file(file_path, server_host_entry.get(), int(server_port_entry.get()))

def select_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        send_file(file_path, server_host_entry.get(), int(server_port_entry.get()))

root = TkinterDnD.Tk()
root.title("File Upload")
root.geometry("400x250")

tk.Label(root, text="Server IP:").pack(pady=5)
server_host_entry = tk.Entry(root)
server_host_entry.pack(pady=5)
server_host_entry.insert(0, "127.0.0.1")

tk.Label(root, text="Server Port:").pack(pady=5)
server_port_entry = tk.Entry(root)
server_port_entry.pack(pady=5)
server_port_entry.insert(0, "5001")

button = tk.Button(root, text="Drag and drop a file here or click to select", width=50, height=10, relief="solid", command=select_file)
button.pack(pady=20)

button.drop_target_register(DND_FILES)
button.dnd_bind('<<Drop>>', drop)

root.mainloop()
