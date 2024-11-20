import logging
import logging.handlers
from flask import Flask, render_template, request, redirect, url_for

# Logging Format
logging_format = logging.Formatter('%(asctime)s %(message)s')

# HTTP Logger
funnel_logger = logging.getLogger("HTTP Logger")
funnel_logger.setLevel(logging.INFO)
funnel_handler = logging.handlers.RotatingFileHandler('http_audits.log', maxBytes=2000, backupCount=5)
funnel_handler.setFormatter(logging_format)
funnel_logger.addHandler(funnel_handler)

# Baseline honeypot

def web_honeypot(input_username="admin", input_password="password") :
    app = Flask(__name__)
    @app.route('/')
    def index():
        return render_template('web-login.html') # insert your personal html
    
    @app.route("/login", methods=['POST'])
    def login() :
        username = request.form['username'] # located at the html file, you will see the id called username and password, used for collect user input.
        password = request.form['password']
        
        ip_address = request.remote_addr
        
        funnel_logger.info(f'Client with IP Address: {ip_address} entered\n Username: {username} | Password: {password}')
        
        if username == input_username and password == input_password :
            return "Congrats ! You now login."# whatever you prefer
        else :
            return "Invalid username or password. Please Try Again!"

    return app

def run_web_honeypot(port = 5001, input_username="username", input_password="password") :
    run_web_honeypot_app = web_honeypot(input_username, input_password)
    run_web_honeypot_app.run(host='0.0.0.0', port=port, debug=True) # 0.0.0.0 is mean that the server will going to listen to all the IP addresses.
    
    return run_web_honeypot_app

run_web_honeypot(port=5001, input_password= "password", input_username= "username")