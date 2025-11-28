import os
from flask import Flask, request, redirect, url_for, render_template,session\
    ,send_from_directory,make_response,jsonify
from werkzeug.utils import secure_filename
from werkzeug.exceptions import InternalServerError
from uploader import upload
from dotenv import load_dotenv
from flask_session import Session
from datetime import timedelta,datetime
import re
from supabaseHandler import userExists,insertUser,getUserData,upsertParticipantData\
    ,transactionExists,insertTransaction,completeTransaction,successfulTransaction\
    ,getAllData,getTransactionCount\
    ,SUPABASE_GENERAL_ERROR,SUPABASE_NO_SUCH_USER_ERROR,SUPABASE_USER_ALREADY_VERIFIED
from sendEmail import sendMail
import random
import time
import hashlib
import json
import orderGenerator



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
@app.route("/portal/very-secret-url/registration")
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


REDIRECT_LOG_FILE = "redirect_logs.txt"
CALLBACK_LOG_FILE = "callback_logs.txt"
if not isDevelopment:
    REDIRECT_LOG_FILE="/home/ubuntu/doDrones/"+REDIRECT_LOG_FILE
    CALLBACK_LOG_FILE="/home/ubuntu/doDrones/"+CALLBACK_LOG_FILE
def log_request_details(request,FILENAME=CALLBACK_LOG_FILE):
    """Extracts relevant request details and logs them to a file."""
    timestamp = datetime.now().isoformat()
    log_entry = {
        "timestamp": timestamp,
        "method": request.method,
        "url": request.url,
        "headers": dict(request.headers),
        "remote_addr": request.remote_addr,
        "form_data": dict(request.form),
        "json_data": request.get_json(silent=True),
        "args": dict(request.args),
    }

    # Append the JSON representation of the log entry to the file
    with open(FILENAME, "a") as f:
        f.write(json.dumps(log_entry, indent=4) + "\n---\n")

    print(f"Logged request details to {FILENAME}")

@app.route("/api/txn-callback", methods=["POST"])
def handle_callback():
    """
    Endpoint to receive callback requests.
    It logs all request details and returns a simple success response.
    """
    log_request_details(request,CALLBACK_LOG_FILE)
    data=request.get_json(silent=True)
    completeTransaction(data['o_id'],data['code'],data["trans_ref_no"],data["status_msg"],data["merc_id"],data["signature"])
    if(data["status_msg"]=="SUCCESS"):
        email=successfulTransaction(data['o_id'])
        sendTransactionStatusToEmail(email,"SUCCESS")
    return jsonify({"status": "received", "message": "Request details logged successfully."}), 200

@app.route("/api/txn-redirect", methods=["GET", "POST", "PUT"])
def handle_redirect():
    """
    Endpoint to receive callback requests.
    It logs all request details and returns a simple success response.
    """
    log_request_details(request,REDIRECT_LOG_FILE)
    url="/portal/registration"
    if(request.args.get('o_id')!=None):
        url+="?o_id="+str(request.args.get('o_id'))
    return redirect(url)
    # return jsonify({"status": "received", "message": "Request details logged successfully."}), 200



def sendTransactionStatusToEmail(reciever,status):
    if status=="SUCCESS":
        textMail=render_template("transactionSuccessEmailText.html")
        HTMLMail=render_template("transactionSuccessEmailHTML.html")
        print(reciever)
        print(textMail)
        sendMail(reciever,"You're In — Your Do Drones 2025 Seat Is Confirmed ✨🚀",textMail,HTMLMail)
    ...


