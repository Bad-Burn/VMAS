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
from models.db import db
from models.visitor import Visitor
from models.visitor_registration import VisitorRegistration
from db_config import init_db, get_db_connection
import json

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

# Initialize database
from db_config import init_db
init_db(app, env)

# Import models
from models.visitor import Visitor
from models.visitor_registration import VisitorRegistration
from models.department import Department
from models.security_guard import SecurityGuard
from models.department_staff import DepartmentStaff
from models.system_log import SystemLog

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

        # Connect to database
        conn = get_db_connection()
        if not conn:
            return jsonify({"success": False, "message": "Database connection error"})

        cursor = conn.cursor(dictionary=True)
        
        # Find user based on role
        if role == 'visitor':
            cursor.execute("""
                SELECT visitor_id as id, 'visitor' as role, visitor_name as name, 
                       password_hash, email 
                FROM visitors 
                WHERE visitor_id = %s
            """, (user_id,))
        elif role == 'department':
            # Allow any department staff to log in and select department
            cursor.execute("""
                SELECT staff_id as id, 'department' as role, staff_name as name,
                       password_hash, email, department_id
                FROM department_staff 
                WHERE staff_id = %s OR email = %s
            """, (user_id, user_id))
        elif role == 'security':
            cursor.execute("""
                SELECT security_id as id, 'security' as role, username as name, 
                       password_hash, email 
                FROM security_guards 
                WHERE security_id = %s
            """, (user_id,))
        
        user = cursor.fetchone()
        print(f"Found user: {user}")  # Debug log

        if not user:
            cursor.close()
            conn.close()
            return jsonify({"success": False, "message": "User not found"})

        # Verify password
        if not check_password_hash(user['password_hash'], password):
            cursor.close()
            conn.close()
            return jsonify({"success": False, "message": "Invalid password"})            # For department staff, optionally store department info
        if role == 'department':
            department_id = data.get('departmentLocation')
            
            if department_id:
                # Get department information if a department was selected
                cursor.execute("""
                    SELECT department_id, department_name, email 
                    FROM departments
                    WHERE department_id = %s
                """, (department_id,))
                department = cursor.fetchone()

                if department:
                    # Update staff's department_id
                    cursor.execute("""
                        UPDATE department_staff 
                        SET department_id = %s
                        WHERE staff_id = %s
                    """, (department_id, user['id']))
                    conn.commit()

                    # Store department info in session
                    session["department_id"] = department['department_id']
                    session["department_name"] = department['department_name']
            else:
                # If no department selected, just set default session values
                session["department_id"] = None
                session["department_name"] = "No Department Selected"

        # Set up session
        session.permanent = True
        session["user_id"] = user['id']
        session["role"] = role
        session["name"] = user.get('name', '')

        # Return success
        cursor.close()
        conn.close()
        return jsonify({
            "success": True,
            "redirect": f"/{role}"
        })
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

        conn = get_db_connection()
        if not conn:
            return jsonify({"success": False, "message": "Database connection error"})

        cursor = conn.cursor(dictionary=True)
        
        # 5. Check if user ID exists in the appropriate table
        id_exists = False
        if role == 'visitor':
            cursor.execute("SELECT visitor_id FROM visitors WHERE visitor_id = %s", (user_id,))
            id_exists = cursor.fetchone() is not None
        elif role == 'department':
            cursor.execute("SELECT staff_id FROM department_staff WHERE staff_id = %s", (user_id,))
            id_exists = cursor.fetchone() is not None
        elif role == 'security':
            cursor.execute("SELECT security_id FROM security_guards WHERE security_id = %s", (user_id,))
            id_exists = cursor.fetchone() is not None

        if id_exists:
            cursor.close()
            conn.close()
            return jsonify({
                "success": False, 
                "message": f"This {role} ID ({user_id}) is already registered"
            })

        # 6. Check if email exists in the appropriate table
        email_exists = False
        if role == 'visitor':
            cursor.execute("SELECT email FROM visitors WHERE email = %s", (email,))
            email_exists = cursor.fetchone() is not None
        elif role == 'department':
            cursor.execute("SELECT email FROM department_staff WHERE email = %s", (email,))
            email_exists = cursor.fetchone() is not None
        elif role == 'security':
            cursor.execute("SELECT email FROM security_guards WHERE email = %s", (email,))
            email_exists = cursor.fetchone() is not None

        if email_exists:
            cursor.close()
            conn.close()
            return jsonify({
                "success": False, 
                "message": "This email address is already registered"
            })

        try:
            print(f"Creating new user: {user_id}")  # Debug log
            
            # 7. Create new user in the appropriate table
            hashed_password = generate_password_hash(password)
            
            if role == 'visitor':
                cursor.execute("""
                    INSERT INTO visitors (visitor_id, visitor_name, email, password_hash)
                    VALUES (%s, %s, %s, %s)
                """, (user_id, name, email, hashed_password))
            elif role == 'department':
                cursor.execute("""
                    INSERT INTO department_staff (staff_id, staff_name, email, password_hash)
                    VALUES (%s, %s, %s, %s)
                """, (user_id, name, email, hashed_password))
            elif role == 'security':
                cursor.execute("""
                    INSERT INTO security_guards (security_id, username, email, password_hash)
                    VALUES (%s, %s, %s, %s)
                """, (user_id, name, email, hashed_password))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            print(f"User registered successfully - ID: {user_id}, Role: {role}")
            return jsonify({
                "success": True,
                "message": "Registration successful! Please log in."
            })

        except Exception as e:
            conn.rollback()
            cursor.close()
            conn.close()
            error_msg = str(e)
            print(f"Database error during registration: {error_msg}")
            return jsonify({
                "success": False, 
                "message": f"Database error: {error_msg}"
            })

    except Exception as e:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
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
    # Define template mapping
    templates = {
        "pending": "Pending-Request.html",
        "qr": "QR-Management.html",
        "history": "security-history.html",
        "profile": "Profile.html",
        "about": "security-about.html",
        "department": "department.html"
    }

    # Handle QR Management view
    if view == 'qr':
        conn = get_db_connection()
        if not conn:
            return "Database connection error", 500

        cursor = conn.cursor(dictionary=True)
        try:
            # Get approved visitors
            cursor.execute("""
                SELECT DISTINCT 
                    v.visitor_id,
                    v.visitor_name,
                    vr.visit_date
                FROM visitors v
                JOIN visitor_registrations vr ON v.visitor_id = vr.visitor_id
                WHERE vr.status = 'approved'
                AND vr.visit_date >= CURDATE()
                ORDER BY vr.visit_date ASC
            """)
            approved_visitors = cursor.fetchall()

            # Get active QR codes
            cursor.execute("""
                SELECT 
                    vq.*,
                    v.visitor_name
                FROM visitor_qr vq
                JOIN visitors v ON v.visitor_id = vq.visitor_id
                WHERE vq.is_active = TRUE
                ORDER BY vq.created_at DESC
            """)
            qr_codes = cursor.fetchall()

            cursor.close()
            conn.close()

            return render_template('QR-Management.html', 
                                approved_visitors=approved_visitors,
                                qr_codes=qr_codes)
        except Exception as e:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
            print(f"Error getting QR data: {str(e)}")
            return "Error loading QR management", 500

    # Handle profile view
    if view == "profile":
        conn = get_db_connection()
        if not conn:
            return "Database connection error", 500
            
        cursor = conn.cursor(dictionary=True)
        try:
            # Get security guard details
            cursor.execute("""
                SELECT security_id, username, email
                FROM security_guards 
                WHERE security_id = %s
            """, (session['user_id'],))
            
            security_guard = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if not security_guard:
                return "Security guard not found", 404
                
            return render_template("Profile.html", user=security_guard)
            
        except Exception as e:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
            print(f"Error getting security guard profile: {str(e)}")
            return "Error loading profile", 500

    # For other views, use the templates dictionary
    if view in templates:
        return render_template(templates[view])
    
    # Default route - show security dashboard
    conn = get_db_connection()
    if not conn:
        return "Database connection error", 500

    cursor = conn.cursor(dictionary=True)
    try:
        # Get statistics
        cursor.execute("SELECT COUNT(*) as count FROM visitor_registrations WHERE status != 'rejected'")
        total_visits = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM visitor_registrations WHERE status = 'pending'")
        pending_count = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM visitor_registrations WHERE status = 'approved' AND DATE(created_at) = CURDATE()")
        approved_today = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM visitor_registrations WHERE status = 'active'")
        active_visits = cursor.fetchone()['count']

        # Get recent approved requests
        cursor.execute("""
            SELECT 
                vr.registration_id as id,
                v.visitor_id,
                v.visitor_name as name,
                vr.purpose,
                vr.visit_date,
                d.department_name as location,
                vr.time_approved,
                vr.created_at as approved_at
            FROM visitor_registrations vr
            JOIN visitors v ON vr.visitor_id = v.visitor_id
            JOIN departments d ON vr.department_id = d.department_id
            WHERE vr.status = 'approved'
            ORDER BY vr.created_at DESC
            LIMIT 10
        """)
        approved_requests = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template("SecDashboard.html", 
                            total_visits=total_visits, 
                            pending_count=pending_count,
                            approved_today=approved_today,
                            active_visits=active_visits,
                            approved_requests=approved_requests)

    except Exception as e:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
        print(f"Error loading dashboard: {str(e)}")
        return render_template("SecDashboard.html", error="Failed to load dashboard data")

