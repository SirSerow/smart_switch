from flask import Flask, render_template, request, send_from_directory, redirect
import serial
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import webbrowser
from skpy import Skype
import threading
import requests
import time

app = Flask(__name__)

# Email configuration (replace with your SMTP server and credentials)
SMTP_SERVER = 'smtp.example.com'
SMTP_PORT = 587
SMTP_USERNAME = 'your_email@example.com'
SMTP_PASSWORD = 'your_email_password'

# Skype configuration (replace with your Skype credentials)
SKYPE_USERNAME = "your_skype_username"
SKYPE_PASSWORD = "your_skype_password"

# Replace 'COMX' with your actual serial port name
SERIAL_PORT = 'COMX'
BAUD_RATE = 115200  # Set the baud rate to match your device configuration

# URL of your Flask application for the serial port listener to make HTTP requests
FLASK_URL = 'http://localhost:5000/execute_action'

current_action = "call"

def send_email(recipient, subject, message):
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)

        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))

        server.sendmail(SMTP_USERNAME, recipient, msg.as_string())
        server.quit()

        return 'Email sent'
    except Exception as e:
        return f'Error: {str(e)}'

def make_skype_call(recipient):
    try:
        skype = Skype(SKYPE_USERNAME, SKYPE_PASSWORD)
        call = skype.callUser(recipient)
        skype.conn.close()
        return f'Skype call initiated to {recipient}'
    except Exception as e:
        return f'Error: {str(e)}'

def open_website(url):
    try:
        webbrowser.open(url)
        return 'Website opened'
    except Exception as e:
        return f'Error: {str(e)}'

def execute_action(message):
    if message == b'Received: BUTTON PRESSED':
        print('Executing action')
        # You can define the action based on your application logic.
        # For example, you can check some condition and execute different actions accordingly.
        action = current_action  # Replace with the appropriate action
        if action == 'call':
            current_action = 'call'
            return make_skype_call("skype_username_or_phone_number") 
        elif action == 'mail':
            current_action = 'mail'
            return send_email("recipient@example.com", "Test Email", "This is a test email.")
        elif action == 'link':
            current_action = 'link'
            return open_website("https://synkom.co.jp/")
        else:
            return 'Unknown action'
    else:
        return 'No action'

@app.route('/')
def home():
    global current_action  # Access the global variable
    return render_template('index.html', current_action=current_action)

@app.route('/execute_action', methods=['POST'])
def execute_serial_action():
    action = request.form.get('action')
    if action == 'button_pressed':
        message = b'button_pressed'
        result = execute_action(message)
        return result
    else:
        return 'No action'

@app.route('/configure')
def configure():
    return render_template('configure.html')

@app.route('/configure', methods=['POST'])
def save_configuration():
    action = request.form.get('action')
    if action == 'make_call':
        recipient = request.form.get('recipient')
        # Save recipient configuration in a database or file
    elif action == 'send_email':
        recipient = request.form.get('recipient')
        subject = request.form.get('subject')
        # Save email configuration in a database or file
    elif action == 'open_website':
        url = request.form.get('url')
        # Save website configuration in a database or file

    return 'Configuration saved'

@app.route('/gif')
def display_gif():
    return render_template('display_gif.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/set_action', methods=['POST'])
def set_action():
    global current_action  # Access the global variable
    current_action = request.form.get('action')
    return redirect('/configure')  # Redirect back to the configuration page

def list_serial_ports():
    try:
        available_ports = []
        for i in range(0, 64):  # Check serial ports from /dev/tty0 to /dev/tty63
            port = f"/dev/ttyUSB{i}"
            try:
                ser = serial.Serial(port)
                ser.close()
                available_ports.append(port)
            except (OSError, serial.SerialException):
                pass
        return available_ports
    except Exception as e:
        print(f"Error: {str(e)}")
        return []

def serial_listener():
    try:
        # List available serial ports
        available_ports = list_serial_ports()

        if not available_ports:
            print("No serial ports found.")
            return

        for port in available_ports:
            try:
                ser = serial.Serial(port, BAUD_RATE)
                print(f"Connected to {port}")
                while True:
                    message = ser.readline().strip()
                    if message:
                        print(f"Received message: {message}")
                    execute_action(message)
                    # Send current action to the serial port
                    ser.write(current_action.encode())
                    time.sleep(0.1)
            except serial.SerialException as e:
                print(f"Serial port error on {port}: {str(e)}")
            finally:
                ser.close()
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == '__main__':
    # Start the serial port listener in a separate thread
    serial_thread = threading.Thread(target=serial_listener)
    serial_thread.daemon = True
    serial_thread.start()

    app.run(host='0.0.0.0', port=5000, debug=True)

    #time.sleep(10)  # Wait for the Flask app to start

    # Open the default browser to the main page of the Flask app
    #webbrowser.open('http://localhost:5000/')

    # Print app started message
    print('App started')
