import os
from supabase import create_client, Client
from dotenv import load_dotenv
import bcrypt
import datetime
import random
import time
load_dotenv()
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

class SupabaseError():...
SUPABASE_NO_SUCH_USER_ERROR = SupabaseError()
SUPABASE_USER_ALREADY_VERIFIED = SupabaseError()
SUPABASE_GENERAL_ERROR = SupabaseError()


def testTable():
    response = (
        supabase.table("items")
        .select("*")
        .execute()
    )
    return response


def insertUser(email):
    response = (
        supabase.table("user")
        .upsert({'email': email},on_conflict='email')
    ).execute()
    return response


def getUserId(email):
    try:
        response = (
            supabase.table("user")
            .select("email,id").eq('email', email)
        ).execute()
        if len(response.data) > 0:
            return response.data[0].get("id")
    except:
        pass
    return None


def userExists(email):
    return getUserId(email) is not None

def getUserData(email):
    participantData={
        'name': None,
        'participantType': None,
        'organization': None,
        'firstName': None,
        'email': email,
        'designation': None,
        'studentLevel': None,
        'ddaeId': None,
        'participantCode': None,
        'merchPassCode': None,
        'attendancePercent': None,
        'attendedSessions': None,
        'attendedSessionNames': None,
        'totalSessions': None,
        'connectionCount': None,
        'courseMaterials': None,
        'phoneWhatsApp':None,
        'graduationMonth':None,
        'graduationYear':None,
        # 'courseMaterials.length': None
    }
    na=None#"N/A"
    import traceback
    try:
        # print('flag1')
        response = (
            supabase.table("user")
            .select("email,id,participant_id").eq('email', email)
        ).execute()
        # print('flag2')
        if len(response.data) > 0:
            # print('flag3')
            userID=response.data[0].get("id")
            participant_id=response.data[0].get("participant_id")
            # print('flag4')
            if participant_id is not None:
                response=(
                    supabase.table("participant")
                    .select()
                    .eq("id",participant_id)
                    .execute()
                )
                # print('flag5')
                if len(response.data)>0:
                    # print('flag6')
                    data=response.data[0]
                    participantData['firstName']=data.get('firstName',na)
                    participantData['name']=data.get('firstName',na)+" "+data.get('lastName','')
                    participantData['participantType']=data.get('participantType',na)
                    participantData['organization']=data.get('organization',na)
                    participantData['studentLevel']=data.get('studentLevel',na)
                    participantData['phoneWhatsApp']=data.get('phoneWhatsApp',na)
                    participantData['graduationMonth']=data.get('graduationMonth',na)
                    participantData['graduationYear']=data.get('graduationYear',na)
                    participantData['hasPaid']=data.get('hadPaid',na)
                    participantData['city']=data.get('city',na)
                    participantData['department']=data.get('department',na)
                    participantData['designation']=data.get('designation',na)
                    participantData['firstName']=data.get('firstName',na)
                    participantData['hearAbout']=data.get('hearAbout',na)
                    participantData['hearAboutOther']=data.get('hearAboutOther',na)
                    participantData['idCardLink']=data.get('idCardLink',na)
                    participantData['idCardName']=data.get('idCardName',na)
                    participantData['iiscAffiliated']=data.get('iiscAffiliated',na)
                    participantData['lastName']=data.get('lastName',na)
                    participantData['phoneWork']=data.get('phoneWork',na)
                    participantData['profilePhotoLink']=data.get('profilePhotoLink',na)
                    participantData['profilePhotoPreview']=data.get('profilePhotoPreview',na)
                    participantData['shareWithParticipants']=data.get('shareWithParticipants',na)
                    participantData['shareWithPartners']=data.get('shareWithPartners',na)
                    participantData['shortBio']=data.get('shortBio',na)
                    participantData['workEmail']=data.get('workEmail',na)
                    participantData['hasPaid']=data.get('hasPaid',na)
                    if participantData['hasPaid']=='true' and data.get('transaction_id') is not None:
                        response=(
                            supabase.table("money_transactions")
                            .select()
                            .eq("id",data.get('transaction_id'))
                            .execute()
                        )
                        if len(response.data)>0:
                            transaction_id=response.data[0].get("id")
                            order_id=response.data[0].get("transaction_id")
                            timeStamp=response.data[0].get("completed_at_server_time")
                            if timeStamp!=None:
                                participantData['transaction_datetime']=timeStamp
                            participantData['transaction_id']=transaction_id
                            participantData['order_id']=order_id
                            participantData['ddaeId']=data.get('ddaeid')
                        try:
                            attendence=getAttendence(None,participant_id=participant_id)
                            participantData['attendedSessions']=attendence.get('attended',0)
                            participantData['attendedSessionNames']=attendence.get('names',[])
                            participantData['totalSessions']=attendence.get('total',0)
                        except:...
                                
                # print('flag7')
                
        else:
            raise Exception()
        ...
    except:
        traceback.print_exc()
        ...
    return participantData

