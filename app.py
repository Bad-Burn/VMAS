from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import timedelta, datetime
from functools import wraps
import qrcode
import io
import base64
import re
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from sqlalchemy.exc import SQLAlchemyError

# Initialize Flask app
app = Flask(__name__, template_folder="templates", static_folder="static")

# Configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config.update(
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "vmas.db"),
    SQLALCHEMY_TRACK_MODIFICATIONS = False,
    SECRET_KEY = "your-secret-key-goes-here",
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30),
    SESSION_TYPE = 'filesystem',
    SESSION_FILE_DIR = os.path.join(basedir, 'flask_session'),
    SESSION_FILE_THRESHOLD = 500
)

# Initialize extensions
from models.db import db, init_db
init_db(app)
Session(app)

# Import models
from models.user import User
from models.visit import Visit
from models.visitor_qr import VisitorQR

try:
    # Create all tables
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("Database tables created successfully!")
except Exception as e:
    print(f"Error creating database tables: {str(e)}")

def generate_qr_code(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_str = base64.b64encode(img_buffer.getvalue()).decode()
    return img_str

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("home"))
        return f(*args, **kwargs)
    return decorated_function

def role_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "role" not in session or session["role"] not in allowed_roles:
                return redirect(url_for("home"))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route("/")
def home():
    if "user_id" in session:
        # If user is already logged in, redirect to their dashboard
        return redirect(url_for(session["role"]))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("mainweb.html")
        
    try:
        data = request.form
        user_id = data.get("userId", '').strip()
        password = data.get("password", '').strip()
        role = data.get("role", '').strip()

        print(f"Login attempt - ID: {user_id}, Role: {role}")  # Debug log

        # Validate input
        if not all([user_id, password, role]):
            return jsonify({"success": False, "message": "All fields are required"})

        # Find user
        user = User.query.filter_by(id=user_id).first()
        print(f"Found user: {user}")  # Debug log

        if not user:
            return jsonify({"success": False, "message": "User not found"})

        if user.role != role:
            return jsonify({"success": False, "message": "Invalid role for this user"})

        if not check_password_hash(user.password, password):
            return jsonify({"success": False, "message": "Invalid password"})

        # User authenticated successfully, set up session
        session.permanent = True
        session["user_id"] = user.id
        session["role"] = user.role
        session["name"] = user.name

        # Return appropriate redirect
        redirects = {
            "security": "/security",
            "department": "/department",
            "visitor": "/visitor"
        }
        
        if role in redirects:
            return jsonify({"success": True, "redirect": redirects[role]})
        return jsonify({"success": False, "message": "Invalid role"})

    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({"success": False, "message": "An error occurred during login"})

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("mainregister.html")
    
    try:
        print("Starting registration process...")  # Debug log
        
        # Get form data
        data = request.form
        user_id = data.get("userId", '').strip()
        password = data.get("password", '').strip()
        role = data.get("role", '').strip()
        name = data.get("name", '').strip()
        email = data.get("email", '').strip()
        
        print(f"Received registration data - ID: {user_id}, Role: {role}, Name: {name}, Email: {email}")

        # 1. Validate required fields
        if not all([user_id, password, role, name, email]):
            missing = [field for field, value in {'userId': user_id, 'password': password, 
                      'role': role, 'name': name, 'email': email}.items() if not value]
            return jsonify({
                "success": False, 
                "message": f"Missing required fields: {', '.join(missing)}"
            })

        # 2. Validate role
        valid_roles = ['visitor', 'department', 'security']
        if role not in valid_roles:
            return jsonify({
                "success": False, 
                "message": f"Invalid role: {role}. Must be one of: {', '.join(valid_roles)}"
            })

        # 3. Validate ID format
        id_patterns = {
            'visitor': r'^V\d{6}$',
            'department': r'^D\d{6}$',
            'security': r'^S\d{6}$'
        }
        
        if not re.match(id_patterns[role], user_id):
            return jsonify({
                "success": False, 
                "message": f"{role.title()} ID must be in format: {role[0].upper()}123456"
            })

        # 4. Validate email format
        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            return jsonify({
                "success": False, 
                "message": "Please enter a valid email address"
            })

        # 5. Check if user ID already exists
        existing_user = User.query.filter_by(id=user_id).first()
        if existing_user:
            return jsonify({
                "success": False, 
                "message": f"This {role} ID ({user_id}) is already registered. Please use a different ID or login."
            })

        # 6. Check if email already exists
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            return jsonify({
                "success": False, 
                "message": "This email address is already registered. Please use a different email or login."
            })

        try:
            print(f"Creating new user: {user_id}")  # Debug log
            
            # 7. Create new user
            new_user = User(
                id=user_id,
                name=name,
                email=email,
                role=role
            )
            new_user.set_password(password)

            print("Adding user to database...")  # Debug log
            db.session.add(new_user)
            db.session.commit()
            
            print(f"User registered successfully - ID: {user_id}, Role: {role}")
            
            return jsonify({
                "success": True,
                "message": "Registration successful! Please log in."
            })

        except SQLAlchemyError as e:
            db.session.rollback()
            error_msg = str(e)
            print(f"Database error during registration: {error_msg}")
            return jsonify({
                "success": False, 
                "message": f"Database error: {error_msg}"
            })

    except Exception as e:
        error_msg = str(e)
        print(f"Unexpected error during registration: {error_msg}")
        return jsonify({
            "success": False,
            "message": f"Error: {error_msg}"
        })

