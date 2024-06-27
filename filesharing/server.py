import socket
import tqdm
from threading import Thread
import os

BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"

clients = []

def handle_client(client_socket, address):
    clients.append(client_socket)
    print(f"[+] {address} is connected.")

    try:
        while True:
            received = client_socket.recv(BUFFER_SIZE).decode()
            if not received:
                break
            file_name, file_size = received.split(SEPARATOR)
            file_name = os.path.basename(file_name)
            file_size = int(file_size)

            print(f"Receiving {file_name} of size {file_size} bytes from {address}")
            
            progress = tqdm.tqdm(range(file_size), f"Receiving {file_name}", unit="B", unit_scale=True, unit_divisor=1024)

            # Inform all other clients about the incoming file
            for client in clients:
                if client != client_socket:
                    client.send(f"{file_name}{SEPARATOR}{file_size}".encode())

            # Receive the file data
            file_path = os.path.join('./filesharing', 'uploads', file_name)
            with open(file_path, "wb") as f:
                while True:
                    bytes_read = client_socket.recv(BUFFER_SIZE)
                    if not bytes_read:
                        break
                    f.write(bytes_read)
                    progress.update(len(bytes_read))
            
            # Notify successful reception
            print(f"Received {file_name} from {address}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()
        clients.remove(client_socket)
        print(f"[-] {address} is disconnected.")

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", 5001))
    server_socket.listen(5)
    print(f"[*] Listening as {'0.0.0.0'}:{5001}")

    while True:
        client_socket, address = server_socket.accept()
        client_handler = Thread(target=handle_client, args=(client_socket, address))
        client_handler.start()

if __name__ == "__main__":
    start_server()
