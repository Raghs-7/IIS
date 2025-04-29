# IIS

## Desription / objective 
The objective of this project is to design, develop, and deploy an AI-powered chatbot capable of
engaging in speech-based conversations with patients in the neurology department. The
chatbot will assist by:
1. Patient Screening: Asking preliminary health-related questions to collect key
information about symptoms, history, and concerns before their consultation.
2. Report Generation: Preparing a summary report for doctors to streamline patient
assessments.
3. Reception Assistance: Acting as a virtual receptionist to provide directions,
appointment confirmations, and general information about hospital services.
4. Multilingual Communication: Communicating in the patient’s preferred language to
ensure inclusivity and ease of interaction for individuals from diverse linguistic
backgrounds.

## Installation Requirements

  Download ollama-lamma3.2

  #For ubuntu users:
      open your terminal
      
      curl -fsSL https://ollama.com/install.sh | sh  
      # this will download and run the installation script
  ![image](https://github.com/user-attachments/assets/5333c1e2-b269-4e99-bab3-8ce515e538ab)
      
      ollama serve 
  # this will start the background server which is nessecary to run the model 
      
      ollama pull llama3.2
  ![image](https://github.com/user-attachments/assets/e60550e8-43ab-4dca-9a9b-25b37803136a)    
  #you can check if your llamma is working fine or not 

      ollama run llama3.2
  ![image](https://github.com/user-attachments/assets/ff334d8b-2279-47b2-a347-4122c35a19fe)
  

##  important modules

    pip instal regex
    pip install pynput
    pip install speech_recognition
    pip install pydub
    pip install word2number  
    pip install fpdf
    pip install pyaudio
    pip install wave
    pip install cryptography.fernet
    pip install os
    pip install pymongo
    pip install pyttsx3
    pip install deep_translator
    pip install gtts
    pip install pygame
    pip install time
    

## command to run the project 

  Copy and paste the following commands into your terminal:

  # Step 1: Clone the repository

    git clone https://github.com/Raghs-7/IIS.git
  ![image](https://github.com/user-attachments/assets/29ee5e01-84c0-45ba-939a-fc5afab523c1)

  # Step 2: Navigate into the project directory

    cd IIS

  # Step 3: setup Mongodb
  copy this mongodb url   
        
        mongodb+srv://raghav24450:iiitd@cluster0.h3b86.mongodb.net/

  open admin.py, doctor.py and main_patient.py in your text editor 

      line no. 37 on admin.py
      line no. 22 on doctor.py
      line no. 25 on main_patient.py

  ![image](https://github.com/user-attachments/assets/79a35575-fac2-45a0-8fd7-a8bef97f8c9d)
        
        MONGO_URI = "mongodb+srv://raghav24450:iiitd@cluster0.h3b86.mongodb.net/"
    
    
  # Step 3: Run the main script
    
    python main_patient.py
  ![image](https://github.com/user-attachments/assets/4df35d37-8f35-4148-aaab-aeb9790d6d02)


