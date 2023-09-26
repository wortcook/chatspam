from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import base64

class RSACrypto:
    def __init__(self):
        # Load the passphrase
        with open('./passcode.txt', 'r') as f:
            passphrase = f.read().strip()

        # Load the private key
        with open('./private.pem', 'r') as f:
            self.__privateKey = RSA.import_key(f.read(), passphrase=passphrase)
        
        # Create the public key
        self.publicKey = self.__privateKey.publickey()

    def encrypt(self, message):
        # Create a cipher object using the private key
        cipher = PKCS1_OAEP.new(self.__privateKey)

        # Encrypt the message and encode it as a Base64 string
        encrypted_message = cipher.encrypt(message.encode())
        return base64.b64encode(encrypted_message).decode()
