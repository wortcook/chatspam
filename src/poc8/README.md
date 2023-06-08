ChatSpam prototype

To run:

server: python RestService.py

Then in another window

client: python Client.py

At the client prompt, enter a message to evaluate.  

Prepend your message with test: to run a test against GPT with your prompt.

Prepend your message with train:(SPAM/HAM) to train against an example message and variations.


Note that right now, training data gets written to ../../data/training_data.csv which isn't
used in the filter.  Next POC....