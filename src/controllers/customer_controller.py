"""Customer controller — Customer management routes."""
import csv
import io
from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from controllers.dashboard_controller import admin_required
from models.customer_model import CustomerModel

customers_bp = Blueprint('customers', __name__, url_prefix='/customers')


@customers_bp.route('/')
@admin_required
def index():
    """List all customers with search and pagination."""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    per_page = 10

    customers, total = CustomerModel.get_paginated(
        page=page, per_page=per_page,
        search=search if search else None
    )

    stats = CustomerModel.get_stats()

    # Pagination info
    total_pages = (total + per_page - 1) // per_page
    pagination = {
        'page': page,
        'per_page': per_page,
        'total': total,
        'total_pages': total_pages,
        'has_prev': page > 1,
        'has_next': page < total_pages,
        'prev_num': page - 1,
        'next_num': page + 1,
    }

    return render_template('Customers.html',
                           customers=customers,
                           stats=stats,
                           pagination=pagination,
                           search=search)


@customers_bp.route('/add', methods=['POST'])
@admin_required
def add():
    """Add a new customer."""
    full_name = request.form.get('full_name', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    id_card = request.form.get('id_card', '').strip()
    nationality = request.form.get('nationality', 'Vietnam').strip()

    # Validation
    errors = []
    if not full_name or len(full_name) < 2:
        errors.append('Full name must be at least 2 characters long.')
    if not email:
        errors.append('Email is required.')
    elif CustomerModel.find_by_email(email):
        errors.append('This email address is already in use.')

    if errors:
        for e in errors:
            flash(e, 'error')
        return redirect(url_for('customers.index'))

    CustomerModel.create(
        full_name=full_name,
        email=email,
        phone=phone or None,
        id_card=id_card or None,
        nationality=nationality,
    )

    flash(f'Customer "{full_name}" added successfully!', 'success')
    return redirect(url_for('customers.index'))


@customers_bp.route('/update/<int:customer_id>', methods=['POST'])
@admin_required
def update(customer_id):
    """Update customer details."""
    customer = CustomerModel.find_by_id(customer_id)
    if not customer:
        flash('Customer not found.', 'error')
        return redirect(url_for('customers.index'))

    updates = {}
    for field in ['full_name', 'phone', 'id_card', 'nationality', 'status']:
        val = request.form.get(field)
        if val is not None:
            updates[field] = val.strip()

    # Email needs uniqueness check
    new_email = request.form.get('email')
    if new_email and new_email.strip() != customer['email']:
        if CustomerModel.find_by_email(new_email.strip()):
            flash('This email address is already in use.', 'error')
            return redirect(url_for('customers.index'))
        updates['email'] = new_email.strip()

    if updates:
        CustomerModel.update(customer_id, **updates)
        flash('Customer updated successfully.', 'success')

    return redirect(url_for('customers.index'))


@customers_bp.route('/delete/<int:customer_id>', methods=['POST'])
@admin_required
def delete(customer_id):
    """Delete a customer."""
    customer = CustomerModel.find_by_id(customer_id)
    if not customer:
        flash('Customer not found.', 'error')
        return redirect(url_for('customers.index'))

    if not CustomerModel.delete(customer_id):
        flash('Unable to delete this customer because they have active bookings.', 'error')
    else:
        flash(f'Customer "{customer["full_name"]}" deleted successfully.', 'success')

    return redirect(url_for('customers.index'))


@customers_bp.route('/export')
@admin_required
def export():
    """Export customer list to CSV."""
    customers = CustomerModel.get_all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Full Name', 'Email', 'Phone', 'ID Card',
                     'Nationality', 'Tier', 'Total Spent', 'Total Bookings',
                     'Status', 'Created At'])

    for c in customers:
        writer.writerow([
            c['id'], c['full_name'], c['email'], c['phone'] or '',
            c['id_card'] or '', c['nationality'], c['tier'],
            c['total_spent'], c['total_bookings'], c['status'],
            c['created_at']
        ])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment;filename=customers_export.csv'}
    )
