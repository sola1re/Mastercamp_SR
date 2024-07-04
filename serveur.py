import socket
import threading
import sqlite3
import json
import hashlib
import os


channels = {}


def init_db():
    pass


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def hash_file(file_path):
    sha256 = hashlib.sha256()
    BUFFER_SIZE = 4096
    with open(file_path, "rb") as f:
        while True:
            data = f.read(BUFFER_SIZE)
            if not data:
                break
            sha256.update(data)
    return sha256.hexdigest()


def login(username, password):
    conn = sqlite3.connect('server_database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username=? AND password=?',
                   (username, hash_password(password)))
    user = cursor.fetchone()
    conn.close()
    return user


def register(username, password):
    conn = sqlite3.connect('server_database.db')
    cursor = conn.cursor()
    try:

        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                       (username, hash_password(password)))

        conn.commit()

        return True
    except sqlite3.IntegrityError:
        print("no")
        return False
    finally:
        conn.close()


def create_channel(name, password, creator_username):
    conn = sqlite3.connect('server_database.db')
    cursor = conn.cursor()
    try:
        # Vérifiez si l'utilisateur existe
        cursor.execute(
            'SELECT ID_user FROM users WHERE username=?', (creator_username,))
        user = cursor.fetchone()
        if user is None:
            print(f"User '{creator_username}' not found")
            return False
        user_id = user[0]
        print(f"user_id: {user_id}")

        # Insérez le nouveau canal
        cursor.execute(
            'INSERT INTO channels (name, password) VALUES (?, ?)', (name, password))
        conn.commit()
        print("Channel inserted")

        # Récupérez l'ID du canal nouvellement créé
        cursor.execute('SELECT ID_channel FROM channels WHERE name=?', (name,))
        channel = cursor.fetchone()
        if channel is None:
            print(f"Channel '{name}' not found after insertion")
            return False
        channel_id = channel[0]
        print(f"channel_id: {channel_id}")

        # Insérez l'utilisateur créateur avec le rôle administrateur dans authorized_users
        cursor.execute(
            'INSERT INTO authorized_users (ID_user, ID_channel, role) VALUES (?, ?, ?)', (user_id, channel_id, 1))
        conn.commit()
        print("Authorized user inserted")
        dossier = f"file_interface/{name}/"
        os.makedirs(dossier, exist_ok=True)
        print(f"Dossier '{dossier}' créé avec succès!")
        return True
    except sqlite3.IntegrityError as e:
        print(f"IntegrityError: {e}")
        return False
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return False
    finally:
        conn.close()


def join_channel(name, password, username):
    conn = sqlite3.connect('server_database.db')
    cursor = conn.cursor()
    cursor.execute(
        'SELECT * FROM channels WHERE name=? AND password=?', (name, password))
    channel = cursor.fetchone()
    if channel:
        channel_id = channel[0]

        cursor.execute(
            'SELECT ID_user FROM users WHERE username=?', (username,))
        user = cursor.fetchone()
        user_id = user[0]
        cursor.execute(
            'SELECT role FROM authorized_users WHERE ID_user=? AND ID_channel=?', (user_id, channel_id))
        # cursor.execute('SELECT * FROM authorized_users ')
        role = cursor.fetchone()
        print("channel role")
        print(channel, role)
        if role != None:
            conn.close()
            # Retourne le canal et le rôle de l'utilisateur
            return channel, role[0]
    conn.close()
    return None, None


def get_channel_id(channel_name):
    conn = sqlite3.connect('server_database.db')
    cursor = conn.cursor()
    cursor.execute(
        'SELECT ID_channel FROM channels WHERE name=?', (channel_name,))
    channel_id = cursor.fetchone()
    conn.close()
    return channel_id[0] if channel_id else None


def get_user_id(username):
    conn = sqlite3.connect('server_database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT ID_user FROM users WHERE username=?', (username,))
    user_id = cursor.fetchone()
    conn.close()
    return user_id[0] if user_id else None


def add_user_to_channel(username, channel_name, role):
    conn = sqlite3.connect('server_database.db')
    cursor = conn.cursor()
    user_id = get_user_id(username)
    channel_id = get_channel_id(channel_name)
    if user_id and channel_id:
        try:
            cursor.execute(
                'INSERT INTO authorized_users (ID_user, ID_channel, role) VALUES (?, ?, ?)', (user_id, channel_id, role))
            conn.commit()
            print("user has been added")
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    return False


