from supabaseHandler import getAllData
import csv
import os
inSameFolder=lambda x:os.path.join(os.path.dirname(__file__),x)
def findUnpaid(ignoreUninterested=False):
    rawData=getAllData()
    filteredData=[]
    for i in rawData['participant']:
        if i['hasPaid']!='true' and (ignoreUninterested or not i['not_interested']):
            filteredData.append({
                'firstName':i['firstName'],
                'lastName':i['lastName'],
                'organization':i['organization'],
                'phoneWhatsApp':i['phoneWhatsApp'],
                'phoneWork':i['phoneWork'],
            })
    return filteredData
    
def saveListOfDictAsCsv(d,*,fileName="unpaidData.csv"):
    if len(d)>0:
        for i in range(len(d)):
            d[i]={'#':i+1,**d[i]}
        headers=d[0].keys()
        # data=[
        #     i.values() for i in d
        # ]
        with open(inSameFolder(fileName),"w",newline='') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(d)
            
    ...
if __name__=="__main__":
    saveListOfDictAsCsv(findUnpaid())