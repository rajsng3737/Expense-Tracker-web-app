from flask import Flask, render_template
app = Flask(__name__)
app.template_folder='./'
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/css_scripts/login.css')
def login_css():
    return render_template('css_scripts/login.css')

if __name__ == '__main__':
    app.run(debug=True)