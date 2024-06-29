import socket
import tkinter as tk
from tkinter import messagebox, filedialog
import os

BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"
SERVER_IP = "127.0.0.1"
SERVER_PORT = 5001

def list_files():
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SERVER_IP, SERVER_PORT))

        request = "LIST_FILES"
        client_socket.send(request.encode())

        files_received = client_socket.recv(BUFFER_SIZE).decode()

        client_socket.close()

        files_list = files_received.split('\n')
        file_listbox.delete(0, tk.END)
        for file_name in files_list:
            if file_name.strip():
                file_listbox.insert(tk.END, file_name)

    except Exception as e:
        messagebox.showerror("Error", f"Error while listing files: {e}")
        
def select_file():
    selected_file = file_listbox.get(tk.ACTIVE)
    if not selected_file:
        messagebox.showerror("Error", "Please select a file.")
        return

    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SERVER_IP, SERVER_PORT))

        client_socket.send(selected_file.encode())

        received = client_socket.recv(BUFFER_SIZE).decode()

        if received == "FILE_NOT_FOUND":
            messagebox.showerror("Error", f"File '{selected_file}' not found on server.")
            return

        if SEPARATOR not in received:
            messagebox.showerror("Error", "Received data format error.")
            return

        parts = received.split(SEPARATOR)
        file_name = parts[0].strip()
        file_size = int(parts[1].strip())

        # Ask user for save path
        save_path = filedialog.asksaveasfilename(initialfile=file_name, defaultextension=".*", filetypes=[("All Files", "*.*")])
        if not save_path:
            client_socket.close()
            return

        # Download the file
        with open(save_path, "wb") as f:
            total_received = 0
            while total_received < file_size:
                bytes_read = client_socket.recv(min(BUFFER_SIZE, file_size - total_received))
                if not bytes_read:
                    break
                f.write(bytes_read)
                total_received += len(bytes_read)

        messagebox.showinfo("Success", f"File {file_name} saved successfully.")

    except Exception as e:
        messagebox.showerror("Error", f"Error while downloading file: {e}")

    finally:
        client_socket.close()

def return_to_menu():
    root.destroy()
    os.system("python ./file_interface.py")

root = tk.Tk()
root.title("File Receiver")
root.geometry("450x300")

file_listbox = tk.Listbox(root, selectmode=tk.SINGLE, width=50, height=10)
file_listbox.pack(pady=20)

list_files_button = tk.Button(root, text="List Files", command=list_files)
list_files_button.pack()

select_file_button = tk.Button(root, text="Select File", command=select_file)
select_file_button.pack()

return_button = tk.Button(root, text="Return", command=return_to_menu)
return_button.place(x=400, y=10)

root.mainloop()
