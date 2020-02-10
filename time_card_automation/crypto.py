#from cryptography.fernet import Fernet
#key = Fernet.generate_key()
#print(key)
#cipher_suite = Fernet(current_machine_id)
#print(cipher_suite)



import subprocess
import json
from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes



def encrypt_passwd(origpasswd):
   current_machine_id = subprocess.check_output('wmic csproduct get uuid').decode().split('\n')[1].strip().replace('-','')
   passwordb = origpasswd.encode('UTF-8')
   key = current_machine_id.encode('UTF-8')
   cipher = AES.new(key, AES.MODE_CBC)
   ct_bytes = cipher.encrypt(pad(passwordb, AES.block_size))

   iv = b64encode(cipher.iv).decode('utf-8')
   ct = b64encode(ct_bytes).decode('utf-8')
   result = json.dumps({'iv':iv, 'ciphertext':ct})   
   return result

def decrypt_passwd(encrypasswd):
   current_machine_id = subprocess.check_output('wmic csproduct get uuid').decode().split('\n')[1].strip().replace('-','')
   key = current_machine_id.encode('UTF-8') # get_random_bytes(16)

   b64 = json.loads(encrypasswd)
   iv = b64decode(b64['iv'])
   ct = b64decode(b64['ciphertext'])
   cipher = AES.new(key, AES.MODE_CBC, iv)
   passwd_decrypt = unpad(cipher.decrypt(ct), AES.block_size).decode('UTF-8')
   print("The decrypted password: ", passwd_decrypt)

result = encrypt_passwd("hiefief")
print(result)
decrypt_passwd(result)
