import argparse 
from honeypot import *

# Parse Arguments

if __name__ == "__main__" :
    parser = argparse.ArgumentParser()
    
    parser.add_argument('-a', '--address', type=str, required=True)
    parser.add_argument('-p', '--port', type=int, required=True)
    parser.add_argument('-u', '--username', type=str)
    parser.add_argument('-pw', '--password', type=str)
    
    parser.add_argument('-s', '--ssh', action="store_true") # action="store_true" means that if the arg has been triggered, it will return True, otherwise it is False.
    parser.add_argument('-w', '--http', action="store_true")
    
    args = parser.parse_args() # collect all the argument and add it to the variable that given.
    
    try :
        if args.ssh :
            print("[-] Running SSH Honeypot...")
            honeypot(args.address, args.port, args.useername, args.password)
            
            if not args.username:
                username = None 
            if not args.password:
                password = None
        
        elif args.http :
            print("[-] Running HTTP WordPress Honeypot...")
            pass
        else :
            print("[!] Choose a honeypot type (SHH --ssh) or (HTTP --http).")
    except :
        print("\n Exiting HONEYPY...\n")