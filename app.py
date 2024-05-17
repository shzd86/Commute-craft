from datetime import datetime
from flask import Flask, request, render_template, redirect, session
from flask_sqlalchemy import SQLAlchemy
import bcrypt

app = Flask(__name__)

# Update MySQL database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:123456@localhost/student'
app.config['MYSQL_HOST'] = "localhost"
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = "123456"
app.config['MYSQL_DB'] = "student"

db = SQLAlchemy(app)
app.secret_key = 'secret_key'


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

    def __init__(self, email, password, name):
        self.name = name
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

class Driver(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

# Create all tables in the database
with app.app_context():
    db.create_all()
    

class Info(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100), nullable=False)
    Phone = db.Column(db.String(100), nullable=False)
    Place = db.Column(db.String(100), nullable=False)
    Time = db.Column(db.String(100), nullable=False)
    
with app.app_context():
    db.create_all()


class Present(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100), nullable=False)
    Date = db.Column(db.String(100), nullable=False)
    Present = db.Column(db.String(100), nullable=False)
    
with app.app_context():
    db.create_all()

class Home(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100), nullable=False)
    Time = db.Column(db.String(100), nullable=False)
    Date = db.Column(db.String(100), nullable=False)

with app.app_context():
    db.create_all()
    




@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return render_template('register.html', error='User with this email already exists.')

        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/login')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session['email'] = user.email
            return redirect('/dashboard')
        else:
            return render_template('login.html', error='Invalid user')

    return render_template('login.html')

@app.route('/driver_login', methods=['POST'])
def driver_login():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        # Check if the driver already exists
        existing_driver = Driver.query.filter_by(email=email).first()
        if existing_driver:
            return render_template('driver_login.html', error='Driver with this email already exists.')

        # Create a new driver
        new_driver = Driver(name=name, email=email, password=password)
        db.session.add(new_driver)
        db.session.commit()

        # Redirect to the driver login page
        return redirect('/dashboard')

    # If it's not a POST request, redirect to the driver registration page
    return redirect('/driver_login')



@app.route('/dashboard')
def dashboard():
    if 'email' in session:
        user = User.query.filter_by(email=session['email']).first()
        return render_template('dashboard.html', user=user)

    return redirect('registration.html')


@app.route('/registeration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        name = request.form['Name']
        phone = request.form['Phone']
        place = request.form['Place']
        time = request.form['Time']

        new_info = Info(Name=name, Phone=phone, Place=place, Time=time)
        db.session.add(new_info)
        db.session.commit()

        return "success"

    return render_template('registration.html')


@app.route('/prebook', methods=['GET', 'POST'])
def prebook():
    if request.method == 'POST':
        name = request.form['Name']
        date_str = request.form['Date']
        present = request.form['Present']

        date_obj = datetime.strptime(date_str, '%d/%m/%Y').date()
        new_present = Present(Name=name, Date=date_obj, Present=present)
        db.session.add(new_present)
        db.session.commit()

        return "success"

    return render_template('prebook.html')


@app.route('/departure', methods=['GET', 'POST'])
def departure():
    if request.method == 'POST':
        name = request.form['Name']
        time = request.form['Time']
        date_str = request.form['Date']

        date_obj = datetime.strptime(date_str, '%d/%m/%Y').date()
        
        new_home = Home(Name=name, Time=time, Date=date_obj)
        db.session.add(new_home)
        db.session.commit()

        return redirect('/departure')

    home_data = Home.query.order_by(Home.Date.desc(), Home.Time.asc()).all()

    return render_template('departure.html', home_data=home_data)


@app.route('/driver')
def driver():
    return render_template('driver.html')


@app.route('/logoutt')
def logoutt():
    return render_template('login.html')

@app.route('/driver_login')
def driver_login_page():
    return render_template('driver_login.html')



@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect('/login')


if __name__ == '__main__':
    app.run(debug=True)
