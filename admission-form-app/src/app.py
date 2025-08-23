# filepath: admission-form-app/src/app.py
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('base.html')

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    email = request.form['email']
    # Process the form data here
    return f"Received: {name}, {email}"

if __name__ == '__main__':
    app.run(debug=True)