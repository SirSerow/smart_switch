from flask import Flask
from routes import register_blueprints
from threading import Thread
import time

app = Flask(__name__)

# Register the blueprints from the routes packages
register_blueprints(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

