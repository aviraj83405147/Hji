from flask import Flask, render_template, request
import requests
import json

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
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
            'haters': haters
        }

        try:
            res = requests.post('http://localhost:5001/send', json=data)
            status = res.text
        except Exception as e:
            status = f"Error: {str(e)}"

    return render_template('index.html', status=status)

if __name__ == '__main__':
    app.run(debug=True)
