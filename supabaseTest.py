import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)
response = (
    supabase.table("items")
    .select("*")
    .execute()
)
print(response)

from supabaseHandler import insertUser,verifyUser
from postgrest.exceptions import APIError
try:
    print(insertUser("testuser41","pass1wwer","alal@lalal.alala"))
except APIError as e:
    print("insert failed")
print(verifyUser("testuser1","pass1wwer1"))
print(verifyUser("testuser1","pass1wwer"))