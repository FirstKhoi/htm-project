-- =====================================================
-- Hotel Management System - Database Schema
-- Group 03 - Software Engineering Project
-- =====================================================

-- Bảng USERS: Quản lý tài khoản đăng nhập
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'staff' CHECK(role IN ('admin', 'staff', 'customer')),
    security_question TEXT,
    security_answer_hash TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Bảng ROOMS: Quản lý phòng khách sạn
CREATE TABLE IF NOT EXISTS rooms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_number TEXT UNIQUE NOT NULL,
    room_name TEXT NOT NULL,
    room_type TEXT NOT NULL CHECK(room_type IN ('VIP', 'Deluxe', 'Standard', 'Single')),
    price_per_night REAL NOT NULL CHECK(price_per_night > 0),
    max_guests INTEGER NOT NULL DEFAULT 2,
    status TEXT NOT NULL DEFAULT 'available' CHECK(status IN ('available', 'occupied', 'cleaning', 'maintenance')),
    description TEXT,
    image_url TEXT,
    floor TEXT,
    wing TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Bảng CUSTOMERS: Quản lý khách hàng
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    id_card TEXT,
    nationality TEXT DEFAULT 'Vietnam',
    tier TEXT DEFAULT 'Standard' CHECK(tier IN ('Platinum', 'Gold', 'Silver', 'Standard')),
    total_spent REAL DEFAULT 0,
    total_bookings INTEGER DEFAULT 0,
    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'dormant', 'blacklisted')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Bảng BOOKINGS: Quản lý đặt phòng
CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_code TEXT UNIQUE NOT NULL,
    customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE RESTRICT,
    room_id INTEGER NOT NULL REFERENCES rooms(id) ON DELETE RESTRICT,
    check_in_date DATE NOT NULL,
    check_out_date DATE NOT NULL,
    num_guests INTEGER NOT NULL DEFAULT 1,
    status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending', 'confirmed', 'checked_in', 'checked_out', 'cancelled')),
    total_amount REAL NOT NULL CHECK(total_amount >= 0),
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CHECK(check_out_date > check_in_date)
);

-- Bảng PAYMENTS: Quản lý thanh toán
CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id INTEGER NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
    amount REAL NOT NULL CHECK(amount > 0),
    payment_method TEXT DEFAULT 'cash' CHECK(payment_method IN ('cash', 'card', 'transfer')),
    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'completed', 'refunded')),
    payment_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    transaction_ref TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- Indexes for performance
-- =====================================================
CREATE INDEX IF NOT EXISTS idx_bookings_customer ON bookings(customer_id);
CREATE INDEX IF NOT EXISTS idx_bookings_room ON bookings(room_id);
CREATE INDEX IF NOT EXISTS idx_bookings_status ON bookings(status);
CREATE INDEX IF NOT EXISTS idx_bookings_dates ON bookings(check_in_date, check_out_date);
CREATE INDEX IF NOT EXISTS idx_payments_booking ON payments(booking_id);
CREATE INDEX IF NOT EXISTS idx_rooms_status ON rooms(status);
CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email);
CREATE INDEX IF NOT EXISTS idx_customers_tier ON customers(tier);