@app.route("/api/get-user-payment-data",methods=['POST'])
def generatePaymentDetails():
    email=session.get('name')
    # print("started api")
    if(email is not None):
        # print("user exists")
        import traceback
        try:
            user_data=getUserData(email)
            # print("participant exists",user_data)
            # print("user_data.get('name')!=None",user_data.get('name')!=None )
            # print("user_data.get('participantType') in ['student','faculty','professional']",user_data.get('participantType') in ['student','faculty','professional']   )
            # print("user_data.get('organization')!=None",user_data.get('organization')!=None )
            # print("user_data.get('firstName')!=None",user_data.get('firstName')!=None   )
            # print("user_data.get('delegate_type')!=None",user_data.get('delegate_type')!=None   )
            # print("user_data.get('phoneWhatsApp')!=None",user_data.get('phoneWhatsApp')!=None   )
            # print("user_data.get('hasPaid')!=None",user_data.get('hasPaid')!=None   )
            # print("user_data.get('city')!=None",user_data.get('city')!=None )
            # print("user_data.get('iiscAffiliated')!=None ",user_data.get('iiscAffiliated')!=None    )
            if(
                user_data.get('name')!=None and
                user_data.get('participantType') in ['student','faculty','professional','test','test_tax'] and
                user_data.get('organization')!=None and
                user_data.get('firstName')!=None and
                user_data.get('designation')!=None and
                user_data.get('phoneWhatsApp')!=None and
                user_data.get('hasPaid')!=None and
                user_data.get('city')!=None and
                user_data.get('iiscAffiliated')!=None 
            ):
                # print("user compete")
                taxApplies=user_data.get('iiscAffiliated')!="yes"
                costs={
                    'student':6000,
                    'faculty':9000,
                    'professional':12000,
                    'test':1,
                    'test_tax':6,
                }
                user_data['base_cost']=int(costs[user_data.get('participantType')])
                user_data['tax']=int(user_data['base_cost']*0.18) #18% GST
                if not taxApplies:
                    user_data['tax']=0
                user_data['total_amount']=int(user_data['base_cost']+user_data['tax'])
                transaction_id=0
                max_payments_reached=getTransactionCount()>70
                user_data['max_registrations_reached']=max_payments_reached
                if(user_data['hasPaid']!='true' and not max_payments_reached):
                    transaction_id=insertTransaction(
                        email=email,
                        base_amount=user_data['base_cost'],
                        tax_amount=user_data['tax'],
                        total_amount=user_data['total_amount'],
                        name=user_data['name'],
                        organisation=user_data['organization']
                    )
                    if(transaction_id is SUPABASE_GENERAL_ERROR):
                        return {"issue":"transaction id not generated"},400
                    orderFromData=orderGenerator.generate(
                        orderID=transaction_id,
                        name=user_data['name'],
                        email=email,
                        delegateType=user_data['participantType'],
                        amount=user_data['total_amount']
                    )
                    user_data['json_data']=orderFromData['json_data']
                    user_data['Signature']=orderFromData['Signature']
                user_data['base_cost']=str(user_data['base_cost'])
                user_data['tax']=str(user_data['tax'])
                user_data['total_amount']=str(user_data['total_amount'])
                return user_data
            return {"user_data":user_data,"issue":"Profile not Completed"},400
        except:
            traceback.print_exc()
    return {"issue":"Unkown error has occured"},400


@app.route("/admin_only/summary")
def event_admin_summary():
    rawData=getAllData()
    summary={
        "Income including taxes":0,
        "Income without taxes":0,
        "Student payment count":0,
        "Faculty payment count":0,
        "Professional payment count":0,
        "Total Transactions":0,
        "Successful Transactions":0,
        "Unsuccessful Transactions":0,
        "total users":len(rawData['user']),
        "total participants":len(rawData['participant']),
        "participants":[]
    }
    money_linking={}
    for i in rawData['money']:
        id=i.get("id")
        money_linking[id]=i
        status=i.get("status_msg")
        base_amt=i.get("base_amount")
        total_amt=i.get("total_amount")
        if status is not None:
            summary['Total Transactions']+=1
            if status=="SUCCESS":
                summary['Successful Transactions']+=1
                summary['Income without taxes']+=base_amt
                summary['Income including taxes']+=total_amt
            else:
                summary['Unsuccessful Transactions']+=1
    participant_user_linking={}
    for i in rawData['user']:
        p_id=i.get("participant_id")
        if p_id is not None:
            participant_user_linking[p_id]=i
    
    for i in rawData['participant']:
        id=i.get("id")
        login_email=participant_user_linking[id].get("email")
        work_email=i.get("workEmail")
        first_name=i.get("firstName")
        org=i.get("organization")
        designation=i.get("participantType")
        has_paid=i.get("hasPaid")=='true'
        whatsapp_phone=i.get("phoneWhatsApp")
        work_phone=i.get("phoneWork")
        ddaeid=i.get("ddaeid")
        city=i.get("city")
        txn_id=i.get("transaction_id")
        summary['participants'].append({
            "id":id,
            "login_email":login_email,
            "work_email":work_email,
            "first_name":first_name,
            "org":org,
            "designation":designation,
            "has_paid":has_paid,
            "whatsapp_phone":whatsapp_phone,
            "work_phone":work_phone,
            "ddaeid":ddaeid,
            "city":city,
        })
        if txn_id is not None:
            if designation=='faculty':
                summary['Faculty payment count']+=1
            elif designation=='student':
                summary['Student payment count']+=1
            elif designation=='professional':
                summary['Professional payment count']+=1
    jsonData=json.dumps(summary)
    return render_template('summary.html', db_summary_json=jsonData)

if __name__ == '__main__':
    if not isDevelopment:
        from waitress import serve
        serve(app, host="0.0.0.0", port=8000)
    else:
        app.run(host="0.0.0.0", port=8000,debug=True)