# Department routes
@app.route("/department")
@app.route("/department/<view>")
@login_required
@role_required(["department"])
def department(view=None):
    conn = get_db_connection()
    if not conn:
        return "Database connection error", 500

    cursor = conn.cursor(dictionary=True)

    try:
        if view == 'profile':
            print(f"Loading profile for staff {session.get('user_id')} in department {session.get('department_id')}")
            
            # Get staff info first
            cursor.execute("""
                SELECT staff_id, staff_name, email, department_id
                FROM department_staff 
                WHERE staff_id = %s
            """, (session.get('user_id'),))
            
            staff_result = cursor.fetchone()
            if not staff_result:
                cursor.close()
                conn.close()
                return "Department staff not found", 404

            # Get department info
            department_id = staff_result['department_id'] or session.get('department_id')
            if department_id:
                cursor.execute("""
                    SELECT department_id, department_name, email as dept_email
                    FROM departments 
                    WHERE department_id = %s
                """, (department_id,))
                dept_result = cursor.fetchone()
            else:
                dept_result = {
                    'department_id': None,
                    'department_name': 'No Department Selected',
                    'dept_email': None
                }

            # Get visit statistics if department is selected
            if department_id:
                cursor.execute("""
                    SELECT 
                        COUNT(registration_id) as total_visits,
                        SUM(CASE 
                            WHEN visit_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
                            THEN 1 
                            ELSE 0 
                        END) as monthly_visits,
                        ROUND(COUNT(registration_id) / 30.0, 1) as avg_daily_visits
                    FROM visitor_registrations
                    WHERE department_id = %s AND status != 'rejected'
                """, (department_id,))
                stats_result = cursor.fetchone()
            else:
                stats_result = {
                    'total_visits': 0,
                    'monthly_visits': 0,
                    'avg_daily_visits': 0
                }

            cursor.close()
            conn.close()

            # Structure the data
            staff = {
                'staff_id': staff_result['staff_id'],
                'staff_name': staff_result['staff_name'],
                'email': staff_result['email']
            }

            department_info = {
                'department_id': department_id,
                'department_name': dept_result['department_name'] if department_id else 'No Department Selected',
                'email': dept_result.get('dept_email')
            }

            stats_data = {
                'total_visits': stats_result['total_visits'] or 0,
                'monthly_visits': stats_result['monthly_visits'] or 0,
                'avg_daily_visits': stats_result['avg_daily_visits'] or 0
            }

            return render_template('department-profile.html', 
                                staff=staff,
                                department=department_info,
                                **stats_data)
                                
        # Rest of the department route code
        # Get visitor statistics for the dashboard
        cursor.execute("""
            SELECT 
                COUNT(*) as total_visits,
                COUNT(IF(status = 'pending', 1, NULL)) as pending_visits,
                COUNT(IF(status = 'approved' AND DATE(created_at) = CURDATE(), 1, NULL)) as today_approved,
                COUNT(IF(status = 'rejected' AND DATE(created_at) = CURDATE(), 1, NULL)) as today_rejected,
                COUNT(IF(visit_date BETWEEN DATE_SUB(CURDATE(), INTERVAL 7 DAY) AND CURDATE(), 1, NULL)) as weekly_visits,
                COUNT(IF(visit_date BETWEEN DATE_SUB(CURDATE(), INTERVAL 30 DAY) AND CURDATE(), 1, NULL)) as monthly_visits,
                ROUND((COUNT(IF(status = 'approved', 1, NULL)) / COUNT(*)) * 100, 1) as approval_rate,
                ROUND(AVG(TIMESTAMPDIFF(HOUR, created_at, time_in)), 1) as avg_response_time
            FROM visitor_registrations 
            WHERE department_id = %s
        """, (session.get('department_id'),))
        stats = cursor.fetchone()

        if not stats:
            stats = {
                'total_visits': 0,
                'pending_visits': 0,
                'today_approved': 0,
                'today_rejected': 0,
                'weekly_visits': 0,
                'monthly_visits': 0,
                'approval_rate': 0,
                'avg_response_time': 0
            }

        # Handle other views
        if view:
            templates = {
                "scanner": "department-scanner.html",  # QR Scanner page
                "history": "department-history.html",  # Visit history page
                "profile": "department-profile.html",  # Department profile
                "about": "department-about.html"       # About page
            }
            return render_template(templates.get(view, "DeptDashboard.html"))

        cursor.close()
        conn.close()
        return render_template("DeptDashboard.html",
                           total_visits=stats['total_visits'],
                           pending_requests=stats['pending_visits'],
                           approved_visits=stats['today_approved'],
                           rejected_visits=stats['today_rejected'],
                           weekly_visits=stats['weekly_visits'],
                           monthly_visits=stats['monthly_visits'],
                           approval_rate=stats['approval_rate'],
                           avg_response_time=stats.get('avg_response_time', 0))
                           
    except Exception as e:
        print(f"Error in department route: {str(e)}")
        return f"Error fetching department data: {str(e)}", 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route("/visitor")
