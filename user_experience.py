import mail3
import pywhatkit as pwk
import pyautogui
import time

# ph = "+919319846396"
message = "Hello , Your report has been generated and has been sent to your MAIL ."
hour = 23 
minute = 3  


# Example usage
sender_email = "goforharsh2006@gmail.com"
sender_password = ""  # Use App Password if 2FA is enabled
# recipient_email = "raghav24450@iiitd.ac.in"
subject = "Test Email with Attachment"
body = "Hello, this is a test email with an attached document."
attachment_path = r"" # Provide the full path of the file

print("Your report Has been generated . You kan Take out of printer Or we can mail you : ")
k = input("Would you like us to have your mail , so that we can send you the mail of report(Y/N) :")

if (k.lower() == 'y'):
    print("thank you for trusting us ")
    em = input("Enter Your mail : ")
    mail3.send_email(sender_email, sender_password, em, subject, body, attachment_path)
    k = input("Would you like us to have your Phone number , so that You can be updated with upcoming new things in hospital (Y/N) :")
    if (k.lower() == 'y'):
        ph = input("Enter ph :")
        pwk.sendwhatmsg(ph, message, hour, minute) 
        time.sleep(15)  
