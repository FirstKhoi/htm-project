"""Booking controller — full booking lifecycle management."""
from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from controllers.dashboard_controller import admin_required, login_required
from models.booking_model import BookingModel
from models.room_model import RoomModel
from models.customer_model import CustomerModel
from models.payment_model import PaymentModel

bookings_bp = Blueprint('bookings', __name__, url_prefix='/bookings')


@bookings_bp.route('/')
@admin_required
def index():
    """List bookings with filter options."""
    status_filter = request.args.get('status')
    search = request.args.get('search', '').strip()
    return render_template('Booking_Management.html',
                           bookings=BookingModel.get_all(status=status_filter,
                                                         search=search or None),
                           rooms=RoomModel.get_all(),
                           customers=CustomerModel.get_all(),
                           current_status=status_filter, search=search)


@bookings_bp.route('/add', methods=['POST'])
@admin_required
def add():
    """Create a new booking (admin)."""
    customer_id = request.form.get('customer_id', type=int)
    room_id = request.form.get('room_id', type=int)
    check_in = request.form.get('check_in_date', '').strip()
    check_out = request.form.get('check_out_date', '').strip()
    num_guests = request.form.get('num_guests', 1, type=int)
    notes = request.form.get('notes', '').strip()

    errors = []
    customer = CustomerModel.find_by_id(customer_id) if customer_id else None
    if not customer:
        errors.append('Customer not found.')

    room = RoomModel.find_by_id(room_id) if room_id else None
    if not room:
        errors.append('Room not found.')

    if not check_in or not check_out:
        errors.append('Check-in and check-out dates are required.')
    else:
        try:
            d_in, d_out = date.fromisoformat(check_in), date.fromisoformat(check_out)
            if d_out <= d_in:
                errors.append('Check-out date must be after check-in date.')
        except ValueError:
            errors.append('Invalid date format (YYYY-MM-DD).')

    if room and num_guests > room['max_guests']:
        errors.append(f'Number of guests ({num_guests}) exceeds room capacity ({room["max_guests"]}).')

    if room and check_in and check_out and not errors:
        if BookingModel.check_overlap(room_id, check_in, check_out):
            errors.append('This room is already booked for the selected dates.')

    if errors:
        for e in errors:
            flash(e, 'error')
        return redirect(url_for('bookings.index'))

    total = BookingModel.calculate_total(room['price_per_night'], check_in, check_out)

    try:
        BookingModel.create(
            customer_id=customer_id, room_id=room_id,
            check_in_date=check_in, check_out_date=check_out,
            num_guests=num_guests, total_amount=total,
            notes=notes or None, enforce_overlap=True)
    except ValueError as exc:
        if str(exc) == 'OVERLAP_BOOKING':
            flash('This room was just booked by another request. Please choose a different room or date range.', 'error')
        else:
            flash('Invalid booking data.', 'error')
        return redirect(url_for('bookings.index'))
    except RuntimeError:
        flash('Unable to generate a new booking code. Please try again.', 'error')
        return redirect(url_for('bookings.index'))

    flash(f'Booking created successfully for {customer["full_name"]} - {room["room_number"]}!', 'success')
    return redirect(url_for('bookings.index'))


@bookings_bp.route('/approve/<int:booking_id>', methods=['POST'])
@admin_required
def approve(booking_id):
    """Approve pending booking → confirmed."""
    booking = BookingModel.find_by_id(booking_id)
    if not booking:
        flash('Booking not found.', 'error')
        return redirect(url_for('bookings.index'))
    if booking['status'] != 'pending':
        flash('Only bookings with "Pending" status can be approved.', 'error')
        return redirect(url_for('bookings.index'))

    BookingModel.update_status(booking_id, 'confirmed')
    flash(f'Booking {booking["booking_code"]} approved successfully!', 'success')
    return redirect(url_for('bookings.index'))


@bookings_bp.route('/checkin/<int:booking_id>', methods=['POST'])
@admin_required
def checkin(booking_id):
    """Check-in guest → confirmed to checked_in."""
    booking = BookingModel.find_by_id(booking_id)
    if not booking:
        flash('Booking not found.', 'error')
        return redirect(url_for('bookings.index'))
    if booking['status'] != 'confirmed':
        flash('Only approved bookings ("Confirmed") can be checked in.', 'error')
        return redirect(url_for('bookings.index'))

    BookingModel.update_status(booking_id, 'checked_in')
    RoomModel.update_status(booking['room_id'], 'occupied')
    flash(f'Check-in successful for {booking["customer_name"]} - {booking["room_number"]}!', 'success')
    return redirect(url_for('bookings.index'))


