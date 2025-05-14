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