def convertTimeStamp(x):
    if type(x) == str:
        return datetime.datetime.strptime(x, "%Y-%m-%dT%H:%M:%S.%f+00:00")
    elif type(x) == datetime.datetime:
        return datetime.datetime.strftime(x, "%Y-%m-%dT%H:%M:%S.%f")[:-1]+"+00:00"

def upsertParticipantData(email,data):
    userID=None,
    participant_id=None
    response = (
        supabase.table("user")
        .select("email,id,participant_id").eq('email', email)
    ).execute()
    if len(response.data) > 0:
        userID=response.data[0].get("id")
        participant_id=response.data[0].get("participant_id")
    if userID is None:
        raise Exception("No such User")
    print(userID,participant_id,'\n',"-"*30)
    if participant_id is None:
        participantResponse=(
            supabase.table("participant")
            .insert({
                'city':data.get('city',''),
                'department':data.get('department',''),
                'designation':data.get('designation',''),
                'firstName':data.get('firstName',''),
                'graduationMonth':data.get('graduationMonth',''),
                'graduationYear':data.get('graduationYear',''),
                'hearAbout':data.get('hearAbout',''),
                'hearAboutOther':data.get('hearAboutOther',''),
                'idCardLink':data.get('idCardLink',''),
                'idCardName':data.get('idCardName',''),
                'iiscAffiliated':data.get('iiscAffiliated',''),
                'lastName':data.get('lastName',''),
                'organization':data.get('organization',''),
                'participantType':data.get('participantType',''),
                'phoneWhatsApp':data.get('phoneWhatsApp',''),
                'phoneWork':data.get('phoneWork',''),
                'profilePhotoLink':data.get('profilePhotoLink',''),
                'profilePhotoPreview':data.get('profilePhotoPreview',''),
                'shareWithParticipants':data.get('shareWithParticipants',''),
                'shareWithPartners':data.get('shareWithPartners',''),
                'shortBio':data.get('shortBio',''),
                'studentLevel':data.get('studentLevel',''),
                'workEmail':data.get('workEmail',''),
                'modifed_on':convertTimeStamp(datetime.datetime.now())
            })
            # .select()
            .execute()
        )
        print(participantResponse)
        if len(participantResponse.data) > 0:
            participant_id=participantResponse.data[0].get("id")
            response3=(
                supabase.table("user")
                .update({"participant_id":participant_id})
                .eq('id',userID)
                .execute()
            )
            return True
    else:
        participantResponse=(
            supabase.table("participant")
            .update({
                'city':data.get('city',''),
                'department':data.get('department',''),
                'designation':data.get('designation',''),
                'firstName':data.get('firstName',''),
                'graduationMonth':data.get('graduationMonth',''),
                'graduationYear':data.get('graduationYear',''),
                'hearAbout':data.get('hearAbout',''),
                'hearAboutOther':data.get('hearAboutOther',''),
                'idCardLink':data.get('idCardLink',''),
                'idCardName':data.get('idCardName',''),
                'iiscAffiliated':data.get('iiscAffiliated',''),
                'lastName':data.get('lastName',''),
                'organization':data.get('organization',''),
                'participantType':data.get('participantType',''),
                'phoneWhatsApp':data.get('phoneWhatsApp',''),
                'phoneWork':data.get('phoneWork',''),
                'profilePhotoLink':data.get('profilePhotoLink',''),
                'profilePhotoPreview':data.get('profilePhotoPreview',''),
                'shareWithParticipants':data.get('shareWithParticipants',''),
                'shareWithPartners':data.get('shareWithPartners',''),
                'shortBio':data.get('shortBio',''),
                'studentLevel':data.get('studentLevel',''),
                'workEmail':data.get('workEmail',''),
            })
            .eq('id',participant_id)
            .execute()
        )
        print("updates")
        if len(participantResponse.data)==1:
            return True
               
    return False
    ...


