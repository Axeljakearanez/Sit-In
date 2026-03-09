from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "ccs_secret_key_2024"

users = []

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ""
    if request.method == 'POST':
        id_number = request.form['id_number'].strip()
        password  = request.form['password'].strip()
        if not id_number or not password:
            error = "Please fill in all fields."
        else:
            user = next((u for u in users if u['id_number'] == id_number and u['password'] == password), None)
            if user:
                session['student_id']   = user['id_number']
                session['student_name'] = user['first_name'] + ' ' + user['last_name']
                return redirect(url_for('login'))
            else:
                error = "Invalid ID Number or Password."
    return render_template('login.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    error   = ""
    success = ""
    if request.method == 'POST':
        id_number    = request.form['id_number'].strip()
        last_name    = request.form['last_name'].strip()
        first_name   = request.form['first_name'].strip()
        middle_name  = request.form['middle_name'].strip()
        course_level = request.form['course_level'].strip()
        password     = request.form['password']
        repeat_pass  = request.form['repeat_password']
        email        = request.form['email'].strip()
        course       = request.form['course'].strip()
        address      = request.form['address'].strip()

        if not id_number or not last_name or not first_name or not password or not email:
            error = "Please fill in all required fields."
        elif password != repeat_pass:
            error = "Passwords do not match."
        elif len(password) < 6:
            error = "Password must be at least 6 characters."
        elif '@' not in email:
            error = "Invalid email address."
        elif any(u['id_number'] == id_number for u in users):
            error = "ID Number already registered."
        else:
            users.append({
                'id_number': id_number, 'last_name': last_name,
                'first_name': first_name, 'middle_name': middle_name,
                'course_level': course_level, 'password': password,
                'email': email, 'course': course, 'address': address
            })
            success = "Account registered successfully!"
    return render_template('register.html', error=error, success=success)

if __name__ == '__main__':
    app.run(debug=True)