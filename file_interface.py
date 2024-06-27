import tkinter as tk
import subprocess

python_path = "C:/Users/iampa/AppData/Local/Programs/Python/Python312/python.exe"
def launch_sender():
    subprocess.Popen([python_path, './filesharing/sender.py'])

def launch_receiver():
    subprocess.Popen([python_path, './filesharing/receiver.py'])

root = tk.Tk()
root.title("File Transfer Interface")
root.geometry("300x150")

sender_button = tk.Button(root, text="Send File", width=20, height=2, command=launch_sender)
sender_button.pack(pady=10)

receiver_button = tk.Button(root, text="Receive Files", width=20, height=2, command=launch_receiver)
receiver_button.pack(pady=10)

root.mainloop()

################################################### Notes ###################################################
'''
- Add Secure connection (hashes to check authenticity and secure connection)
- Common file space (with access rights (eyfeline's database), read, edit/write, execute)
    - Send server, then transmit to everyone (2 steps)
- Encrypt symetric key with RSA and send it to db

'''