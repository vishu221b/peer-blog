from flask import (
    Flask, render_template, request, session
)
from src.models import User
from src import Database


app = Flask(__name__)
app.secret_key = "NotSecure"


@app.before_first_request
def initialize_db():
    Database.initialize()


@app.route('/')
def home():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_user():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        user = User(email=email, password=password)
        if user.is_login_valid():
            user.login(email)
        return render_template('profile.html', email=session['email'])


if __name__ == "__main__":
    app.run(port=5000, debug=True)
