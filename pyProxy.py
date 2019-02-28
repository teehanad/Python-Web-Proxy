import socket, sys, threading, os, time

DEFAULT_PORT = 8080             # System default port
MAX_CONNECTION = 50             # Maximum backlog of requests
BUFFER_SIZE = 5120              # buffer size     
cache ={}                       # cache implemented using dictionary (Hashmap)
                                # storing key value pairs enables access of stored data by URL.
DEBUG = False                   # Boolean value to activate debug print statments
ADVANCED_MODE = False           # Boolean value to activate advanced user mode (Displays more data... raw data)
TIMER = False                   # Boolean value to activate time prints
theBlacklist = []               # implemented using a list so you can .remove aswell as append
t0 = 0
t1 = 0


# Main Method, this serves as the main menu of the managmanet console.
# The user is propted to start the program or enter set up to change settings of the proxy. This method is later on.
# We also capture KeyboardInterupts and terminate on reciving one with out the traceback printing to console. no Reason other than looks nicer
def main():  
    global theBlacklist         #initilize the blacklist list from a text file
    with open('blacklist.txt', 'r') as filehandle:  
        for line in filehandle:
            urlAdd = line[:-1]          #ignores the new line char that messes up the list when added
            theBlacklist.append(urlAdd) 

    print('-----------------------------------------------------------------')
    print("Welcome to Adam's proxy server!")
    print("Type 'START' to get started")
    print("Type 'SETUP' to enter the options menu and access the Blacklist ")
    print("If you wish to quit the program type 'QUIT'")
    print('-----------------------------------------------------------------')


    correctInput = False               # Eanbles looping until correct input 
    while correctInput == False:
        try:
            inputText = str(raw_input("Type here: "))    # Prompt user for choice

            if(inputText == 'START'):          # if user chooses to start then call start method and end loop for input
                correctInput = True
                run_proxy()
                

            elif(inputText == 'SETUP'):        # if user wanst to see the options then display them in console
                options()

            elif(inputText == 'QUIT'):
                exit()
                print('Goodbye')
                
            else:
                print("ERROR - Try that again ")      # Upon error tell user to try again and repeat until input gotten
        except KeyboardInterrupt:
            print()
            print(" ... Keyboard Interupt ... Exiting ... ")      # Quit on iterupt
            exit()


# This function sets up or initial socket for out proxy server and binds it to our port on our local machine
# it then recives data through that connection and creates threads to handle the requests
def run_proxy():
    port = str(raw_input("Enter a listning port value or enter 'D' to use system default 8080: "))
    if port == 'D':
        port = DEFAULT_PORT
    else:
        port = int(port)

    if DEBUG == True:
        print('-------------------------------DEBUG-------------------------------------')
        print('... Port ' + str(port) + ' selected ...') 
        print('-------------------------------DEBUG-------------------------------------')


    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)       # creates server socket
        server.bind(('', int(port)))                              # binds socket to local host and chosen port. '' = localhost
        server.listen(MAX_CONNECTION)                                    # listens for requests through that port to a backlog of MAX_CONNECTION in size
        print("Proxy Started locally on Port: " + str(port)) # Tell user the proxy has started on their chosen port so they know they can use it now
    except Exception:                                               # upon reaching an exception just pass over, could make it mor meaning full but works
        pass

    while True:
        try:
            conn, addr = server.accept()                     # accept a connection from our backlog and retuen a new socket object conn and address for connection
            request = conn.recv(BUFFER_SIZE)            # recive data into our buffer of length BUFFER_SIZE from that connection
            if ADVANCED_MODE == True:
                    print('-------------------------------ADVANCED_MODE-------------------------------------')
                    print('... Raw request data ...' )
                    print(request)
                    print('-------------------------------ADVANCED_MODE-------------------------------------')

            pyThread = threading.Thread(target = HTTPRequestParcer, args=(conn, request))     # create a thread to handle this connection request 1st calling
            pyThread.daemon = True                                                            # The HTTP parser
            pyThread.start()
        except KeyboardInterrupt:                       # upon detection of an interupt then end the program and print message displaying so
            s.close()
            print(" ... Keyboard Interupt ... Exiting ... ")
            sys.exit()

    s.close() # close socket