def insertTransaction(email,base_amount,tax_amount,total_amount,name,organisation):
    import traceback
    try:
        response = (
            supabase.table("user")
            .select("email,id,participant_id").eq('email', email)
        ).execute()
        # print("flag1")
        if len(response.data)>0:
            # print("flag2")
            userID=response.data[0].get("id")
            participant_id=response.data[0].get("participant_id")
            if(participant_id is not None):
                # print("flag3")
                random.seed(time.time_ns())
                rand_val=random.randint(100000,999999)
                while transactionExists(rand_val):
                    rand_val=random.randint(100000,999999)
                    # print("flag4",rand_val)
                # print("flag5")
                response = (
                    supabase.table("money_transactions")
                    .insert({
                        "transaction_id":rand_val,
                        "participant_id":participant_id,
                        "user_id":userID,
                        "base_amount":base_amount,
                        "tax_amount":tax_amount,
                        "total_amount":total_amount,
                        "name":name,
                        "organization":organisation,
                        "hasCompleted":False,
                        "started_at_server_time":convertTimeStamp(datetime.datetime.now())
                    })
                    .execute()
                )
                # print("flag6")
                if len(response.data)==1:
                    # print("flag7")
                    return rand_val
                ...
    except Exception as e:
        traceback.print_exc()
    return SUPABASE_GENERAL_ERROR

def transactionExists(txnId):
    try:
        response = (
            supabase.table("money_transactions")
            .select()
            .eq('transaction_id', txnId)
        ).execute()
        if response.data[0] is not None:
            return True
    except:
        return False

def completeTransaction(txnId,txn_code,trans_ref_no,status_msg,merc_id,signature):
    try:
        response = (
            supabase.table("money_transactions")
            .update({
                "txn_code":txn_code,
                "trans_ref_no":trans_ref_no,
                "status_msg":status_msg,
                "merc_id":merc_id,
                "signature":signature,
                "hasCompleted":True
            })
            .eq('transaction_id', txnId)
        ).execute()
        if response.data[0] is not None:
            return True
    except:
        return False

def successfulTransaction(txnId):
    try:
        response = (
            supabase.table("money_transactions")
            .update({"completed_at_server_time":convertTimeStamp(datetime.datetime.now())})
            .eq('transaction_id', txnId)
        ).execute()
        if len(response.data)==1:
            recordID=response.data[0].get('id')
            userID=response.data[0].get('user_id')
            participantID=response.data[0].get('participant_id')
            if participantID is not None:
                response2=(
                    supabase.table("participant")
                    .select(count='exact',head=True)
                    .neq('ddaeid',None)
                    .execute()
                )
                nextDdaeIdNo=response2.count+1
                DdaeId="DDAE25%03d"%nextDdaeIdNo
                response3=(
                    supabase.table("participant")
                    .update({"hasPaid":"true","transaction_id":recordID,"ddaeid":DdaeId})
                    .eq('id',participantID)
                    .execute()
                )
                response4=(
                    supabase.table("user")
                    .select()
                    .eq('id',userID)
                    .execute()
                )
                return response4.data[0].get("email")
            return True
        # else:
        #     print(response)
    except:
        return False

