from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = 'ccs_secret_key_2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ccs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'webp'}

db = SQLAlchemy(app)

# ─── CREATE UPLOAD FOLDER IF NOT EXISTS ───
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ─── DATABASE MODEL ───
class Student(db.Model):
    id           = db.Column(db.Integer, primary_key=True)
    id_number    = db.Column(db.String(20), unique=True, nullable=False)
    last_name    = db.Column(db.String(50), nullable=False)
    first_name   = db.Column(db.String(50), nullable=False)
    middle_name  = db.Column(db.String(50))
    course       = db.Column(db.String(20), nullable=False)
    course_level = db.Column(db.String(5), nullable=False)
    email        = db.Column(db.String(100), unique=True, nullable=False)
    password     = db.Column(db.String(200), nullable=False)
    address      = db.Column(db.String(200))
    profile_pic  = db.Column(db.String(200), default='default.png')

# ─── CREATE TABLES ───
with app.app_context():
    db.create_all()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# ─── ROUTES ───
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    show_modal = False
    session_name = None
    if request.method == 'POST':
        id_number = request.form['id_number']
        password  = request.form['password']

        student = Student.query.filter_by(id_number=id_number).first()

        if not student:
            error = 'ID number not found.'
        elif not check_password_hash(student.password, password):
            error = 'Incorrect password.'
        else:
            session['student_id'] = student.id
            session['student_name'] = student.first_name
            show_modal = True
            session_name = f"{student.first_name} {student.middle_name} {student.last_name}"

    return render_template('login.html', error=error, show_modal=show_modal, session_name=session_name)

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    success = None
    if request.method == 'POST':
        id_number       = request.form['id_number']
        last_name       = request.form['last_name']
        first_name      = request.form['first_name']
        middle_name     = request.form.get('middle_name', '')
        course          = request.form['course']
        course_level    = request.form['course_level']
        email           = request.form['email']
        password        = request.form['password']
        repeat_password = request.form['repeat_password']
        address         = request.form.get('address', '')

        if not course or course == '':
            error = 'Please select a course.'
        elif not course_level or course_level == '':
            error = 'Please select a year level.'
        elif len(password) < 6:
            error = 'Password must be at least 6 characters.'
        elif password != repeat_password:
            error = 'Passwords do not match.'
        elif Student.query.filter_by(id_number=id_number).first():
            error = 'ID number already registered.'
        elif Student.query.filter_by(email=email).first():
            error = 'Email already registered.'
        else:
            hashed_pw = generate_password_hash(password)
            new_student = Student(
                id_number    = id_number,
                last_name    = last_name,
                first_name   = first_name,
                middle_name  = middle_name,
                course       = course,
                course_level = course_level,
                email        = email,
                password     = hashed_pw,
                address      = address
            )
            db.session.add(new_student)
            db.session.commit()
            success = 'Account created successfully!'

    return render_template('register.html', error=error, success=success)

@app.route('/dashboard')
def dashboard():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('dashboard.html', student=student)

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'student_id' not in session:
        return redirect(url_for('login'))

    student = Student.query.get(session['student_id'])
    error = None
    success = None

    if request.method == 'POST':
        first_name       = request.form['first_name']
        last_name        = request.form['last_name']
        middle_name      = request.form.get('middle_name', '')
        email            = request.form['email']
        address          = request.form.get('address', '')
        new_password     = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        # ─ Handle profile picture upload ─
        if 'profile_pic' in request.files:
            file = request.files['profile_pic']
            if file and allowed_file(file.filename):
                filename = secure_filename(f"student_{student.id_number}.{file.filename.rsplit('.', 1)[1].lower()}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                student.profile_pic = filename

        existing = Student.query.filter_by(email=email).first()
        if existing and existing.id != student.id:
            error = 'Email is already used by another account.'
        elif new_password and len(new_password) < 6:
            error = 'New password must be at least 6 characters.'
        elif new_password and new_password != confirm_password:
            error = 'Passwords do not match.'
        else:
            student.first_name  = first_name
            student.last_name   = last_name
            student.middle_name = middle_name
            student.email       = email
            student.address     = address

            if new_password:
                student.password = generate_password_hash(new_password)

            db.session.commit()
            session['student_name'] = student.first_name
            success = 'Profile updated successfully!'

    return render_template('edit_profile.html', student=student, error=error, success=success)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