@app.route("/visitor/<view>")
@login_required
@role_required(["visitor"])
def visitor(view=None):
    if view:
        # Handle QR code view
        if view == 'qr':
            conn = get_db_connection()
            if not conn:
                return "Database connection error", 500

            cursor = conn.cursor(dictionary=True)
            try:
                # Get visitor's active QR code and registration info
                cursor.execute("""
                    SELECT 
                        v.visitor_name,
                        v.visitor_id,
                        vr.visit_date,
                        vr.status,
                        vq.qr_code,
                        vq.is_active,
                        vq.valid_until
                    FROM visitors v
                    LEFT JOIN visitor_registrations vr ON v.visitor_id = vr.visitor_id
                    LEFT JOIN visitor_qr vq ON v.visitor_id = vq.visitor_id
                    WHERE v.visitor_id = %s
                    AND vr.status = 'approved'
                    ORDER BY vr.visit_date DESC
                    LIMIT 1
                """, (session['user_id'],))
                visitor_info = cursor.fetchone()
                
                cursor.close()
                conn.close()
                
                return render_template('visitor-qr.html', visitor_qr=visitor_info)
            
            except Exception as e:
                print(f"Error in visitor QR route: {str(e)}")
                if 'cursor' in locals():
                    cursor.close()
                if 'conn' in locals():
                    conn.close()
                return "Error processing QR code", 500        # Handle profile view
        elif view == 'profile':
            conn = get_db_connection()
            if not conn:
                return "Database connection error", 500

            cursor = conn.cursor(dictionary=True)
            try:
                # Get visitor's profile information with visit statistics
                cursor.execute("""
                    WITH visit_stats AS (
                        SELECT 
                            COUNT(*) as total_visits,
                            COUNT(IF(status = 'completed', 1, NULL)) as completed_visits,
                            COUNT(IF(DATE(visit_date) >= DATE_SUB(CURDATE(), INTERVAL 30 DAY), 1, NULL)) as recent_visits
                        FROM visitor_registrations
                        WHERE visitor_id = %s
                    )
                    SELECT 
                        v.visitor_id as id,
                        v.visitor_name as name,
                        v.email,
                        v.address,
                        v.contact_no,
                        v.qr_code_path as photo_url,
                        vs.total_visits,
                        vs.completed_visits,
                        vs.recent_visits,
                        v.created_at as member_since
                    FROM visitors v
                    CROSS JOIN visit_stats vs
                    WHERE v.visitor_id = %s
                """, (session['user_id'], session['user_id']))
                
                visitor_info = cursor.fetchone()
                cursor.close()
                conn.close()
                
                if not visitor_info:
                    return "Visitor not found", 404

                return render_template('visitor-profile.html', user=visitor_info)

            except Exception as e:
                print(f"Error loading visitor profile: {str(e)}")
                if 'cursor' in locals():
                    cursor.close()
                if 'conn' in locals():
                    conn.close()
                return "Error loading profile", 500

        # Handle other views
        else:
            templates = {
                "form": "visitor-form.html",
                "history": "visitor-history.html",
                "about": "visitor-about.html",
                "profile": "visitor-profile.html"
            }
            return render_template(templates.get(view, "VisitorDashboard.html"))

    # Default route - show dashboard
    return render_template("VisitorDashboard.html")

