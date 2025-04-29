import regex as re
from pynput import keyboard
import speech_recognition as sr
from pydub import AudioSegment
from word2number import w2n  
from fpdf import FPDF
import pyaudio
import wave
from cryptography.fernet import Fernet
import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import logging
import symptoms
import admin
import doctor
import pyttsx3

from deep_translator import GoogleTranslator
from gtts import gTTS
import pygame
import time

MONGO_URI = "" # Replace with your MongoDB URI

#text to speech setup
text_to_speech_engine = pyttsx3.init()

try:
    myclient = MongoClient(MONGO_URI)
    db = myclient["health_care"]  # Use your new database instead of 'admin'
    col = db["info"]
    sk = db["admin_key"]
    logging.info("Connected to MongoDB Atlas successfully!")
except ConnectionFailure as e:
    logging.error(f"MongoDB connection failed: {e}")
    exit()

def on_press(key):
    if key == keyboard.Key.enter:
        global stop
        stop = True

def encrypt_data(text):
    results = list(sk.find({}))
    f = results[0]['key']
    f = Fernet(f)
    message = text.encode("utf-8")
    encMessage = f.encrypt(message)
    return encMessage

def decrypt_data(encMessage):
    results = list(sk.find({}))
    f = results[0]['key']
    f = Fernet(f)
    decMessage = f.decrypt(encMessage)
    return decMessage.decode('utf-8')

def store_info(data):
    data["demographic"]["name"] = encrypt_data(data["demographic"]["name"])
    data["demographic"]["contact"] = encrypt_data(data["demographic"]["contact"])
    if db is not None:
        try:
            col.insert_one(data)
            logging.info("Data inserted successfully!")
        except Exception as e:
            logging.error(f"Error inserting data: {e}")
    else :
        give_output("error! while store info ")

stop = False
global tv
tv = 0

# def stop_recording():
#     global stop
#     stop = True
    



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
        pdf.cell(col_widths[2], row_height, str(details.get("severity" , " ")), border=1)
        pdf.cell(col_widths[3], row_height, details.get("duration" , " "), border=1)
        pdf.cell(col_widths[4], row_height, details.get("addnote" , " ") , border=1, ln=True)
    
    pdf.ln(5)

    pdf.output(filename)
    give_output(f"Patient report successfully saved as {filename}.")

# def record_audio(filename="user_voice.wav", duration=5, sample_rate=44100):
#     give_output("Recording... Press 'enter' to stop early.")    
#     audio = sd.rec(int(sample_rate * duration), samplerate=sample_rate, channels=2, dtype=np.int16)
#     listener = keyboard.Listener(on_press=on_press)
#     listener.start()
#     stop_recording = False
#     for _ in range(duration * 10): 
#         if stop:  
#             stop_recording = True
#             break
#         sd.sleep(100)  
#     if stop_recording:
#         give_output("Stopping recording early...")
#         sd.stop()  
#         audio = audio[:int(sample_rate * (_ / 10)), :]  
#     sd.wait()  
#     sf.write(filename, audio, sample_rate)

def record_audio(filename="user_voice.wav", duration=10, sample_rate=16000):
    chunk = 1024
    format = pyaudio.paInt16
    channels = 1
    global stop
    p = pyaudio.PyAudio()

    stream = p.open(format=format,
                    channels=channels,
                    rate=sample_rate,
                    input=True,
                    frames_per_buffer=chunk)

    print("Recording... Press 'enter' to stop early.")
    listener = keyboard.Listener(on_press=on_press)
    frames = []
    listener.start()
    for _ in range(0, int(sample_rate / chunk * duration)):
        data = stream.read(chunk)
        frames.append(data)
        if stop:
            break
    stop = False
    give_output("Recording stopped.")
    stream.stop_stream()
    stream.close()
    p.terminate()
    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(format))
    wf.setframerate(sample_rate)
    wf.writeframes(b''.join(frames))
    wf.close()
    give_output(f"Recording saved as {filename}")


def text_from_audio():
    audio = AudioSegment.from_wav("user_voice.wav")
    audio.export("temp.wav", format="wav")

    recognizer = sr.Recognizer()
    c = 0
    with sr.AudioFile("temp.wav") as source:
        audio_data = recognizer.record(source)
    text = ''
    try:
        text = recognizer.recognize_google(audio_data)
        give_output("Patient : " + text)
    except sr.UnknownValueError:
        c = 1
        # give_output("error")
        # give_output("Google Web Speech API could not understand the audio")
    except sr.RequestError as e:
        c = 1
        # give_output(f"Could not request results from Google Web Speech API; {e}")
    return text , c


