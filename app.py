import os
from flask import Flask, request, redirect, url_for, render_template,session,send_from_directory,make_response,jsonify
from werkzeug.utils import secure_filename
from werkzeug.exceptions import InternalServerError
from uploader import upload
from dotenv import load_dotenv
from flask_session import Session
from datetime import timedelta,datetime
import re
from supabaseHandler import userExists,insertUser,getUserData,upsertParticipantData\
    ,SUPABASE_GENERAL_ERROR,SUPABASE_NO_SUCH_USER_ERROR,SUPABASE_USER_ALREADY_VERIFIED
from sendEmail import sendMail
import random
import time


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
app.url_map.strict_slashes = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
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

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if isDevelopment:
#         if request.method == 'POST':
#             username = request.form.get('username')
#             password = request.form.get('password')
#             if verifyUser(username, password):
#                 session.permanent=True
#                 app.permanent_session_lifetime=timedelta(weeks=1)
#                 session["name"]=username
#                 return "logged in successfully"
#             print("wrong cred")
#             return render_template("login_temp.html",wrong_cred=True)
#         return render_template("login_temp.html")
    
    
# @app.route('/signup', methods=['GET', 'POST'])
# def signup():
#     if isDevelopment:
#         if request.method == 'POST':
#             username = request.form.get('username')
#             password = request.form.get('password')
#             email = request.form.get('email')
#             userValid=validateUsername(username)
#             passValid=validatePassword(password)
#             emailValid=validateEmail(email)
#             if userValid and passValid and emailValid:
#                 status=userExists(username)
#                 if status is None:
#                     return 'Server Error. Please try again '
#                 if status == False:
#                     status=insertUser(username,password,email)
#                     if len(status.data)==1:
#                         session.permanent=True
#                         app.permanent_session_lifetime=timedelta(seconds=17)
#                         session["name"]=username
#                         return "signed up and logged in successfully"
#                     return 'Server Error. Please try again '
#                 else:
#                     return render_template("signup.html",duplicate_user=True)
                    
#             ctx={
#             "invalid_username":not userValid,
#             "invalid_email":not emailValid,
#             "invalid_password":not passValid,
#             }
#             return render_template("signup.html",**ctx)
            
#         return render_template("signup.html")


@app.route("/logout")
def logout():
    session.clear()
    response=make_response(redirect("/"))
    for cookie_name in request.cookies:
        response.delete_cookie(cookie_name, path='/')
    return response 

# @app.route('/uploadtest', methods=['GET', 'POST'])
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


@app.route("/faq")
@app.route("/program")
@app.route("/login")
@app.route("/login/verify")
@app.route("/portal")
@app.route("/portal/profile")
@app.route("/portal/registration")
@app.route("/")
def index():
    return render_template("index.html")

#@app.route('/sponsers/<path:filename>')
#def serve_sponser_static(filename):
#    """
#    Serves files from the 'static' directory when the URL starts with '/sponsers/'.
#    """
#    # Use send_from_directory to safely serve the file
#    return send_from_directory(STATIC_DIR,"sponsers"+ filename)

# @app.route('/sponsors', defaults={'path': ''})
# @app.route('/sponsors/<path:path>')
# def redirect_xd(path):
#     new_url = '/static/sponsors'
#     if path:
#         new_url = f"{new_url}/{path}"
#     # return custom_static(new_url)
#     response=make_response(redirect(new_url, code=301))
#     response.headers['Cache-Control'] = 'public, max-age=300'
#     return response



@app.route('/static/<path:filename>')
def custom_static(filename):
    static_folder = os.path.join(app.root_path, 'static')
    response = make_response(send_from_directory(static_folder, filename))
    if filename.endswith(".svg"):
        response.headers['Cache-Control'] = 'public, max-age=300'
    return response

@app.route("/health")
def healthCheck():
    return "yes"

