# Admission Form Application

This project is an admission form application built using Flask. It allows users to submit their admission details through a web form.

## Project Structure

```
admission-form-app
├── src
│   ├── app.py                # Entry point of the application
│   ├── forms
│   │   └── __init__.py       # Form classes using Flask-WTF
│   ├── models
│   │   └── __init__.py       # Data models for the application
│   ├── routes
│   │   └── __init__.py       # Application routes
│   └── templates
│       └── base.html         # Base HTML template
├── requirements.txt           # Project dependencies
└── README.md                  # Project documentation
```

## Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd admission-form-app
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```
     source venv/bin/activate
     ```

4. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

To run the application, execute the following command:
```
python src/app.py
```

Visit `http://127.0.0.1:5000` in your web browser to access the admission form.