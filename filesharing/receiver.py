# receiver.py
import socket
import tqdm
import os
from threading import Thread

BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"

UPLOAD_FOLDER = './filesharing/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

LOG_PATH = './filesharing/received.log'

def handle_client(client_socket, address):
    print(f"[+] {address} is connected.")

    received = client_socket.recv(BUFFER_SIZE).decode()
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

    client_socket.close()
    log_received_file(file_path)

def log_received_file(file_path):
    with open(LOG_PATH, "a") as log_file:
        log_file.write(f"Received file: {file_path}\n")
    print(f"Logged received file: {file_path}")

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    server_socket.listen(5)
    print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")

    while True:
        client_socket, address = server_socket.accept()
        client_handler = Thread(target=handle_client, args=(client_socket, address))
        client_handler.start()

if __name__ == "__main__":
    SERVER_HOST = "0.0.0.0"
    SERVER_PORT = 5001

    start_server()