def erase_users(username, channel):
    conn = sqlite3.connect('server_database.db')
    cursor = conn.cursor()
    user_id = get_user_id(username)
    channel_id = get_channel_id(channel)
    if user_id and channel_id:
        try:
            cursor.execute(
                'DELETE FROM authorized_users WHERE ID_user=? AND ID_channel=?', (user_id, channel_id))
            conn.commit()
            print("user has been erased")
            return True
        except sqlite3.IntegrityError as e:
            print(f"IntegrityError: {e}")
            return False
        finally:
            conn.close()
    else:
        print("User ID or Channel ID not found")
    return False


def get_channel_history(name):
    conn = sqlite3.connect('server_database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT ID_channel FROM channels WHERE name=?', (name,))
    channel_id = cursor.fetchone()
    cursor.execute(
        'SELECT * FROM messages WHERE ID_channel=? ORDER BY timestamp ASC', (channel_id[0],))
    messages = cursor.fetchall()
    conn.close()
    return messages


def save_message(username, channel, message):
    conn = sqlite3.connect('server_database.db')
    cursor = conn.cursor()
    user_id = get_user_id(username)
    channel_id = get_channel_id(channel)
    print(user_id, channel_id)
    cursor.execute('''
        INSERT INTO messages (ID_user, ID_channel, content,type) VALUES (?, ?, ?, 1)
    ''', (user_id, channel_id, message))
    print("yes")
    conn.commit()
    conn.close()


