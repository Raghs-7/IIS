import requests
import json
import pandas as pd

in_method = lambda x : input()
out_method = lambda x: print(x)

url = "http://localhost:11434/api/chat"

def get_content(filename):
    f = open(filename, "r")
    return f.read()

filelist = ["neurological_symptoms.csv", "Symptom.csv"]

def get_symptom_list(filelist):
    sym_list = set()
    for filepath in filelist:
        data = pd.read_csv(filepath)
        for col in data:
            if str(col).lower() == "symptom":
                temp = data[col].to_list()
                for ele in temp:
                    ele:str
                    ele = ele.replace("_"," ")
                sym_list.union(set(temp))
    list = ""
    for symptom in sym_list:
        list += f"{symptom} \n"
    return list
    
def request_ollama(prompt, content, ai = "llama3.2"):
    request = {
    "model": ai,
    "messages": [
        {
        "role": "system",
        "content": prompt
        },
        {
            "role": "user", 
            "content": content
        }
    ],
    "stream": False
    }
    print("Please wait this might take some time.....")
    response = requests.post(url, json=request)

    data = response.json()
    if response.status_code == 200:
        inreply = data["message"]["content"]
        inreply:str
        return inreply
    else:
        print(f"Error: {response.status_code} - {response.text}")
    
def fixJson(defective_json):
    reply = request_ollama(
        prompt="""You are a tool used to fix defective JOSN file, 
        remove any Note, explanations, comments, or any additional text and Only return a valid JSON file
        make minimum changes to make it valid,
        Do NOT make up your own words and add them to the file
        You **MUST** ONLY reply in **VALID JSON FORMAT**
        """,
        content= defective_json
    )
    try:
        reply = json.loads(reply)
    except json.JSONDecodeError:
        reply = fixJson(reply)
    return reply

def get_symptoms(conversation):
    
    symptoms = str(get_symptom_list(filelist))

    reply = request_ollama(
        prompt= """You are a tool used to extract possible symptoms from a patient's dialogue. Your response MUST be in valid JSON format—nothing else.

Rules:
1) Extract ALL symptoms

If and ONLY IF a phrase in the dialogue indicates **discomfort** or a **symptom** or **disease**, include it exactly as it appears: "<phrase>": "<symptom>"

2) DO NOT MODIFY PHRASES

You MUST NOT edit, reword, summarize, or change any words in <phrase>. Use only what is written in the dialogue.
BE PRECISE WITH SYMPTOMS

Keep <symptom> concise. Avoid extra words or unnecessary descriptions.
Return an empty JSON {} if no symptoms exist

3) ALWAYS RETURN VALID JSON
If the input is empty or contains no symptoms, return {}
Do **NOT** include explanations, comments, or any additional text—only valid JSON.
examples of clear symptoms -""" + "\n" + symptoms + "\n" + str(get_content("example1.txt")),
        content= conversation,
    )
    reply = reply.strip("stop")
    reply = reply.strip()
    reply = reply.strip("```")
    reply = reply.strip("json")
    # print(reply)
    try:
        reply = json.loads(reply)
    except json.JSONDecodeError:
        reply = fixJson(reply)
    # print(reply)
    symptomlis = []
    for phrase in reply:
        symptom = reply[phrase]
        status = request_ollama(
            prompt= """You are a tool used to check symptom clearity, reply ONLY IN **BOOL**-
            follow these step by step:
            1 Step:
            If the symptom appers **exactly word for word** in knowladge base, you **MUST** respont with "true"
            2 Step:
            If the symptom correspond to **MORE THAN ONE** element in the knowladge base, you **MUST** respond with "false"
            3 Step:
            If the symptom is clearly present in your knowladge base and correspond to **ONLY ONE** element, you **MUST** respond with "true"
            4 Step:
            if the symptom does not correspond with anything in the knowladge but still is clear enough like the rest of the symptoms in the knowladge base, respond with "true" otherwise "false"

            YOU MUST **NEVER** RETURN ANYTHING OTHER THAN A VALID BOOL
            your knowladge base -""" + "\n" + symptoms + "\n" + str(get_content("example2.txt")),
            content= symptom
        )
        # print(f"{symptom} : {status}")
        if status.strip().lower() in ["true", "false"]:
            symptomlis.append((phrase, symptom, status))
        else:
            pass
    
    clear = []
    unclear = []
    for element in symptomlis:
        if element[2] == "false":
            potential = request_ollama(
                prompt=f"""You are a tool used to check possible symptoms from a query, reply ONLY IN **PYTHON LIST**-
                1 Step:
                for the given ("<Context>", "<Keyword>"), find all the symptoms in the knowladge base that it correspond with and put them in the python list as : ["<symptom1>", "<symptom2>", "<symptom3>"]
                2 Step:
                respond with empty list if you find nothing : []

                you MUST **NEVER** respond with anything **OTHER THAN** a **VALID** PYTHON LIST
                you MUST **ONLY** respond with  a PYTHON LIST 
                your knowladge base -""" + "\n" + symptoms + "\n",
                content= str((element[0], element[1]))
            )
            lis = eval(potential)
            # print(lis)
            lis = [lis[i].lower() for i in range(len(lis))]
            unclear.append((element[0],lis))
        else:
            clear.append((element[0], element[1]))
    # print(clear, unclear)
    return clear, unclear

def process_symptoms(sentence):
    clear , unclear = get_symptoms(sentence)
    for element in unclear:
        out_method(f"I'm sorry, I didn't understand that. ")
        if len(element[1]) :
            out_method(f"By '{element[0]}' did you mean one of the following: "+ " , ".join(element[1]) + "? Please choose one.")
        else:
            out_method(f"Could you please re-phrase what you meant by {element[0]}")
        reply = in_method('')
        if reply.lower() in element[1]:
            clear.append((element[0], reply))
        else:
            clear += process_symptoms(reply)
        
    if len(clear) == 0:
        out_method("Sorry I didn't get that, chould you rephrase you problem? ")
        reply = in_method('')
        clear = process_symptoms(reply)
    return clear
        
            
def ask_by_ai(reply):
    lis = process_symptoms(reply)
    result = [lis[i][1] for i in range(len(lis))]
    return result

def main(sentence, input_method = lambda x : input(), output_method = lambda x: print(x)):
    global in_method
    global out_method
    in_method = input_method
    out_method = output_method
    return ask_by_ai(sentence)

# print(main(input()))
# print(ask_by_ai(input(), lambda x : input(x)))