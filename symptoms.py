import requests
import json
import pandas as pd

url = "http://localhost:11434/api/chat"

f = open("example.txt", "r")
examples = f.read()

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

def take_responce(question):
    reply = input(question)
    if reply.lower in ["none", "no","stop"]:
        return ""
    else:
        return reply

def get_symptoms(conversation):
    request = {
    "model": "deepseek-r1",
    "messages": [
        {
        "role": "system",
        "content": """ You are a tool designed to help doctor by listing out the symptoms of a patient and responds in valid JSON format only, here is what you are suppose to do--
    1)**Clear Symptoms**:
    - If a symptom clearly exists in your knowledge base, add it to the JSON as: "<symptom>": { "status": true }
    2)**Extra informative symptoms**: 
    - If a symptom exists in the knowledge base and ncludes extra **details** (like location, severity, duration etc.) **must** indclude: "<symptom>": { "status": true, "addinfo": "<extra details>" }
    3)**Ambiguous Symptoms**: 
    - If a symptom is **unclear** or **vague** or **matches multiple symptoms**, AI **must** set `"status": false`.  
    - The `"possible"` field **must** contain **only** symptoms from the **knowledge base**.  
    - ❌ AI **must not** generate new possible symptoms outside the knowledge base.  
    - final form:  "<symptom>": { "status": false, "possible": ["<possible symptom 1>", "<possible symptom 2>"] }
    - ✅ Example: { "don't feel good": { "status": false, "possible": ["vertigo", "low blood pressure", "dehydration"] } }
    4)**Valid symptom not in the knowledgebase**: If a symptom is not in your knowledge base but still clearly valid, handle it as:
    Clear Symptom (1) if no extra info is provided.
    Extra Informative Symptom (2) if additional details are present.
    5)**Non-symptom Statements**: AI **must** Ignore statements that do not describe any symptoms.
    6)Return only JSON. No explanations, no extra text.
    your knowledge base includes- """ + "\n" +str(get_symptom_list(filelist)) + "\n" + str(examples)
        },
        {
            "role": "user", 
            "content": conversation
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
        # print(inreply)
        # print("__________________")
        reply = inreply.split("</think>")[1]
        reply = reply.strip()
        reply = reply.strip("```")
        reply = reply.strip("json")
        return reply
    else:
        print(f"Error: {response.status_code} - {response.text}")


def process_symptoms(response_json, in_method):
    try:
        # Load the JSON response
        data = json.loads(response_json.strip("stop"))  # Remove "stop" if present

        # Lists to store symptoms and clarifications
        clear_symptoms = []
        ambiguous_symptoms = []

        for symptom, details in data.items():
            if details.get("status"):  # If symptom is clear
                addinfo = details.get("addinfo", "")
                if addinfo:
                    clear_symptoms.append(f"{symptom} ({addinfo})")
                else:
                    clear_symptoms.append(symptom)
            else:  # If symptom is ambiguous
                possible = details.get("possible", [])
                if len(possible) > 0 and not any( symp == "" for symp in possible):   
                    ambiguous_symptoms.append((symptom, possible))

        # Display clear symptoms
        if clear_symptoms:
            print("\n✅ Identified Symptoms:")
            for symptom in clear_symptoms:
                print(f"  - {symptom}")

        # Ask for clarification on ambiguous symptoms
        if ambiguous_symptoms:
            print("\n Some symptoms need clarification:")
            for symptom, possible in ambiguous_symptoms:
                for ele in possible:
                    ele:str
                    ele = ele.replace("_", " ")
                possible_list = ", ".join(possible)
                print(f" when you mentioned '{symptom}', can you please clarify? did you mean one of - {possible_list} - Please choose one or more.")
                resp = in_method()
                flag = False
                for symptom in possible:
                    if symptom in resp:
                        clear_symptoms.append(symptom)
                        flag = True
                if not flag:
                    clear_symptoms += (process_symptoms(get_symptoms(resp)))

        if not ambiguous_symptoms and not clear_symptoms:
            print("I am sorry but I couldn't understand, could you please describe them in different words?")

        return clear_symptoms
    except json.JSONDecodeError:
        print("Error: Invalid JSON response received from AI.")

def ask_by_ai(reply,in_mthod):
    result  =[]
    # reply = input("Please desribe all your symptoms. (enter none, if there are no more) \n")
    if reply.lower() in ["none", "no","stop"]:
        return result
    else:
        result += process_symptoms(get_symptoms(reply),in_mthod)
    return result

# list = ask_by_ai()
# print("✅ Identified Symptoms: ")
# for sym in list:
#     print(sym)
