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
                AND visit_date = %s
            """, (today,))
            approved_visits = cursor.fetchone()['count']

            cursor.execute("""
                SELECT COUNT(*) as count FROM visitor_registrations 
                WHERE status = 'active'
                AND time_in IS NOT NULL 
                AND time_out IS NULL
            """)
            active_visits = cursor.fetchone()['count']

            cursor.close()
            conn.close()

            return render_template('security-about.html',
                                total_visitors=total_visitors,
                                pending_requests=pending_requests,
                                approved_visits=approved_visits,
                                active_visits=active_visits)

        except Exception as e:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
            print(f"Error getting statistics: {str(e)}")
            return "Error loading statistics", 500

    # Handle history view
    if view == 'history':
        return render_template('security-history.html')

    # Handle all other views
    if view:
        return render_template(templates.get(view, "SecDashboard.html"))

    # Default view
    return render_template("SecDashboard.html")
