from thread import *
import sys, socket, os

defaultPort = 8080
serverPort = 8001
MAX_QUEUE = 50
BUFFER_SIZE = 4096
class ProxyFactory(http.HTTPFactory):
        protocol = proxy.Proxy


def main():
    correctInput = False
    while correctInput == False:
        try:
            inputText = input('Hello, type start to start or type "setup" to enter set up: ')

            if(inputText == 'start'):
                correctInput = True
                start()
                

            elif(inputText == 'setup'):
                correctInput = True
                display_Options()
                
            else:
                print("ERROR - Try that input again")
        except KeyboardInterrupt:
            print()
            print(" ... Keyboard Interupt ... Exiting ... ")
            exit()


def start()
