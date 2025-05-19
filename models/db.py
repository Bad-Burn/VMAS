from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Import all models
from models.security_guard import SecurityGuard
from models.department import Department
from models.visitor import Visitor
from models.visitor_registration import VisitorRegistration
from models.department_staff import DepartmentStaff
from models.system_log import SystemLog

def init_db(app):
    db.init_app(app)
