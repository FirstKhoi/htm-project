"""Authentication controller — Login, Register, Logout, Forgot Password routes."""
import re
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.user_model import UserModel
from models.customer_model import CustomerModel


auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def _validate_email(email: str) -> bool:
    """Check if email format is valid."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page and form handler."""
    if 'user_id' in session:
        # Redirect to the correct page based on role
        role = session.get('role', '')
        if role in ('admin', 'staff'):
            return redirect(url_for('dashboard.index'))
        return redirect(url_for('rooms.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        # Validation
        if not email or not password:
            flash('Please enter both email and password.', 'error')
            return render_template('Login.html', mode='login', email=email)

        # Find user
        user = UserModel.find_by_email(email)
        if not user:
            flash('No account found with that email address.', 'error')
            return render_template('Login.html', mode='login', email=email)

        # Verify password
        if not UserModel.verify_password(user['password_hash'], password):
            flash('Incorrect password.', 'error')
            return render_template('Login.html', mode='login', email=email)

        # Set session
        session['user_id'] = user['id']
        session['user_email'] = user['email']
        session['user_name'] = user['full_name']
        session['role'] = user['role']

        flash(f'Welcome back, {user["full_name"]}!', 'success')

        # Redirect based on role
        if user['role'] in ('admin', 'staff'):
            return redirect(url_for('dashboard.index'))
        return redirect(url_for('rooms.index'))

    return render_template('Login.html', mode='login')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Register page and form handler."""
    if 'user_id' in session:
        role = session.get('role', '')
        if role in ('admin', 'staff'):
            return redirect(url_for('dashboard.index'))
        return redirect(url_for('rooms.index'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        security_question = request.form.get('security_question', '').strip()
        security_answer = request.form.get('security_answer', '').strip()

        # Validation
        errors = []
        if not full_name or len(full_name) < 2:
            errors.append('Full name must be at least 2 characters long.')
        if not _validate_email(email):
            errors.append('Invalid email address.')
        if len(password) < 6:
            errors.append('Password must be at least 6 characters long.')
        if password != confirm_password:
            errors.append('Password confirmation does not match.')

        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('Login.html', mode='register',
                                   full_name=full_name, email=email)

        # Check if email exists
        if UserModel.find_by_email(email):
            flash('This email address is already in use.', 'error')
            return render_template('Login.html', mode='register',
                                   full_name=full_name, email=email)

        # Create user (customer role)
        try:
            user_id = UserModel.create(
                email=email,
                password=password,
                full_name=full_name,
                role='customer',
                security_question=security_question or None,
                security_answer=security_answer or None
            )

            # Also create a customer record linked to this user
            CustomerModel.create(
                full_name=full_name,
                email=email,
                user_id=user_id
            )

            flash('Registration successful! Please sign in.', 'success')
            return redirect(url_for('auth.login'))

        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'error')
            return render_template('Login.html', mode='register',
                                   full_name=full_name, email=email)

    return render_template('Login.html', mode='register')


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Forgot password flow using security questions."""
    if request.method == 'POST':
        step = request.form.get('step', 'find_email')

        if step == 'find_email':
            email = request.form.get('email', '').strip()
            user = UserModel.find_by_email(email)

            if not user:
                flash('No account found with that email address.', 'error')
                return render_template('Login.html', mode='forgot', step='find_email')

            if not user['security_question']:
                flash('This account does not have a security question set.', 'error')
                return render_template('Login.html', mode='forgot', step='find_email')

            # Store email in session — not in hidden form field
            session['reset_email'] = email

            return render_template('Login.html', mode='forgot', step='answer',
                                   email=email,
                                   security_question=user['security_question'])

        elif step == 'verify_answer':
            # Read email from session — tamper-proof
            email = session.get('reset_email', '')
            answer = request.form.get('security_answer', '').strip()

            if not email:
                flash('Your session has expired. Please try again.', 'error')
                return redirect(url_for('auth.forgot_password'))

            user = UserModel.find_by_email(email)
            if not user or not UserModel.verify_security_answer(
                    user['security_answer_hash'], answer):
                flash('Incorrect answer.', 'error')
                return render_template('Login.html', mode='forgot', step='answer',
                                       email=email,
                                       security_question=user['security_question'])

            # Mark as verified in session
            session['reset_verified'] = True

            return render_template('Login.html', mode='forgot', step='reset',
                                   email=email)

        elif step == 'reset_password':
            # Read email from session — tamper-proof
            email = session.get('reset_email', '')
            verified = session.get('reset_verified', False)

            if not email or not verified:
                flash('Your session has expired. Please try again.', 'error')
                return redirect(url_for('auth.forgot_password'))

            new_password = request.form.get('new_password', '')
            confirm_password = request.form.get('confirm_password', '')

            if len(new_password) < 6:
                flash('Password must be at least 6 characters long.', 'error')
                return render_template('Login.html', mode='forgot', step='reset',
                                       email=email)

            if new_password != confirm_password:
                flash('Password confirmation does not match.', 'error')
                return render_template('Login.html', mode='forgot', step='reset',
                                       email=email)

            user = UserModel.find_by_email(email)
            if user:
                UserModel.update_password(user['id'], new_password)
                # Clean up session
                session.pop('reset_email', None)
                session.pop('reset_verified', None)
                flash('Password reset successful! Please sign in.', 'success')
                return redirect(url_for('auth.login'))

    return render_template('Login.html', mode='forgot', step='find_email')


@auth_bp.route('/logout')
def logout():
    """Log out and clear session."""
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('auth.login'))
