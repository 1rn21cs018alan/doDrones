import json
import hashlib
import dotenv
import os
dotenv.load_dotenv()
KEY=os.environ.get("IISC_SECRET_KEY")

def sha(txt):
    sha256_hash = hashlib.sha256()
    sha256_hash.update(txt.encode('utf-8'))
    return sha256_hash.hexdigest()

def generate(orderID,name,email,delegateType,amount):#Assuming INR
    global KEY
    o,n,e,d,a=map(str,[orderID,name,email,delegateType,amount])
    concat=o+n+e+d+a+KEY
    hash=sha(concat)
    data={
        "o_id":o,
        "name":n,
        "email":e,
        "delegate_type":d,
        "amount":a,
        "currency":"INR",
        "signature":hash,
    }
    return {"json_data":json.dumps(data),"Signature":hash}


if __name__=="__main__":
    for data in (generate(
        2147480,
        "alan",
        "alanjimcy@gmail.com",
        "TEST",
        1.01
    ),
     generate(
        1234,
        "ttt",
        "t@t.com",
        "AAA",
        1
    )):
        print(f"Signature:{data['Signature']}")
        print("json_data:"+data['json_data'])