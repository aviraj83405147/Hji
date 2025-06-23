from flask import Flask, render_template, request, redirect, session, url_for
from werkzeug.utils import secure_filename
import os
import json
import requests

app = Flask(__name__)
app.secret_key = 'supersecretkey'

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'json'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def login():
    error = ''
    if request.method == 'POST':
        if 'creds' not in request.files:
            error = 'No file part'
        file = request.files['creds']
        if file.filename == '':
            error = 'No selected file'
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Optional: Try to parse JSON to ensure it's valid
            try:
                with open(filepath, 'r') as f:
                    creds_data = json.load(f)
                session['creds_file'] = filename
                return redirect('/dashboard')
            except Exception as e:
                error = 'Invalid creds.json file.'

    return render_template('upload.html', error=error)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'creds_file' not in session:
        return redirect(url_for('login'))

    status = ''
    if request.method == 'POST':
        message = request.form.get('message')
        numbers = request.form.get('numbers')
        delay = request.form.get('delay')
        haters = request.form.get('haters')

        data = {
            'message': message,
            'numbers': numbers,
            'delay': delay,
            'haters': haters,
            'creds_file': session['creds_file']
        }

        try:
            res = requests.post('http://localhost:5001/send', json=data)
            status = res.text
        except Exception as e:
            status = f"Error: {str(e)}"

    return render_template('index.html', status=status)

@app.route('/logout')
def logout():
    session.pop('creds_file', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
