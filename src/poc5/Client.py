import requests

class SpamFilterClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def send_message(self, path, message):
        # Construct the URL for the request
        url = f"{self.base_url}/{path}/{message}"

        print(f'URL is {url}')
        # Send the GET request
        response = requests.get(url)


        # Check the response status code
        if response.status_code == 200:
            # If the request was successful, print the response data
            return response.json()
        else:
            # If the request failed, print an error message
            print(f"Error: Received status code {response.status_code}")
            return None

def main():
    # Create an instance of the SpamFilterClient
    client = SpamFilterClient("http://127.0.0.1:5000")

    # Get the path from the command line arguments
    path = input("Enter the path: ")

    while True:
        # Prompt the user to enter a message
        message = input("Enter a message (or 'exit' to quit): ")

        # If the user entered 'exit', break out of the loop
        if message.lower() == 'exit':
            break

        # Send the message to the SpamFilter service
        response = client.send_message(path, message)

        # If the request was successful, print the response data
        if response is not None:
            print(response)

if __name__ == "__main__":
    main()