@app.route("/visitor/submit_request", methods=["POST"])
@login_required
@role_required(["visitor"])
def submit_visit_request():
    try:
        data = request.form
        conn = get_db_connection()
        if not conn:
            return jsonify({"success": False, "message": "Database connection error"})

        cursor = conn.cursor(dictionary=True)
        
        try:
            # First get the department ID from the department name
            cursor.execute("""
                SELECT department_id FROM departments 
                WHERE department_name = %s OR department_name LIKE %s
            """, (data["location"], f"%{data['location']}%"))
            department = cursor.fetchone()
            
            if not department:
                # If department doesn't exist, create it with a new ID
                cursor.execute("SELECT MAX(CAST(SUBSTRING(department_id, 2) AS UNSIGNED)) FROM departments")
                max_id = cursor.fetchone()['MAX(CAST(SUBSTRING(department_id, 2) AS UNSIGNED))'] or 0
                new_dept_id = f"D{str(max_id + 1).zfill(6)}"
                
                cursor.execute("""
                    INSERT INTO departments (department_id, department_name)
                    VALUES (%s, %s)
                """, (new_dept_id, data["location"]))
                department = {'department_id': new_dept_id}

            # Now insert the visitor registration
            cursor.execute("""
                INSERT INTO visitor_registrations 
                (visitor_id, purpose, visit_date, status, department_id, created_at)
                VALUES (%s, %s, %s, %s, %s, NOW())
            """, (
                session["user_id"],
                data["purpose"],
                datetime.strptime(data["date"], "%Y-%m-%d").date(),
                'pending',
                department["department_id"]
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return jsonify({"success": True, "message": "Visit request submitted successfully"})
            
        except Exception as e:
            conn.rollback()
            cursor.close()
            conn.close()
            return jsonify({"success": False, "error": f"Database error: {str(e)}"})
            
    except Exception as e:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
        return jsonify({"success": False, "error": str(e)})

@app.route("/security/approve_visit", methods=["POST"])
@login_required
@role_required(["security"])
def approve_visit():
    try:
        data = request.form
        visit_id = data.get("visitId")
        
        conn = get_db_connection()
        if not conn:
            return jsonify({"success": False, "message": "Database connection error"})

        cursor = conn.cursor(dictionary=True)
        
        # Get the visit request and visitor details
        cursor.execute("""
            SELECT v.*, vr.* 
            FROM visits v
            JOIN visitor_registrations vr ON v.visitor_id = vr.visitor_id
            WHERE v.id = %s
        """, (visit_id,))
        visit = cursor.fetchone()
        
        if not visit:
            cursor.close()
            conn.close()
            return jsonify({"success": False, "message": "Visit request not found"})
        
        # Generate QR code with visitor and visit information
        qr_data = {
            "visitor_id": visit['visitor_id'],
            "visit_id": visit['id'],
            "name": visit['name'],
            "date": visit['visit_date'].isoformat(),
            "location": visit['department_id'],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            # Generate QR code image
            qr_code_img = generate_qr_code(json.dumps(qr_data))
            
            # Check if visitor already has a QR code
            cursor.execute("""
                SELECT * FROM visitor_qr 
                WHERE visitor_id = %s
            """, (visit['visitor_id'],))
            existing_qr = cursor.fetchone()
            
            if existing_qr:
                # Update existing QR code
                cursor.execute("""
                    UPDATE visitor_qr 
                    SET qr_code = %s, valid_until = %s, is_active = TRUE
                    WHERE visitor_id = %s
                """, (qr_code_img, visit['visit_date'], visit['visitor_id']))
            else:
                # Create new QR code entry
                cursor.execute("""
                    INSERT INTO visitor_qr 
                    (visitor_id, qr_code, valid_until, is_active)
                    VALUES (%s, %s, %s, %s)
                """, (visit['visitor_id'], qr_code_img, visit['visit_date'], True))
            
            # Update visit status to approved
            cursor.execute("""
                UPDATE visits 
                SET status = 'approved',
                approved_by_security_id = %s,
                approval_date = %s
                WHERE id = %s
            """, (session['user_id'], datetime.utcnow(), visit_id))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return jsonify({
                "success": True,
                "message": "Visit request approved and QR code generated successfully"
            })
            
        except Exception as e:
            conn.rollback()
            cursor.close()
            conn.close()
            return jsonify({"success": False, "error": f"Error generating QR code: {str(e)}"})
            
    except Exception as e:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
        return jsonify({"success": False, "error": str(e)})

@app.route("/security/reject_request", methods=["POST"])
@login_required
@role_required(["security"])
def reject_request():
    try:
        data = request.get_json()
        request_id = data.get('requestId')
        
        if not request_id:
            return jsonify({"success": False, "error": "Request ID is required"})

        conn = get_db_connection()
        if not conn:
            return jsonify({"success": False, "error": "Database connection error"})

        cursor = conn.cursor(dictionary=True)
        try:
            # Update the request status to rejected
            cursor.execute("""
                UPDATE visitor_registrations 
                SET status = 'rejected'
                WHERE registration_id = %s
            """, (request_id,))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return jsonify({"success": True, "message": "Request rejected successfully"})
            
        except Exception as e:
            conn.rollback()
            cursor.close()
            conn.close()
            return jsonify({"success": False, "error": f"Database error: {str(e)}"})
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/security/approve_request", methods=["POST"])
@login_required
@role_required(["security"])
def approve_request():
    try:
        data = request.get_json()
        request_id = data.get('requestId')
        
        if not request_id:
            return jsonify({"success": False, "error": "Request ID is required"})

        conn = get_db_connection()
        if not conn:
            return jsonify({"success": False, "error": "Database connection error"})

        cursor = conn.cursor(dictionary=True)
        try:
            # Update the request status to approved
            cursor.execute("""
                UPDATE visitor_registrations 
                SET status = 'approved',
                    approved_by_security_id = %s,
                    time_approved = NOW()
                WHERE registration_id = %s
            """, (session['user_id'], request_id))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return jsonify({"success": True, "message": "Request approved successfully"})
            
        except Exception as e:
            conn.rollback()
            cursor.close()
            conn.close()
            return jsonify({"success": False, "error": f"Database error: {str(e)}"})
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/department/verify_visitor", methods=["POST"])
@login_required
@role_required(["department"])
def verify_visitor():
    try:
        data = request.get_json()
        visitor_id = data.get('visitor_id')
        visit_id = data.get('visit_id')

        if not visitor_id:
            return jsonify({
                "success": False,
                "message": "Missing visitor ID"
            })

        conn = get_db_connection()
        if not conn:
            return jsonify({
                "success": False,
                "message": "Database connection error"
            })

        cursor = conn.cursor(dictionary=True)

        # Check if visitor has an approved visit for today
        cursor.execute("""
            SELECT 
                vr.*,
                v.visitor_name,
                v.email,
                v.contact_no,
                v.address,
                d.department_name
            FROM visitor_registrations vr
            JOIN visitors v ON vr.visitor_id = v.visitor_id
            JOIN departments d ON vr.department_id = d.department_id
            WHERE vr.visitor_id = %s 
            AND vr.department_id = %s
            AND vr.status IN ('approved', 'active')
            AND vr.visit_date = CURDATE()
            AND (vr.time_out IS NULL)
        """, (visitor_id, session['user_id']))

        visit = cursor.fetchone()

        if not visit:
            cursor.close()
            conn.close()
            return jsonify({
                "success": False,
                "status": "Invalid",
                "message": "No valid visit found for this visitor today"
            })

        current_time = datetime.now()
        current_time_str = current_time.strftime('%I:%M %p')

        # Check if visitor is checking in or out
        if visit['time_in'] is None:
            # Check in
            cursor.execute("""
                UPDATE visitor_registrations 
                SET status = 'active',
                    time_in = %s
                WHERE registration_id = %s
            """, (current_time, visit['registration_id']))

            action = "checked in"
        else:
            # Check out
            cursor.execute("""
                UPDATE visitor_registrations 
                SET status = 'completed',
                    time_out = %s
                WHERE registration_id = %s
            """, (current_time, visit['registration_id']))

            action = "checked out"

        # Log the action
        cursor.execute("""
            INSERT INTO system_logs 
            (staff_id, action, related_department_id, ip_address, timestamp)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            session['user_id'],
            f"Visitor {visitor_id} {action} at {current_time_str}",
            session['user_id'],
            request.remote_addr,
            current_time
        ))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            "success": True,
            "status": "Valid",
            "message": f"Visitor successfully {action}",
            "visitor": {
                "id": visitor_id,
                "name": visit['visitor_name'],
                "email": visit['email'],
                "phone": visit['contact_no'],
                "address": visit['address'],
                "purpose": visit['purpose'],
                "department": visit['department_name'],
                "visitDate": visit['visit_date'].strftime('%B %d, %Y'),
                "action": action,
                "time": current_time_str
            }
        })

    except Exception as e:
        print(f"Error verifying visitor: {str(e)}")
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
        return jsonify({
            "success": False,
            "message": f"Error verifying visitor: {str(e)}"
        })

    except Exception as e:
        print(f"Error verifying QR code: {str(e)}")
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
        return jsonify({
            "success": False,
            "message": f"Error verifying QR code: {str(e)}"
        })

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/check_users")
def check_users():
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"success": False, "message": "Database connection error"})

        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT id, role, name, email FROM users")
        users = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({"success": True, "users": users})
        
    except Exception as e:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
        return jsonify({"success": False, "error": str(e)})

# Route for security visit history page
@app.route("/security/history")
@login_required
@role_required(["security"])
def security_history():
    return render_template("security-history.html")

# API route to get visit history data
@app.route("/security/get_history")
@login_required
@role_required(["security"])
def get_security_history():
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({
                "success": False,
                "message": "Database connection error"
            })

        cursor = conn.cursor(dictionary=True)

        # Get all visit records with visitor and department information
        cursor.execute("""
            SELECT 
                vr.registration_id as id,
                v.visitor_id,
                v.visitor_name as name,
                v.qr_code_path as visitor_photo,
                vr.purpose,
                d.department_name as location,
                vr.visit_date as date,
                vr.time_in,
                vr.time_out,
                vr.status
            FROM visitor_registrations vr
            JOIN visitors v ON v.visitor_id = vr.visitor_id
            JOIN departments d ON d.department_id = vr.department_id
            ORDER BY vr.visit_date DESC, vr.created_at DESC
        """)
        
        visits = cursor.fetchall()

        # Convert dates and times to string format
        for visit in visits:
            visit['date'] = visit['date'].strftime('%Y-%m-%d') if visit['date'] else None
            visit['time_in'] = visit['time_in'].strftime('%H:%M:%S') if visit['time_in'] else None
            visit['time_out'] = visit['time_out'].strftime('%H:%M:%S') if visit['time_out'] else None

        cursor.close()
        conn.close()

        return jsonify({
            "success": True,
            "visits": visits
        })

    except Exception as e:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
        print(f"Error getting visit history: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Error retrieving visit history: {str(e)}"
        })

@app.route("/security/generate_qr", methods=["POST"])
@login_required
@role_required(["security"])
def generate_qr():
    try:
        data = request.get_json()
        visitor_id = data.get('visitor_id')
        
        if not visitor_id:
            return jsonify({"success": False, "message": "Visitor ID is required"})

        conn = get_db_connection()
        if not conn:
            return jsonify({"success": False, "message": "Database connection error"})

        cursor = conn.cursor(dictionary=True)
        
        # Verify visitor is approved
        cursor.execute("""
            SELECT 
                v.*,
                vr.visit_date,
                vr.purpose,
                d.department_id,
                d.department_name
            FROM visitors v
            JOIN visitor_registrations vr ON v.visitor_id = vr.visitor_id
            JOIN departments d ON vr.department_id = d.department_id
            WHERE v.visitor_id = %s AND vr.status = 'approved'
            ORDER BY vr.visit_date DESC LIMIT 1
        """, (visitor_id,))
        
        visitor = cursor.fetchone()
        if not visitor:
            cursor.close()
            conn.close()
            return jsonify({"success": False, "message": "No approved visit found for this visitor"})

        # Generate QR code data
        qr_data = {
            "visitor_id": visitor_id,
            "name": visitor["visitor_name"],
            "email": visitor["email"],
            "phone": visitor["contact_no"],
            "address": visitor["address"],
            "purpose": visitor["purpose"],
            "visitDate": visitor["visit_date"].strftime('%B %d, %Y'),
            "department": visitor["department_name"],
            "timestamp": datetime.utcnow().isoformat()
        }

        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(json.dumps(qr_data))
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_str = base64.b64encode(img_buffer.getvalue()).decode()

        # Check if visitor already has a QR code
        cursor.execute("""
            SELECT * FROM visitor_qr 
            WHERE visitor_id = %s
        """, (visitor_id,))
        existing_qr = cursor.fetchone()

        if existing_qr:
            # Update existing QR code
            cursor.execute("""
                UPDATE visitor_qr 
                SET qr_code = %s,
                    valid_until = %s,
                    is_active = TRUE,
                    updated_at = NOW()
                WHERE visitor_id = %s
            """, (img_str, visitor["visit_date"], visitor_id))
        else:
            # Create new QR code entry
            cursor.execute("""
                INSERT INTO visitor_qr 
                (visitor_id, qr_code, valid_until, is_active)
                VALUES (%s, %s, %s, TRUE)
            """, (visitor_id, img_str, visitor["visit_date"]))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            "success": True,
            "message": "QR code generated successfully"
        })

    except Exception as e:
        print(f"Error generating QR code: {str(e)}")
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
        return jsonify({
            "success": False,
            "message": f"Error generating QR code: {str(e)}"
        })

@app.route("/security/get_pending_requests")
@login_required
@role_required(["security"])
def get_pending_requests():
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({
                "success": False,
                "message": "Database connection error"
            })

        cursor = conn.cursor(dictionary=True)

        # Get all pending requests with visitor and department information
        cursor.execute("""
            SELECT 
                vr.registration_id as id,
                v.visitor_id,
                v.visitor_name as name,
                vr.purpose,
                d.department_name as location,
                vr.visit_date as date,
                UPPER(vr.status) as status,
                v.address,
                v.contact_no as contactNo
            FROM visitor_registrations vr
            JOIN visitors v ON v.visitor_id = vr.visitor_id
            LEFT JOIN departments d ON d.department_id = vr.department_id
            WHERE LOWER(vr.status) = 'pending'
            ORDER BY vr.created_at DESC
        """)
        
        pending_requests = cursor.fetchall()

        # Convert dates to string format for JSON serialization
        for request in pending_requests:
            request['date'] = request['date'].strftime('%Y-%m-%d') if request['date'] else None

        cursor.close()
        conn.close()

        return jsonify({
            "success": True,
            "requests": pending_requests
        })

    except Exception as e:
        print(f"Error getting pending requests: {str(e)}")
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
        return jsonify({
            "success": False,
            "message": f"Error getting pending requests: {str(e)}"
        })

@app.route("/get_departments")
def get_departments():
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"success": False, "message": "Database connection error"})

        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT department_id, department_name 
            FROM departments 
            ORDER BY department_name
        """)
        
        departments = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({"success": True, "departments": departments})
    except Exception as e:
        print(f"Error fetching departments: {str(e)}")
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
        return jsonify({"success": False, "message": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
