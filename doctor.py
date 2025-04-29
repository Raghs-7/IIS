# command for difining admin username and admin password
'''
export ADMIN_USERNAME="admin"
export ADMIN_PASSWORD="supersecurepassword"

echo 'export ADMIN_USERNAME="admin"' >> ~/.bashrc
echo 'export ADMIN_PASSWORD="supersecurepassword"' >> ~/.bashrc
source ~/.bashrc  # Apply changes

'''

from cryptography.fernet import Fernet
import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import logging
import os
import hashlib
from pprint import pp

MONGO_URI = "" # Replace with your MongoDB URI

# Connect to MongoDB
try:
    myclient = MongoClient(MONGO_URI)
    db = myclient["health_care"]
    doctor_col = db["doctors"]
    col = db["info"]
    logging.info("Connected to MongoDB Atlas successfully!")
except ConnectionFailure as e:
    logging.error(f"MongoDB connection failed: {e}")
    exit()

adkey = db["admin_key"]
# Store this key in an environment variable
def encrypt_data(text):
    results = list(adkey.find({}))
    f = results[0]['key']
    f = Fernet(f)
    message = text.encode("utf-8")
    encMessage = f.encrypt(message)
    return encMessage

def decrypt_data(encMessage):
    results = list(adkey.find({}))
    f = results[0]['key']
    f = Fernet(f)
    decMessage = f.decrypt(encMessage)
    return decMessage.decode('utf-8')

def change_password(username,old_password,new_password):
    user = doctor_col.find_one({"username": username})

    if user:
        stored_password_encrypted = user["pwd"]  # Directly retrieve encrypted password

        # Decrypt stored password
        decrypted_stored_password = decrypt_data(stored_password_encrypted)
        # print(f"Decrypted Stored Password: {decrypted_stored_password}")

        # Compare passwords
        if decrypted_stored_password != old_password:
            print("Invalid username or password!")
            return False
            
    new_hashed_password = encrypt_data(new_password)
    
    # Update the password in the database
    doctor_col.update_one({"username": username}, {"$set": {"pwd": new_hashed_password}})
    print("Password changed successfully!")
    return True



def get_users_by_severity(threshold):
    # Fetch one document to get symptom keys dynamically
    sample_doc = col.find_one({"symptoms": {"$exists": True, "$ne": {}}}, {"symptoms": 1})

    if not sample_doc:
        print("No records found with symptoms.")
        return []

    symptom_keys = list(sample_doc["symptoms"].keys())  # Get all symptom names dynamically

    query = {
        "symptoms": {"$exists": True, "$ne": {}},
        "$or": [{f"symptoms.{symptom}.severity": {"$gt": threshold}} for symptom in symptom_keys]
    }

    users = list(col.find(query, {"_id": 0}))  # Exclude _id field from results

    if not users:
        print(f"No users found with any symptom severity greater than {threshold}")
        return []

    for user in users:
        pp(user)

    return users

def get_patients_by_age(threshold_age):
    results = col.find({"$expr": {"$gt": [{"$toInt": "$demographic.age"}, threshold_age]}},{"_id": 0})

    results_list = list(results)  # Convert cursor to list

    if not results_list:
        print(f"No patients found older than {threshold_age}")
        return []

    for patient in results_list:
        pp(patient)

    return results_list

def login(username, password):
    # Fetch user data from MongoDB
    user = doctor_col.find_one({"username": username})

    if user:
        stored_password_encrypted = user["pwd"]
       # Directly retrieve encrypted password
        # print(f"Stored Encrypted Password from DB: {stored_password_encrypted}")

        # Decrypt stored password
        decrypted_stored_password = decrypt_data(stored_password_encrypted)
        # print(f"Decrypted Stored Password: {decrypted_stored_password}")

        # Compare passwords
        if decrypted_stored_password == password:
            print(f"Login successful for {username}!")
            return True

    print("Invalid username or password!")
    return False

def get_patients_by_symptom(symptom):
    query = {f"symptoms.{symptom}": {"$exists": True}}
    patients = col.find(query, {"_id": 0})  # Remove _id from output

    if not patients:
        "No patients found with this symptom."
        return
    lst = list(patients)
    for idx in range(len(lst)):
        pp(lst[idx])
    return

def doctor2():
    print("Chatbot , Welocmes the Doctor")
    print("First of all , Log into the system")
    while True:
        u = input("Enter username: ")
        p = input("Enter password: ")
        n = login(u,p)
        if n == False:
            print("Please Try again")
            continue
        else:
            oper(u)



def oper(u):
    print(f"Hello {u} , Welcome back !!. what will you like to do today ")
    
    print("1: Get entry by setting a threshold in severity")

    print("2: See entry by setting a threshold in age ")

    print("3: See entry by symptoms ")

    print("4: change password")
    
    print("5: exit")
    k = 0
    while k!= 5:
        k = int(input("Enter a choice"))
        if k == 1:
            x = int(input("Enter a threshold: for severity"))
            get_users_by_severity(x)

        elif k == 2:
            x = int(input("Enter a threshold for age: "))
            get_patients_by_age(x)
        elif k==3:
            x = input("Enter symptom: ")
            get_patients_by_symptom(x)
        elif k ==4:
            use = input("Enter username")
            pw = input("Enter old password")
            nw = input("Enter new password")
            l = change_password(use , pw , nw)
            if l == False:
                print("Try again")
                k = 4
                continue
        elif k == 5:
            break
        elif k!= 1 or k!= 2 or k!= 3 or k != 4 or k!= 5:
            print("Invalid input")
            k  = int(input("Enter a choice"))
        else:
            print("What Next ??")

# doctor2()
