import requests
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
                sym_list.union(set(temp))
    list = ""
    for symptom in sym_list:
        list += f"{symptom} \n"
    return list

def get_symptoms(conversation):
    sentence = "My head is bleeding !!!"
    request = {
    "model": "deepseek-r1",
    "messages": [
        {
        "role": "user",
        "content": f""" You are a medical chatbot designed to help doctor by listing out the symptoms of a patient, here is what you are suppose to do--
    1)**Clear Symptoms**: For specific issues that are directly found in your knowledge base, simple list them out then stop
    2)**Extra informative symptoms**: For specific issues that are directly found in your knowladge base but additional information is also given (eg, location), list the base symptom with additional information in parenthesis
    3)**Ambiguous Symptoms**: For unclear symptoms which are similar to more than one symptom in knowledge base, ask for clarification using examples of what they might be experiencing
    4)**Valid symptom not in the knowledgebase**: If a symptom is clear enough to be of use to the doctor but is not mentioned in the knowladge base, treat it as 1) or 2) depending on situation
    5)**Non-symptom Statements**: If a statement isn't describing any symptom, respond with "I'm sorry, but I can't help with that. what are your symptoms?"
    6)Do not explain yourself, if you are clear only list out the symptoms and nothing else
    your knowledge base includes- 

    {get_symptom_list(filelist)}

    {examples}
    Now, start
    {conversation}"""
        }
    ],
    "stream": False
    }

    response = requests.post(url, json=request)

    data = response.json()
    if response.status_code == 200:
        inreply = data["message"]["content"]
        inreply:str
        print(inreply)
        print("__________________")
        reply = inreply.split("</think>")[1]
        reply = reply.strip()
        conversation += "\n" +reply + "\n"
        print(reply)
        if any([i in reply for i in ["?", ".", "I'm"]]):
            while True:
                next = input("enter your reply - :")
                if next == "-1":
                    print(inreply[0])
                else:
                    break
            return get_symptoms(conversation + f"Patient: {next}")
        else:
            reply = reply.split("\n")
            return reply
    else:
        print(f"Error: {response.status_code} - {response.text}")

print(get_symptoms(f"Patient: {input()}"))