# This method is our parser for HTTP Requests. Upon reciving a request and pulling the data from the socket it parses the data
# into two sections, The first is the absolute URI and the second is the URL of the website being aceesed.
def HTTPRequestParcer(conn, request):
    global t0 
    t0 = time.time() #timestamp t0
    try:
        first_line = request.split('\n')[0]
        url = first_line.split(' ')[1]

        if DEBUG == True:
            print('-------------------------------DEBUG-------------------------------------')
            print('... First Line ... ')
            print(first_line)
            print('... URL ... ')
            print(url)
            print('-------------------------------DEBUG-------------------------------------')

        #TODO: FIX THIS! For now if a HTTPS request is made I have set the proxy to send a kind message to users to tell them 
        # sorry that I could'nt get the proxy to handle https requests yet but I will continue to look into it and hopfully fix it.
        if 'CONNECT' in first_line:
            print("Unfortunatly this proxy can't handle HTTPS requests just yet, maybe in a future update ;) - Adam - Dev")
            
        # If it is a HTTP request then take it appart using Python 2 find feature to search the raw data
        # for the port and webserver address based on sperator values, calculated if needed or if not present
        # use system defaults to generate address and port
        else:                          
            http_pos = url.find("://")     
            if(http_pos == -1):
                temp = url
            else:
                temp = url[(http_pos+3):]


            port_pos = temp.find(":")
            webserver_pos = temp.find("/")
            if webserver_pos == -1:
                webserver_pos = len(temp)
            webserver = ""
            port = -1
            if (port_pos==-1 or webserver_pos <port_pos):
                port = 80
                webserver = temp[:webserver_pos]
            else:
                port = int((temp[(port_pos+1):])[:webserver_pos-port_pos-1])
                webserver = temp[:port_pos]
                if DEBUG == True:
                    print('-------------------------------DEBUG-------------------------------------')
                    print('... Webserver ... ')
                    print(webserver)
                    print('... Port ... ')
                    print(port)
                    print('-------------------------------DEBUG-------------------------------------')

            push_request(webserver, port, conn, request) #Call to the push request method.
    except Exception, e:
        pass

# This function handles the actual request for the page information from proxy to  server. If it is a case that the info
# is already present in  the cahce then it will retun that info and finish off there.
# if the info is not in  the cahce it will make a request to the server for the web page and the cache that info for the future
# it also checks for requests made to blacklisted url's and ends them
def push_request(webserver, port, conn, request):
    global theBlacklist
    global t0
    global t1
    checkURL = 'http://' + webserver
    try:
        if checkURL in theBlacklist:   #checks in the url or full url are in the blacklist
            print("Looks like you are trying to access a blacklisted sight -_- move along") #if one or both are then tell user they are caught out
            conn.close()    #close the connection
            return      #end process

        if request in cache: # check for presence of request in our hashmap (Dict)
            conn.send(cache[request])  # if it is there, send data to browser
            conn.close()               # close connection
            print("Cache hit on " + webserver + ", sent page to browser") # inform user of what we have done
            t1 = time.time() #timestamp t1
            if TIMER == True:
                print('-------------------------------TIMER-------------------------------------')
                print('process took ' + str(t1-t0) + ' seconds to retrieve from cache' ) #prints Timestamp 1 - Timestamp 0 go give elapsed time
                print('-------------------------------TIMER-------------------------------------')
            return  # end function with no return value

        #If the website is not in the cache we need to get it. sends request to a server for webpage
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   # create a new socket
        s.connect((webserver, port))    # connect to the webserver from our HTTP request
        s.send(request)    # send our request

        while True:
            #We will (Hopfully) get a reply from the server with the webpage we requested. We will store this in cahce for next time
            # and of course we will also display this on the browser
            reply = s.recv(BUFFER_SIZE) # recive our reply 
            if(len(reply)>0):   # make sure the reply makes sense, make sure its not nothing
                cache[request] = reply  # if its something then store its key value pair, URL:REQUEST in our cahce (Dict/Hashmap)
                conn.send(reply)    # Send that response back to the client
                print("Request for " + webserver + " has been taken care of and cached") 
            else:
                break # if the response didn't make sense or seem useful then break out, no need to store junk

            s.close() # close the proxy to webserver connection
            conn.close() # close connection from client to proxy
            t1 = time.time()
            if TIMER == True:
                print('-------------------------------TIMER-------------------------------------')
                print('process took ' + str(t1-t0) + ' seconds to retrieve from server' ) #prints Timestamp 1 - Timestamp 0 go give elapsed time
                print('-------------------------------TIMER-------------------------------------')

    except socket.error:    
        s.close()   # same closes as before then exit system
        conn.close()
        sys.exit()
        

    except KeyboardInterrupt:  # same as above except in response to keyboard interupt and tells user its quiting, this ones intentional
        s.close()
        conn.close()
        print(" ... Keyboard Interupt ... Exiting ... ")      # Quit on iterupt
        sys.exit()

