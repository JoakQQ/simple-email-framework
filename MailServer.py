import socket
import threading
import struct
import time
import sys

#constants
MAX_USERS = 10 # maximum number of users server is listening to

def user_password(name):
    try:
        f = open("ClientInfo.txt", "r")
    except IOError as emsg:
        print("Open info file error: ", emsg)
        print("Exiting server thread ...")
        sys.exit(1)

    contents = f.read().split("\n")
    if name not in contents:
        return None
    return contents[contents.index(name) + 1]

def write_email(socket, recipient, sender, title):
    timenow = time.strftime("%a, %d %b %Y %I:%M:%S %Z", time.gmtime())
    contents = "*FROM " + sender + "\nTITLE " + title + "\nTIME " + timenow + "\n"
    decoded_data = None
    while decoded_data != ".":
        try:
            data = socket.recv(1024)
        except error as emsg:
            print("Socket recieve error: ", emsg)
            print("Exiting server thread ...")
            sys.exit(1)

        decoded_data = data.decode(encoding='utf-8')
        if decoded_data == ".":
            contents += ("\n")
        else:
            contents += (decoded_data + "\n")

    if recipient == "":
        return 200, "Recipient is missing"
    elif title == "":
        return 200, "Title is missing"

    filename = recipient + ".txt"
    try:
        f = open(filename, "a")
    except IOError as emsg:
        print("File IO error: ", emsg)
        print("Exiting server thread ...")
        sys.exit(1)

    f.write(contents)
    f.close()
    return 250, "Content ok"

def retrieve_email(socket, name, num):
    content_list = []
    filename = name + ".txt"
    try:
        f = open(filename, "r")
    except IOError as emsg:
        print("File " + filename + " does not exist")
        try:
            socket.send(bytes(".", encoding='utf-8'))
            return
        except error as emsg:
            print("Send content error: ", emsg)
            print("Exiting server thread ...")
            sys.exit(1)
    contents = f.read().split("\n")
    try:
        for line in contents:
            if "*FROM " in line or "FROM " in line:
                content_list.append(line + "\n")
            elif line != "\n":
                content_list[len(content_list) - 1] += line + "\n"
    except IndexError as emsg:
        print("Client does not have mail")
        try:
            socket.send(bytes(".", encoding='utf-8'))
            return
        except error as emsg:
            print("Send content error: ", emsg)
            print("Exiting server thread ...")
            sys.exit(1)

    if content_list[num - 1][0] == "*":
        content_list[num - 1] = content_list[num - 1].lstrip("*")
        f = open(filename, "w")
        for content in content_list:
            f.write(content)
        f.close()


    content_to_send = content_list[num - 1].split("\n")
    for i in range(len(content_to_send) + 1):
        time.sleep(0.01)
        if i == len(content_to_send):
            try:
                socket.send(bytes(".", encoding='utf-8'))
            except error as emsg:
                print("Send content error: ", emsg)
                print("Exiting server thread ...")
                sys.exit(1)
        else:
            try:
                socket.send(bytes(content_to_send[i], encoding='utf-8'))
            except error as emsg:
                print("Send content error: ", emsg)
                print("Exiting server thread ...")
                sys.exit(1)

def delete_email(num, name):
    content_list = []
    filename = name + ".txt"
    f = open(filename, "r")
    contents = f.read().split("\n")
    for line in contents:
        if "*FROM " in line or "FROM " in line:
            content_list.append(line + "\n")
        elif line != "\n":
            content_list[len(content_list) - 1] += line + "\n"
    f.close()

    content_list.pop(num - 1)

    f = open(filename, "w")
    for content in content_list:
        f.write(content)
    f.close()

def list_email(socket, name):
    content_list = []
    filename = name + ".txt"
    try:
        f = open(filename, "r")
    except IOError:
        print("File " + filename + " does not exist")
        try:
            socket.send(bytes(".", encoding='utf-8'))
            return
        except error as emsg:
            print("Send content error: ", emsg)
            print("Exiting server thread ...")
            sys.exit(1)
    contents = f.read().split("\n")
    for line in contents:
        if "*FROM " in line:
            content_list.append("*" + str(len(content_list) + 1) + " " + line.lstrip("*") + " ")
        elif "FROM " in line:
            content_list.append(str(len(content_list) + 1) + " " + line + " ")
        elif "TITLE " in line:
            content_list[len(content_list) - 1] += line + " "
        elif "TIME " in line:
            content_list[len(content_list) - 1] += line + " "
    f.close()

    for i in range(len(content_list) + 1):
        packed_content = None
        content = None

        if i == len(content_list):
            content = "."
        else:
            content = content_list[i]

        try:
            socket.send(bytes(content, encoding='utf-8'))
        except error as emsg:
            print("Send content error: ", emsg)
            print("Exiting server thread ...")
            sys.exit(1)

