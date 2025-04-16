from cryptography.fernet import Fernet
import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import logging
import base64
import getpass
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from pprint import pp
import os
from fpdf import FPDF
import mail3

# Example usage
sender_email = "goforharsh2006@gmail.com"
sender_password = ""  # Use App Password if 2FA is enabled
recipient_email = "raghav24450@iiitd.ac.in"
subject = "Test Email with Attachment"
body = "Hello, this is a test email with an attached document."
attachment_path = r"C:\Users\msnvi\Desktop\MY_PROGRAMS\patient_report2.pdf" # Provide the full path of the file



salt = b'\\xd9\\xd3\\nnw\\x86\\xbc^\\xd1d\\x825\\x03D\\x9fy'

def derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=390000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

MONGO_URI = "mongodb+srv://raghav24450:iiitd@cluster0.h3b86.mongodb.net/"

try:
    myclient = MongoClient(MONGO_URI)
    db = myclient["health_care"]  # Use your new database instead of 'admin'
    secure_col = db["admin_secure"]
    doctor_set = db["doctors"]
    col = db["info"]
    adkey = db["admin_key"]
    logging.info("Connected to MongoDB Atlas successfully!")
except ConnectionFailure as e:
    logging.error(f"MongoDB connection failed: {e}")
    exit()


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


def signup(username, password):
    results = list(secure_col.find({}))
    if not results:
        pass
    else:
        print("There only be one admin at a time .")
        return False

    user_data = {
        "username": username,
        "pwd": password
    }
    k = input("Enter a secure key whcih will decide to encrypt:")
    key = derive_key(k, salt)
    global f
    f = Fernet(key)
    print(f)

    data = {"key" : key}
    adkey.insert_one(data)
    
    user_data["pwd"] = encrypt_data(user_data["pwd"])
    print(decrypt_data(user_data["pwd"]))

    # Insert user into collection
    secure_col.delete_many({})

    secure_col.insert_one(user_data)
    print(f"User {username} signed up successfully!")
    return True

def login(username, password):
    # Fetch user data from MongoDB
    user = secure_col.find_one({"username": username})

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

def signupofdoctor(username, password):
    # results = list(secure_col.find({}))
    # print("username of same doctors erro genetartee")
    while(True):
        if doctor_set.find_one({"username": username}):
            print("Username already exists!")
            username = input("Enter another username ")
            return False
        else:
            break 
    user_data = {
        "username": username,
        "pwd": password,
        
    }
    user_data["pwd"] = encrypt_data(user_data["pwd"])
    
    doctor_set.insert_one(user_data)
    print(f"Doctor {username} signed up successfully!")
    return True



def admin2():
    print("Chatbot , Welcomes the admin")
    print("what you will like to do ? ")
    print("1: Sign up")
    print("2: Log in")

    k = int(input("Enter option : "))
    st = 3
    while (True):
        if k == 1:
            results = list(secure_col.find({}))
            if results:
                print("There can only be one admin . exiting the chatbot")
                exit()
            u = input("Enter username: ")
            p = input("Enter password: ")
            cp = input("Confirm password : ")
            while p!=cp:
                print("password and confirm password do not match")
                p = input("Enter password: ")
                cp = input("Confirm password : ")

            l = signup(u,p)
            if l == False:
                "Admin is already assigned . Proceed to Log in "
                k = 2
                continue
            else:
                k =2 
                continue
        elif k == 2:
            u = input("Enter username: ")
            p = input("Enter password: ")
            k  = login(u,p)
            if k == False:
                while(st!= 0 or k == True):
                    print("You have 3 more chances left else all data will be deleted dur to privacy reasons")
                    u = input("Enter username: ")
                    p = input("Enter password: ")
                    k  = login(u,p)
                    st = st-1
                if st == 0:
                    print("delteing all entries and closing the chatbot")
                    exit()
                else:
                    operations(u)
                    break
            else:
                operations(u)
                break
        else:
            print('valid option number ')
            k = int(input("enter choice"))


def find_entry_by_name(name):
    results = []
    lst = list(col.find({}))
    for idx in range(len(lst)):
        if decrypt_data(lst[idx]["demographic"]["name"]) == name:
            results.append(lst[idx])
    
    # results = list(col.find({"demographic.name": decrypt_data(name)}))
    if not results:
        print("No records found for the given name.")
        return
    elif len(results) == 1:
        pp(results)
        # col.delete_one({"_id": results[0]["_id"]})
        # print("Entry deleted successfully.")
    else:
        print("Multiple entries found:")
        for i, record in enumerate(results):
            print(f"{i + 1}: {record}")

def delete_all_entries():
    collection = db.info
    result = collection.delete_many({})
    print(f"Deleted {result.deleted_count} entries from the collection.")

def delete_entry_by_name(name):
    results = []
    lst = list(col.find({}))
    for idx in range(len(lst)):
        if decrypt_data(lst[idx]["demographic"]["name"]) == name:
            results.append(lst[idx])
    
    if not results:
        print("No records found for the given name.")
        return
    elif len(results) == 1:
        col.delete_one({"_id": results[0]["_id"]})
        print("Entry deleted successfully.")
    else:
        print("Multiple entries found:")
        for i, record in enumerate(results):
            print(f"{i + 1}: {record}")
        choice = int(input("Enter the number of the entry you want to delete: "))
        if 1 <= choice <= len(results):
            col.delete_one({"_id": results[choice - 1]["_id"]})
            print("Selected entry deleted successfully.")
        else:
            print("Invalid selection.")

