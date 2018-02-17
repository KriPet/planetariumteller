from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Show(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.String(10), nullable=False, default="")
    show = db.Column(db.String(100), nullable=False, default="")
    visitors = db.Column(db.Integer, nullable=False, default=0)
    vert = db.Column(db.String(50), nullable=False, default="")


if __name__ == "__main__":
    print("Setting up database tables")
    db.create_all()
    print("Done")