def command_handler(socket, signal_pack, userinfo):
    logged_in = False # whether an user is logged in or not
    recipient = ""
    title = ""

    while True:
        send_status = True
        response_status = None
        response_content = None
        packed_response = None

        try:
            recv_command = socket.recv(1024)
        except error as emsg:
            print("Socket recieve error: ", emsg)
            print("Exiting server thread ...")
            sys.exit(1)

        try:
            command_num, command_arg = signal_pack.unpack(recv_command)
        except struct.error as emsg:
            print("Unpack package error: ", emsg)
            print("Exiting server thread ...")
            sys.exit(1)

        decoded_command_arg = command_arg.strip(b'\x00').decode(encoding='utf-8')

        if command_num == 0:
            if logged_in == True:
                response_status = 200
                response_content = "Already logged in"
            else:
                userinfo["username"] = decoded_command_arg
                userinfo["password"] = user_password(userinfo["username"])

                if userinfo["password"] is not None:
                    response_status = 250
                    response_content = "Username ok"
                else:
                    response_status = 200
                    response_content = "Username does not exist"

        elif command_num == 1:
            if logged_in == True:
                response_status = 200
                response_content = "Already logged in"
            else:
                if userinfo["username"] is not None and userinfo["username"] != "":
                    if userinfo["password"] == decoded_command_arg:
                        # success login
                        logged_in = True
                        response_status = 250
                        response_content = "User authenticated"
                    else:
                        response_status = 200
                        response_content = "Authentication failure"
                else:
                    response_status = 200
                    response_content = "Username is missing"

        elif logged_in == True:
            if command_num == 2:
                if decoded_command_arg != "":
                    if user_password(decoded_command_arg) is not None:
                        response_status = 250
                        response_content = "Recipient ok"
                        recipient = decoded_command_arg
                    else:
                        response_status = 200
                        response_content = "Recipient does not exist on the server"
                        recipient = ""
                else:
                    response_status = 200
                    response_content = "Recipient is missing"
                    recipient = ""
            elif command_num == 3:
                if recipient != "":
                    response_status = 250
                    response_content = "Title ok"
                    title = decoded_command_arg
                else:
                    response_status = 200
                    response_content = "Recipient is missing"
                    title = ""
            elif command_num == 4:
                response_status, response_content = write_email(socket, recipient, userinfo["username"], title)
            elif command_num == 5:
                send_status = False
                list_email(socket, userinfo["username"])
            elif command_num == 6:
                send_status = False
                if decoded_command_arg != "":
                    try:
                        n = int(decoded_command_arg)
                        retrieve_email(socket, userinfo["username"], n)
                    except ValueError:
                        try:
                            socket.send(bytes(".", encoding='utf-8'))
                        except error as emsg:
                            print("Send content error: ", emsg)
                            print("Exiting server thread ...")
                            sys.exit(1)
                    except IndexError:
                        try:
                            socket.send(bytes(".", encoding='utf-8'))
                        except error as emsg:
                            print("Send content error: ", emsg)
                            print("Exiting server thread ...")
                            sys.exit(1)
                else:
                    try:
                        socket.send(bytes(".", encoding='utf-8'))
                    except error as emsg:
                        print("Send content error: ", emsg)
                        print("Exiting server thread ...")
                        sys.exit(1)
            elif command_num == 7:
                if decoded_command_arg != "":
                    try:
                        n = int(decoded_command_arg)
                        delete_email(n, userinfo["username"])
                        response_status = 250
                        response_content = "Delete ok"
                    except IndexError as emsg:
                        print("Client deleting email out of range")
                        response_status = 200
                        response_content = "Index of email out of range"
                    except ValueError as emsg:
                        print("Integer convertion error: ", emsg)
                        response_status = 200
                        response_content = "Index of email should be integer"
                    except IOError as emsg:
                        print("File IO error: ", emsg)
                        print("Exiting server thread ...")
                        sys.exit(1)
                    except error as emsg:
                        print("Unexpected error: ", emsg)
                        print("Exiting server thread ...")
                        sys.exit(1)
                else:
                    response_status = 200
                    response_content = "Index of email is missing"
            if command_num == 8:
                try:
                    packed_response = signal_pack.pack(250, bytes("Exit ok", encoding='utf-8'))
                except struct.error as emsg:
                    print("Pack status response error: ", emsg)
                    print("Exiting server thread ...")
                    sys.exit(1)
                try:
                    socket.send(packed_response)
                except error as emsg:
                    print("Send response error: ", emsg)
                    print("Exiting server thread ...")
                    sys.exit(1)

                print("Client disconnected")
                print("Exiting server thread ...")
                sys.exit(0)
        elif logged_in == False:
            if command_num == 5 or command_num == 6:
                try:
                    print(".")
                    socket.send(bytes(".", encoding='utf-8'))
                except error as emsg:
                    print("Send response error: ", emsg)
                    print("Exiting server thread ...")
                    sys.exit(1)
                continue
            else:
                response_status = 200
                response_content = "User not logged in yet"
            
        print(response_status)
        print(response_content)
        # pack status
        if send_status == True:
            try:
                packed_response = signal_pack.pack(response_status, bytes(response_content, encoding='utf-8'))
            except struct.error as emsg:
                print("Pack status response error: ", emsg)
                print("Exiting server thread ...")
                sys.exit(1)
            try:
                socket.send(packed_response)
            except error as emsg:
                print("Send response error: ", emsg)
                print("Exiting server thread ...")
                sys.exit(1)

class ServerThread(threading.Thread):
    def __init__(self, client, signal_pack):
        threading.Thread.__init__(self)
        self.client = client
        self.signal_pack = signal_pack
        self.userinfo = {"username" : None, "password" : None}

    def run(self):
        connectionSocket, addr = self.client

        command_handler(connectionSocket, self.signal_pack, self.userinfo)

        connectionSocket.close()

class ServerMain:
    def server_run(self):
        # struct
        try:
            signal_pack = struct.Struct('I 512s')
        except struct.error as emsg:
            print("Struct error: ", emsg)
            print("Exiting program ...")
            sys.exit(1)

        # server connection
        serverPort = 12000

        try:
            serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            serverSocket.bind(("", serverPort))
            serverSocket.listen(MAX_USERS)
        except error as emsg:
            print("Socket error: ", emsg)
            print("Exiting program ...")
            sys.exit(1)

        print("Mail server is ready")
        # threading
        while True:
            try:
                client = serverSocket.accept()
            except error as emsg:
                print("Socket acception error: ", emsg)

            t = ServerThread(client, signal_pack)
            t.start()

if __name__ == '__main__':
	server = ServerMain()
	server.server_run()
