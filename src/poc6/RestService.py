#a REST service with a single get method that takes a path parameter a query string parameter named message 
# and returns the message if it is not spam, and an empty string if it is spam.
from flask import Flask, request
from flask_restful import Resource, Api

import Filter
import pandas as pd

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import hashlib
import binascii



app = Flask(__name__)
api = Api(app)

class SpamFilter(Resource):
    def __init__(self):
        df = pd.read_csv('../../data/spam_ham_prompts.csv')
        print(df)

        self.payload = Filter.fit(df,df['label'])

        #read the contents of the passcode file
        passcodeFile = open("../../data/passcode.txt", "r")

        #read the passcode from the file
        passcode = passcodeFile.read()

        print("passcode: ", passcode)

        # Generate a seed from the passcode
        seed = hashlib.sha256(passcode.encode('utf8')).digest()

        print("seed: ", seed)

        # Generate public and private keys using the seed
        self.key = RSA.generate(2048)

        print("key: ", self.key)


    def encrypt_message(self,messageHash):
        # Generate a seed from the passcode

        # Create a cipher using the private key and use it to encrypt the messageHash
        cipher = PKCS1_OAEP.new(self.key)
        messageHashEnc = cipher.encrypt(messageHash.encode('utf8'))

        # Return the encrypted messageHash and the public key
        return {
            "messageHashEnc": binascii.hexlify(messageHashEnc).hex(),
            "publicKey": self.key.publickey().exportKey('PEM').hex()
        }


    def get(self, path, message):
        # message = request.args.get('message')

        # We'll need to implement these functions: load_model and predict_spam.
        # They load the trained model and use it to predict whether a message is spam.
        is_spam = self.predict_spam(message)

        # setup a JSON response object
        # the first field is is_spam, which is a boolean
        # the second field is message, which is the message if it is not spam, and an empty string if it is spam
        # the third field is the hash of the message

        m = hashlib.sha224()
        m.update(message.encode('utf-8'))

        # Encrypt the messageHash
        encryptedMessageHash = self.encrypt_message(m.hexdigest())

        response = {
            "is_spam": is_spam,
            "hash": m.hexdigest(),
            "encryptedMessageHash": encryptedMessageHash['messageHashEnc'],
            "publicKey": encryptedMessageHash['publicKey']
        }   

        # serialize response to JSON
        return response
            
    
    def predict_spam(self,message):
        # return true if the message is spam
        if(Filter.predict(self.payload,message) == 'spam'):
            return True
        else:
            return False    


api.add_resource(SpamFilter, '/<string:path>/<string:message>')


if __name__ == '__main__':
    app.run(debug=True)