def findUserbyOrderId(txnId):
    response = (
        supabase.table("participant")
        .select('money_transactions(id,transaction_id)')
        .eq("money_transactions.transaction_id", txnId)
    ).execute()
    return response.data

    ...

def getAllData():
    participantResponse=(
        supabase.table("participant")
        .select()
        .execute()
    )
    userResponse=(
        supabase.table("user")
        .select()
        .execute()
    )
    moneyResponse=(
        supabase.table("money_transactions")
        .select()
        .execute()
    )
    return {
        "participant":participantResponse.data,
        "user":userResponse.data,
        "money":moneyResponse.data
    }
    ...

def getTransactionCount():
    response=(
        supabase.table("money_transactions")
        .select(count='exact',head=True)
        .eq("status_msg","SUCCESS")
        .execute()
    )
    return response.count

def getUserDataByDDAEID(id):
    participantData={
        'organization': None,
        'firstName': None,
        'lastName': None,
        'ddaeId': None,
        'shortBio': None,
        # 'courseMaterials.length': None
    }
    na=None#"N/A"
    import traceback
    try:
        # print('flag1')
        response = (
            supabase.table("participant")
            .select("").eq('ddaeid',id)
        ).execute()
        # print('flag2')
        if len(response.data) > 0:
            data=response.data[0]
            participantData['firstName']=data.get('firstName',na)
            participantData['name']=data.get('firstName',na)+" "+data.get('lastName','')
            participantData['participantType']=data.get('participantType',na)
            participantData['organization']=data.get('organization',na)
            participantData['studentLevel']=data.get('studentLevel',na)
            participantData['phoneWhatsApp']=data.get('phoneWhatsApp',na)
            participantData['graduationMonth']=data.get('graduationMonth',na)
            participantData['graduationYear']=data.get('graduationYear',na)
            participantData['hasPaid']=data.get('hadPaid',na)
            participantData['city']=data.get('city',na)
            participantData['department']=data.get('department',na)
            participantData['designation']=data.get('designation',na)
            participantData['firstName']=data.get('firstName',na)
            participantData['hearAbout']=data.get('hearAbout',na)
            participantData['hearAboutOther']=data.get('hearAboutOther',na)
            participantData['idCardLink']=data.get('idCardLink',na)
            participantData['idCardName']=data.get('idCardName',na)
            participantData['iiscAffiliated']=data.get('iiscAffiliated',na)
            participantData['lastName']=data.get('lastName',na)
            participantData['phoneWork']=data.get('phoneWork',na)
            participantData['profilePhotoLink']=data.get('profilePhotoLink',na)
            participantData['profilePhotoPreview']=data.get('profilePhotoPreview',na)
            participantData['shareWithParticipants']=data.get('shareWithParticipants',na)
            participantData['shareWithPartners']=data.get('shareWithPartners',na)
            participantData['shortBio']=data.get('shortBio',na)
            participantData['workEmail']=data.get('workEmail',na)
            participantData['hasPaid']=data.get('hasPaid',na)
            if participantData['hasPaid']=='true' and data.get('transaction_id') is not None:
                response=(
                    supabase.table("money_transactions")
                    .select()
                    .eq("id",data.get('transaction_id'))
                    .execute()
                )
                if len(response.data)>0:
                    transaction_id=response.data[0].get("id")
                    order_id=response.data[0].get("transaction_id")
                    timeStamp=response.data[0].get("completed_at_server_time")
                    if timeStamp!=None:
                        participantData['transaction_datetime']=timeStamp
                    participantData['transaction_id']=transaction_id
                    participantData['order_id']=order_id
                    participantData['ddaeId']=data.get('ddaeid')                
        else:
            raise Exception()
        ...
    except:
        traceback.print_exc()
        ...
    return participantData
    
