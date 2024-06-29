
import tkinter as tk
import subprocess
import sys

def launch_sender():
    subprocess.Popen([sys.executable, './filesharing/sender.py'])
    root.destroy()


def launch_receiver():
    subprocess.Popen([sys.executable, './filesharing/receiver.py'])
    root.destroy()

def exit():
    root.destroy()

root = tk.Tk()
root.title("CryptoChat")
root.geometry("300x200")

sender_button = tk.Button(root, text="Send File", width=20, height=2, command=launch_sender)
sender_button.pack(pady=10)

receiver_button = tk.Button(root, text="Receive Files", width=20, height=2, command=launch_receiver)
receiver_button.pack(pady=10)

exit_button = tk.Button(root, text="Exit", width=20, height=2, command=exit)
exit_button.pack(pady=10)

root.mainloop()