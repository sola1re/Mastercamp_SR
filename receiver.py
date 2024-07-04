import socket
import tkinter as tk
from tkinter import messagebox, filedialog
import json


BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"
SERVER_IP = "127.0.0.1"
SERVER_PORT = 12345


class ReceiverApp():
    def __init__(self, channel, role):
        self.role = role
        self.channel = channel
        self.root = tk.Tk()
        self.root.title("CrytoChat")
        self.root.geometry("450x300")
        self.root.iconbitmap("./file_interface/logo.ico")
        self.root.resizable(width=False, height=False)
        self.root.configure(bg='#74abdc')

        self.file_listbox = tk.Listbox(
            self.root, selectmode=tk.SINGLE, width=50, height=10)
        self.file_listbox.pack(pady=(40, 30))

        button_frame = tk.Frame(self.root, bg='#74abdc')
        button_frame.pack()

        self.list_files_button = tk.Button(button_frame, text="Lister fichier", font=(
            'helvetica', '10', 'bold'), command=self.list_files)
        self.list_files_button.pack(side=tk.LEFT, padx=20)
        if self.role != 3:
            self.select_file_button = tk.Button(button_frame, text="Selectionner fichier", font=(
                'helvetica', '10', 'bold'), command=self.select_file)
            self.select_file_button.pack(side=tk.LEFT, padx=20)

        return_button = tk.Button(
            self.root, text="Retour", command=lambda: self.return_to_menu)
        return_button.place(x=400, y=10)

        self.root.mainloop()

    def list_files(self):
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((SERVER_IP, SERVER_PORT))
            request = {"action": "List_file",
                       "data": {'channel': self.channel}}
            client_socket.send(json.dumps(request).encode())

            files_received = client_socket.recv(BUFFER_SIZE).decode()

            client_socket.close()

            files_list = files_received.split('\n')
            self.file_listbox.delete(0, tk.END)
            for file_name in files_list:
                if file_name.strip():
                    self.file_listbox.insert(tk.END, file_name)

        except Exception as e:
            messagebox.showerror("Error", f"Error while listing files: {e}")

    def select_file(self):
        selected_file = self.file_listbox.get(tk.ACTIVE)
        if not selected_file:
            messagebox.showerror("Error", "Please select a file.")
            return

        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((SERVER_IP, SERVER_PORT))
            print(selected_file)
            request = {"action": "select_file", "data": {
                'channel': self.channel, "selected_file": selected_file}}
            client_socket.send(json.dumps(request).encode())

            received = client_socket.recv(BUFFER_SIZE).decode()

            if received == "FILE_NOT_FOUND":
                messagebox.showerror(
                    "Error", f"File '{selected_file}' not found on server.")
                return

            if SEPARATOR not in received:
                messagebox.showerror("Error", "Received data format error.")
                return

            parts = received.split(SEPARATOR)
            file_name = parts[0].strip()
            file_size = int(parts[1].strip())

            # Ask user for save path
            save_path = filedialog.asksaveasfilename(
                initialfile=file_name, defaultextension=".*", filetypes=[("All Files", "*.*")])
            if not save_path:
                client_socket.close()
                return

            # Download the file
            with open(save_path, "wb") as f:
                total_received = 0
                while total_received < file_size:
                    bytes_read = client_socket.recv(
                        min(BUFFER_SIZE, file_size - total_received))
                    if not bytes_read:
                        break
                    f.write(bytes_read)
                    total_received += len(bytes_read)

            messagebox.showinfo("Success", f"File {
                                file_name} saved successfully.")

        except Exception as e:
            messagebox.showerror("Error", f"Error while downloading file: {e}")

        finally:
            client_socket.close()

    def return_to_menu(self):
        self.root.destroy()