@bookings_bp.route('/checkout/<int:booking_id>', methods=['POST'])
@admin_required
def checkout(booking_id):
    """Check-out guest → creates payment, updates room."""
    payment_method = request.form.get('payment_method', 'cash')
    try:
        booking = BookingModel.checkout_booking(booking_id, payment_method)
    except ValueError as exc:
        msgs = {
            'BOOKING_NOT_FOUND': 'Booking not found.',
            'INVALID_STATUS': 'Only bookings with "Checked In" status can be checked out.',
            'INVALID_PAYMENT_METHOD': 'Invalid payment method.',
        }
        flash(msgs.get(str(exc), 'Checkout failed because the data is invalid.'), 'error')
        return redirect(url_for('bookings.index'))
    except Exception:
        flash('An error occurred while processing check-out. No partial data was saved.', 'error')
        return redirect(url_for('bookings.index'))

    flash(f'Check-out successful! Payment of ${booking["total_amount"]:.2f} has been recorded.', 'success')
    return redirect(url_for('bookings.index'))


@bookings_bp.route('/cancel/<int:booking_id>', methods=['POST'])
@admin_required
def cancel(booking_id):
    """Cancel booking, create refund if payment exists."""
    booking = BookingModel.find_by_id(booking_id)
    if not booking:
        flash('Booking not found.', 'error')
        return redirect(url_for('bookings.index'))
    if booking['status'] in ('checked_out', 'cancelled'):
        flash('Unable to cancel a completed or already cancelled booking.', 'error')
        return redirect(url_for('bookings.index'))

    if booking['status'] == 'checked_in':
        RoomModel.update_status(booking['room_id'], 'available')

    # Refund existing payments
    payments = PaymentModel.get_by_booking(booking_id)
    completed_amount = sum(p['amount'] for p in payments if p['status'] == 'completed')
    if completed_amount > 0:
        PaymentModel.create_refund(booking_id, completed_amount)

    BookingModel.update_status(booking_id, 'cancelled')
    flash(f'Booking {booking["booking_code"]} has been cancelled.', 'success')
    return redirect(url_for('bookings.index'))


@bookings_bp.route('/customer-book', methods=['POST'])
@login_required
def customer_book():
    """Customer self-service booking (status = pending)."""
    room_id = request.form.get('room_id', type=int)
    check_in = request.form.get('check_in_date', '').strip()
    check_out = request.form.get('check_out_date', '').strip()
    num_guests = request.form.get('num_guests', 1, type=int)
    notes = request.form.get('notes', '').strip()

    # Find linked customer
    customer = CustomerModel.find_by_email(session.get('user_email', ''))
    if not customer:
        flash('Customer profile not found. Please contact an administrator.', 'error')
        return redirect(url_for('rooms.index'))

    room = RoomModel.find_by_id(room_id) if room_id else None
    if not room:
        flash('Room not found.', 'error')
        return redirect(url_for('rooms.index'))
    if room['status'] != 'available':
        flash('This room is currently unavailable.', 'error')
        return redirect(url_for('rooms.index'))

    errors = []
    if not check_in or not check_out:
        errors.append('Check-in and check-out dates are required.')
    else:
        try:
            d_in, d_out = date.fromisoformat(check_in), date.fromisoformat(check_out)
            if d_out <= d_in:
                errors.append('Check-out date must be after check-in date.')
            if d_in < date.today():
                errors.append('Check-in date cannot be in the past.')
        except ValueError:
            errors.append('Invalid date format.')

    if room and num_guests > room['max_guests']:
        errors.append(f'Number of guests ({num_guests}) exceeds room capacity ({room["max_guests"]}).')

    if room and check_in and check_out and not errors:
        if BookingModel.check_overlap(room_id, check_in, check_out):
            errors.append('This room is already booked for the selected dates.')

    if errors:
        for e in errors:
            flash(e, 'error')
        return redirect(url_for('rooms.index'))

    total = BookingModel.calculate_total(room['price_per_night'], check_in, check_out)

    try:
        BookingModel.create(
            customer_id=customer['id'], room_id=room_id,
            check_in_date=check_in, check_out_date=check_out,
            num_guests=num_guests, total_amount=total,
            notes=notes or None, enforce_overlap=True)
    except ValueError as exc:
        if str(exc) == 'OVERLAP_BOOKING':
            flash('This room was just booked by another request. Please choose a different date range.', 'error')
        else:
            flash('Unable to create the booking because the data is invalid.', 'error')
        return redirect(url_for('rooms.index'))
    except RuntimeError:
        flash('Unable to generate a new booking code. Please try again.', 'error')
        return redirect(url_for('rooms.index'))

    flash(f'Your booking request for room {room["room_number"]} has been submitted! Please wait for admin confirmation.', 'success')
    return redirect(url_for('rooms.index'))
