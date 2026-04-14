import customtkinter as ctk
from tkinter import messagebox
import sys
import os
from PIL import Image
import sqlite3
from datetime import datetime

# Import modules
from modules.dashboard import DashboardFrame
from modules.customers import CustomersFrame
from modules.bookings import BookingsFrame
from modules.services import ServicesFrame
from modules.reports import ReportsFrame
from modules.settings import SettingsFrame

# Configure appearance
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class AnanyaVideoLabApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Window configuration
        self.title("Ananya Video Lab Manager - Professional Video & Photography Management")
        self.geometry("1400x800")
        self.minsize(1200, 600)
        
        # Set icon (optional - you can add your own icon)
        # self.iconbitmap("assets/logo.ico")
        
        # Colors
        self.primary_color = "#B71C1C"  # Deep Maroon
        self.secondary_color = "#D4AF37"  # Soft Gold
        self.bg_color = "#FFFFFF"  # White
        self.text_color = "#2C2C2C"  # Dark Gray
        
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create sidebar
        self.create_sidebar()
        
        # Create main content area
        self.main_frame = ctk.CTkFrame(self, fg_color=self.bg_color)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        # Initialize database
        self.init_database()
        
        # Show dashboard by default
        self.show_dashboard()
        
        # Load sample data if database is empty
        self.check_and_load_sample_data()
    
    def create_sidebar(self):
        """Create sidebar navigation"""
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0, fg_color=self.primary_color)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        
        # Business name header
        header_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        header_frame.pack(pady=(30, 20))
        
        title_label = ctk.CTkLabel(header_frame, text="Ananya Video\nMixing Lab", 
                                   font=ctk.CTkFont(size=20, weight="bold"),
                                   text_color=self.secondary_color, justify="center")
        title_label.pack()
        
        subtitle_label = ctk.CTkLabel(header_frame, text="Professional Manager",
                                     font=ctk.CTkFont(size=12),
                                     text_color="white")
        subtitle_label.pack(pady=(5, 0))
        
        # Navigation buttons
        nav_buttons = [
            ("🏠 Dashboard", self.show_dashboard),
            ("👥 Customers", self.show_customers),
            ("📅 Bookings", self.show_bookings),
            ("🛠️ Services", self.show_services),
            ("📊 Reports", self.show_reports),
            ("⚙️ Settings", self.show_settings)
        ]
        
        for text, command in nav_buttons:
            btn = ctk.CTkButton(self.sidebar, text=text, command=command,
                               fg_color="transparent", hover_color="#8B0000",
                               anchor="w", font=ctk.CTkFont(size=14),
                               height=45, corner_radius=0)
            btn.pack(fill="x", padx=0, pady=2)
        
        # Exit button at bottom
        exit_btn = ctk.CTkButton(self.sidebar, text="🚪 Exit", command=self.exit_app,
                                fg_color="transparent", hover_color="#8B0000",
                                anchor="w", font=ctk.CTkFont(size=14),
                                height=45, corner_radius=0)
        exit_btn.pack(side="bottom", fill="x", pady=(0, 20))
    
    def init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect('ananya_video_lab.db')
        cursor = conn.cursor()
        
        # Create tables
        cursor.executescript('''
            -- Customers table
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                primary_phone TEXT UNIQUE NOT NULL,
                alternate_phone TEXT,
                email TEXT,
                address TEXT,
                remarks TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            -- Bookings table
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                booking_id TEXT UNIQUE NOT NULL,
                customer_id INTEGER NOT NULL,
                booking_date DATE NOT NULL,
                total_amount REAL DEFAULT 0,
                advance_paid REAL DEFAULT 0,
                balance_due REAL DEFAULT 0,
                status TEXT DEFAULT 'Pending',
                remarks TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            );
            
            -- Events table
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                booking_id INTEGER NOT NULL,
                event_type TEXT NOT NULL,
                event_date DATE NOT NULL,
                venue TEXT,
                start_time TEXT,
                end_time TEXT,
                custom_event_type TEXT,
                FOREIGN KEY (booking_id) REFERENCES bookings(id)
            );
            
            -- Services table
            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_name TEXT UNIQUE NOT NULL,
                default_rate REAL DEFAULT 0,
                unit TEXT DEFAULT 'Per Event'
            );
            
            -- Event Services (Line items)
            CREATE TABLE IF NOT EXISTS event_services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL,
                service_id INTEGER NOT NULL,
                quantity INTEGER DEFAULT 1,
                rate REAL NOT NULL,
                total REAL NOT NULL,
                FOREIGN KEY (event_id) REFERENCES events(id),
                FOREIGN KEY (service_id) REFERENCES services(id)
            );
            
            -- Karizma Album Details
            CREATE TABLE IF NOT EXISTS karizma_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_service_id INTEGER NOT NULL,
                number_of_pages INTEGER,
                photos_per_page INTEGER,
                page_finish_type TEXT,
                price_per_page REAL,
                total_amount REAL,
                FOREIGN KEY (event_service_id) REFERENCES event_services(id)
            );
            
            -- Settings table
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            );
        ''')
        
        # Insert default services if not exists
        default_services = [
            ('Cinematic Videography (4K)', 35000, 'Per Event'),
            ('HD Videography', 25000, 'Per Event'),
            ('Traditional Videography', 15000, 'Per Event'),
            ('Candid Photography', 20000, 'Per Event'),
            ('Traditional Photography', 10000, 'Per Event'),
            ('Drone Videography', 8000, 'Per Event'),
            ('Pre-Wedding Shoot', 15000, 'Per Event'),
            ('Post-Wedding Shoot', 12000, 'Per Event'),
            ('Karizma Album', 0, 'Per Page'),
            ('LED Video Wall', 15000, 'Per Event'),
            ('LED TV Setup', 5000, 'Per Event'),
            ('Lighted Photo Frame', 2000, 'Per Event'),
            ('Projector + Screen', 3000, 'Per Event'),
            ('Video Editing & Colour Grading', 10000, 'Per Event'),
            ('Full Event Coverage', 50000, 'Per Event')
        ]
        
        for service in default_services:
            cursor.execute('''
                INSERT OR IGNORE INTO services (service_name, default_rate, unit)
                VALUES (?, ?, ?)
            ''', service)
        
        # Insert default settings
        default_settings = [
            ('business_name', 'Ananya Video Mixing Lab'),
            ('business_address', 'Munger, Bihar'),
            ('business_phone', '9204679011'),
            ('business_alternate_phone', ''),
            ('business_email', 'info@ananyavideo.com'),
            ('business_gst', ''),
            ('footer_note', 'Thank you for choosing Ananya Video Mixing Lab')
        ]
        
        for key, value in default_settings:
            cursor.execute('''
                INSERT OR IGNORE INTO settings (key, value)
                VALUES (?, ?)
            ''', (key, value))
        
        conn.commit()
        conn.close()
    
    def check_and_load_sample_data(self):
        """Load sample data if database is empty"""
        conn = sqlite3.connect('ananya_video_lab.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM customers")
        customer_count = cursor.fetchone()[0]
        
        if customer_count == 0:
            # Insert sample customers
            sample_customers = [
                ('Rahul Sharma', '9876543210', '9876543211', 'rahul@gmail.com', 'Patna, Bihar', 'Wedding client'),
                ('Priya Singh', '9876543212', '', 'priya@gmail.com', 'Munger, Bihar', 'Birthday party'),
                ('Amit Kumar', '9876543213', '9876543214', 'amit@gmail.com', 'Bhagalpur, Bihar', 'Corporate event')
            ]
            
            for customer in sample_customers:
                cursor.execute('''
                    INSERT INTO customers (full_name, primary_phone, alternate_phone, email, address, remarks)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', customer)
            
            # Get customer IDs
            cursor.execute("SELECT id FROM customers")
            customer_ids = [row[0] for row in cursor.fetchall()]
            
            # Insert sample bookings
            for i, cust_id in enumerate(customer_ids, 1):
                booking_id = f"ANV-202604-{str(i).zfill(3)}"
                cursor.execute('''
                    INSERT INTO bookings (booking_id, customer_id, booking_date, total_amount, advance_paid, balance_due, status)
                    VALUES (?, ?, DATE('now'), 50000, 20000, 30000, 'Confirmed')
                ''', (booking_id, cust_id))
            
            conn.commit()
        
        conn.close()
    
    def show_dashboard(self):
        """Show dashboard frame"""
        self.clear_main_frame()
        dashboard = DashboardFrame(self.main_frame, self)
        dashboard.pack(fill="both", expand=True)
    
    def show_customers(self):
        """Show customers frame"""
        self.clear_main_frame()
        customers = CustomersFrame(self.main_frame, self)
        customers.pack(fill="both", expand=True)
    
    def show_bookings(self):
        """Show bookings frame"""
        self.clear_main_frame()
        bookings = BookingsFrame(self.main_frame, self)
        bookings.pack(fill="both", expand=True)
    
    def show_services(self):
        """Show services frame"""
        self.clear_main_frame()
        services = ServicesFrame(self.main_frame, self)
        services.pack(fill="both", expand=True)
    
    def show_reports(self):
        """Show reports frame"""
        self.clear_main_frame()
        reports = ReportsFrame(self.main_frame, self)
        reports.pack(fill="both", expand=True)
    
    def show_settings(self):
        """Show settings frame"""
        self.clear_main_frame()
        settings = SettingsFrame(self.main_frame, self)
        settings.pack(fill="both", expand=True)
    
    def clear_main_frame(self):
        """Clear main frame content"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
    
    def exit_app(self):
        """Exit application"""
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.quit()
            sys.exit(0)

if __name__ == "__main__":
    app = AnanyaVideoLabApp()
    app.mainloop()