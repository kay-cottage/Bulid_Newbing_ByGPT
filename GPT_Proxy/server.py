from flask import Flask, request, jsonify,render_template
import requests
import json
from Crypto.Cipher import AES
import openai
import base64


def pad(text):
    while len(text) % 16 != 0:
        text += b' '
    return text

def unpad(text):
    return text.rstrip(b' ')


def encrypt(key,plaintext):
    aes = AES.new(key, AES.MODE_ECB)
    plaintext = plaintext.encode('utf-8')
    plaintext = pad(plaintext)
    ciphertext = aes.encrypt(plaintext)
    e=base64.b64encode(ciphertext)
    del plaintext,key,ciphertext
    return str(e, encoding = "utf-8")  



def decrypt(key,e):
    aes = AES.new(key, AES.MODE_ECB)
    e=bytes(e,encoding = "utf-8")
    e=base64.b64decode(e)
    plaintext = aes.decrypt(e)
    plaintext = unpad(plaintext)
    plaintext = plaintext.decode('utf-8')
    del key,e
    return plaintext



def openai_request(apikey,messages):
    #messages 'str'or [{xxx}]
    openai.api_key =apikey
    completion = openai.ChatCompletion.create(
          model="gpt-3.5-turbo",
          messages=messages
        )
    
    return completion



@app.route("/chat", methods=["POST"])
def send_message():
    try:
        data_s = request.json["message"]
        mess_d=decrypt(key,data_s)
        mess_d=dict(eval(mess_d))
        apikey=mess_d['apikey']
        messages=mess_d['mess_l']
        completion=openai_request(apikey,messages)
        reply=str(json.loads(json.dumps(completion.choices[0].message)))
        en_d=encrypt(key,reply)
        del completion,data_s,apikey,messages
        return jsonify({"reply": en_d})
    except Exception as e:
        return jsonify({"reply": str(e)})


    

if __name__ == "__main__":
    app = Flask(__name__)
    global key
    with open('config.json','r',encoding='utf-8') as f:
        config=json.load(f)
        key=bytes(config['key'],encoding='utf-8')  
    app.run(host='0.0.0.0',port=10001,debug=False)