@app.route("/security")
@app.route("/security/<view>")
@login_required
@role_required(["security"])
def security(view=None):
    if view:
        templates = {
            "pending": "Pending-Request.html",
            "qr": "QR-Management.html",
            "history": "History.html",
            "profile": "Profile.html",
            "about": "About.html",
            "department": "department.html"
        }
        return render_template(templates.get(view, "SecDashboard.html"))
    return render_template("SecDashboard.html")

@app.route("/department")
@app.route("/department/<view>")
@login_required
@role_required(["department"])
def department(view=None):
    if view:
        templates = {
            "pending": "Pending-Request.html",
            "qr": "QR-Management.html",
            "history": "History.html",
            "profile": "Profile.html",
            "about": "About.html"
        }
        return render_template(templates.get(view, "department.html"))
    return render_template("department.html")

@app.route("/visitor")
@app.route("/visitor/<view>")
@login_required
@role_required(["visitor"])
def visitor(view=None):
    if view:
        if view == 'qr':
            # Get visitor's QR code
            visitor_qr = VisitorQR.query.filter_by(visitor_id=session['user_id']).first()
            
            # Get visitor's latest approved visit
            latest_visit = Visit.query.filter_by(
                visitor_id=session['user_id'],
                status='approved'
            ).order_by(Visit.date.desc()).first()
            
            # If there's no QR code but there's an approved visit, generate one
            if not visitor_qr and latest_visit:
                qr_data = {
                    "visitor_id": latest_visit.visitor_id,
                    "visit_id": latest_visit.id,
                    "name": latest_visit.name,
                    "date": latest_visit.date.isoformat(),
                    "location": latest_visit.location,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                qr_code_img = generate_qr_code(str(qr_data))
                visitor_qr = VisitorQR(
                    visitor_id=latest_visit.visitor_id,
                    qr_code=qr_code_img,
                    valid_until=latest_visit.date,
                    is_active=True
                )
                db.session.add(visitor_qr)
                db.session.commit()
            
            return render_template('visitor-qr.html', visitor_qr=visitor_qr)
            
        templates = {
            "form": "visitor-form.html", 
            "history": "History.html",
            "about": "About.html"
        }
        return render_template(templates.get(view, "VisitorDashboard.html"))
    return render_template("VisitorDashboard.html")

@app.route("/visitor/submit_request", methods=["POST"])
@login_required
@role_required(["visitor"])
def submit_visit_request():
    try:
        data = request.form
        visit = Visit(
            id=f"VR{data['id'][-6:]}",  # VR + last 6 digits of visitor ID
            visitor_id=session["user_id"],
            name=data["name"],
            address=data["address"],
            contact_no=data["contactNo"],
            purpose=data["purpose"],
            location=data["location"],
            date=datetime.strptime(data["date"], "%Y-%m-%d").date()
        )
        db.session.add(visit)
        db.session.commit()
        return jsonify({"success": True, "message": "Visit request submitted successfully"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/security/approve_visit", methods=["POST"])
@login_required
@role_required(["security"])
def approve_visit():
    try:
        data = request.form
        visit_id = data.get("visitId")
        
        # Get the visit request
        visit = Visit.query.get(visit_id)
        if not visit:
            return jsonify({"success": False, "message": "Visit request not found"})
        
        # Generate QR code with visitor and visit information
        qr_data = {
            "visitor_id": visit.visitor_id,
            "visit_id": visit.id,
            "name": visit.name,
            "date": visit.date.isoformat(),
            "location": visit.location,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            # Create QR code
            qr_code_img = generate_qr_code(str(qr_data))
            
            # Save QR code to database
            visitor_qr = VisitorQR.query.filter_by(visitor_id=visit.visitor_id).first()
            if visitor_qr:
                visitor_qr.qr_code = qr_code_img
                visitor_qr.valid_until = visit.date
                visitor_qr.is_active = True
            else:
                visitor_qr = VisitorQR(
                    visitor_id=visit.visitor_id,
                    qr_code=qr_code_img,
                    valid_until=visit.date,
                    is_active=True
                )
                db.session.add(visitor_qr)
            
            # Update visit status
            visit.status = "approved"
            db.session.commit()
            
            return jsonify({
                "success": True,
                "message": "Visit request approved and QR code generated successfully"
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "error": f"Error generating QR code: {str(e)}"})
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/check_users")
def check_users():
    try:
        users = User.query.all()
        user_list = []
        for user in users:
            user_list.append({
                'id': user.id,
                'role': user.role,
                'name': user.name,
                'email': user.email
            })
        return jsonify({"success": True, "users": user_list})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
