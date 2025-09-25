from flask import Blueprint, render_template, url_for,  request, redirect

auth_bp = Blueprint("auth", __name__, template_folder="templates")

# Register
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Handle registration form (save to DB later if needed)
        return redirect(url_for('auth.login'))
    return render_template('register.html', title="Register")

# Login
@auth_bp.route('/login', methods=['GET', 'POST'])
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

    return render_template("login.html", role=role, title="Login")