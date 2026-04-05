# 🏨 Hotel Management System (HMS)

> **Software Engineering Project — Group 03**
>
> A modern desktop application for hotel operations management built with Python, Flask, and pywebview.

---

## 📋 Table of Contents

- [Project Overview](#-project-overview)
- [Key Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [Default Accounts](#-default-accounts)
- [Team Members](#-team-members)
- [Documentation](#-documentation)

---

## 📝 Project Overview

The **Hotel Management System (HMS)** is a full-featured desktop application designed to streamline hotel operations, including room booking, guest management, billing, and revenue reporting. The system provides separate interfaces for **Admin/Staff** and **Customers**, with role-based access control.

### System Architecture

```
┌──────────────────────────────────────────────────┐
│              pywebview (Desktop Window)           │
│  ┌────────────────────────────────────────────┐   │
│  │         Flask Web Application              │   │
│  │  ┌──────────┐ ┌────────────┐ ┌──────────┐  │   │
│  │  │Controller│→│   Model    │→│ Database │  │   │
│  │  │ (Routes) │ │(Bus. Logic)│ │ (SQLite) │  │   │
│  │  └──────────┘ └────────────┘ └──────────┘  │   │
│  │  ┌──────────────────────────────────────┐  │   │
│  │  │     Templates (Jinja2 + Tailwind)    │  │   │
│  │  └──────────────────────────────────────┘  │   │
│  └────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────┘
```

---

## ✨ Key Features

### 🔐 Authentication & Authorization
- User login / registration with role-based access (Admin, Staff, Customer)
- Password recovery via security questions
- Secure password hashing (PBKDF2-SHA256)

### 📊 Admin Dashboard
- Real-time occupancy overview
- Pending booking alerts
- Today's revenue & check-in schedule
- Recent booking activity feed

### 🛏️ Room Management
- Full CRUD operations for rooms
- Room types: VIP, Deluxe, Standard, Single
- Status tracking: Available, Occupied, Cleaning, Maintenance
- Grid view with visual status indicators

### 📅 Booking Management
- Complete booking workflow: `Pending → Confirmed → Checked-in → Checked-out`
- Admin booking creation & customer self-service booking
- Automatic date overlap detection
- Booking cancellation with refund processing

### 👥 Customer Management
- Customer registry with search & pagination
- Loyalty tier system: Platinum, Gold, Silver, Standard
- Auto-tier upgrade based on spending & booking history
- CSV data export

### 💳 Payment & Billing
- Automatic payment recording on checkout
- Multiple payment methods (Cash, Card, Transfer)
- Refund processing for cancelled bookings

### 📈 Revenue Reports
- Key metrics: Total Revenue, Occupancy Rate, ADR, RevPAR
- Revenue breakdown by room type
- Top-performing rooms ranking
- Recent billing activity timeline
- Date range filtering

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| **Language** | Python 3.x |
| **Backend** | Flask 3.0+ (Web framework) |
| **Frontend** | Jinja2 Templates + TailwindCSS |
| **Desktop** | pywebview 5.0+ (Native window wrapper) |
| **Database** | SQLite 3 (Relational DB) |
| **Auth** | Werkzeug (Password hashing) |
| **Icons** | Google Material Symbols |
| **Fonts** | Inter, Manrope (Google Fonts) |

### Development Tools

| Tool | Purpose |
|---|---|
| VS Code | IDE |
| Jira | Project management (Kanban) |
| Figma | UI/UX design |
| diagrams.net | UML diagrams |
| Git & GitHub | Version control |

---

## 📂 Project Structure

```text
htm-project/
├── docs/                          # Project documentation
│   ├── Class_Diagram.pdf          # UML class diagram
│   ├── Context_DFD.pdf            # Data flow diagram
│   ├── Usecase.pdf                # Use case diagram
│   └── ReportHtm.pdf              # Project report
│
├── src/                           # Source code
│   ├── app.py                     # Application entry point
│   ├── config.py                  # App configuration
│   ├── seed_data.py               # Initial data seeding
│   │
│   ├── controllers/               # Route handlers (MVC - Controller)
│   │   ├── auth_controller.py     # Login, Register, Forgot Password
│   │   ├── dashboard_controller.py# Admin dashboard + auth decorators
│   │   ├── booking_controller.py  # Booking CRUD & workflow
│   │   ├── customer_controller.py # Customer CRUD & export
│   │   ├── room_controller.py     # Room CRUD & status
│   │   └── report_controller.py   # Revenue analytics
│   │
│   ├── models/                    # Business logic (MVC - Model)
│   │   ├── user_model.py          # User authentication operations
│   │   ├── room_model.py          # Room CRUD & status summary
│   │   ├── booking_model.py       # Booking CRUD & overlap detection
│   │   ├── customer_model.py      # Customer CRUD & tier system
│   │   └── payment_model.py       # Payment & revenue queries
│   │
│   ├── templates/                 # UI pages (MVC - View)
│   │   ├── base.html              # Layout template with sidebar
│   │   ├── Login.html             # Auth pages (Login/Register/Forgot)
│   │   ├── Admin_Dashboard.html   # Dashboard overview
│   │   ├── Rooms_Booking.html     # Room grid + booking modal
│   │   ├── Booking_Management.html# Booking list & management
│   │   ├── Customers.html         # Customer registry
│   │   └── View_Reports.html      # Revenue reports
│   │
│   └── database/                  # Database layer
│       ├── db_manager.py          # Connection manager & query helpers
│       └── schema.sql             # Table definitions & indexes
│
├── test/                          # Test cases
├── requirements.txt               # Python dependencies
├── .gitignore                     # Git ignore rules
└── README.md                      # This file
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+** installed ([Download](https://www.python.org/downloads/))
- **pip** package manager (included with Python)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/htm-project.git
   cd htm-project
   ```

2. **Create and activate virtual environment**
   ```bash
   # macOS / Linux
   python3 -m venv .venv
   source .venv/bin/activate

   # Windows
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   cd src
   python app.py
   ```

   The desktop window will open automatically. On first run, the database is created and seeded with sample data.

---

## 🔑 Default Accounts

| Role | Email | Password |
|---|---|---|
| **Admin** | `admin@group03hotel.com` | `admin123` |
| **Staff** | `staff@group03hotel.com` | `staff123` |
| **Customer** | *(Register via the app)* | — |

---

## 👥 Team Members

| # | Name | Role | Responsibilities |
|---|---|---|---|
| 1 | **Nguyen Cong Thanh** | 🎯 Leader | General Management, Database Design, Code Review |
| 2 | **Luong Nhat Khoi** | 🔧 Vice Leader | System Architect, Business Logic, Jira/GitHub Manager |
| 3 | **Huynh Nhat Hoa** | 🎨 Member | UI/UX Developer |
| 4 | **Nguyen Minh Man** | ⚙️ Member | Core Logic Developer |
| 5 | **Nguyen Hoang Bao Anh** | 📝 Member | QA/QC, Technical Writer |

---

## 📚 Documentation

All project documentation is available in the [`docs/`](docs/) folder:

- **Class Diagram** — Object-oriented structure of the system
- **Context DFD** — Data flow between system components
- **Use Case Diagram** — User interaction scenarios
- **Project Report** — Full technical report

---

<div align="center">

**Group 03 — Software Engineering Project © 2026**

</div>