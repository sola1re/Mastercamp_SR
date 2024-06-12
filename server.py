import socket

def start_server(host='0.0.0.0', port=12345):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Serveur démarré sur {host}:{port}")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connexion acceptée de {client_address}")

        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            print(f"Reçu de {client_address}: {data.decode()}")
            client_socket.send(data)  # Echo back the received data

        client_socket.close()
        print(f"Connexion fermée de {client_address}")

if __name__ == "__main__":
    start_server()
