# Lab: 2FA broken logic
### https://portswigger.net/web-security/authentication/multi-factor/lab-2fa-broken-logic

This is a brute force challenge that requires you to guess the multi factor code of another user to "login" as them

### Testing
To start, navigate to the /login page which you can access with the "My Account" link on the right hand side of the page

Then you need to login to your account. The username and password were already given in the lab description
* Username: wiener
* Password: peter

Click login and your redirected to the /login2 page asking for a multi factor code

To get the code, use the Email client button at the top of the page to open a new tab. This tab acts as your email inbox

You will have received an email with the multi factor code and can now return to the /login2 page to enter the code and click the login button

### Exploit
To solve the lab you have to log in as carlos.

To do this you need to open Burpsuite Community to capture two requests.

First Log out of your current session. Then click the "My account" link again or navigate back to the /login page. 

With Burpsuite running capture the login for this page and sent the request to Repeater

Then do the same for /login2. You can use any multi factor code, like 1234, as we just need to know what the request will look like

Now that you have the request for /login you will notice the request has a verify flag that is currently set to wiener. We need to change this to carlos and send the request again

````
Cookie: session=Y3s93Vm06E4Cbw1GMIAcHw51vlI6tXEi; verify=carlos
````

What this will do is send a multi factor code to the email that carlos has on file. 

Now that the code has been requested, we need to change the request on /login2 as well. 

Now look at the /login2 request that we captured and change the verify flag to carlos again. 

Now copy the response into a file locally. For reference I called my file burpSuiteRequestText, and its uploaded to this github directory 

Next we need a list of all possible multi factor codes. The code is no more than 4 digits but contains leading zeros. Example 0023 or 0432 are valid codes. 

To do this we can run a small bash command

````
seq -w 0001 9999 > passwordList 
````

Now that we have the two files needed we can use the pythonBrute.py in this github directory to brute force the code

There are three variables to understand
* burpSuiteRequestText is the request from burpsuite we want to loop through
* passwordList is a file that has all the codes we want to try
* https is the type of prefix we want to add to the url (note that portswigger only runs on https)

Note: this script is using threading and a batch system, so you can change the speed at which you want to send request by updating the chunk number at the top of the script
````
chunk = 100;  #how many requests to send before checking for a success        
````

Tip: Try to send at least one /login2 request from Burpsuite before running the script to make sure your session is still active. If not just capture another /login2 request and make sure to update the burpSuiteRequestText file

Now we can run the command in python3

````
python3 pythonBrute.py burpSuiteRequestText passwordList https
````

If all goes well the progam should show the code for carlos

````
Found Value is: **** With response length of ****
````

At this time the lab should be solved and you can refresh the page to confirm

### Troubleshooting

If the script is throwing errors try to lower the chunk number to cut down on the amount of requests at one time

If the script completes but doesn't find any codes then double check that the passwordList is correct and that your session has not expired. Also make sure you have included https on the end of the command

### Conclusion 
This writeup was done because the community version of burpsuite throttles you when using the intruder functionality making this lab take hours to brute force. With this script the whole lab can be completed in less than 10 minutes. So hopefully this is helpful to others that also want to learn on the cheap

