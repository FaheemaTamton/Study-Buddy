from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import date, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import random
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'supersecretkey123'
db = SQLAlchemy(app)

# --- Models ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    logs = db.relationship('StudyLog', backref='user', lazy=True)

class StudyLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, default=date.today)
    duration = db.Column(db.Integer)  # minutes

    def __repr__(self):
        return f"<StudyLog {self.date} - {self.duration}min>"

# --- Motivational messages ---
messages = [
    "You're doing great! 🌸",
    "One step closer to your goal! 💪",
    "Keep going, you can do it! 🌟",
    "Focus and shine! ✨",
    "Study smart, stay happy! 😊"
]

with app.app_context():
    db.create_all()

# --- Routes ---
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    today = date.today()
    today_logs = StudyLog.query.filter_by(user_id=user_id, date=today).all()
    total_minutes = sum([log.duration for log in today_logs])
    
    streak = calculate_streak(user_id)
    msg = random.choice(messages)
    
    return render_template('index.html', total_minutes=total_minutes, streak=streak, message=msg)

@app.route('/add_session', methods=['POST'])
def add_session():
    if 'user_id' not in session:
        flash("Please login first!")
        return redirect(url_for('login'))

    duration = int(request.form.get('duration'))
    new_log = StudyLog(user_id=session['user_id'], date=date.today(), duration=duration)
    db.session.add(new_log)
    db.session.commit()
    return redirect(url_for('index'))

# --- Session History ---
@app.route('/history')
def history():
    if 'user_id' not in session:
        flash("Please login first!")
        return redirect(url_for('login'))

    user_id = session['user_id']
    sessions = StudyLog.query.filter_by(user_id=user_id).order_by(StudyLog.date.desc()).all()
    return render_template('history.html', sessions=sessions)

@app.route('/delete/<int:id>')
def delete_session(id):
    if 'user_id' not in session:
        flash("Please login first!")
        return redirect(url_for('login'))

    session_to_delete = StudyLog.query.get_or_404(id)
    db.session.delete(session_to_delete)
    db.session.commit()
    return redirect(url_for('history'))

# --- Calculate streak ---
def calculate_streak(user_id):
    logs = StudyLog.query.filter_by(user_id=user_id).order_by(StudyLog.date.asc()).all()
    if not logs:
        return 0
    streak = 0
    today = date.today()
    delta = 0
    for log in reversed(logs):
        if log.date == today - timedelta(days=delta):
            streak += 1
            delta += 1
        else:
            break
    return streak

# --- Registration ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_pw)
        try:
            db.session.add(new_user)
            db.session.commit()
            flash("Account created! Please login.")
            return redirect(url_for('login'))
        except IntegrityError:
            db.session.rollback()
            flash("Username already exists! Please choose another.")
            return redirect(url_for('register'))
    return render_template('register.html')

# --- Login ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password, password):
            flash("Invalid username or password!")
            return redirect(url_for('login'))
        session['user_id'] = user.id
        session['username'] = user.username
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))



if __name__ == '__main__':
    app.run(debug=True)
