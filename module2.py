# import sounddevice as sd
# import numpy as np
# import soundfile as sf
import regex as re
from pynput import keyboard
import speech_recognition as sr
from pydub import AudioSegment
from word2number import w2n  
from fpdf import FPDF
import symptoms
import pyaudio
import wave


stop = False

def on_press(key):
    if key == keyboard.Key.enter:
        global stop
        stop = True

# def generate_report(dic,text_summary, filename="patient_report.pdf"):
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

# def record_audio(filename="user_voice.wav", duration=5, sample_rate=44100):
#     print("Recording... Press 'enter' to stop early.")    
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
#         print("Stopping recording early...")
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

    print("Recording... Press 'q' to stop early.")
    listener = keyboard.Listener(on_press=on_press)
    frames = []
    listener.start()
    for _ in range(0, int(sample_rate / chunk * duration)):
        data = stream.read(chunk)
        frames.append(data)
        if stop:
            break
    stop = False
    print("Recording stopped.")
    stream.stop_stream()
    stream.close()
    p.terminate()
    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(format))
    wf.setframerate(sample_rate)
    wf.writeframes(b''.join(frames))
    wf.close()
    print(f"Recording saved as {filename}")



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
        print("Patient : " + text)
    except sr.UnknownValueError:
        c = 1
        print("Google Web Speech API could not understand the audio")
    except sr.RequestError as e:
        print(f"Could not request results from Google Web Speech API; {e}")
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
            pass  
    return extracted_numbers[0]

def ask_for_valid_duration():
    while True:
        print("chatbot: Could you repeat that? Please tell the duration in hours,weeks , days, months, or years. ")
        record_audio(duration=4)
        duration,d = text_from_audio()
        # duration = input("chatbot: Could you repeat that? Please input the duration in hours, days, months, or years.\nPatient: ")
        extracted_duration = extract_valid_duration(duration)
        if extracted_duration:
            return extracted_duration

def valid_severity(severity):
    # severity = severity if severity.isdigit() else str(w2n.word_to_num(severity.lower()))
    k  = severity.split(" ")
    l = k.index('out')
    i = k[l-1]
    d = { "one" : 1, "two" : 2 , "three" : 3 , "four" : 4 , "five" : 5 , "six" :6, "seven ":  7, "eight" : 8 , "nine" : 9 }
    if i in d:
        i = d[i]
    return int(i)
    # return severity.isdigit() and 1 <= int(severity) <= 10

def ask_for_valid_severity():
    while True:
        print("chatbot: Could you repeat that? How severe it feels on a scale of 1-10?  (3 out of 10 , 7 out of 10 )  ")
        record_audio(duration=10)
        severity ,d= text_from_audio()
        if d == 1:
            ask_for_valid_severity()
        # severity = input("chatbot: Could you repeat that? How severe it feels on a scale of 1-10?\nPatient: ")
        if valid_severity(severity) in [1,2,3,4,5,6,7,8,9,10]:
            return valid_severity(severity)

def valid_freq(txt):
    valid_freq = ['rare' , 'often' , 'constently' , 'rarely' , 'oftenly' , 'frequently' , 'occasionally']   
    txt = txt.split(' ')
    ans = []
    for i in valid_freq:
        if i in txt:
            ans.append(i)
    return ans

def ask_for_valid_freq(i):
    
    print(f'chatbot: How frequently do you feel {i}( Rare ,  Often , Constently , rarely , frequently, occasionally)? ')
    record_audio(duration=4)
    freq ,c= text_from_audio()
    if valid_freq(freq):
        k = valid_freq(freq)
        return k[0]
    while True:
        print(f'chatbot: Could you repeat that? How frequently do you feel {i} (Rare/Often/Constently , occasionally)?')
        record_audio(duration=4)
        freq,d = text_from_audio()
        if valid_freq(freq):
                k = valid_freq(freq)
                return k[0]
    

def get_input(duration = 10):
    record_audio(duration= duration)
    global stop
    stop = False
    return text_from_audio()[0]    

def get_symptoms(sentence):
    result = symptoms.ask_by_ai(sentence, get_input)
    return result
    # return ["headache"]

nested_dict = {'symptoms' : {}}
def chatbot():
    symptoms = []

    while True:
        print("Please desribe your symptoms")
        sentence = get_input()
        symptoms = get_symptoms(sentence)
        if not symptoms:
            print("I see some ambiguity response . Please descibe in detail . ")
        else:
            for i in symptoms:
                global nested_dict
            #   if(nested_dict.get('symptoms'[i]) == None):
                nested_dict['symptoms'][i] = {"severity": "", "duration": "", "frequency": "" , }
                print(f'chatbot: How long have you been experiencing {i}? (Please tell duration in hours,weeks,days, months, or years.)')
                record_audio(duration=10)
                duration ,d= text_from_audio()
                extracted_duration = extract_valid_duration(duration)
                if not extracted_duration:
                    extracted_duration = ask_for_valid_duration()
                nested_dict['symptoms'][i]["duration"] = extracted_duration

                print(f'chatbot: How severe it feels on a scale of 1-10? say it like (3 out of 10 , 7 out of 10 )')
                record_audio(duration=10)

                severity,d = text_from_audio()
                
                if valid_severity(severity) not in [1 ,2,3,4,5,6,7,8,9,10]:
                    severity = ask_for_valid_severity()
                severity = valid_severity(severity)
                nested_dict['symptoms'][i]["severity"] = severity

                frequency = ask_for_valid_freq(i)
                nested_dict['symptoms'][i]["frequency"] = frequency

                print("chatbot : Any Addtional note you want to add ?")
                record_audio(duration=10)

                add_note,d = text_from_audio()
                nested_dict['symptoms'][i]["add_note"] = add_note


            print(f'chatbot: Thank you. Do you have any other symptoms?')
            record_audio(duration=10)

            c ,d= text_from_audio()
            if 'no' in c.lower():
                # print(summary(nested_dict))

                # generate_report(nested_dict,text_summary, filename="patient_report2.pdf")
                generate_report(nested_dict, filename="patient_report2.pdf")
                break

def start():
    
    demo ={}
    print("chatbot: What is your name?")          
    record_audio(duration=5)


    name,c = text_from_audio()
    # name = input("Patient: ")
    print(f'chatbot: Hello {name}! I’m your medical assistant chatbot. I’ll ask you a few questions to help the doctor understand your condition better ,But first off all let me know you first !!')
    print("chatot : what is your age?")
    record_audio(duration=5)

    age,c = text_from_audio()
    # age = input("Patient: ")    #!!
    print("chatot : what is your Gender?")
    record_audio(duration=5)

    gender,c = text_from_audio()
    
    if gender.lower() == 'mail':
        gender = 'male'
    # gender = input("Patient: ")  #!!!
    print("chatot : what is your contact.NO?")
    record_audio(duration=5)

    contact,c = text_from_audio()
    # contact = input("Patient: "qqqq) #!!!!
    demo["name"] = name
    demo["age"] = age
    demo["gender"] = gender
    demo["contact"] = contact
    nested_dict['demographic'] = demo
    chatbot()

start()

print(nested_dict)

