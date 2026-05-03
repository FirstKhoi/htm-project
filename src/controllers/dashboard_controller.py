"""Dashboard controller — admin overview with aggregated data."""
from functools import wraps
from flask import Blueprint, render_template, session, redirect, url_for, flash
from models.room_model import RoomModel
from models.booking_model import BookingModel
from models.payment_model import PaymentModel

dashboard_bp = Blueprint('dashboard', __name__)


def login_required(f):
    """Require any logged-in user."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please sign in to continue.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    """Require admin or staff role."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        if session.get('role') not in ('admin', 'staff'):
            session.clear()
            flash('You do not have permission to access this page. Please sign in with an Admin or Staff account.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@admin_required
def index():
    """Render admin dashboard with stats."""
    room_summary = RoomModel.get_status_summary()
    return render_template('Admin_Dashboard.html',
                           room_summary=room_summary,
                           pending_count=BookingModel.get_pending_count(),
                           today_revenue=PaymentModel.get_today_revenue(),
                           recent_bookings=BookingModel.get_recent(limit=5),
                           today_checkins=BookingModel.get_today_checkins())
