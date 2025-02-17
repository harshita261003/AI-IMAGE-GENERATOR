import os
import torch
import base64
from io import BytesIO
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_bcrypt import Bcrypt
from flask_mysqldb import MySQL
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from diffusers import StableDiffusionPipeline

app = Flask(__name__)
app.secret_key = "your_secret_key"

# MySQL Database Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'  # Change if needed
app.config['MYSQL_PASSWORD'] = ''  # Change if needed
app.config['MYSQL_DB'] = 'image'

mysql = MySQL(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"  # Direct user to login page if not authenticated

# User Class for Flask-Login
class User(UserMixin):
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email

@login_manager.user_loader
def load_user(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()
    if user:
        return User(user[0], user[1], user[2])
    return None

# Authentication Routes
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, hashed_pw))
        mysql.connection.commit()
        cur.close()

        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()

        if user and bcrypt.check_password_hash(user[3], password):  # Check hashed password
            user_obj = User(user[0], user[1], user[2])  # Create user object
            login_user(user_obj)  # Log the user in
            session["user"] = user[1]  # Store username in session
            flash("Login successful!", "success")
            return redirect(url_for("home"))  # Redirect to home page after login

        flash("Invalid credentials, please try again!", "error")
        return redirect(url_for("login"))  # Stay on login page

    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))

# Home Route - Protected by Login
@app.route("/")
@login_required
def home():
    return render_template("index.html", username=current_user.username)

# Stable Diffusion Setup
HUGGINGFACE_TOKEN = os.getenv("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")  # Replace with your token

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model_id = "CompVis/stable-diffusion-v1-4"
pipe = StableDiffusionPipeline.from_pretrained(
    model_id,
    revision="fp16" if torch.cuda.is_available() else "fp32",
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    use_auth_token=HUGGINGFACE_TOKEN
)
pipe.to(device)

@app.route("/generate", methods=["POST"])
@login_required
def generate():
    data = request.get_json()
    prompt = data.get("prompt", "").strip()

    if not prompt:
        return jsonify({"error": "Prompt cannot be empty"}), 400

    # Generate Image
    with torch.autocast(device.type):
        image = pipe(prompt, guidance_scale=8.5).images[0]

    # Convert image to Base64 string
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

    return jsonify({"image_base64": f"data:image/png;base64,{img_str}"})

if __name__ == "__main__":
    app.run(debug=True)
