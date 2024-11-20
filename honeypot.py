# Libraries
import logging
import socket
import paramiko
import socket
import threading
from logging.handlers import RotatingFileHandler

# Constants
loggin_format = logging.Formatter('%(message)s')
SSH_BANNER = 'SSH-2.0-MySSHServer_1.0'

#host_key = 'server.key' # private key
host_key = paramiko.RSAKey(filename='server.key')

# Loggers & Logging files 
funnel_logger = logging.getLogger('FunnelLogger')
funnel_logger.setLevel(logging.INFO)
funnel_handler = RotatingFileHandler('audits.log', maxBytes=2000, backupCount=5)
funnel_handler.setFormatter(loggin_format)
funnel_logger.addHandler(funnel_handler)

creds_logger = logging.getLogger('CredsLogger')
creds_logger.setLevel(logging.INFO)
creds_handler = RotatingFileHandler('cmd_audits.log', maxBytes=2000, backupCount=5)
creds_handler.setFormatter(loggin_format)
creds_logger.addHandler(creds_handler)

# Emulated Shell

def emulated_shell(channel, client_ip) :
    channel.send(b'Vincent$') #$ means in the standard user permission (not in the elevated environment (sudo)
    command = b"" # listening for user input
    while True :
        char = channel.recv(1) # 1 is listening
        channel.send(char)
        if not char :
            channel.close()
        
        command += char
        
        if char == b'\r' :
            if command.strip() == b'exit' :
                response = b'\nGoodBye!\n'
                channel.close()
            elif command.strip() == b'pwd' :
                response = b'\\usr\\local' + b'\r\n'
                creds_logger.info(f"Command {command.strip()}" + " executed by " + f"{client_ip}")
            elif command.strip() == b'whoami' :
                response = b'\n' + b"CEO" + b'\r\n'
                creds_logger.info(f"Command {command.strip()}" + " executed by " + f"{client_ip}")
            elif command.strip() == b'ls' :
                response = b'\n' + b"sesame.conf" + b'\r\n'
                creds_logger.info(f"Command {command.strip()}" + " executed by " + f"{client_ip}")
            elif command.strip() == b'cat sesame.conf' :
                response = b'\n' + b"Go to abceo.com" + b'\r\n'
                creds_logger.info(f"Command {command.strip()}" + " executed by " + f"{client_ip}")
            else :
                response = b'\n' + bytes(command.strip()) + b'\r\n'
                creds_logger.info(f"Command {command.strip()}" + " executed by " + f"{client_ip}")
        
        
            channel.send(response)
            channel.send(b'Vincent$')
            command = b""

# SSH Server + Sockets

class Server(paramiko.ServerInterface) :
    
    def __init__(self, client_ip, input_username=None, input_password=None) :
        self.event = threading.Event()
        self.client_ip = client_ip 
        self.input_username = input_username
        self.input_password = input_password
    
    def check_channel_request(self, kind: str, chanid: int) -> int:
        if kind == 'session' : # if channel type is channel
            return paramiko.OPEN_SUCCEEDED
    
    def get_allowed_auth(self) :
        return "password" 
        
    def check_auth_password(self, username, password) :
        funnel_logger.info(f"Client {self.client_ip} attempted connection with " + f"username: {username}, " + f"password: {password}")
        creds_logger.info(f"{self.client_ip}, {username}, {password}")
        if self.input_username is not None and self.input_password is not None :
            if username == self.input_username and password == self.input_password :
                return paramiko.AUTH_SUCCESSFUL
            else :
                return paramiko.AUTH_FAILED
        else :
            return paramiko.AUTH_SUCCESSFUL
        
    def check_channel_shell_request(self, channel) :
        self.event.set()
        return True
    
    def check_channel_pty_request(self, channel: paramiko.Channel, term: bytes, width: int, height: int, pixelwidth: int, pixelheight: int, modes: bytes) :
        return True
    
    def check_channel_exec_request(self, channel, command) :
        command = str(command)
        return True
    
def client_handle(client, addr, username, password) :
    client_ip = addr[0]
    print(f"{client_ip} has connected to the server.")
    
    
    try :
        transport = paramiko.Transport(client)
        transport.local_version = SSH_BANNER
        Sserver = Server(client_ip=client_ip, input_username=username, input_password=password)
        
        transport.add_server_key(host_key)
        
        transport.start_server(server=Sserver)
        
        channel = transport.accept(100) # 100 seconds
        
        if channel is None :
            print("No channel was opened.")
        
        standard_banner = "Welcome!"
        channel.send(standard_banner)
        emulated_shell(channel, client_ip=client_ip)
    except Exception as error:
        print(error)
        print("Something wrong!")
    finally :
        try :
            transport.close()
        except Exception as error :
            print(error)
            print("Something wrong!")
        client.close()
        
# Provision SSH-based Honeypot

def honeypot(address, port, username, password) :
    
    socks = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # AF_INET - IPV4 addr, SOCK_STREAM - listening to TCP port
    socks.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    socks.bind((address,port))
    
    socks.listen(100) # max capacity is 100 users
    print(f"SSH server is listening on port: {port}")
    
    while True :
        try: 
            client, addr = socks.accept()
            ssh_honeypot_thread = threading.Thread(target=client_handle, args=(client, addr, username, password)) # args is according to the client_handle parameters.
            ssh_honeypot_thread.start()
            
        except Exception as error :
            print(error)

honeypot('192.168.56.1', 2250, 'Vincent', "password") # also can set to None