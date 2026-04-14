import customtkinter as ctk
from tkinter import messagebox
import sqlite3
from datetime import datetime, timedelta
from PIL import Image, ImageTk
import os

class DashboardFrame(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="#FFFFFF")
        self.app = app
        self.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.load_dashboard_data()
        self.create_widgets()
    
    def load_dashboard_data(self):
        """Load data for dashboard"""
        conn = sqlite3.connect('ananya_video_lab.db')
        cursor = conn.cursor()
        
        # Get total customers
        cursor.execute("SELECT COUNT(*) FROM customers")
        self.total_customers = cursor.fetchone()[0]
        
        # Get today's bookings
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute('''
            SELECT COUNT(*) FROM bookings 
            WHERE booking_date = ?
        ''', (today,))
        self.today_bookings = cursor.fetchone()[0]
        
        # Get pending balances
        cursor.execute("SELECT SUM(balance_due) FROM bookings WHERE status != 'Cancelled'")
        result = cursor.fetchone()[0]
        self.pending_balances = result if result else 0
        
        # Get recent bookings
        cursor.execute('''
            SELECT b.booking_id, c.full_name, b.total_amount, b.advance_paid, b.balance_due, b.status
            FROM bookings b
            JOIN customers c ON b.customer_id = c.id
            ORDER BY b.created_at DESC
            LIMIT 5
        ''')
        self.recent_bookings = cursor.fetchall()
        
        conn.close()
    
    def create_widgets(self):
        """Create dashboard widgets"""
        # Welcome message
        welcome_frame = ctk.CTkFrame(self, fg_color="#B71C1C", corner_radius=10)
        welcome_frame.pack(fill="x", pady=(0, 20))
        
        welcome_label = ctk.CTkLabel(welcome_frame, 
                                     text=f"Welcome to Ananya Video Mixing Lab, Munger, Bihar",
                                     font=ctk.CTkFont(size=24, weight="bold"),
                                     text_color="#D4AF37")
        welcome_label.pack(pady=30)
        
        date_label = ctk.CTkLabel(welcome_frame,
                                  text=datetime.now().strftime("%A, %d %B %Y"),
                                  font=ctk.CTkFont(size=14),
                                  text_color="white")
        date_label.pack(pady=(0, 30))
        
        # Stats cards
        stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        stats_frame.pack(fill="x", pady=20)
        
        # Configure grid for 3 columns
        for i in range(3):
            stats_frame.grid_columnconfigure(i, weight=1)
        
        # Card 1: Today's Bookings
        card1 = self.create_stat_card(stats_frame, "📅 Today's Bookings", str(self.today_bookings), "#2196F3", 0)
        card1.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Card 2: Total Customers
        card2 = self.create_stat_card(stats_frame, "👥 Total Customers", str(self.total_customers), "#4CAF50", 1)
        card2.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        # Card 3: Pending Balances
        card3 = self.create_stat_card(stats_frame, "💰 Pending Balances", f"₹{self.pending_balances:,.0f}", "#FF9800", 2)
        card3.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
        
        # Quick action buttons
        actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        actions_frame.pack(fill="x", pady=20)
        
        quick_buttons = [
            ("👤 New Customer", self.new_customer, "#4CAF50"),
            ("📅 New Booking", self.new_booking, "#2196F3"),
            ("🧾 Generate Receipt", self.generate_receipt, "#FF9800"),
            ("📊 View Reports", self.view_reports, "#9C27B0")
        ]
        
        for i, (text, command, color) in enumerate(quick_buttons):
            btn = ctk.CTkButton(actions_frame, text=text, command=command,
                               fg_color=color, hover_color=self.darken_color(color),
                               font=ctk.CTkFont(size=14, weight="bold"),
                               height=50, corner_radius=10)
            btn.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")
            actions_frame.grid_columnconfigure(i, weight=1)
        
        # Recent bookings section
        recent_frame = ctk.CTkFrame(self, fg_color="#F5F5F5", corner_radius=10)
        recent_frame.pack(fill="both", expand=True, pady=20)
        
        title_label = ctk.CTkLabel(recent_frame, text="Recent Bookings",
                                   font=ctk.CTkFont(size=18, weight="bold"),
                                   text_color="#B71C1C")
        title_label.pack(pady=15)
        
        # Create table header
        header_frame = ctk.CTkFrame(recent_frame, fg_color="#B71C1C", corner_radius=5)
        header_frame.pack(fill="x", padx=20, pady=(0, 5))
        
        headers = ["Booking ID", "Customer", "Total Amount", "Advance", "Balance", "Status"]
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(header_frame, text=header,
                                font=ctk.CTkFont(size=12, weight="bold"),
                                text_color="white")
            label.grid(row=0, column=i, padx=10, pady=10, sticky="w")
            header_frame.grid_columnconfigure(i, weight=1)
        
        # Display recent bookings
        if self.recent_bookings:
            for idx, booking in enumerate(self.recent_bookings):
                row_frame = ctk.CTkFrame(recent_frame, fg_color="white", corner_radius=5)
                row_frame.pack(fill="x", padx=20, pady=2)
                
                # Status color
                status_color = {
                    'Pending': '#FF9800',
                    'Confirmed': '#4CAF50',
                    'Completed': '#2196F3',
                    'Cancelled': '#F44336'
                }.get(booking[5], '#9E9E9E')
                
                values = [
                    booking[0],  # Booking ID
                    booking[1],  # Customer
                    f"₹{booking[2]:,.0f}",  # Total
                    f"₹{booking[3]:,.0f}",  # Advance
                    f"₹{booking[4]:,.0f}",  # Balance
                ]
                
                for i, value in enumerate(values):
                    label = ctk.CTkLabel(row_frame, text=value,
                                        font=ctk.CTkFont(size=11),
                                        text_color="#2C2C2C")
                    label.grid(row=0, column=i, padx=10, pady=8, sticky="w")
                    row_frame.grid_columnconfigure(i, weight=1)
                
                # Status with color
                status_label = ctk.CTkLabel(row_frame, text=booking[5],
                                           font=ctk.CTkFont(size=11, weight="bold"),
                                           text_color=status_color)
                status_label.grid(row=0, column=5, padx=10, pady=8, sticky="w")
        else:
            no_data_label = ctk.CTkLabel(recent_frame, text="No recent bookings found",
                                        font=ctk.CTkFont(size=14),
                                        text_color="#757575")
            no_data_label.pack(pady=30)
    
    def create_stat_card(self, parent, title, value, color, column):
        """Create statistics card"""
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=10, border_width=1, border_color="#E0E0E0")
        
        title_label = ctk.CTkLabel(card, text=title,
                                  font=ctk.CTkFont(size=12),
                                  text_color="#757575")
        title_label.pack(pady=(15, 5))
        
        value_label = ctk.CTkLabel(card, text=value,
                                  font=ctk.CTkFont(size=32, weight="bold"),
                                  text_color=color)
        value_label.pack(pady=(0, 15))
        
        return card
    
    def darken_color(self, color):
        """Return darker shade of color"""
        colors = {
            "#4CAF50": "#388E3C",
            "#2196F3": "#1976D2",
            "#FF9800": "#F57C00",
            "#9C27B0": "#7B1FA2"
        }
        return colors.get(color, color)
    
    def new_customer(self):
        """Open new customer dialog"""
        self.app.show_customers()
        messagebox.showinfo("Info", "Please add customer details in Customers section")
    
    def new_booking(self):
        """Open new booking dialog"""
        self.app.show_bookings()
        messagebox.showinfo("Info", "Please create booking in Bookings section")
    
    def generate_receipt(self):
        """Generate receipt for selected booking"""
        messagebox.showinfo("Info", "Please go to Bookings section and click Generate Receipt for a specific booking")
    
    def view_reports(self):
        """View reports"""
        self.app.show_reports()