# app/routes/auth.py

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from flask import abort
from gramatike_app.models import User
from werkzeug.security import check_password_hash

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        from datetime import datetime
        if not user or not check_password_hash(user.password, request.form['password']):
            flash('Login inválido.')
            return render_template('login.html')
        if getattr(user, 'is_banned', False):
            flash(f'Conta banida: {user.ban_reason or "motivo não especificado"}')
            return render_template('login.html')
        if getattr(user, 'suspended_until', None) and user.suspended_until and datetime.utcnow() < user.suspended_until:
            flash(f'Conta suspensa até {user.suspended_until.strftime('%d/%m %H:%M')}')
            return render_template('login.html')
        login_user(user)
        return redirect(url_for('main.dashboard'))
    
    # GET
    return render_template('login.html')