def handle_client(client_socket):
    try:
        while True:
            request = client_socket.recv(1024).decode()
            request_data = json.loads(request)
            action = request_data.get("action")
            data = request_data.get("data")
            response = {"status": "error", "message": "Invalid request"}

            if action == "login":
                username = data.get("username")
                password = data.get("password")
                if login(username, password):
                    response = {"status": "success"}
                else:
                    response = {"status": "failure"}
                client_socket.sendall(json.dumps(response).encode())
            elif action == "List_file":
                try:
                    channel = data["channel"]

                    directory_path = f'./file_interface/{channel}'

                    # Vérifiez si le répertoire existe
                    if not os.path.exists(directory_path):
                        response = "DIRECTORY_NOT_FOUND"
                        client_socket.send(response.encode())
                        return

                    files = os.listdir(directory_path)

                    if not files:
                        response = "NO_FILES"
                    else:
                        files_str = "\n".join(files)
                        response = files_str
                    client_socket.send(response.encode())

                except Exception as e:
                    error_message = f"Error listing files: {e}"
                    print(error_message)
                    client_socket.send(f"ERROR: {error_message}".encode())
            elif action == "upload_file":
                BUFFER_SIZE = 4096
                file_name = data["file_name"]
                file_size_str = data["file_size"]
                file_hash = data["file_hash"]
                channel = data["channel"]

                file_size = int(file_size_str)
                file_name = os.path.basename(file_name)

                file_path = os.path.join(
                    f"./file_interface/{channel}", file_name)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)

                with open(file_path, "wb") as f:
                    total_received = 0
                    while total_received < file_size:
                        bytes_read = client_socket.recv(
                            min(BUFFER_SIZE, file_size - total_received))
                        if not bytes_read:
                            break
                        f.write(bytes_read)
                        total_received += len(bytes_read)

                received_file_hash = hash_file(file_path)

                if received_file_hash == file_hash:
                    print(f"File {file_name} integrity verified.")
                else:
                    print(f"File {file_name} integrity verification failed. Expected {
                          file_hash}, got {received_file_hash}")
            elif action == "select_file":
                SEPARATOR = "<SEPARATOR>"
                BUFFER_SIZE = 4096
                file_name = data["selected_file"].strip()
                file_path = os.path.join(
                    f"./file_interface/{data['channel']}", file_name)

                if not os.path.exists(file_path):
                    print(f"File '{file_name}' not found.")
                    client_socket.send("FILE_NOT_FOUND".encode())
                    continue

                file_size = os.path.getsize(file_path)
                client_socket.send(f"{file_name}{SEPARATOR}{
                                   file_size}".encode())

                with open(file_path, "rb") as f:
                    while True:
                        bytes_read = f.read(BUFFER_SIZE)
                        if not bytes_read:
                            break
                        client_socket.sendall(bytes_read)

                print(f"Sent {file_name} ({file_size} bytes) to {
                      client_socket.getpeername()}")
            elif action == "add_users":
                username = data.get("username")
                role = data.get("role")
                channel = data.get("channel")
                if add_user_to_channel(username, channel, role):
                    response = {"status": "success"}
                else:
                    response = {"status": "failure"}
                client_socket.sendall(json.dumps(response).encode())
            elif action == "erase_users":
                username = data.get("username")
                channel = data.get("channel")
                if erase_users(username, channel):
                    response = {"status": "success"}
                else:
                    response = {"status": "failure"}
                client_socket.sendall(json.dumps(response).encode())
            elif action == "register":
                username = data.get("username")
                password = data.get("password")
                if register(username, password):
                    response = {"status": "success"}
                else:
                    response = {"status": "failure"}
                client_socket.sendall(json.dumps(response).encode())

            elif action == "create_channel":
                channel_name = data.get("channel_name")
                password = data.get("password")
                username = data.get("username")
                if create_channel(channel_name, password, username):
                    response = {"status": "success"}
                else:
                    response = {"status": "failure"}
                client_socket.sendall(json.dumps(response).encode())

            elif action == "join_channel":
                channel_name = data.get("channel_name")
                password = data.get("password")
                username = data.get("username")

                # Check if channel exists and password matches
                channel = join_channel(channel_name, password, username)
                if channel[0]:

                    if channel_name not in channels:
                        channels[channel_name] = []
                    channels[channel_name].append(client_socket)

                    # Send channel join success message and history to client
                    history = get_channel_history(channel_name)
                    history_messages = []
                    conn = sqlite3.connect('server_database.db')
                    cursor = conn.cursor()
                    for msg in history:
                        cursor.execute(
                            'SELECT username FROM users WHERE ID_user=?', (msg[3],))
                        user_id = cursor.fetchone()
                        history_messages.append(
                            {"username": user_id[0], "message": msg[1]})
                    conn.close()
                    response = {
                        "status": "success",
                        "message": f"Successfully joined channel {channel_name}!",
                        "history": history_messages,
                        "role": channel[1]
                    }
                else:
                    response = {
                        "status": "failure",
                        "message": "Channel name or password incorrect."
                    }
                client_socket.sendall(json.dumps(response).encode())

            elif action == "send_message":
                channel_name = data.get("channel_name")
                message = data.get("message")
                username = data.get("username")
                save_message(username, channel_name, message)

            elif action == "get_new_messages":
                channel_name = data.get("channel_name")

                history = get_channel_history(channel_name)
                history_messages = []
                conn = sqlite3.connect('server_database.db')
                cursor = conn.cursor()
                for msg in history:
                    cursor.execute(
                        'SELECT username FROM users WHERE ID_user=?', (msg[3],))
                    user_id = cursor.fetchone()
                    history_messages.append(
                        {"username": user_id[0], "message": msg[1]})
                response = {
                    "status": "success",
                    "messages": history_messages
                }
                conn.close()
                client_socket.sendall(json.dumps(response).encode())

            elif action == "add_user_to_channel":
                channel_name = data.get("channel_name")
                username = data.get("username")
                # Default role is user (0), admin is (1)
                role = data.get("role", 0)
                if add_user_to_channel(username, channel_name, role):
                    response = {
                        "status": "success",
                        "message": f"User {username} added to channel {channel_name} with role {role}"
                    }
                else:
                    response = {
                        "status": "failure",
                        "message": f"Failed to add user {username} to channel {channel_name}"
                    }
                client_socket.sendall(json.dumps(response).encode())

    except Exception as e:
        pass
    finally:
        client_socket.close()


def start_server(host, port=12345):
    init_db()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen()
    print(f"Server started on {host}:{port}, waiting for connections...")

    while True:
        conn, addr = server_socket.accept()
        print(f"New connection from {addr}")
        threading.Thread(target=handle_client, args=(conn,)).start()


if __name__ == "__main__":
    start_server('127.0.0.1')