def extract_valid_duration(sentence):

    pattern = r'(\b\d+\b|\b(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|' \
              r'sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred)\b)\s+' \
              r'(hours?|weeks?|days?|months?|years?)'
    
    matches = re.findall(pattern, sentence, re.IGNORECASE)
    extracted_numbers = []
    for num, _ in matches:
        try:
            extracted_numbers.append(num+" "+_ if num.isdigit() else str(w2n.word_to_num(num.lower()))+" "+_)
        except ValueError:
            return []
            
    return extracted_numbers[0]

def ask_for_valid_duration():
    while True:
        give_output("chatbot: Could you repeat that? Please tell the duration in hours,weeks , days, months, or years. ")
        # record_audio(duration=4)
        # duration,d = text_from_audio()
        duration = get_input(tv , 'duration ')
        # duration = input("chatbot: Could you repeat that? Please input the duration in hours, days, months, or years.\nPatient: ")
        extracted_duration = extract_valid_duration(duration)
        if extracted_duration:
            return extracted_duration

def valid_severity(severity):
    # severity = severity if severity.isdigit() else str(w2n.word_to_num(severity.lower()))
    k  = severity.split(" ")
    l = k.index('out')
    i = k[l-1]
    d = { "one" : 1, "two" : 2 , "three" : 3 , "four" : 4 , "five" : 5 , "six" :6, "seven ":  7, "eight" : 8 , "nine" : 9 , 'ten' :10}
    if i in d:
        i = d[i]
    return int(i)
    # return severity.isdigit() and 1 <= int(severity) <= 10

def ask_for_valid_severity():
    while True:
        give_output("chatbot: Could you repeat that? How severe it feels on a scale of 1-10?  (3 out of 10 , 7 out of 10 )  ")
        # record_audio(duration=10)
        # severity ,d= text_from_audio()
        severity = get_input(tv , 'severity')
        if valid_severity(severity) not in [1 ,2,3,4,5,6,7,8,9,10]:
                ask_for_valid_severity()
        # severity = input("chatbot: Could you repeat that? How severe it feels on a scale of 1-10?\nPatient: ")
        else:
            return valid_severity(severity)

def valid_freq(txt):
    valid_freq = ['rare' , 'often' , 'constantly' , 'rarely' , 'oftenly' , 'frequently' , 'occasionally']   
    # txt = txt.split(' ')
    ans = []
    for i in valid_freq:
        if i in txt.lower():
            ans.append(i)
    return ans

def ask_for_valid_freq(i):
    while True:
        give_output(f'chatbot: Could you repeat that? How frequently do you feel {i} (Rare/Often/Constantly , occasionally)?')
        # record_audio(duration=4)
        # freq,d = text_from_audio()
        freq = get_input(tv , 'frequency')
        if valid_freq(freq):
                k = valid_freq(freq)
                return k[0]
    

# def get_input(duration = 10):
#     record_audio(duration= duration)
#     global stop
#     stop = False
#     return text_from_audio()[0]   

def get_input(tv:int, d:str ,duration = 10) -> str:
    if tv ==0:
        t = input("Patient: ")
    else:
        record_audio(duration= duration)
        global stop
        stop = False
        t,c = text_from_audio()
        while c!=0:
            give_output(f"Sorry , I think there is some problem with mic or some background noise , could you please rephrase it or repeat it \n or would you like to switch to text?")
            record_audio(duration= duration)

            stop = False
            t,c = text_from_audio()

    t = translate_text(t, 'auto', 'en')
    print(f"translated text - {t}")
    return t



languages = {
    "1": {"code": "en", "name": "English"},
    "2": {"code": "hi", "name": "Hindi"},
    "3": {"code": "fr", "name": "French"},
    "4": {"code": "es", "name": "Spanish"},
    "5": {"code": "de", "name": "German"}
}

global target_lang

def select_language():
    print("\nSelect a language:")
    for key, lang in languages.items():
        print(f"{key}: {lang['name']}")
    while True:
        choice = input("Enter the number of your preferred language: ").strip()
        if choice in languages:
            return languages[choice]
        print("Invalid choice. Please try again.")

def translate_text(text, source_lang, target_lang):
    try:
        if source_lang == target_lang:
            return text
        return GoogleTranslator(source=source_lang, target=target_lang).translate(text)
    except Exception as e:
        print(f"Translation error: {e}")
        return text

def text_to_speech(text, lang_code):
    try:
        tts = gTTS(text=text, lang=lang_code)
        tts.save("response.mp3")
        pygame.mixer.init()
        pygame.mixer.music.load("response.mp3")
        pygame.mixer.music.play()
       
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        pygame.mixer.music.unload()
        os.remove("response.mp3")
    except Exception as e:
        print(f"TTS Error: {e}")


