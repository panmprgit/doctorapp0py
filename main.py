import tkinter as tk
from tkinter import ttk

class DashboardApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Dashboard Main Window")
        self.geometry("900x600")
        self.resizable(False, False)
        self.create_widgets()

    def create_widgets(self):
        # Sidebar frame
        sidebar = tk.Frame(self, bg="#2e3f4f", width=200, height=600)
        sidebar.pack(side="left", fill="y")

        # Sidebar buttons
        buttons = [
            ("Dashboard", self.show_dashboard),
            ("Transactions", self.show_transactions),
            ("Reports", self.show_reports),
            ("Settings", self.show_settings)
        ]
        for idx, (text, command) in enumerate(buttons):
            btn = tk.Button(sidebar, text=text, command=command,
                            bg="#374e63", fg="white", bd=0,
                            font=("Segoe UI", 12), activebackground="#425d7a")
            btn.place(x=0, y=40 * idx, width=200, height=40)

        # Main content area
        self.main_frame = tk.Frame(self, bg="#f4f4f4", width=700, height=600)
        self.main_frame.pack(side="left", fill="both", expand=True)

        self.show_dashboard()

    def clear_main(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_dashboard(self):
        self.clear_main()
        label = tk.Label(self.main_frame, text="Welcome to Your Dashboard!",
                         font=("Segoe UI", 18, "bold"), bg="#f4f4f4")
        label.pack(pady=40)

    def show_transactions(self):
        self.clear_main()
        label = tk.Label(self.main_frame, text="Transactions",
                         font=("Segoe UI", 16, "bold"), bg="#f4f4f4")
        label.pack(pady=40)

    def show_reports(self):
        self.clear_main()
        label = tk.Label(self.main_frame, text="Reports",
                         font=("Segoe UI", 16, "bold"), bg="#f4f4f4")
        label.pack(pady=40)

    def show_settings(self):
        self.clear_main()
        label = tk.Label(self.main_frame, text="Settings",
                         font=("Segoe UI", 16, "bold"), bg="#f4f4f4")
        label.pack(pady=40)

if __name__ == "__main__":
    app = DashboardApp()
    app.mainloop()