def allentries_patient():
    results = list(col.find({}, {"_id": 0}))
    for idx in range(len(results)):
        results[idx]["demographic"]["name"] =  decrypt_data(results[idx]["demographic"]["name"]) 
        results[idx]["demographic"]["contact"] =  decrypt_data(results[idx]["demographic"]["contact"]) 
    for element in results:
        pp(element)

## doctor
def doctor_info():
    results = list(doctor_set.find({}, {"_id": 0,"pwd": 0}))
    for element in results:
        pp(element)

def get_patients_by_severity(threshold):
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

    for idx in range(len(users)):
        users[idx]["demographic"]["name"] =  decrypt_data(users[idx]["demographic"]["name"]) 
        users[idx]["demographic"]["contact"] =  decrypt_data(users[idx]["demographic"]["contact"]) 

    if not users:
        print(f"No users found with any symptom severity greater than {threshold}")
        return []

    for user in users:
        pp(user)

    return users


def get_patients_by_symptom(symptom):
    query = {f"symptoms.{symptom}": {"$exists": True}}
    patients = col.find(query, {"_id": 0})  # Remove _id from output
    patients = list(patients)

    for idx in range(len(list(patients))):
        patients[idx]["demographic"]["name"] =  decrypt_data(patients[idx]["demographic"]["name"]) 
        patients[idx]["demographic"]["contact"] =  decrypt_data(patients[idx]["demographic"]["contact"]) 

    if not patients:
        "No patients found with this symptom."
        return
    lst = list(patients)
    for idx in range(len(lst)):
        pp(lst[idx])
    return

def generate_report(dic, filename="patient_report.pdf"):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Title
    pdf.set_font("Arial", style='B', size=18)
    pdf.cell(200, 10, "PATIENT SCREENING REPORT", ln=True, align='C')
    pdf.ln(10)  

    # Patient Details Section
    pdf.set_font("Arial", style='B', size=14)
    pdf.cell(190, 10, "Patient Details", ln=True, border='B')
    pdf.set_font("Arial", size=12)
    pdf.ln(5)  

    # Create a table for patient details
    col_width = 95  
    row_height = 10 
    for key, value in dic["demographic"].items():
        pdf.cell(col_width, row_height, key.capitalize(), border=1)
        pdf.cell(col_width, row_height, str(value), border=1, ln=True)
    pdf.ln(10)    

    # Symptoms Summary Section
    pdf.set_font("Arial", style='B', size=14)
    pdf.cell(190, 10, "Symptoms Summary", ln=True, border='B')
    pdf.set_font("Arial", size=12)
    pdf.ln(5)  

    # Define column widths for the symptoms table
    col_widths = [40, 30, 30, 40, 50]  
    headers = ["Symptom", "Frequency", "Severity", "Duration", "Additional Notes"]
    row_height = 10

    # Add table headers
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], row_height, header, border=1, align='C')
    pdf.ln(row_height)

    # Add symptom data rows
    for symptom, details in dic["symptoms"].items():
        pdf.cell(col_widths[0], row_height, symptom, border=1)
        pdf.cell(col_widths[1], row_height, details.get("frequency", " "), border=1)
        pdf.cell(col_widths[2], row_height, details.get("severty" , " "), border=1)
        pdf.cell(col_widths[3], row_height, details.get("duration" , " "), border=1)
        pdf.cell(col_widths[4], row_height, details.get("addnote" , " ") , border=1, ln=True)
    
    pdf.ln(5)

    pdf.output(filename)
    print(f"Patient report successfully saved as {filename}.")


def get_patients_by_age(threshold_age):
    results = col.find({"$expr": {"$gt": [{"$toInt": "$demographic.age"}, threshold_age]}},{"_id": 0})

    results = list(results)  # Convert cursor to list
    for idx in range(len(results)):
        results[idx]["demographic"]["name"] =  decrypt_data(results[idx]["demographic"]["name"]) 
        results[idx]["demographic"]["contact"] =  decrypt_data(results[idx]["demographic"]["contact"]) 

    if not results:
        print(f"No patients found older than {threshold_age}")
        return []

    for patient in results:
        pp(patient)

def operations(u):
    print(f"Hello {u} , Welcome back !!. what will you like to do today ")
    print("1: Store the information of doctor ")
    print("2: See all the Entries ")
    print("3: See the Entry by Name")
    print("4: Get entry by setting a threshold in severity")
    print("5: See entry by setting a threshold in age ")
    print("6: See all the entries with filter of symptom")
    print("7: Print all doctors ")
    print("8: Delete entry by name")
    print("9: delete all entries")
    print("10: Sent a e-mail of report  ")
    print("11: exit")
    k = 0
    # k= int(input("Enter option"))
    while k != 11:
        k= int(input("Enter option: "))
        if k == 1:
            user = input("Enter username: ")
            passs = input("Enter password: ")
            signupofdoctor(user , passs)
        elif k ==2:
            allentries_patient()
        elif k == 3:
            name = input("Enter name ")
            find_entry_by_name(name)
        elif k== 4:
            th = int(input("Enter threshold : "))
            
            get_patients_by_severity(th)
        elif k == 5:
            ag = int(input("Enter age: "))
            get_patients_by_age(ag)
        elif k ==6:
            n = input("Enter symptoms ")
            get_patients_by_symptom(n)
        elif k == 7:
            doctor_info()
        elif k == 8:
            name = input("Enter name: ")
            delete_entry_by_name(name)
        elif k ==9:
            delete_all_entries()
        elif k ==10 :
            mail3.send_email(sender_email, sender_password, recipient_email, subject, body, attachment_path)
        elif k== 11:
            break


        
# admin2()


# signup("harsh" , "1234")
