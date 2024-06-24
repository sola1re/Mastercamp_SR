import socket
import tqdm
import os

# Set up the server
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 5001
BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"

# Create the uploads folder if it doesn't exist
UPLOAD_FOLDER = './uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Create the server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER_HOST, SERVER_PORT))
server_socket.listen(5)
print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")

# Accept connection
client_socket, address = server_socket.accept()
print(f"[+] {address} is connected.")

# Receive the file information
received = client_socket.recv(BUFFER_SIZE).decode()
file_name, file_size = received.split(SEPARATOR)
file_name = os.path.basename(file_name)
file_size = int(file_size)

# Prepend the upload directory to the file name
file_path = os.path.join(UPLOAD_FOLDER, file_name)

# Start receiving the file
progress = tqdm.tqdm(range(file_size), f"Receiving {file_name}", unit="B", unit_scale=True, unit_divisor=1024)
with open(file_path, "wb") as f:
    while True:
        bytes_read = client_socket.recv(BUFFER_SIZE)
        if not bytes_read:
            # File transfer is done
            break
        f.write(bytes_read)
        progress.update(len(bytes_read))

# Close the client socket
client_socket.close()
# Close the server socket
server_socket.close()