def give_output(output : str) -> None:
    # print( f"english - {output}")
    output = translate_text(output, "en", target_lang['code'])
    print(output)
    if tv:
        text_to_speech(output.lstrip("CHATBOT:"), target_lang['code'])
    # voices = text_to_speech_engine.getProperty('voices')
    # text_to_speech_engine.setProperty('voice', voices[87].id)
    # text_to_speech_engine.say(output.lstrip("CHATBOT:"))
    # text_to_speech_engine.runAndWait()

def get_symptoms(sentence):
    result = symptoms.main(sentence, input_method= lambda x: get_input(tv = tv, d = "symptoms"), output_method= give_output)
    return result

nested_dict = {'symptoms' : {}}
def chatbot():
    symptoms = []

    while True:
        give_output("Please describe your symptoms")
        sentence = get_input(tv , 'symptoms')
        symptoms = get_symptoms(sentence)
        if not symptoms:
            give_output("I see some ambiguity response . Please descibe in detail . ")
        else:
            for i in symptoms:
                global nested_dict
            #   if(nested_dict.get('symptoms'[i]) == None):
                nested_dict['symptoms'][i] = {"severity": "", "duration": "", "frequency": "" , }

                give_output(f'chatbot: How long have you been experiencing {i}? (Please tell duration in hours,weeks,days, months, or years.)')
                # record_audio(duration=10)
                # duration ,d= text_from_audio()
                duration = get_input(tv , 'duration ')
                extracted_duration = extract_valid_duration(duration)
                if not extracted_duration:
                    extracted_duration = ask_for_valid_duration()
                nested_dict['symptoms'][i]["duration"] = extracted_duration

                give_output(f'chatbot: How severe it feels on a scale of 1-10? say it like (3 out of 10 , 7 out of 10 )')
                # record_audio(duration=10)

                # severity,d = text_from_audio()
                severity = get_input(tv , 'severity')
                severity = valid_severity(severity)
                if severity not in [1 ,2,3,4,5,6,7,8,9,10]:
                    severity = ask_for_valid_severity()
                

                nested_dict['symptoms'][i]["severity"] = severity

                give_output(f'chatbot: How frequently do you feel {i}( Rare ,  Often , Constantly , rarely , frequently, occasionally)? ')
                # record_audio(duration=4)
                # freq ,c= text_from_audio()
                freq = get_input(tv , 'freqency')
                k = valid_freq(freq)
                if k:
                    # k = valid_freq(freq)
                    frequency =  k[0]
                else:
                    frequency = ask_for_valid_freq(i)
                nested_dict['symptoms'][i]["frequency"] = frequency

                give_output("chatbot : Any Addtional note you want to add ?")
                # record_audio(duration=10)

                # add_note,d = text_from_audio()
                add_note = get_input(tv , 'addnote')

                nested_dict['symptoms'][i]["add_note"] = add_note


            give_output(f'chatbot: Thank you. Do you have any other symptoms?')
            # record_audio(duration=10)

            # c ,d= text_from_audio()
            c = get_input(tv , 'statement')
            if 'no' in c.lower():
                # give_output(summary(nested_dict))

                # generate_report(nested_dict,text_summary, filename="patient_report2.pdf")
                generate_report(nested_dict, filename="patient_report2.pdf")
                store_info(nested_dict)
                break

def start():
    global target_lang
    target_lang = select_language()
    k = input("First of all, would you like to continue with VOICE or TEXT???? (v/t) : ")

    global tv
    tv = 0
    if k == 'v':
        tv = 1

    demo ={}

    give_output("chatbot: What is your name?")   
    name  = get_input(tv , 'name')
    
    give_output(f'chatbot: Hello {name}! I’m your medical assistant chatbot. I’ll ask you a few questions to help the doctor understand your condition better ,But first of all, let me know you first !!')
    
    give_output("chatbot : what is your age?")
    age  = get_input(tv , 'age')

    give_output("chatbot : what is your Gender?")
    gender  = get_input(tv, 'gender')

    if gender.lower() == 'mail':
        gender = 'male'
    give_output("chatbot : what is your contact number?")
    contact  = get_input(tv , 'contact')

    demo["name"] = name
    demo["age"] = age
    demo["gender"] = gender
    demo["contact"] = contact
    nested_dict['demographic'] = demo
    chatbot()


def new():
    k = input("Identify Yourself as Doctor or Admin or Patient (Doctor/Admin/Patient): ").strip().lower()

    if k == 'doctor':  
        doctor.doctor2()
    elif k == 'admin':  
        admin.admin2()

    else:
        start()
            

new()
# print(nested_dict)
# start()
