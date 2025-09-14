from flask import Flask, render_template, url_for,  request, redirect
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/services")
def services():
    return render_template("services.html")

# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Handle registration form (save to DB later if needed)
        return redirect(url_for('login'))
    return render_template('Login_Files/register.html', title="Register")

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    role = request.args.get("role")
    if not role:
        role = "patient"  # Default to patient login

    if request.method == "POST":
        role = request.form.get("role")
        username = request.form.get("username")
        password = request.form.get("password")
        # handle login logic based on role here
        return f"Logged in as {role}: {username}"

    return render_template("Login_Files/login.html", role=role, title="Login")


if __name__ == "__main__":
    app.run(debug=True)