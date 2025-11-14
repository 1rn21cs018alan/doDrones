import os
from flask import Flask, request, redirect, url_for, render_template,session
from werkzeug.utils import secure_filename
from uploader import upload
from dotenv import load_dotenv
from flask_session import Session
from datetime import timedelta
import re
from supabaseHandler import verifyUser,userExists,insertUser


load_dotenv()

isDevelopment = os.environ.get("IS_DEVELOPMENT") == "YES"
print(isDevelopment)
# Configure upload folder and allowed extensions
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["SESSION_PERMANENT"] = True
# app.config['SECRET_KEY'] = '1234567890'
# app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(minutes=5)
app.config["SESSION_TYPE"] = "filesystem"
Session(app) 
# Helper function to check allowed file extensions


def allowedFile(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validateUsername(x):
    s=r"^[a-zA-Z][a-zA-Z0-9_]{4,32}$"
    return re.match(s,x)
def validatePassword(x):
    s=r"^[a-zA-Z0-9!@#$%_]{8,32}$"
    return re.match(s,x)
def validateEmail(x):
    s=r"^[^@]+@[^@]+\.[^@]+$"
    return re.match(s,x)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if isDevelopment:
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            if verifyUser(username, password):
                session.permanent=True
                app.permanent_session_lifetime=timedelta(seconds=17)
                session["name"]=username
                return "logged in successfully"
            print("wrong cred")
            return render_template("login_temp.html",wrong_cred=True)
                
        return render_template("login_temp.html")
    
    
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if isDevelopment:
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            email = request.form.get('email')
            userValid=validateUsername(username)
            passValid=validatePassword(password)
            emailValid=validateEmail(email)
            if userValid and passValid and emailValid:
                status=userExists(username)
                if status is None:
                    return 'Server Error. Please try again '
                if status == False:
                    status=insertUser(username,password,email)
                    if len(status.data)==1:
                        session.permanent=True
                        app.permanent_session_lifetime=timedelta(seconds=17)
                        session["name"]=username
                        return "signed up and logged in successfully"
                    return 'Server Error. Please try again '
                else:
                    return render_template("signup.html",duplicate_user=True)
                    
            ctx={
            "invalid_username":not userValid,
            "invalid_email":not emailValid,
            "invalid_password":not passValid,
            }
            return render_template("signup.html",**ctx)
            
        return render_template("signup.html")


@app.route("/logout")
def logout():
    session["name"] = None
    return redirect("/")

@app.route('/uploadtest', methods=['GET', 'POST'])
def uploadFile():
    if isDevelopment:
        if session.get("name") is None:
            return "User not Logged in"
        if request.method == 'POST':
            # Check if a file is part of the request
            if 'file' not in request.files:
                return redirect(request.url)  # No file part in the request

            file = request.files['file']
            # If the user does not select a file, the browser submits an empty file without a filename.
            if file.filename == '':
                return redirect(request.url)

            # print(type(file.read()))
            # Save the file if it's allowed
            try:
                if file and allowedFile(file.filename):
                    filename = secure_filename(file.filename)
                    fileData = file.read()
                    if(len(fileData)>(5*(2**20))):
                        return 'File exceeds 5MB!'
                    id = upload(filename, fileData)
                    # print(file,dir(file))
                    # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    return 'File uploaded successfully!'
            except:
                ...
            return "File Upload Failed"

        return render_template('upload.html')


@app.route("/")
def index():
    return render_template("index.html")

if __name__ == '__main__':
    if isDevelopment:
        from waitress import serve
        serve(app, host="0.0.0.0", port=8000)
    else:
        app.run(host="0.0.0.0", debug=True)
