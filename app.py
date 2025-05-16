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
from db_config import get_db_connection

# Initialize Flask app
app = Flask(__name__, template_folder="templates", static_folder="static")

# Configuration
app.config.update(
    SECRET_KEY = "your-secret-key-goes-here",
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30),
    SESSION_TYPE = 'filesystem'
)

# Initialize extensions
Session(app)



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
        
        # Find user
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        print(f"Found user: {user}")  # Debug log

        if not user:
            cursor.close()
            conn.close()
            return jsonify({"success": False, "message": "User not found"})

        if user['role'] != role:
            cursor.close()
            conn.close()
            return jsonify({"success": False, "message": "Invalid role for this user"})

        if not check_password_hash(user['password'], password):
            cursor.close()
            conn.close()
            return jsonify({"success": False, "message": "Invalid password"})

        # User authenticated successfully, set up session
        cursor.close()
        conn.close()
        
        session.permanent = True
        session["user_id"] = user['id']
        session["role"] = user['role']
        session["name"] = user['name']

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

        conn = get_db_connection()
        if not conn:
            return jsonify({"success": False, "message": "Database connection error"})

        cursor = conn.cursor(dictionary=True)
        
        # 5. Check if user ID exists
        cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({
                "success": False, 
                "message": f"This {role} ID ({user_id}) is already registered"
            })

        # 6. Check if email exists
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({
                "success": False, 
                "message": "This email address is already registered"
            })

        try:
            print(f"Creating new user: {user_id}")  # Debug log
            
            # 7. Create new user
            hashed_password = generate_password_hash(password)
            cursor.execute("""
                INSERT INTO users (id, name, email, password, role)
                VALUES (%s, %s, %s, %s, %s)
            """, (user_id, name, email, hashed_password, role))
            
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

    # Handle history view
    if view == 'history':
        return render_template('security-history.html')

    # Handle about view separately for statistics
    if view == 'about':
        conn = get_db_connection()
        if not conn:
            return "Database connection error", 500

        cursor = conn.cursor(dictionary=True)
        try:
            # Get statistics
            cursor.execute("SELECT COUNT(*) as count FROM users WHERE role = 'visitor'")
            total_visitors = cursor.fetchone()['count']

            cursor.execute("SELECT COUNT(*) as count FROM visitor_registrations WHERE status = 'pending'")
            pending_requests = cursor.fetchone()['count']

            today = datetime.now().date()
            cursor.execute("""
                SELECT COUNT(*) as count FROM visitor_registrations 
                WHERE status = 'approved' 
                AND DATE(visit_date) = %s
            """, (today,))
            approved_visits = cursor.fetchone()['count']

            cursor.execute("""
                SELECT COUNT(*) as count FROM visitor_registrations 
                WHERE status = 'active'
                AND time_in IS NOT NULL 
                AND time_out IS NULL
            """)
            active_visits = cursor.fetchone()['count']

            return render_template('security-about.html',
                                total_visitors=total_visitors,
                                pending_requests=pending_requests,
                                approved_visits=approved_visits,
                                active_visits=active_visits)

        except Exception as e:
            print(f"Error getting statistics: {str(e)}")
            return "Error loading statistics", 500

        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    # Handle all other views
    if view and view in templates:
        return render_template(templates[view])

    # Default view (dashboard)
    return render_template("SecDashboard.html")    # Handle history view first
    if view == 'history':
        return render_template('security-history.html')
    
    # Handle about view with statistics
    elif view == 'about':
        conn = get_db_connection()
        if not conn:
            return "Database connection error", 500

        cursor = conn.cursor(dictionary=True)
        try:
            # Get statistics
            cursor.execute("SELECT COUNT(*) as count FROM users WHERE role = 'visitor'")
            total_visitors = cursor.fetchone()['count']

            cursor.execute("SELECT COUNT(*) as count FROM visitor_registrations WHERE status = 'pending'")
            pending_requests = cursor.fetchone()['count']

            today = datetime.now().date()
            cursor.execute("""
                SELECT COUNT(*) as count FROM visitor_registrations 
                WHERE status = 'approved' 
                AND DATE(visit_date) = %s
            """, (today,))
            approved_visits = cursor.fetchone()['count']

            cursor.execute("""
                SELECT COUNT(*) as count FROM visitor_registrations 
                WHERE status = 'active'
                AND time_in IS NOT NULL 
                AND time_out IS NULL
            """)
            active_visits = cursor.fetchone()['count']

            return render_template('security-about.html',
                                total_visitors=total_visitors,
                                pending_requests=pending_requests,
                                approved_visits=approved_visits,
                                active_visits=active_visits)

        except Exception as e:
            print(f"Error getting statistics: {str(e)}")
            return "Error loading statistics", 500

        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    # Handle other views using template mapping
    elif view in templates:
        return render_template(templates[view])

    # Default to dashboard view
    return render_template("SecDashboard.html")

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
        """, (session.get('user_id'),))
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

        # Get recent visits for the dashboard
        cursor.execute("""
            SELECT 
                vr.registration_id,
                v.visitor_name as name,
                vr.purpose,
                vr.visit_date,
                vr.status,
                vr.created_at
            FROM visitor_registrations vr
            JOIN visitors v ON v.visitor_id = vr.visitor_id
            WHERE vr.department_id = %s
            ORDER BY vr.created_at DESC
            LIMIT 10
        """, (session.get('user_id'),))
        recent_visits = cursor.fetchall() or []

        if view:
            templates = {
                "scanner": "department-scanner.html",  # QR Scanner page
                "history": "department-history.html",  # Visit history page
                "profile": "department-profile.html",  # Department profile
                "about": "department-about.html"       # About page
            }
            
            if view == 'history':
                cursor.execute("""
                    SELECT 
                        vr.registration_id,
                        v.visitor_id,
                        v.visitor_name as name,
                        vr.purpose,
                        vr.visit_date as date,
                        vr.status,
                        vr.time_in,
                        vr.time_out,
                        vr.created_at,
                        d.department_name as location
                    FROM visitor_registrations vr
                    JOIN visitors v ON v.visitor_id = vr.visitor_id
                    LEFT JOIN departments d ON d.department_id = vr.department_id
                    WHERE vr.department_id = %s 
                    ORDER BY vr.visit_date DESC, vr.created_at DESC
                    LIMIT 20
                """, (session.get('user_id'),))
                visits = cursor.fetchall() or []
                cursor.close()
                conn.close()
                return render_template('department-history.html', visits=visits)
            
            elif view == 'profile':
                # Get department info
                cursor.execute("""
                    SELECT * FROM departments WHERE department_id = %s
                """, (session.get('user_id'),))
                department = cursor.fetchone()
                
                cursor.close()
                conn.close()
                return render_template('department-profile.html', 
                                    department=department,
                                    total_visits=stats['total_visits'],
                                    monthly_visits=stats['monthly_visits'],
                                    avg_daily_visits=stats.get('avg_response_time', 0))

            cursor.close()
            conn.close()
            return render_template(templates.get(view, "DeptDashboard.html"))

        cursor.close()
        conn.close()
        return render_template("DeptDashboard.html",
                           recent_visits=recent_visits,
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
        # Handle visitor history view
        if view == 'history':
            conn = get_db_connection()
            if not conn:
                return "Database connection error", 500

            cursor = conn.cursor(dictionary=True)
            try:                # Get visitor's visit history
                cursor.execute("""
                    SELECT 
                        vr.registration_id,
                        v.visitor_name as name,
                        vr.purpose,
                        vr.visit_date,
                        d.department_name as location,
                        vr.status,
                        vr.created_at
                    FROM visitor_registrations vr
                    JOIN visitors v ON v.visitor_id = vr.visitor_id
                    JOIN departments d ON d.department_id = vr.department_id
                    WHERE vr.visitor_id = %s 
                    ORDER BY vr.visit_date DESC, vr.created_at DESC
                """, (session['user_id'],))
                visits = cursor.fetchall()
                
                cursor.close()
                conn.close()
                return render_template('visitor-history.html', visits=visits)
                
            except Exception as e:
                print(f"Error in visitor history: {str(e)}")
                if 'cursor' in locals():
                    cursor.close()
                if 'conn' in locals():
                    conn.close()
                return "Error loading visit history", 500

        # Handle QR code view
        elif view == 'qr':
            conn = get_db_connection()
            if not conn:
                return "Database connection error", 500

            cursor = conn.cursor(dictionary=True)
            try:
                # Get visitor's active registration and QR code
                cursor.execute("""
                    SELECT v.*, vr.visit_date, vr.status, vr.qr_code_path
                    FROM visitors v
                    LEFT JOIN visitor_registrations vr ON v.visitor_id = vr.visitor_id
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
                return "Error processing QR code", 500

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
            visit_id = f"VR{session['user_id'][-6:]}"
            cursor.execute("""
                INSERT INTO visits 
                (id, visitor_id, name, address, contact_no, purpose, location, date, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                visit_id,
                session["user_id"],
                data["name"],
                data["address"],
                data["contactNo"],
                data["purpose"],
                data["location"],
                datetime.strptime(data["date"], "%Y-%m-%d").date(),
                'pending'
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
        
        # Get the visit request
        cursor.execute("""
            SELECT * FROM visits 
            WHERE id = %s
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
            "date": visit['date'].isoformat(),
            "location": visit['location'],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            # Create QR code
            qr_code_img = generate_qr_code(str(qr_data))
            
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
                """, (qr_code_img, visit['date'], visit['visitor_id']))
            else:
                # Create new QR code entry
                cursor.execute("""
                    INSERT INTO visitor_qr 
                    (visitor_id, qr_code, valid_until, is_active)
                    VALUES (%s, %s, %s, %s)
                """, (visit['visitor_id'], qr_code_img, visit['date'], True))
            
            # Update visit status to approved
            cursor.execute("""
                UPDATE visits 
                SET status = 'approved'
                WHERE id = %s
            """, (visit_id,))
            
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

@app.route("/department/verify_visitor", methods=["POST"])
@login_required
@role_required(["department"])
def verify_visitor():
    try:
        data = request.get_json()
        visitor_id = data.get('visitor_id')

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
                v.phone 
            FROM visitor_registrations vr
            JOIN visitors v ON vr.visitor_id = v.visitor_id
            WHERE vr.visitor_id = %s 
            AND vr.department_id = %s
            AND vr.status = 'approved'
            AND vr.visit_date = CURDATE()
            AND (vr.time_out IS NULL OR vr.time_in IS NULL)
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

        # Check if visitor is checking in or out
        if visit['time_in'] is None:
            # Check in
            cursor.execute("""
                UPDATE visitor_registrations 
                SET status = 'active',
                    time_in = NOW(),
                    updated_at = NOW()
                WHERE registration_id = %s
            """, (visit['registration_id'],))

            action = "checked in"
            current_time = datetime.now().strftime('%I:%M %p')
        else:
            # Check out
            cursor.execute("""
                UPDATE visitor_registrations 
                SET status = 'completed',
                    time_out = NOW(),
                    updated_at = NOW()
                WHERE registration_id = %s
            """, (visit['registration_id'],))

            action = "checked out"
            current_time = datetime.now().strftime('%I:%M %p')

        # Log the action
        cursor.execute("""
            INSERT INTO system_logs 
            (staff_id, action, related_department_id, ip_address)
            VALUES (%s, %s, %s, %s)
        """, (
            session['user_id'],
            f"Visitor {visitor_id} {action} at {current_time}",
            session['user_id'],
            request.remote_addr
        ))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            "success": True,
            "status": "Valid",
            "message": f"Visitor successfully {action}",
            "visitor": {
                "name": visit['visitor_name'],
                "email": visit['email'],
                "phone": visit['phone'],
                "purpose": visit['purpose'],
                "action": action,
                "time": current_time
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

if __name__ == "__main__":
    app.run(debug=True)
