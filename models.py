from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Show(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.String(10), nullable=False, default="")
    show = db.Column(db.String(100), nullable=False, default="")
    visitors = db.Column(db.Integer, nullable=False, default=0)
    vert = db.Column(db.String(50), nullable=False, default="")


