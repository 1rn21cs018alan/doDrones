import os
from supabase import create_client, Client
from dotenv import load_dotenv
import bcrypt
import datetime
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

# if __name__ == "__main__":
#     import random
#     import time
#     random.seed(time.time_ns())
#     v = random.randint(100000, 999999)
#     print(v)
