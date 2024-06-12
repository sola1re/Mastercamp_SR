import ttkbootstrap as ttk
from client_app import ClientApp

if __name__ == "__main__":
    root = ttk.Window(themename="superhero")  # Use a valid theme name
    app = ClientApp(root)
    root.mainloop()