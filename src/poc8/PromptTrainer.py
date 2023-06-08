import openai
import csv

INITIAL_SYSTEM_PROMPT = """
You are a chat security assistant.  You will be given a message from a user that is meant
to be malicious or to use the system in a way that is not intended.  The intent of the system
is to be a helpful AI assistant capable of answering end user questions within a particular
domain.  You will review the conversation between the user and the assistant.
You will determine if the user is attempting to use the system in a way that is not intended.
You will classify the message as either SPAM or HAM.  If the user is attempting to use the system
in a way that is not intended, you will classify the message as SPAM.  If the user is not attempting
to use the system in a way that is not intended, you will classify the message as HAM.
examples.

The user will provide an example of either HAM or SPAM.  The message will be of the form:

{SPAM or HAM} {message}

You will provide an example of the message that matches the category of the original message
but is a variation of that message.  The message should be in the same category as the original.
Think carefully and check that the message is in the same category as the original message.
Once the initial example has been provided.  If the user responds "Next" you will product another example.
"""

class PromptTrainer:
    def __init__(self):
        openai.api_key = open("../../api_key.txt", "r").read().strip()

    def train(self, message):

        trainingMessages = [{
            "role": "system",
            "content" : INITIAL_SYSTEM_PROMPT
            },{
            "role": "user",
            "content": message
        }]

        #loop 10 times
        for i in range(10):
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages = trainingMessages,
                temperature=1.2,
                max_tokens=200
            )
        
            responseText = response['choices'][0]['message']['content']

            trainingMessages.append({
                "role": "assistant",
                "content" : responseText
            })

            trainingMessages.append({
                "role": "system",
                "content" : "Now do the same thing again.  Use the user message to create a new message that is in the same category as the original message.  If the message is SPAM, create a new message that is also SPAM.  If the message is HAM, create a new message that is also HAM."
            })

            print('=============================================')
            print(responseText)
            print('=============================================')
        
            #Append the response to the training data

            if(responseText.startswith('SPAM ')):
                responseText = responseText[5:]
            elif(responseText.startswith('HAM ')):
                responseText = responseText[4:]

            with open('../../data/training_data.csv', 'a') as csvfile:
                if(message.startswith('SPAM')):
                    writer = csv.writer(csvfile)
                    writer.writerow(['spam',responseText])
                else:
                    writer = csv.writer(csvfile)
                    writer.writerow(['ham',responseText])



