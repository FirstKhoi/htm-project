"""Room controller — room CRUD and status management."""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from controllers.dashboard_controller import admin_required, login_required
from models.room_model import RoomModel

rooms_bp = Blueprint('rooms', __name__, url_prefix='/rooms')


@rooms_bp.route('/')
@login_required
def index():
    """List rooms with status summary."""
    status_filter = request.args.get('status')
    type_filter = request.args.get('type')
    return render_template('Rooms_Booking.html',
                           rooms=RoomModel.get_all(status=status_filter, room_type=type_filter),
                           summary=RoomModel.get_status_summary(),
                           current_status=status_filter, current_type=type_filter)


@rooms_bp.route('/add', methods=['POST'])
@admin_required
def add():
    """Add a new room."""
    room_number = request.form.get('room_number', '').strip()
    room_name = request.form.get('room_name', '').strip()
    room_type = request.form.get('room_type', '').strip()
    price = request.form.get('price_per_night', '0')
    max_guests = request.form.get('max_guests', '2')
    description = request.form.get('description', '').strip()
    floor = request.form.get('floor', '').strip()
    wing = request.form.get('wing', '').strip()
    image_url = request.form.get('image_url', '').strip()

    errors = []
    if not room_number:
        errors.append('Room number is required.')
    elif RoomModel.find_by_number(room_number):
        errors.append(f'Room number "{room_number}" already exists.')
    if not room_name:
        errors.append('Room name is required.')
    if room_type not in ('VIP', 'Deluxe', 'Standard', 'Single'):
        errors.append('Invalid room type.')

    try:
        price = float(price)
        if price <= 0: raise ValueError
    except ValueError:
        errors.append('Room price must be a positive number.')

    try:
        max_guests = int(max_guests)
        if max_guests < 1 or max_guests > 10: raise ValueError
    except ValueError:
        errors.append('Maximum guests must be between 1 and 10.')

    if errors:
        for e in errors:
            flash(e, 'error')
        return redirect(url_for('rooms.index'))

    RoomModel.create(
        room_number=room_number, room_name=room_name, room_type=room_type,
        price_per_night=price, max_guests=max_guests,
        description=description or None, image_url=image_url or None,
        floor=floor or None, wing=wing or None)

    flash(f'Room {room_number} added successfully!', 'success')
    return redirect(url_for('rooms.index'))


@rooms_bp.route('/update/<int:room_id>', methods=['POST'])
@admin_required
def update(room_id):
    """Update room details."""
    room = RoomModel.find_by_id(room_id)
    if not room:
        flash('Room not found.', 'error')
        return redirect(url_for('rooms.index'))

    updates = {}
    for field in ['room_name', 'room_type', 'description', 'floor', 'wing', 'image_url']:
        val = request.form.get(field)
        if val is not None:
            updates[field] = val.strip()

    price = request.form.get('price_per_night')
    if price:
        try:
            updates['price_per_night'] = float(price)
        except ValueError:
            flash('Invalid room price.', 'error')
            return redirect(url_for('rooms.index'))

    guests = request.form.get('max_guests')
    if guests:
        try:
            updates['max_guests'] = int(guests)
        except ValueError:
            flash('Invalid guest count.', 'error')
            return redirect(url_for('rooms.index'))

    if updates:
        RoomModel.update(room_id, **updates)
        flash('Room updated successfully.', 'success')
    return redirect(url_for('rooms.index'))


@rooms_bp.route('/delete/<int:room_id>', methods=['POST'])
@admin_required
def delete(room_id):
    """Delete a room."""
    room = RoomModel.find_by_id(room_id)
    if not room:
        flash('Room not found.', 'error')
        return redirect(url_for('rooms.index'))

    if not RoomModel.delete(room_id):
        flash('Unable to delete this room because it has active bookings.', 'error')
    else:
        flash(f'Room {room["room_number"]} deleted successfully.', 'success')
    return redirect(url_for('rooms.index'))


@rooms_bp.route('/status/<int:room_id>', methods=['POST'])
@admin_required
def update_status(room_id):
    """Update room status."""
    new_status = request.form.get('status')
    if new_status not in ('available', 'occupied', 'cleaning', 'maintenance'):
        flash('Invalid status.', 'error')
        return redirect(url_for('rooms.index'))
    RoomModel.update_status(room_id, new_status)
    flash('Room status updated successfully.', 'success')
    return redirect(url_for('rooms.index'))