# This is the options menu for the managment console, It enables you to toggel two modes, DEBUG and ADVANCED
# It also provides access to the blacklist menu where users can change settings regarding the blacklisting of URL's
def options():
    global DEBUG
    global ADVANCED_MODE
    global TIMER
    finishedOptions = False   
    print('-----------------------------------------------------------------')
    print("Welcome to the options menu!")
    print("Type 'DEBUG' to toggle debug mode")
    print("Type 'TIMER' to toggle timer mode")
    print("Type 'ADVANCED' to toggle display or more complex and raw data ")
    print("Type 'BLACKLIST' to enter the URL blacklisting menue" )
    print("When you are finished type 'QUIT'")            # Eanbles looping until correct input 
    print('-----------------------------------------------------------------')

    while finishedOptions == False:
        try:
            inputText = str(raw_input('Type here: '))     # Prompt user for choice
            if(inputText == 'DEBUG'):          # if user chooses to debug then check current state and toggle to other
                if DEBUG == False:
                    DEBUG = True
                else:
                    DEBUG = False
                print('-----------------------------------------------------------------')
                print('Debug mode: ' + str(DEBUG))
                print('-----------------------------------------------------------------')

            elif(inputText == 'TIMER'):          # if user chooses to Timer then check current state and toggle to other
                if TIMER == False:
                    TIMER = True
                else:
                    TIMER = False
                print('-----------------------------------------------------------------')
                print('Timer mode: ' + str(TIMER))
                print('-----------------------------------------------------------------')

            elif(inputText == 'ADVANCED'):        # same as above but for advanced mode
                if ADVANCED_MODE == False:
                    ADVANCED_MODE = True
                else:
                    ADVANCED_MODE = False
                print('-----------------------------------------------------------------')
                print('Advanced mode: ' + str(ADVANCED_MODE))
                print('-----------------------------------------------------------------')

            elif(inputText == 'BLACKLIST'):     #if user chooses blacklist then go to blacklist menu function
                blacklist()
                
            elif(inputText == 'QUIT'):          # return to main menu
                finishedOptions = True
                print('-----------------------------------------------------------------')
                print("Welcome to Adam's proxy server!")
                print("Type 'START' to get started")
                print("Type 'SETUP' to enter the options menu and access the Blacklist ")
                print("If you wish to quit the program type 'QUIT'")
                print('-----------------------------------------------------------------')

            else:
                print("ERROR - Try that again ")      # Upon error tell user to try again and repeat until input gotten
        except KeyboardInterrupt:
            print()
            print(" ... Keyboard Interupt ... Exiting ... ")      # Quit on iterupt
            exit()


#This is our blacklist function, it allows the user to add or remove url's from the blacklist and also can
#be used to diplay all current blacklisted URL's
def blacklist():
    global theBlacklist
    finishedBlacklist = False               # Eanbles looping until correct input 
    print('-----------------------------------------------------------------')
    print("Welcome to the blacklist options menu!")
    print("Type 'ADD' to add a URL to the Blacklist")
    print("Type 'REMOVE' to remove a URL from the Blacklist ")
    print("Type 'PRINT' to print the list of blacklisted URL's" )
    print("When you are finished type 'QUIT'")
    print('-----------------------------------------------------------------')

    while finishedBlacklist == False:
        
        try:
            inputText = str(raw_input('Type here: '))    # Prompt user for choice
            if(inputText == 'ADD'):          # if user chooses ADD then promopt for URL and append list
                inputText = str(raw_input('Type URL you wish to ADD to list here: '))   # Prompt user for choice
                theBlacklist.append(inputText)

            elif(inputText == 'REMOVE'):        # if user chooses remove, prompt for url and remove
                inputText = str(raw_input('Type URL you wish to REMOVE from list here or ALL to remove all: '))     # Prompt user for choice
                if inputText == 'ALL':
                    theBlacklist = []
                else:
                    theBlacklist.remove(inputText)
                
            elif(inputText == 'PRINT'):         # print all blacklisted url's currently in list
                print("--------------------Current Blacklisted URL's--------------------")
                for URL in theBlacklist:
                    print(URL)
                
            elif(inputText == 'QUIT'):              #quit back to options, reprint the options choices
                finishedBlacklist = True
                f = open("blacklist.txt", "w")
                for URL in theBlacklist:
                    f.write(URL+'\n')

                print('-----------------------------------------------------------------')
                print("Welcome to the options menu!")
                print("Type 'DEBUG' to toggle debug mode")
                print("Type 'ADVANCED' to toggle display or more complex and raw data ")
                print("Type 'BLACKLIST' to enter the URL blacklisting menue" )
                print("When you are finished type 'QUIT'")            # Eanbles looping until correct input 
                print('-----------------------------------------------------------------')


            else:
                print("ERROR - Try that again ")      # Upon error tell user to try again and repeat until input gotten
        except KeyboardInterrupt:
            print()
            print(" ... Keyboard Interupt ... Exiting ... ")      # Quit on iterupt
            exit()


                
                


if __name__ == '__main__':
	main()