def insertAttendenceLog(*,ddaeid,scannerEmail,className):
    response=(
        supabase.table("participant")
        .select()
        .eq("ddaeid",ddaeid)
        .execute()
    )
    print(response,ddaeid)
    if len(response.data)>0:
        dt=convertTimeStamp(datetime.datetime.now())
        data=response.data[0]
        id=data.get("id")
        name=data.get("firstName")+" "+data.get("lastName")
        insertResponse=(
            supabase.table("attendence_logs")
            .insert({
                "participant_id":id,
                "participant_name":name,
                "class_name":className,
                "scanning_staff_email":scannerEmail
            })
            .execute()
        )
        return name
        # print(insertResponse)
    
def getAttendence(email,*,participant_id=None):
    class temp:
        def __init__(self,pid):
            self.data=[{"participant_id":pid}]
    response=temp(participant_id)
    if participant_id is None:
        response=(
            supabase.table("user")
            .select()
            .eq("email",email)
            .execute()
        )
    if len(response.data)>0:
        pid=response.data[0].get("participant_id")
        classes=[
            "Day 1: Inauguration",
            "Day 1: Theory 1- Introduction to UAVs",
            "Day 1: Theory 2- Aerodynamics & Design -1",
            "Day 1: Theory 3- Structures & Analysis -1",
            "Day 1: Guest Lecture 1",
            "Day 1: Theory 4- Avionics -1",
            "Day 1: Theory 5- Propulsion -1",

            "Day 2: Theory 6- Avionics -2",
            "Day 2: Theory 7- Autopilot and Control Systems -1",
            "Day 2: Theory 8- Aerodynamics and Fixed Wing Design -2",
            "Day 2: Theory 9- Drone Building Methodology",
            "Day 2: Practical 1",

            "Day 3: Theory 10- Autopilot and Control Systems -2",
            "Day 3: Theory 11- Structures & Analysis -2",
            "Day 3: Theory 12- Propulsion -2",
            "Day 3: Theory 13- Ground Control",
            "Day 3: Practical 2",

            "Day 4: Guest Lecture 2",
            "Day 4: Theory 14- Computer Vision and ROS",
            "Day 4: Guest Lecture 3",
            "Day 4: Guest Lecture 4",
            "Day 4: Practical 3",

            "Day 5: Flight Operations and Demonstrations",
            "Day 5: Guest Lecture 5",
            "Day 5: Panel Discussion",
            "Day 5: Valedictory",
        ]
        checklist={i:False for i in classes}
        import traceback
        try:
            response=(
                supabase.table("attendence_logs")
                .select()
                .eq("participant_id",pid)
                .execute()
            )
            for i in response.data:
                cn=i.get("class_name")
                if cn in checklist:
                    checklist[cn]=True
                else:
                    print("Found Invalid classname",cn)
            # checklist["Day 1: Inauguration"]=True
            # checklist["Day 1: Theory 1- Introduction to UAVs"]=True
            # checklist["Day 1: Theory 2- Aerodynamics & Design -1"]=True
            # checklist["Day 1: Theory 3- Structures & Analysis -1"]=True
            # checklist["Day 1: Guest Lecture 1"]=True
            # checklist["Day 1: Theory 4- Avionics -1"]=True
            # checklist["Day 1: Theory 5- Propulsion -1"]=True
        except:
            traceback.print_exc()
            ...
        return {"attended":sum(checklist.values()),"total":len(checklist),"names":[i for i in checklist if i]}
    return {"total":0,"attended":0}
    
    
    
if __name__ == "__main__":
    # import random
    import time
    # print(getTransactionCount())
    # print(findUserbyOrderId(700980))
    print(getAttendence("test@gmail.com"))
    # print(successfulTransaction(804376))
    # random.seed(time.time_ns())
    # v = random.randint(100000, 999999)
    # print(v)
    # print(completeTransaction(
    #     573785,
    #     "SPG-0000",
    #     "UPIINTENTed03c79dcdab4200200785",
    #     "SUCCESS",
    #     "CONF_FC_5737851764163563156",
    #     "682fa99c3aa6ddd6fbbdf6805f1553690bde2b2d0cfa3fb2a17e9ba7b19a6312"))
