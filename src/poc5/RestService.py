#a REST service with a single get method that takes a path parameter a query string parameter named message 
# and returns the message if it is not spam, and an empty string if it is spam.
from flask import Flask, request
from flask_restful import Resource, Api

import Filter
import pandas as pd

import hashlib


app = Flask(__name__)
api = Api(app)

class SpamFilter(Resource):
    def __init__(self):
        df = pd.read_csv('../../data/spam_ham_prompts.csv')
        print(df)
        self.payload = Filter.fit(df,df['label'])

    def get(self, path, message):
        # message = request.args.get('message')

        # We'll need to implement these functions: load_model and predict_spam.
        # They load the trained model and use it to predict whether a message is spam.
        is_spam = self.predict_spam(message)

        # setup a JSON response object
        # the first field is is_spam, which is a boolean
        # the second field is message, which is the message if it is not spam, and an empty string if it is spam
        # the third field is the hash of the message

        returnMessage = message if is_spam == False else ""

        m = hashlib.sha256()
        m.update(message.encode('utf-8'))

        response = {
            "is_spam": is_spam,
            "message": returnMessage,
            "hash": m.hexdigest()
        }   

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