# @app.route("/speacial_test_cases/verifyEmail/<string:email>")
# def testEmail(email):
#     if isDevelopment:
#         random.seed(time.time_ns())
#         validityPeriod=10#mins
#         resendWaitingPeriod=3#mins
#         if session.get("name") is not None:
#             if datetime.now()>session.get("OTP_RESEND_AFTER",datetime(2003,1,1)):
#                 currentOTP=random.randint(100000,999999)
#                 username=session.get("name")
#                 dateVerify=datetime.now()
#                 responseData=insertOTP(username,currentOTP,expiryTimeDelta=timedelta(minutes=resendWaitingPeriod))
#                 if responseData is SUPABASE_GENERAL_ERROR:
#                     return InternalServerError("An Unkown Error Has Occured")
#                 elif responseData is SUPABASE_NO_SUCH_USER_ERROR:
#                     return InternalServerError("User Doesn't Exist")
#                 elif responseData is SUPABASE_USER_ALREADY_VERIFIED:
#                     return "USER ALREADY VERIFIED"
#                 OTP,creationDate=responseData
#                 if currentOTP==OTP and creationDate>dateVerify:    #means old OTP is either expired or absent, and created timestamp is after verification timstamp
#                     print(f"OTP: for {username},{email} is {OTP}")
#                     session["OTP"]=OTP
#                     session["OTP_VALIDITY"]=creationDate+timedelta(minutes=validityPeriod)
#                     session["OTP_RESEND_AFTER"]=creationDate+timedelta(minutes=resendWaitingPeriod)
#                     emailHtmlMessage=render_template("email.html",OTP_CODE=OTP,VALIDITY_PERIOD=f"{validityPeriod}mins")
#                     emailTextOnlyMessage=render_template("email_nonhtml.html",OTP_CODE=OTP,VALIDITY_PERIOD=f"{validityPeriod}mins")
#                     # print(repr(emailMessage))
#                     # sendMail(email,"OTP Verification for Do Drones 2025",emailTextOnlyMessage,emailHtmlMessage)
#                     return emailHtmlMessage
#                 print(
#                     creationDate,"\n",
#                     timedelta(minutes=resendWaitingPeriod),"\n",
#                     datetime.now(),"\n",
#                     creationDate+timedelta(minutes=resendWaitingPeriod),"\n",
#                     creationDate+timedelta(minutes=resendWaitingPeriod)-datetime.now(),"\n",
#                     creationDate+timedelta(minutes=resendWaitingPeriod)<datetime.now(),"\n",
#                 )
#             print(repr(session.get("OTP_RESEND_AFTER")),repr(datetime.now()))
#             return "OTP already generated, please wait for %s seconds before requesting another OTP"%(session.get("OTP_RESEND_AFTER")-datetime.now()).seconds,200
#         return "NOT LOGGED IN",404

emailOTPS={}

@app.route("/api/auth/send-otp",methods=['POST'])
def sendOtpToEmail():
    global emailOTPS
    isSent={"isSent":True}
    notSent=lambda x="Unknown Error":{"isSent":False,"issue":x}
    if request.is_json:
        data = request.json
        email = data.get('email')
        print(email)
        if email is not None:
            if validateEmail(email):
                emailOTPS.setdefault(email,{})
                random.seed(time.time_ns())
                validityPeriod=10#mins
                resendWaitingPeriod=3#mins
                d23=datetime(2023,1,1)
                resendAfter=max(emailOTPS[email].get("OTP_RESEND_AFTER",d23),session.get("OTP_RESEND_AFTER",d23))
                if datetime.now()>resendAfter:
                    OTP=str(random.randint(100000,999999))
                    creationDate=datetime.now()
                    print(f"OTP: for {email} is {OTP}")
                    session["OTP"]=OTP
                    session["OTP_VALIDITY"]=creationDate+timedelta(minutes=validityPeriod)
                    session["OTP_RESEND_AFTER"]=creationDate+timedelta(minutes=resendWaitingPeriod)
                    emailOTPS[email]["OTP"]=session["OTP"]
                    emailOTPS[email]["OTP_VALIDITY"]=session["OTP_VALIDITY"]
                    emailOTPS[email]["OTP_RESEND_AFTER"]=session["OTP_RESEND_AFTER"]
                    emailHtmlMessage=render_template("email.html",OTP_CODE=OTP,VALIDITY_PERIOD=f"{validityPeriod}mins")
                    emailTextOnlyMessage=render_template("email_nonhtml.html",OTP_CODE=OTP,VALIDITY_PERIOD=f"{validityPeriod}mins")
                    print(emailTextOnlyMessage)
                    sendMail(email,"OTP Verification for Do Drones 2025",emailTextOnlyMessage,emailHtmlMessage)
                    return isSent#emailHtmlMessage
                
                print(repr(session.get("OTP_RESEND_AFTER")),repr(datetime.now()))
                return notSent("OTP already generated, please wait for %s seconds before requesting another OTP"%
                        (resendAfter-datetime.now()).seconds)
            return notSent("Invaid Email Format")
        return notSent("No Email given")
    else:
        return jsonify({"error": "Request must be JSON"}), 400

