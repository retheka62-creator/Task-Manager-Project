from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, \
    login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

app = Flask(__name__)
app.secret_key = "super-secret"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///task_manager.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    tasks = db.relationship('Task', backref='user', lazy=True)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.Date)
    priority = db.Column(db.String(10), default='Medium')
    status = db.Column(db.String(20), default='Pending')
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash("Username already exists")
            return redirect(url_for('register'))
        hashed = generate_password_hash(password)
        user = User(username=username, password_hash=hashed)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful. Please log in.")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid username or password")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.due_date).all()
    total = len(tasks)
    completed = sum(t.status == 'Completed' for t in tasks)
    pending = sum(t.status == 'Pending' for t in tasks)
    from datetime import datetime
    return render_template(
        'dashboard.html',
        tasks=tasks, total=total, completed=completed,
        pending=pending, now=datetime.utcnow
    )

@app.route('/task/create', methods=['POST'])
@login_required
def create_task():
    d = request.form
    due_date = datetime.datetime.strptime(d.get('due_date'), '%Y-%m-%d').date() if d.get('due_date') else None
    t = Task(
        user_id=current_user.id,
        title=d['title'],
        description=d.get('description'),
        due_date=due_date,
        priority=d.get('priority', 'Medium'))
    db.session.add(t)
    db.session.commit()
    flash("Task created!")
    return redirect(url_for('dashboard'))

@app.route('/task/<int:task_id>/edit', methods=['POST'])
@login_required
def edit_task(task_id):
    t = Task.query.get_or_404(task_id)
    if t.user_id != current_user.id:
        flash("Unauthorized.")
        return redirect(url_for('dashboard'))
    d = request.form
    t.title = d['title']
    t.description = d.get('description')
    t.due_date = datetime.datetime.strptime(d.get('due_date'), '%Y-%m-%d').date() if d.get('due_date') else None
    t.priority = d.get('priority', 'Medium')
    db.session.commit()
    flash("Task updated.")
    return redirect(url_for('dashboard'))

@app.route('/task/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    t = Task.query.get_or_404(task_id)
    if t.user_id != current_user.id:
        flash("Unauthorized.")
        return redirect(url_for('dashboard'))
    db.session.delete(t)
    db.session.commit()
    flash("Task deleted!")
    return redirect(url_for('dashboard'))

@app.route('/task/<int:task_id>/complete', methods=['POST'])
@login_required
def complete_task(task_id):
    t = Task.query.get_or_404(task_id)
    if t.user_id != current_user.id:
        flash("Unauthorized.")
        return redirect(url_for('dashboard'))
    t.status = 'Completed'
    db.session.commit()
    flash("Task marked as completed!")
    return redirect(url_for('dashboard'))

if __name__ == "__main__":
    # Only first run: uncomment next two lines, then re-comment.
    # with app.app_context():
    #     db.create_all()
    app.run(debug=True)