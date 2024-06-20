import socket
import threading
import sqlite3

channels = {}  # Dictionnaire pour suivre les connexions des clients par canal

# Initialiser la base de données
def init_db():
    conn = sqlite3.connect('chat.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            channel TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Enregistrer un message dans la base de données
def save_message(username, channel, message):
    conn = sqlite3.connect('chat.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO messages (username, channel, message) VALUES (?, ?, ?)
    ''', (username, channel, message))
    conn.commit()
    conn.close()

# Récupérer les messages historiques d'un canal
def get_channel_messages(channel):
    conn = sqlite3.connect('chat.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT username, message FROM messages WHERE channel = ? ORDER BY timestamp
    ''', (channel,))
    messages = cursor.fetchall()
    conn.close()
    return messages

def broadcast(message, channel):
    for client in channels[channel]:
        try:
            client.send(message)
        except:
            client.close()
            channels[channel].remove(client)

def handle_client(conn, addr):
    print(f"Nouvelle connexion de {addr}")
    username = f"User{addr[1]}"  # Utilisateur temporaire basé sur le port

    while True:
        try:
            conn.send("Veuillez entrer le nom du canal : ".encode())
            channel = conn.recv(1024).decode().strip()
            if not channel:
                continue
            
            if channel not in channels:
                channels[channel] = []
            channels[channel].append(conn)
            
            conn.send(f"Vous avez rejoint le canal {channel}\n".encode())
            print(conn)
            # Envoyer les messages historiques
            messages = get_channel_messages(channel)
            for msg in messages:
                conn.send(f"{msg[0]}: {msg[1]}\n".encode())
            
            broadcast(f"{username} a rejoint le canal {channel}\n".encode(), channel)
            
            while True:
                message = conn.recv(1024)
                if message:
                    decoded_message = message.decode().strip()
                    broadcast(f"{username}: {decoded_message}\n".encode(), channel)
                    save_message(username, channel, decoded_message)
                else:
                    conn.close()
                    channels[channel].remove(conn)
                    broadcast(f"{username} a quitté le canal.\n".encode(), channel)
                    break
        except:
            break

def start_server(host, port=12345):
    init_db()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen()
    print(f"Serveur démarré sur {host}:{port}, en attente de connexion...")

    while True:
        conn, addr = server_socket.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"Nombre de connexions actives: {threading.active_count() - 1}")

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception as e:
        print(f"Erreur lors de la récupération de l'adresse IP: {e}")
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

if __name__ == "__main__":
    local_ip = get_local_ip()
    print(f"L'adresse IP locale est : {local_ip}")
    start_server(local_ip)
