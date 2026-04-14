import customtkinter as ctk

class SettingsFrame(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        ctk.CTkLabel(self, text="Application Settings", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=50)
        ctk.CTkLabel(self, text="Module under development", font=ctk.CTkFont(size=14)).pack(pady=10)
