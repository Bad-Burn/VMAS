from flask import Flask
from models.db import db, init_db
from models.user import User
from models.visit import Visit
from models.visitor_qr import VisitorQR

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vmas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

init_db(app)

with app.app_context():
    print("Dropping all tables...")
    db.drop_all()
    print("Creating all tables...")
    db.create_all()
    print("Database tables created successfully!")
