import socket
import tqdm
from threading import Thread
import os

BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"
SERVER_IP = "0.0.0.0"
SERVER_PORT = 5001


######### Receiver
def list_files():
    try:
        files = os.listdir('./filesharing/uploads')
        files_str = "\n".join(files)
        return files_str
    
    except Exception as e:
        return f"Error listing files: {e}"

def send_file(client_socket, file_name):
    try:
        file_path = os.path.join('./filesharing/uploads', file_name)
        file_size = os.path.getsize(file_path)
        client_socket.send(f"{file_name}{SEPARATOR}{file_size}".encode())

        with open(file_path, "rb") as f:
            while True:
                bytes_read = f.read(BUFFER_SIZE)
                if not bytes_read:
                    break
                client_socket.sendall(bytes_read)

        print(f"Sent {file_name} ({file_size} bytes) to {client_socket.getpeername()}")

    except Exception as e:
        client_socket.send(f"Error sending file: {e}".encode())
        print(f"Error sending file {file_name}: {e}")

#########


import hashlib

def hash_file(file_path):
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while True:
            data = f.read(BUFFER_SIZE)
            if not data:
                break
            sha256.update(data)
    return sha256.hexdigest()

def handle_client(client_socket, address):
    print(f"[+] {address} is connected.")

    try:
        while True:
            data = client_socket.recv(BUFFER_SIZE).decode()
            if not data:
                break

            if SEPARATOR in data:
                parts = data.split(SEPARATOR)
                if len(parts) == 3:
                    file_name, file_size_str, file_hash = parts
                    file_size = int(file_size_str)
                    file_name = os.path.basename(file_name)

                    file_path = os.path.join('./filesharing/uploads', file_name)
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)

                    with open(file_path, "wb") as f:
                        total_received = 0
                        while total_received < file_size:
                            bytes_read = client_socket.recv(min(BUFFER_SIZE, file_size - total_received))
                            if not bytes_read:
                                break
                            f.write(bytes_read)
                            total_received += len(bytes_read)

                    print(f"Successfully received {file_name} ({total_received} bytes) from {address}")

                    received_file_hash = hash_file(file_path)
                    if received_file_hash == file_hash:
                        print(f"File {file_name} integrity verified.")
                    else:
                        print(f"File {file_name} integrity verification failed. Expected {file_hash}, got {received_file_hash}")
                else:
                    print("Received data does not split into exactly 3 parts.")
            else:
                if data == "LIST_FILES":
                    files = os.listdir('./filesharing/uploads')
                    files_str = "\n".join(files)
                    client_socket.send(files_str.encode())
                else:
                    file_name = data.strip()
                    file_path = os.path.join('./filesharing/uploads', file_name)

                    if not os.path.exists(file_path):
                        print(f"File '{file_name}' not found.")
                        client_socket.send("FILE_NOT_FOUND".encode())
                        continue

                    file_size = os.path.getsize(file_path)
                    client_socket.send(f"{file_name}{SEPARATOR}{file_size}".encode())

                    with open(file_path, "rb") as f:
                        while True:
                            bytes_read = f.read(BUFFER_SIZE)
                            if not bytes_read:
                                break
                            client_socket.sendall(bytes_read)

                    print(f"Sent {file_name} ({file_size} bytes) to {client_socket.getpeername()}")

    except Exception as e:
        print(f"Error handling client {address}: {e}")
    
    finally:
        client_socket.close()
        print(f"[-] {address} is disconnected.")

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen(5)
    print(f"[*] Listening as {SERVER_IP}:{SERVER_PORT}")

    while True:
        client_socket, address = server_socket.accept()
        client_handler = Thread(target=handle_client, args=(client_socket, address))
        client_handler.start()

if __name__ == "__main__":
    start_server()
