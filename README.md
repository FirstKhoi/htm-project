<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/Flask-3.0-000000?logo=flask" alt="Flask"/>
  <img src="https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite&logoColor=white" alt="SQLite"/>
  <img src="https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white" alt="Docker"/>
  <img src="https://img.shields.io/badge/License-MIT-yellow" alt="License"/>
</p>

<h1 align="center">🏨 Hotel Management System</h1>

<p align="center">
  <strong>A full-stack desktop & containerized hotel operations platform</strong><br/>
  <em>Built with Flask · Jinja2 · TailwindCSS · SQLite · pywebview · Docker</em>
</p>

<p align="center">
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-features">Features</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-docker-deployment">Docker</a> •
  <a href="#-project-structure">Structure</a> •
  <a href="#-team">Team</a>
</p>

---

## 🚀 Quick Start

### Option 1 — Desktop App (pywebview)

```bash
# Clone & setup
git clone https://github.com/FirstKhoi/htm-project.git
cd htm-project

# Virtual environment
python3 -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows

# Install & run
pip install -r requirements.txt
cd src && python app.py
```

> A native desktop window opens automatically. Database is created and seeded on first launch.

### Option 2 — Docker (no Python required)

```bash
git clone https://github.com/FirstKhoi/htm-project.git
cd htm-project
docker compose up --build
```

Open **http://localhost:8080/auth/login** in your browser.

### Default Accounts

| Role | Email | Password |
|:---|:---|:---|
| 🔑 **Admin** | `admin@group03hotel.com` | `admin123` |
| 👤 **Staff** | `staff@group03hotel.com` | `staff123` |
| 🧳 **Customer** | *Register via the app* | — |

---

## ✨ Features

### Authentication & Security
- Role-based access control — **Admin**, **Staff**, **Customer**
- CSRF-protected forms on every POST endpoint
- PBKDF2-SHA256 password hashing
- Password recovery via security questions

### Admin Dashboard
- Real-time room occupancy overview
- Pending booking alerts with one-click approval
- Today's revenue & scheduled check-ins
- Recent booking activity feed

### Room Management
- Full CRUD with modal UI
- Room types: **VIP** · **Deluxe** · **Standard** · **Single**
- Status lifecycle: `Available → Occupied → Cleaning → Maintenance`
- Grid view with visual status indicators

### Booking Workflow
- Complete lifecycle: `Pending → Confirmed → Checked-in → Checked-out`
- Admin booking creation & customer self-service
- Atomic checkout with payment recording
- Automatic date overlap detection
- Cancellation with refund processing

### Customer Registry
- Search, pagination & CSV data export
- Loyalty tier system: **Platinum** · **Gold** · **Silver** · **Standard**
- Auto-tier upgrade based on spending & booking history

### Revenue Reports
- Key metrics: **Total Revenue** · **Occupancy Rate** · **ADR** · **RevPAR**
- Revenue breakdown by room type with progress bars
- Top-performing rooms ranking
- Date range filtering

---

## 🏗 Architecture

### System Overview

```
┌──────────────────────────────────────────────────────┐
│          pywebview (Desktop)  /  Browser (Docker)     │
│  ┌────────────────────────────────────────────────┐   │
│  │              Flask Application                 │   │
│  │                                                │   │
│  │   Controller ──→ Model ──→ Database (SQLite)   │
│  │       ↓                                        │
│  │   Templates (Jinja2 + TailwindCSS CDN)         │
│  │                                                │
│  └────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────┘
```

### Design Pattern — MVC

| Layer | Responsibility | Files |
|:---|:---|:---|
| **Controller** | Route handling, request validation, auth guards | `controllers/*.py` |
| **Model** | Business logic, DB queries, data integrity | `models/*.py` |
| **View** | UI rendering, Jinja2 templates, TailwindCSS | `templates/*.html` |
| **Database** | Schema, connection pooling, query helpers | `database/` |

### Tech Stack

| Category | Technology |
|:---|:---|
| **Language** | Python 3.12 |
| **Backend** | Flask 3.0 · Werkzeug · Jinja2 |
| **Frontend** | TailwindCSS (CDN) · Google Material Symbols · Inter + Manrope fonts |
| **Desktop** | pywebview 5.0 (native window) |
| **Database** | SQLite 3 with FK constraints |
| **Container** | Docker · Docker Compose |
| **Security** | CSRF tokens · PBKDF2-SHA256 hashing · Session-based auth |

---

## 🐳 Docker Deployment

| File | Purpose |
|:---|:---|
| `Dockerfile` | Python 3.12-slim image, installs Flask dependencies |
| `docker-compose.yml` | Port mapping `8080:5000`, persistent volume for SQLite |
| `requirements-docker.txt` | Flask-only deps (no pywebview) |
| `src/web_server.py` | Headless Flask entry point |

