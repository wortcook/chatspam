#a REST service with a single get method that takes a path parameter a query string parameter named message 
# and returns the message if it is not spam, and an empty string if it is spam.
from flask import Flask, request
from flask_restful import Resource, Api

import Filter
from MessageCoding import RSACrypto
import pandas as pd

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import hashlib
import time



app = Flask(__name__)
api = Api(app)

class SpamFilter(Resource):
    def __init__(self):
        print("Initializing SpamFilter")
        df = pd.read_csv('./spam_ham_prompts.csv')
        print(df)

        self.payload = Filter.fit(df,df['label'])
        self.messageCoder = RSACrypto()


    def encrypt_message(self,messageHash):
        return self.messageCoder.encrypt(messageHash)


    def get(self, originalMessage):
        message = " ".join(originalMessage.lower().split())

        print("message: " + message)
        
        return self.handle_message(message)
        
    
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

        maxScore = hamScore + spamScore

        if(maxScore == 0):
            maxScore = 1

        finalScore = (hamScore - spamScore)/maxScore

        innerResponse = {
            "version" : "1.0",
            "timestamp": currentTimeInMilliseconds,
            "hash": m.hexdigest(),
            "api" : "https://chatsafe.io/api/v1/check/",
            "score" : finalScore,
            "signature": encryptedMessageHash,
            "key": self.messageCoder.publicKey.export_key().decode('utf-8')
        }

        # get the json string value of innerResponse
        irh = hashlib.sha256()
        irh.update(str(innerResponse).encode('utf-8'))
        innerResponseHash = irh.hexdigest()
        encryptedSummaryHash = self.encrypt_message(irh.hexdigest())


        response = {
            "messageSummary": innerResponse,
            "messageSummaryHash" : innerResponseHash,
            "messageSummarySignature": encryptedSummaryHash
        }

        # serialize response to JSON
        return response
            
    
    def predict_spam(self,message):
        # return true if the message is spam
        return Filter.predict(self.payload,message)


api.add_resource(SpamFilter, '/api/v1/check/<string:originalMessage>')


if __name__ == '__main__':
    print("Starting service")
    app.run(debug=True, host='0.0.0.0')
