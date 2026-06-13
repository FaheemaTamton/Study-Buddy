from app import db
from datetime import date

class StudyLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, default=date.today)
    duration = db.Column(db.Integer)  # minutes

    user = db.relationship('User', backref=db.backref('logs', lazy=True))


class StudyLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # link to User table
    date = db.Column(db.Date, default=date.today)
    duration = db.Column(db.Integer)  # minutes

    def __repr__(self):
        return f"<StudyLog {self.date} - {self.duration}min>"
