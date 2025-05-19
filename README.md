# VMASS (Visitor Management and Analysis System)

## Overview
VMASS is a comprehensive Visitor Management and Analysis System designed for institutional use. It provides features for visitor registration, QR code-based check-in/check-out, visit history tracking, and administrative controls.

## Setup Instructions for Collaborators

### 1. Prerequisites
Make sure you have the following installed on your laptop:
- Python 3.x (Download from [python.org](https://www.python.org/downloads/))
- Git (Download from [git-scm.com](https://git-scm.com/downloads))

### 2. Clone the Repository
Open PowerShell and run these commands:
```powershell
# Create a directory for the project
mkdir VMASS
cd VMASS

# Clone the repository
git clone https://github.com/Bad-Burn/VMAS.git .

# The dot (.) at the end means clone into current directory
```

### 3. Set Up Python Virtual Environment
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

### 4. Configure the Application
The application will create its database automatically on first run. No additional configuration is needed, but you can optionally set a custom secret key:
```powershell
$env:SECRET_KEY = "your-secure-secret-key"
```

### 5. Run the Application
```powershell
python app.py
```

The application will be available at `http://localhost:5000`

## Project Structure
```
VMASS/
├── app.py              # Main application file
├── requirements.txt    # Python dependencies
├── models/            # Database models
│   ├── __init__.py
│   ├── db.py         # Database configuration
│   ├── user.py       # User model
│   ├── visit.py      # Visit model
│   ├── visitor.py    # Visitor model
│   └── visitor_qr.py # QR code management
├── static/           # Static assets
│   ├── css/         # Stylesheets
│   ├── images/      # Image assets
│   └── js/          # JavaScript files
└── templates/        # HTML templates
    ├── VisitorDashboard.html
    ├── visitor-form.html
    ├── visitor-qr.html
    └── other template files
```

## Troubleshooting Guide

### Common Issues and Solutions

1. **Import Errors**
   - Make sure your virtual environment is activated
   - Check that all dependencies are installed: `pip install -r requirements.txt`

2. **Database Issues**
   - If you see database errors, delete `vmas.db` and restart the application
   - The database will be recreated automatically

3. **Session Errors**
   - Ensure the `flask_session` directory exists
   - Clear old session files if you experience login issues

4. **Missing Static Files**
   - Verify that all files in the `static` directory were cloned correctly
   - Check file permissions

### Development Notes

1. **Local Database**
   - Each developer works with their own local `vmas.db`
   - Do not commit the database file
   - Database schema is created automatically on first run

2. **Version Control**
   - Always pull latest changes before starting work: `git pull`
   - Create new branches for features: `git checkout -b feature-name`
   - Don't commit `__pycache__`, `flask_session`, or `vmas.db`

3. **Environment Setup**
   - Always use virtual environment
   - Keep `requirements.txt` updated if you add new packages

For additional help or to report issues, please use the GitHub issues page.

3. Create and activate virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```

4. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

5. Initialize the database:
   ```powershell
   python app.py
   ```

6. Access the application:
   - Open your web browser and navigate to `http://localhost:5000`
   - The application should now be running and ready to use

## Project Structure
- `/models` - Database models and configurations
- `/static` - CSS, JavaScript, and image assets
- `/templates` - HTML templates
- `app.py` - Main application file
- `requirements.txt` - Project dependencies
