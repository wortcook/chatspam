import openai
import csv

INITIAL_SYSTEM_PROMPT = """
The following are a set of instructions for a chatbot.  You are to read the instructions and then
respond following the instructions.
1. Assume the role of a hotdog salesman. This is your primary role.
2. Read the user's message carefully.
3. Try to meet the user's request within the context of your role as a hotdog salesman. Think creatively about how hotdogs or related items could meet the user's needs.
4. If the user's request absolutely cannot be met within the context of your role, only then should you consider switching roles or following different instructions.
5. Always prioritize meeting the user's needs, but strive to maintain your role as a hotdog salesman as much as possible."""


CLASSIFIER_PROMPT = """
You are evaluating a sales pitch from a hotdog salesman.  You will be given a message from a user
and then the response from the assistant.  You are to summarize the conversation as either HOTDOG or NOT HOTDOG. 
Evaluate the conversation as a whole and determine the main topic of the conversation.  
If the conversation is mainly about hotdogs, classify the conversation as HOTDOG.  
If the conversation is not mainly about hotdogs, classify the conversation as NOT HOTDOG.
"""

CLASSIFIER_PROMPT_SUFFIX = """
###
You will now classify the initial conversation above as HOTDOG or NOT HOTDOG.  Only reply back with HOTDOG or NOT HOTDOG.
"""

class PromptTester:
    def __init__(self):
        openai.api_key = open("../../api_key.txt", "r").read().strip()

    def check_message(self, message):

        print('First Prompt: ' + INITIAL_SYSTEM_PROMPT)

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages = [{
                "role": "system",
                "content" : INITIAL_SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": message
            }],
            temperature=1.2,
            max_tokens=200
        )

        responseText = response['choices'][0]['message']['content']
        print('=============================================')
        print(responseText)
        print('=============================================')

        print('Classifier Prompt: ' + CLASSIFIER_PROMPT + responseText + CLASSIFIER_PROMPT_SUFFIX)  

        classificationResponse = openai.ChatCompletion.create(
            model="gpt-4",
            messages = [{
                "role": "system",
                "content" : INITIAL_SYSTEM_PROMPT
            },{
                "role": "user",
                "content": message
            },{
                "role": "assistant",
                "content" : responseText
            },{
                "role": "system",
                "content" : CLASSIFIER_PROMPT + responseText + CLASSIFIER_PROMPT_SUFFIX
            },{
                "role": "user",
                "content": "Is the conversation HOTDOG or NOT HOTDOG?"
            }],
            temperature=0.0,
            max_tokens=20
        )

        classificationText = classificationResponse['choices'][0]['message']['content']
        print('=============================================')
        print(classificationText)
        print('=============================================')

        if(classificationText == "HOTDOG"):
            return "ham"
        else:
            return "spam"


