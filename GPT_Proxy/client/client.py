import requests
import json
from Crypto.Cipher import AES
import base64

# 定义一个函数，用于对明文进行补位，使其长度为16的倍数
def pad(text):
    while len(text) % 16 != 0:
        text += b' '
    return text

# 定义一个函数，用于对密文进行去位，去除多余的空格
def unpad(text):
    return text.rstrip(b' ')


def encrypt(key,plaintext):
    aes = AES.new(key, AES.MODE_ECB)
    plaintext = plaintext.encode('utf-8')
    plaintext = pad(plaintext)
    ciphertext = aes.encrypt(plaintext)
    e=base64.b64encode(ciphertext)
    return str(e, encoding = "utf-8")  

def decrypt(key,e):
    aes = AES.new(key, AES.MODE_ECB)
    e=bytes(e,encoding = "utf-8")
    e=base64.b64decode(e)
    plaintext = aes.decrypt(e)
    plaintext = unpad(plaintext)
    plaintext = plaintext.decode('utf-8')
    return plaintext


def pre_request_api(history,key,apikey):
    mess_dict={}
    mess_dict['mess_l']=history
    mess_dict['apikey']=apikey
    data_e=str(mess_dict)
    en_d=encrypt(key,data_e)
    return en_d
    

def request_api(key,url,apikey,history,text):
    data={}
    data["role"]="user"
    data["content"]=text
    history.append(data)    
    data_s=pre_request_api(history,key,apikey)

    message={}
    message['message']=data_s
    x = requests.post(url, json = message)
    response=json.loads(x.text)
    return response

def main():
    with open('config.json','r',encoding='utf-8') as f:
        config=json.load(f)
        key=config['key'].encode('utf-8')
        url=config['url']
        apikey=config['apikey']
        turn=config['history turn']
        history=[]
    while 1:
        try:
            text=input('ME:')
            if len(history)>turn:
                history=history[-turn:]
            response=request_api(key,url,apikey,history,text)
            response=response['reply']
            #print(response)
            response=decrypt(key,response)
            response=dict(eval(response))
            history.append(response)
            print('\nChatGPT: '+response['content']+'\n')
        except:
            continue
 
    

if __name__ == '__main__':
    main()
