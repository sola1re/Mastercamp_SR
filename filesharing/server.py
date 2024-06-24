import socket
import tqdm
import os
from threading import Thread

# Secure key exchange (hash)
# Retransmit file to ip addr of client 2
# espace partagé où

BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"

UPLOAD_FOLDER = './uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

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

    # Retransmit file to another client
    retransmit_file(file_path)

def retransmit_file(file_path):
    recipient_ip = input("Enter recipient IP address: ")
    recipient_port = int(input("Enter recipient port: "))
    file_size = os.path.getsize(file_path)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((recipient_ip, recipient_port))
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
