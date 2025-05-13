from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import timedelta
from functools import wraps

app = Flask(__name__, 
    template_folder="templates",
    static_folder="static")

# Configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "vmas.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.urandom(24).hex()  # Generate a secure random key
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)  # Session timeout

# Enable session
app.permanent_session_lifetime = timedelta(minutes=30)

db = SQLAlchemy(app)

# User Model
class User(db.Model):
    id = db.Column(db.String(7), primary_key=True)  # Format: V123456, D123456, S123456
    password = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # visitor, department, security
    name = db.Column(db.String(100))
    email = db.Column(db.String(120))

# Create database tables
with app.app_context():
    db.create_all()

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
        user_id = data.get("userId")
        password = data.get("password")
        role = data.get("role")

        print(f"Login attempt - ID: {user_id}, Role: {role}")  # Debug log

        if not all([user_id, password, role]):
            return jsonify({"success": False, "message": "All fields are required"})

        user = User.query.filter_by(id=user_id).first()

        if user and user.role == role and check_password_hash(user.password, password):
            # Set up session
            session.permanent = True
            session["user_id"] = user.id
            session["role"] = user.role
            session["name"] = user.name

            # Return appropriate redirect
            if role == "security":
                return jsonify({"success": True, "redirect": "/security"})
            elif role == "department":
                return jsonify({"success": True, "redirect": "/department"})
            elif role == "visitor":
                return jsonify({"success": True, "redirect": "/visitor"})
        
        return jsonify({"success": False, "message": "Invalid credentials"})
    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({"success": False, "message": "An error occurred during login"})

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("mainregister.html")
    
    try:
        data = request.form
        user_id = data.get("userId")
        password = data.get("password")
        role = data.get("role")
        name = data.get("name")
        email = data.get("email")

        # Validate required fields
        if not all([user_id, password, role, name, email]):
            return jsonify({"success": False, "message": "All fields are required"})

        # Check if user ID already exists
        if User.query.filter_by(id=user_id).first():
            return jsonify({
                "success": False, 
                "message": f"This {role} ID ({user_id}) is already registered. Please use a different ID or login."
            })
            
        # Check if email already exists
        if User.query.filter_by(email=email).first():
            return jsonify({
                "success": False, 
                "message": "This email is already registered. Please use a different email or login."
            })

        # Validate ID format
        id_patterns = {
            "visitor": r"^V\d{6}$",
            "department": r"^D\d{6}$",
            "security": r"^S\d{6}$"
        }
        
        if role not in id_patterns:
            return jsonify({"success": False, "message": "Invalid role selected"})
        
        import re
        if not re.match(id_patterns[role], user_id):
            return jsonify({
                "success": False, 
                "message": f"Invalid ID format. Must be {role[0].upper()}123456"
            })

        # Validate email format
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return jsonify({
                "success": False,
                "message": "Invalid email format"
            })

        # Check if user already exists
        if User.query.filter_by(id=user_id).first():
            return jsonify({"success": False, "message": "User ID already exists"})

        if User.query.filter_by(email=email).first():
            return jsonify({"success": False, "message": "Email already registered"})

        # Create new user
        new_user = User(
            id=user_id,
            password=generate_password_hash(password),
            role=role,
            name=name,
            email=email
        )

        db.session.add(new_user)
        db.session.commit()
        return jsonify({
            "success": True,
            "message": "Registration successful! Please login."
        })

    except Exception as e:
        db.session.rollback()
        print(f"Registration error: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Registration failed. Please try again."
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
        templates = {
            "history": "History.html",
            "profile": "Profile.html",
            "about": "About.html"
        }
        return render_template(templates.get(view, "Profile.html"))
    return render_template("Profile.html")

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
