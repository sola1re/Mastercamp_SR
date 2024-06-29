import socket
import hashlib
import os
import tqdm
import tkinter as tk
from tkinter import filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD
import hashlib

BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"
SERVER_IP = "127.0.0.1"
SERVER_PORT = 5001

######### Hash
def hash_file(file_path):
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(BUFFER_SIZE), b""):
            sha256.update(byte_block)
    return sha256.hexdigest()


def send_file(file_path, server_host, server_port):
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    file_hash = hash_file(file_path)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client_socket.connect((server_host, server_port))
        metadata = f"{file_name}{SEPARATOR}{file_size}{SEPARATOR}{file_hash}"
        client_socket.send(metadata.encode())

        with open(file_path, "rb") as f:
            progress = tqdm.tqdm(range(file_size), f"Sending {file_name}", unit="B", unit_scale=True, unit_divisor=1024)
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


def drop(event):
    file_path = event.data.strip("{}")
    send_file(file_path, SERVER_IP, SERVER_PORT)

def select_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        send_file(file_path, SERVER_IP, SERVER_PORT)



def return_to_menu():
    root.destroy()
    os.system("python ./file_interface.py")

root = TkinterDnD.Tk()
root.title("File Upload")
root.geometry("400x250")

return_button = tk.Button(root, text="Return", command=return_to_menu)
return_button.place(x=350, y=10)

button = tk.Button(root, text="Drag and drop a file here or click to select", width=50, height=10, relief="solid", command=select_file)
button.pack(pady=50)

button.drop_target_register(DND_FILES)
button.dnd_bind('<<Drop>>', drop)

root.mainloop()