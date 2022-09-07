import os
import sys
import socket
from threading import Thread, Lock
import paramiko
from shlex import split

def parse_input_args(args): # parse input arguments
    try:
        if "-p" in args:
            i = args.index("-p")
            if not (i + 1 >= len(args)):
                port = args[i + 1]
        return int(port)
    except:
        print("\033[91mMissing or invalid input parameters")
        exit(1)

def exec_command(command, channel, fs): # executes a shell program
    parts = split(command)
    print(parts)
    program = parts[0]
    if program == 'ls':
        out = ''
        for element in fs.keys():
            out += element + '  '
        if out:
            out += '\n'
        channel.sendall(out.encode())
    elif program == 'echo':
        if not len(parts) == 4:
            channel.sendall("echo: Wrong arguments\n".encode())
        else:
            text = parts[1]
            filename = parts[3]
            if ".txt" not in filename[-4:]:
                channel.sendall("echo: Unknown file extension\n".encode())
            else:
                fs[filename] = text
    elif program == 'cat':
        if not len(parts) == 2:
            channel.sendall("cat: Wrong arguments\n".encode())
        else:
            filename = parts[1]
            if ".txt" not in filename[-4:]:
                channel.sendall("cat: Unknown file extension\n".encode())
            else:
                file_content = fs.get(filename, 0)
                if file_content:
                    channel.sendall(file_content.encode())
                    channel.sendall("\n".encode())
                else:
                    out = "cat: file " + filename + " not found\n"
                    channel.sendall(out.encode())
    elif program == 'cp':
        if not len(parts) == 3:
            channel.sendall("cp: Wrong arguments\n".encode())
        else:
            source = parts[1]
            destination = parts[2]
            if ".txt" not in source[-4:] or ".txt" not in destination[-4:]:
                channel.sendall("cp: Unknown file extension\n".encode())
            else:
                source_content = fs.get(source, 0)
                if source_content:
                    fs[destination] = source_content
                else:
                    out = "cp: file " + source + " not found\n"
                    channel.sendall(out.encode())
    else:
        output = program + " : command not found\n"
        channel.sendall(output.encode())

def fake_shell(channel, username): # mimics a shell
    channel.settimeout(60)
    fs = dict()
    while True:
        try:
            shell_prefix = username + '@remotehost:/$ '
            channel.sendall(shell_prefix.encode())
            buffer = b''
            while b'\n' not in buffer:
                buffer += channel.recv(1)
                if not buffer:
                    break
            if buffer:
                exec_command(buffer.decode().strip(), channel, fs)
        except Exception as e:
            print("Exception occurred: ", e)
            channel.close()
            break

class sshServer(paramiko.ServerInterface):
    def __init__(self, attempts, lock):
        self.username = None
        self.attempts = attempts
        self.lock = lock

    def check_channel_request(self, kind, chanid):
        return paramiko.OPEN_SUCCEEDED

    def get_allowed_auths(self, username):
        return 'password'

    def check_auth_password(self, username, password): # ssh authorization
        with self.lock:
            attemptno = self.attempts.get(username, 0)
            if attemptno:
                self.attempts[username] += 1
                if self.attempts[username] >= 5:
                    self.username = username
                    return paramiko.AUTH_SUCCESSFUL
            else:
                self.attempts[username] = 1
            return paramiko.AUTH_FAILED

    def check_channel_shell_request(self, channel):
        shell = Thread(target=fake_shell, args=[channel, self.username])
        shell.start()
        return True

def retrieve_key(): # generates a private key for the ssh server or retrieves it from file (if it exists)
    if os.path.exists('serverkey'):
        key = paramiko.RSAKey.from_private_key_file(filename="serverkey")
    else:
        key = paramiko.RSAKey.generate(1024)
        key.write_private_key_file(filename="serverkey")
    return key

def main():
    if os.getuid() != 0:
        print("I need root privileges to run")
        exit(1)

    port = parse_input_args(sys.argv[1:])
    key = retrieve_key()
    print("\033[93m########## \033[92mHONEYPORT ACTIVE \033[93m############\033[0m")
    try:
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serverSocket.bind(('localhost', port))
        serverSocket.listen(5)
        attempts = dict() # dictionary that keeps track of the number of attempted logins to a specific account
        lock = Lock() # lock used to avoid race conditions when the dictionary is manipulated by different concurrent threads
        while True:
            client, addr = serverSocket.accept()
            print("Connected to ", addr)
            server = sshServer(attempts, lock)
            transport = paramiko.Transport(client)
            transport.add_server_key(key)
            transport.start_server(server=server)
    except Exception as e:
        print("\033[93m########## \033[92mHONEYPORT STOPPED \033[93m############")
        print(e)

if __name__ == "__main__":
    main()