@app.route("/api/auth/verify-otp",methods=['POST'])
def verifyOTP():
    global emailOTPS
    isAuth={'isAuthenticated':True}
    notAuth=lambda x:{'isAuthenticated':False,'issue':x}
    if request.is_json:
        data = request.json
        email = data.get('email')
        otp = data.get('otp')
        if email in emailOTPS:
            cur=datetime.now()
            if cur<emailOTPS[email].get("OTP_VALIDITY",datetime(2100,1,1)):
                if otp==emailOTPS[email].get("OTP"):
                    session.clear()
                    session['name']=email
                    insertUser(email)
                    emailOTPS.pop(email)
                    response=make_response(isAuth)
                    response.set_cookie('sessionExists', 'True', httponly=False) 
                    return response
                return notAuth("OTP invalid")
            return notAuth("OTP expired")
        return notAuth("OTP for this login was not sent to mail")
    return notAuth("not a json")

@app.route("/api/check-auth")
def authCheck():
    isAuth=jsonify({'isAuthenticated':True})
    notAuth=jsonify({'isAuthenticated':False})
    if session.get("name") is None:
        return notAuth
    return isAuth

@app.route("/api/get-user-data",methods=['POST'])
def getData():
    email=session.get('name')
    if(email is not None):
        return getUserData(email)
    return {},400

@app.route("/api/save-profile-data",methods=['POST'])
def saveProfile():
    isSaved={'saved':True}
    notSaved=lambda x='Unkown Error Occured':{'saved':False,'issue':x}
    email= session.get('name')
    if email is not None:
        expectedData={
            "firstName":None,
            "lastName":None,
            "city":None,
            "phoneWhatsApp":None,
            "phoneWork":None,
            "workEmail":None,
            "profilePhoto":None,
            "profilePhotoPreview":None,
            "iiscAffiliated":None,
            "organization":None,
            "department":None,
            "participantType":None,
            "studentLevel":None,#could be none
            "graduationMonth":None,
            "graduationYear":None,
            "designation":None,
            "hearAbout":None,
            "hearAboutOther":None,
            "idCard":None,
            "idCardName":None,
            "shortBio":None,#could be None
            "shareWithParticipants":None,
            "shareWithPartners":None,
        }
        from pprint import pprint
        pprint(request.form)
        for i in expectedData:
            if i in ['idCard','profilePhoto']:
                value=request.files.get(i)
                expectedData[i]=value
            else:
                value=request.form.get(i)
                expectedData[i]=value
        pprint(expectedData)
        file=expectedData['idCard']
        if file and allowedFile(file.filename):
            filename = secure_filename(file.filename)
            fileData = file.read()
            if(len(fileData)>(4*(2**20))):
                return notSaved('ID Card exceeds 4MB!')
            id = upload(filename, fileData)
            expectedData['idCardLink']=id
        file=expectedData['profilePhoto']
        if file and allowedFile(file.filename):
            filename = secure_filename(file.filename)
            fileData = file.read()
            if(len(fileData)>(4*(2**20))):
                return notSaved('Profile Photo exceeds 4MB!')
            id = upload(filename, fileData)
            expectedData['profilePhotoLink']=id
        if upsertParticipantData(email,expectedData) is True:
            return isSaved
        return notSaved('Request not Saved'),400
    return notSaved('user not logged in'),400

if __name__ == '__main__':
    if not isDevelopment:
        from waitress import serve
        serve(app, host="0.0.0.0", port=8000)
    else:
        app.run(host="0.0.0.0", port=8000,debug=True)