```bash
# Build & run
docker compose up --build

# Run in background
docker compose up --build -d

# Stop
docker compose down

# Full reset (delete database)
docker compose down -v
```

> **Note**: Docker mode serves Flask directly via browser. Desktop mode uses pywebview for a native window experience. All logic and UI are identical.

---

## 📂 Project Structure

```
htm-project/
│
├── src/                            # Application source
│   ├── app.py                      # App factory, CSRF, context processors
│   ├── config.py                   # Environment-based configuration
│   ├── seed_data.py                # Initial data seeding (users + rooms)
│   ├── web_server.py               # Docker entry point (headless Flask)
│   │
│   ├── controllers/                # MVC — Controllers
│   │   ├── auth_controller.py      #   Login, Register, Forgot Password
│   │   ├── dashboard_controller.py #   Admin dashboard, auth decorators
│   │   ├── booking_controller.py   #   Booking CRUD & lifecycle
│   │   ├── customer_controller.py  #   Customer CRUD & CSV export
│   │   ├── room_controller.py      #   Room CRUD & status management
│   │   └── report_controller.py    #   Revenue analytics & metrics
│   │
│   ├── models/                     # MVC — Models
│   │   ├── user_model.py           #   User auth & password hashing
│   │   ├── room_model.py           #   Room CRUD & status summary
│   │   ├── booking_model.py        #   Booking CRUD, overlap detection, checkout
│   │   ├── customer_model.py       #   Customer CRUD & tier system
│   │   └── payment_model.py        #   Payment records & revenue queries
│   │
│   ├── templates/                  # MVC — Views
│   │   ├── base.html               #   Shared layout (sidebar, toast, nav)
│   │   ├── Login.html              #   Auth forms (login/register/forgot)
│   │   ├── Admin_Dashboard.html    #   Dashboard with stats & activity
│   │   ├── Rooms_Booking.html      #   Room grid with CRUD modals
│   │   ├── Booking_Management.html #   Booking list & workflow actions
│   │   ├── Customers.html          #   Customer registry & search
│   │   └── View_Reports.html       #   Revenue charts & metrics
│   │
│   └── database/                   # Data layer
│       ├── db_manager.py           #   SQLite connection & query helpers
│       └── schema.sql              #   Table definitions & indexes
│
├
│
├── graph/                          # Exported UML diagrams (PDF)
├── test/                           # Unit & integration tests
│
├── Dockerfile                      # Docker image definition
├── docker-compose.yml              # Container orchestration
├── .dockerignore                   # Docker build exclusions
├── requirements.txt                # Desktop dependencies
├── requirements-docker.txt         # Docker dependencies
├── .gitignore                      # Git exclusions
└── README.md
```

---

## 📚 Documentation

All project documentation is available in the [`docs/`](docs/) and [`graph/`](graph/) folders:

| Document | Description |
|:---|:---|
| **Class Diagram** | Object-oriented structure of the system |
| **ERD** | Entity-Relationship diagram for the database |
| **Context DFD** | High-level data flow between system and actors |
| **Level-1 DFD** | Detailed data flow within system processes |
| **Use Case Diagram** | User interaction scenarios by role |
| **Test Cases** | Full QA test case documentation |

---

## 👥 Team

<table>
  <tr>
    <th>#</th>
    <th>Name</th>
    <th>Role</th>
    <th>Responsibilities</th>
  </tr>
  <tr>
    <td>1</td>
    <td><strong>Nguyen Cong Thanh</strong></td>
    <td>🎯 Leader</td>
    <td>General Management · Database Design · Code Review</td>
  </tr>
  <tr>
    <td>2</td>
    <td><strong>Luong Nhat Khoi</strong></td>
    <td>🔧 Vice Leader</td>
    <td>System Architect · Business Logic · Jira/GitHub Manager</td>
  </tr>
  <tr>
    <td>3</td>
    <td><strong>Huynh Nhat Hoa</strong></td>
    <td>🎨 Member</td>
    <td>UI/UX Developer</td>
  </tr>
  <tr>
    <td>4</td>
    <td><strong>Nguyen Minh Man</strong></td>
    <td>⚙️ Member</td>
    <td>Core Logic Developer</td>
  </tr>
  <tr>
    <td>5</td>
    <td><strong>Nguyen Hoang Bao Anh</strong></td>
    <td>📝 Member</td>
    <td>QA/QC · Technical Writer</td>
  </tr>
</table>

---

<p align="center">
  <strong>Group 03 — Software Engineering Project © 2026</strong><br/>
  <sub>Built with ❤️ using Python · Flask · TailwindCSS · Docker</sub>
</p>