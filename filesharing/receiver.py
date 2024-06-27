import socket
import tqdm
import os
from threading import Thread
import tkinter as tk
from tkinter import messagebox
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"

UPLOAD_FOLDER = './filesharing/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

LOG_PATH = './filesharing/received.log'

KEY = b'CA-US2W09BNIb_pw2Afimoey6HrU3CMh38jGNut01qg='  # This should match the encryption key used by the sender

def decrypt_file(file_path, key):
    try:
        with open(file_path, 'rb') as f:
            iv = f.read(16)  # Read the IV from the file
            cipher = AES.new(key, AES.MODE_CBC, iv)
            ciphertext = f.read()

        decrypted_data = unpad(cipher.decrypt(ciphertext), AES.block_size)
        
        # Save the decrypted data to a file
        decrypted_file_path = file_path.replace('.enc', '')
        with open(decrypted_file_path, 'wb') as f:
            f.write(decrypted_data)
        
        # Remove the original encrypted file
        os.remove(file_path)
        return decrypted_file_path
    except Exception as e:
        print(f"Error decrypting file {file_path}: {e}")
        return None

def receive_file(client_socket, update_ui_callback):
    try:
        while True:
            received = client_socket.recv(BUFFER_SIZE).decode()
            if not received:
                break
            file_name, file_size = received.split(SEPARATOR)
            file_name = os.path.basename(file_name)
            file_size = int(file_size)

            file_path = os.path.join(UPLOAD_FOLDER, file_name)
            progress = tqdm.tqdm(range(file_size), f"Receiving {file_name}", unit="B", unit_scale=True, unit_divisor=1024)
            with open(file_path, "wb") as f:
                while True:
                    bytes_read = client_socket.recv(BUFFER_SIZE)
                    if not bytes_read:
                        break
                    f.write(bytes_read)
                    progress.update(len(bytes_read))
            
            decrypted_file_path = decrypt_file(file_path, KEY)
            if decrypted_file_path:
                log_received_file(decrypted_file_path)
                update_ui_callback(decrypted_file_path)
    except Exception as e:
        print(f"Error receiving file: {e}")
    finally:
        client_socket.close()

def log_received_file(file_path):
    with open(LOG_PATH, "a") as log_file:
        log_file.write(f"Received and decrypted file: {file_path}\n")
    print(f"Logged received file: {file_path}")

def start_receiver(update_ui_callback):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_HOST, SERVER_PORT))
    receive_file(client_socket, update_ui_callback)

def start_receiver_thread(update_ui_callback):
    receiver_thread = Thread(target=start_receiver, args=(update_ui_callback,))
    receiver_thread.daemon = True
    receiver_thread.start()

def on_file_received(file_path):
    messagebox.showinfo("File Received", f"Received and decrypted file: {file_path}")

# GUI setup
def setup_gui():
    root = tk.Tk()
    root.title("File Receiver")
    root.geometry("300x100")
    
    label = tk.Label(root, text="Waiting for files...")
    label.pack(pady=20)
    
    start_receiver_thread(on_file_received)
    
    root.mainloop()

if __name__ == "__main__":
    SERVER_HOST = "127.0.0.1"  # server's IP address
    SERVER_PORT = 5001

    setup_gui()
