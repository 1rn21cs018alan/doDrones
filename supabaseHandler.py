import os
from supabase import create_client, Client
from dotenv import load_dotenv
import bcrypt
load_dotenv()
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def testTable():
    response = (
    supabase.table("items")
    .select("*")
    .execute()
    )
    return response

def passwordHash(x:str):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(x.encode(), salt)
    return hashed_password.decode()    

def insertUser(username,password,email):
    password=passwordHash(password)
    response=(
    supabase.table("user")
    .insert({'username':username,'password':password,'email':email})
    ).execute()
    return response


def verifyUser(username,password):
    # password=passwordHash(password)
    response=(
    supabase.table("user")
    .select("password").eq('username',username)
    ).execute()
    try:
        hashedPass=response.data[0].get('password')
        return((bcrypt.checkpw(password.encode(),hashedPass.encode())))
    except:
        return False
    
def userExists(username):
    # password=passwordHash(password)
    try:
        response=(
        supabase.table("user")
        .select("username").eq('username',username)
        ).execute()
        return len(response.data)!=0
    except:
        return None