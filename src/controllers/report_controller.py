"""Report controller — Revenue insights and analytics."""
from flask import Blueprint, render_template, request
from controllers.dashboard_controller import admin_required
from models.payment_model import PaymentModel
from models.room_model import RoomModel
from database.db_manager import get_db

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

@reports_bp.route('/')
@admin_required
def index():
    """Render the reports page with analytics data."""
    # Date range filtering
    start_date = (request.args.get('start') or '').strip() or None
    end_date = (request.args.get('end') or '').strip() or None

    # 1. Total Revenue
    total_revenue = PaymentModel.get_total_revenue(start_date, end_date)

    # 2. Occupancy Rate
    room_summary = RoomModel.get_status_summary()
    total_rooms = room_summary['total'] or 1
    occupied = room_summary.get('occupied', 0)
    occupancy_rate = round((occupied / total_rooms) * 100, 1)

    # 3. Average Daily Rate (ADR)
    db = get_db()
    nights_query = """
        SELECT COALESCE(SUM(
            CAST(JULIANDAY(check_out_date) - JULIANDAY(check_in_date) AS INTEGER)
        ), 1)
        FROM bookings
        WHERE status IN ('checked_in', 'checked_out')
    """
    nights_params = []
    if start_date:
        nights_query += " AND DATE(check_out_date) >= DATE(?)"
        nights_params.append(start_date)
    if end_date:
        nights_query += " AND DATE(check_out_date) <= DATE(?)"
        nights_params.append(end_date)
    total_nights_sold = db.count(nights_query, tuple(nights_params)) or 1
    adr = round(total_revenue / total_nights_sold, 2)

    # 4. RevPAR
    revpar = round(adr * (occupancy_rate / 100), 2)

    # 5. Revenue by room type
    revenue_by_type = PaymentModel.get_revenue_by_room_type(start_date, end_date)

    # Calculate percentage for each type
    total_for_pct = sum(r['revenue'] for r in revenue_by_type) or 1
    for r in revenue_by_type:
        r['percentage'] = round((r['revenue'] / total_for_pct) * 100, 1)

    # 6. Top rooms by revenue
    top_rooms_query = """
        SELECT r.room_number, r.room_name, r.room_type,
               COALESCE(SUM(p.amount), 0) as total_revenue,
               COUNT(DISTINCT b.id) as booking_count
        FROM rooms r
        LEFT JOIN bookings b ON r.id = b.room_id
        LEFT JOIN payments p ON b.id = p.booking_id AND p.status = 'completed'
    """
    top_rooms_params = []
    if start_date:
        top_rooms_query += " AND DATE(p.payment_date) >= DATE(?)"
        top_rooms_params.append(start_date)
    if end_date:
        top_rooms_query += " AND DATE(p.payment_date) <= DATE(?)"
        top_rooms_params.append(end_date)
    top_rooms_query += """
        GROUP BY r.id
        ORDER BY total_revenue DESC
        LIMIT 5
    """
    top_rooms = db.fetch_all(top_rooms_query, tuple(top_rooms_params))

    # 7. Recent payments
    recent_payments = PaymentModel.get_recent(
        limit=5, start_date=start_date, end_date=end_date
    )

    return render_template('View_Reports.html',
                           total_revenue=total_revenue,
                           occupancy_rate=occupancy_rate,
                           adr=adr,
                           revpar=revpar,
                           revenue_by_type=revenue_by_type,
                           top_rooms=top_rooms,
                           recent_payments=recent_payments,
                           start_date=start_date,
                           end_date=end_date)
