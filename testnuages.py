#!/usr/bin/python
import requests,json,argparse,sys
parser = argparse.ArgumentParser()
parser.add_argument("-i",help="IP of the nuages server to test")
parser.add_argument("-p",help="port of the nuages server to test, default=3030")
parsed = parser.parse_args()
if not parsed.i:
    print("failed to provide ip, use --help for details")
    sys.exit(1)
if parsed.p:
    port = parsed.p
else:
    port = "3030"
URL = "http://"+parsed.i+":"+port+"/implant/register"
def registerImplant(URL):
   #Register the implant
   #pulled right out of nuages wiki
   heads = {'content-type': 'application/json'}
   regData = {
  "hostname": "John-PC", 
  "username": "John", 
  "localIp": "192.168.0.3", 
  "sourceIp": "", 
  "os": "windows", 
  "handler": "Direct", 
  "connectionString": "http://127.0.0.1:3333", 
  "options": {}, 
  "supportedPayloads": [ 
  
    "Command",
    "Exit",
    "Download",
    "Upload",
    "Configure"
  ]
   }
   try:
      r = requests.post(url = URL, headers=heads, data=json.dumps(regData))
      print("response from server:",r.text)
   except Exception as e:
      debug("registration failed, err:{}".format(e))
        #response text  
      debug("Response:{}".format(r.text))
      try:
         self.id = json.loads(r.text)["_id"]
      except Exception as e:
         debug("didn't receive id from registration response, err:{}".format(e))

print("registering implant...")
registerImplant(URL)
