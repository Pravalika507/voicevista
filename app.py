from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from assistant import process_voice_command
from openrouter_chatbot import get_chatbot_response
import datetime
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_super_secret_key_keep_this_secure'

# Configure upload folder and allowed extensions
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client['voicesecure']
users_collection = db['users']

# Login Route (Always opens first)
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Please fill in all fields', 'error')
            return render_template('login.html')

        user = users_collection.find_one({'username': username})

        if user and check_password_hash(user.get('password', ''), password):
            session['username'] = username
            session['email'] = user.get('email', '')
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
            return render_template('login.html')

    return render_template('login.html')

# Forgot Password Route - added in the login page
@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        username = request.form.get('username')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if not all([username, new_password, confirm_password]):
            flash('Please fill in all fields', 'error')
            return render_template('forgot_password.html')

        if new_password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('forgot_password.html')

        user = users_collection.find_one({'username': username})
        if not user:
            flash('User not found', 'error')
            return render_template('forgot_password.html')

        hashed_password = generate_password_hash(new_password)
        users_collection.update_one(
            {'username': username},
            {'$set': {'password': hashed_password}}
        )

        flash('Password updated successfully! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('forgot_password.html')

# Register Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    session.clear()  # Clear any existing session
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        voiceprint = request.form.get('voiceprint', '')
        
        # Handle file upload
        profile_photo = None
        if 'profile_photo' in request.files:
            file = request.files['profile_photo']
            if file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Create uploads directory if it doesn't exist
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                profile_photo = filepath

        if not all([username, email, password, confirm_password]):
            flash('Please fill in all required fields', 'error')
            return render_template('register.html')

        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('register.html')

        if users_collection.find_one({'$or': [{'username': username}, {'email': email}]}):
            flash('Username or email already exists', 'error')
            return render_template('register.html')

        hashed_password = generate_password_hash(password)

        user_data = {
            'username': username,
            'email': email,
            'password': hashed_password,
            'voiceprint': voiceprint,
            'created_at': datetime.datetime.utcnow()
        }

        # Add profile photo path if uploaded
        if profile_photo:
            user_data['profile_photo'] = profile_photo

        users_collection.insert_one(user_data)

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# Dashboard Route
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        flash('Please login to access this page.', 'error')
        return redirect(url_for('login'))
    
    # Fetch user info from the database
    user = users_collection.find_one({'username': session['username']})
    profile_photo = user.get('profile_photo', 'static/default-avatar.jpg')  # Default if no photo

    return render_template('dashboard.html', 
                         username=session['username'],
                         email=session.get('email', ''),
                         profile_photo=profile_photo)

# Voice Login Endpoint
@app.route('/voice-login', methods=['POST'])
def voice_login():
    data = request.get_json()
    username = data.get('username')
    voiceprint = data.get('voiceprint')
    
    user = users_collection.find_one({'username': username})
    
    if user and user.get('voiceprint'):
        # Simulated voice match check
        session['username'] = username
        session['email'] = user.get('email', '')
        return jsonify({'success': True})
    
    return jsonify({'success': False})

# Voice Command Processing
@app.route('/process_voice', methods=['POST'])
def process_voice():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
        
    data = request.get_json()
    command = data.get('command', '')
    result = process_voice_command(command)
    return jsonify({'result': result})

# Chat Endpoint
@app.route('/chat', methods=['POST'])
def chat():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
        
    data = request.get_json()
    user_message = data.get('message', '')
    bot_reply = get_chatbot_response(user_message)
    return jsonify({
        'reply': bot_reply,
        'messageId': str(datetime.datetime.now().timestamp())
    })

# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('login'))

# Help Page
@app.route('/help')
def help():
    return render_template('help.html')

if __name__ == "__main__":
    # Create upload directory if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)