#a REST service with a single get method that takes a path parameter a query string parameter named message 
# and returns the message if it is not spam, and an empty string if it is spam.
from flask import Flask, request
from flask_restful import Resource, Api

import Filter
from MessageCoding import RSACrypto
from PromptTester import PromptTester
from PromptTrainer import PromptTrainer
import pandas as pd

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import hashlib
import time



app = Flask(__name__)
api = Api(app)

class SpamFilter(Resource):
    def __init__(self):
        df = pd.read_csv('../../data/spam_ham_prompts.csv')
        print(df)

        self.payload = Filter.fit(df,df['label'])
        self.messageCoder = RSACrypto()
        self.promptTester = PromptTester()


    def encrypt_message(self,messageHash):
        return self.messageCoder.encrypt(messageHash)


    def get(self, path, originalMessage):
        message = " ".join(originalMessage.lower().split())

        print("message: " + message)
        
        if(originalMessage.startswith("TeSt")):
            message = message[4:]
            return self.handle_test_message(message)
        elif(originalMessage.startswith("TrAiN")):
            message = message[5:]
            return self.handle_train_message(message)
        else:
            return self.handle_message(message)
        
    def handle_test_message(self, message):
        messageResponse = self.handle_message(message)

        messageIsSpam = messageResponse['response']['isSpam']
        print("messageIsSpam: " + str(messageIsSpam))
        messageTestResult = self.promptTester.check_message(message)

        messageResponse['responseTest'] = {}
        if(messageTestResult == 'spam'):
            if(messageIsSpam == 'True'):
                messageResponse['responseTest']['isSpam'] = 'true-positive'
            else:
                messageResponse['responseTest']['isSpam'] = 'FALSE NEGATIVE'
        else:
            if(messageIsSpam == 'True'):
                messageResponse['responseTest']['isSpam'] = 'FALSE POSITIVE'
            else:
                messageResponse['responseTest']['isSpam'] = 'true-negative'

        return messageResponse


    
    def handle_train_message(self, message):
        trainer = PromptTrainer()
        trainer.train(message)

    def handle_message(self, message):
        # message = request.args.get('message')

        # We'll need to implement these functions: load_model and predict_spam.
        # They load the trained model and use it to predict whether a message is spam.
        is_spam = self.predict_spam(message)

        spamScore = is_spam['tags']['spam']
        hamScore = is_spam['tags']['ham']

        maxScore = max(spamScore,hamScore)
        if(maxScore == 0):
            maxScore = 1
        is_spam['tags']['spam'] = spamScore/maxScore
        is_spam['tags']['ham'] = hamScore/maxScore

        # setup a JSON response object
        # the first field is is_spam, which is a boolean
        # the second field is message, which is the message if it is not spam, and an empty string if it is spam
        # the third field is the hash of the message

        m = hashlib.sha256()
        m.update(message.encode('utf-8'))

        # Encrypt the messageHash
        encryptedMessageHash = self.encrypt_message(m.hexdigest())

        currentTimeInMilliseconds = int(round(time.time() * 1000))


        innerResponse = {
            "timestamp": currentTimeInMilliseconds,
            "isSpam": str(spamScore > hamScore),
            "spamScore": is_spam,
            "messageHash": m.hexdigest(),
            "encryptedMessageHash": encryptedMessageHash,
            "publicKey": self.messageCoder.publicKey.export_key().decode('utf-8')
        }

        response = {
            "response": innerResponse,
            "responseHash": hashlib.sha256(str(innerResponse).encode('utf-8')).hexdigest()
        }

        # serialize response to JSON
        return response
            
    
    def predict_spam(self,message):
        # return true if the message is spam
        return Filter.predict(self.payload,message)


api.add_resource(SpamFilter, '/<string:path>/<string:originalMessage>')


if __name__ == '__main__':
    app.run(debug=True)
