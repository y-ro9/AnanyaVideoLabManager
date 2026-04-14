import customtkinter as ctk

class BookingsFrame(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        ctk.CTkLabel(self, text="Bookings Management", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=50)
        ctk.CTkLabel(self, text="Module under development", font=ctk.CTkFont(size=14)).pack(pady=10)
