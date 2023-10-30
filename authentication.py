from flask import Flask, render_template, request, url_for, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import secrets
app = Flask(__name__)
app.secret_key=secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://rick:hellomoto@127.0.0.1/ExpenseSystemDB'
db=SQLAlchemy(app)
bcrypt=Bcrypt(app)
class Authentication(db.Model):
    username = db.Column(db.String(65),unique=True,nullable=False)
    email = db.Column(db.String(65),unique=True,nullable=False,primary_key=True)
    password = db.Column(db.String(220), nullable=False)
    def __init__(self,username,email,password):
        self.username=username
        self.email=email
        self.password=password

app.template_folder='./'

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    elif request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        check_user = Authentication.query.filter_by(username=username).first()
        if check_user:
            flash('Username already exists', 'danger')
        else:
            # Hash the password before storing it
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            new_user = Authentication(username=username, email=email, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash("Account Created Successfully.", "success")
            return redirect(url_for('login'))
@app.route('/css_scripts/login.css')
def login_css():
    return render_template('css_scripts/login.css')

if __name__ == '__main__':
    app.run(debug=True)