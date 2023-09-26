FROM python:latest

RUN pip install pycryptodome pandas flask_restful flask

ADD RestService.py .
ADD MessageCoding.py .
ADD Filter.py .
ADD spam_ham_prompts.csv .
ADD private.pem .
ADD passcode.txt .

EXPOSE 5000

CMD ["python", "RestService.py"]
