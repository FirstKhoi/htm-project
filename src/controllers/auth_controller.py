"""Auth controller — Login, Register, Logout, Forgot Password."""
import re
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.user_model import UserModel
from models.customer_model import CustomerModel

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


def _validate_email(email: str) -> bool:
    return bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle login form."""
    if 'user_id' in session:
        role = session.get('role', '')
        return redirect(url_for('dashboard.index') if role in ('admin', 'staff')
                        else url_for('rooms.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Please enter both email and password.', 'error')
            return render_template('Login.html', mode='login', email=email)

        user = UserModel.find_by_email(email)
        if not user:
            flash('No account found with that email address.', 'error')
            return render_template('Login.html', mode='login', email=email)

        if not UserModel.verify_password(user['password_hash'], password):
            flash('Incorrect password.', 'error')
            return render_template('Login.html', mode='login', email=email)

        # Set session
        session['user_id'] = user['id']
        session['user_email'] = user['email']
        session['user_name'] = user['full_name']
        session['role'] = user['role']
        flash(f'Welcome back, {user["full_name"]}!', 'success')

        return redirect(url_for('dashboard.index') if user['role'] in ('admin', 'staff')
                        else url_for('rooms.index'))

    return render_template('Login.html', mode='login')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle registration form."""
    if 'user_id' in session:
        role = session.get('role', '')
        return redirect(url_for('dashboard.index') if role in ('admin', 'staff')
                        else url_for('rooms.index'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')
        sec_q = request.form.get('security_question', '').strip()
        sec_a = request.form.get('security_answer', '').strip()

        # Validation
        errors = []
        if not full_name or len(full_name) < 2:
            errors.append('Full name must be at least 2 characters long.')
        if not _validate_email(email):
            errors.append('Invalid email address.')
        if len(password) < 6:
            errors.append('Password must be at least 6 characters long.')
        if password != confirm:
            errors.append('Password confirmation does not match.')

        if errors:
            for e in errors:
                flash(e, 'error')
            return render_template('Login.html', mode='register',
                                   full_name=full_name, email=email)

        if UserModel.find_by_email(email):
            flash('This email address is already in use.', 'error')
            return render_template('Login.html', mode='register',
                                   full_name=full_name, email=email)

        try:
            user_id = UserModel.create(
                email=email, password=password, full_name=full_name,
                role='customer', security_question=sec_q or None,
                security_answer=sec_a or None)
            CustomerModel.create(full_name=full_name, email=email, user_id=user_id)
            flash('Registration successful! Please sign in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'error')
            return render_template('Login.html', mode='register',
                                   full_name=full_name, email=email)

    return render_template('Login.html', mode='register')


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Multi-step password recovery via security questions."""
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

            session['reset_email'] = email
            return render_template('Login.html', mode='forgot', step='answer',
                                   email=email, security_question=user['security_question'])

        elif step == 'verify_answer':
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
                                       email=email, security_question=user['security_question'])

            session['reset_verified'] = True
            return render_template('Login.html', mode='forgot', step='reset', email=email)

        elif step == 'reset_password':
            email = session.get('reset_email', '')
            if not email or not session.get('reset_verified'):
                flash('Your session has expired. Please try again.', 'error')
                return redirect(url_for('auth.forgot_password'))

            new_pw = request.form.get('new_password', '')
            confirm = request.form.get('confirm_password', '')

            if len(new_pw) < 6:
                flash('Password must be at least 6 characters long.', 'error')
                return render_template('Login.html', mode='forgot', step='reset', email=email)
            if new_pw != confirm:
                flash('Password confirmation does not match.', 'error')
                return render_template('Login.html', mode='forgot', step='reset', email=email)

            user = UserModel.find_by_email(email)
            if user:
                UserModel.update_password(user['id'], new_pw)
                session.pop('reset_email', None)
                session.pop('reset_verified', None)
                flash('Password reset successful! Please sign in.', 'success')
                return redirect(url_for('auth.login'))

    return render_template('Login.html', mode='forgot', step='find_email')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('auth.login'))
