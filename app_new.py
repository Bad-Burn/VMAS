from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import timedelta, datetime
from functools import wraps
import qrcode
import io
import base64
import re
from flask_session import Session
from models import db, SecurityGuard, Department, Visitor, VisitorRegistration, DepartmentStaff, SystemLog, VisitorQR
from db_config import init_db

# Initialize Flask app
app = Flask(__name__, template_folder="templates", static_folder="static")

# Get environment setting
env = os.getenv('FLASK_ENV', 'development')

# Load the appropriate configuration
from config import config
app.config.from_object(config[env])

# Set session lifetime
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

# Initialize extensions
Session(app)
init_db(app)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('mainweb.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user_type = request.form.get('user_type')

        if user_type == 'security':
            user = SecurityGuard.query.filter_by(email=email).first()
        elif user_type == 'department':
            user = DepartmentStaff.query.filter_by(email=email).first()
        elif user_type == 'visitor':
            user = Visitor.query.filter_by(email=email).first()
        else:
            return jsonify({'error': 'Invalid user type'}), 400

        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.security_id if user_type == 'security' else \
                                user.staff_id if user_type == 'department' else \
                                user.visitor_id
            session['user_type'] = user_type
            
            if user_type == 'security':
                return redirect(url_for('security_dashboard'))
            elif user_type == 'department':
                return redirect(url_for('department_dashboard'))
            else:
                return redirect(url_for('visitor_dashboard'))
        
        return jsonify({'error': 'Invalid credentials'}), 401

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user_type = request.form.get('user_type')
        
        # Check if email already exists
        if user_type == 'visitor':
            if Visitor.query.filter_by(email=email).first():
                return jsonify({'error': 'Email already registered'}), 400
            
            new_user = Visitor(
                visitor_id=generate_id('V'),
                email=email,
                visitor_name=request.form.get('name'),
                password_hash=generate_password_hash(password),
                address=request.form.get('address'),
                contact_no=request.form.get('contact')
            )
        
        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    return render_template('register.html')

def generate_id(prefix):
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    return f"{prefix}{timestamp}"

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
