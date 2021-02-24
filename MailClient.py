import socket
import struct
import sys

command_list = ["#USERNAME", # 0
                "#PASSWORD", # 1
                "#SENDTO",   # 2
                "#TITLE",    # 3
                "#CONTENT",  # 4
                "#LIST",     # 5
                "#RETRIEVE", # 6
                "#DELETE",   # 7
                "#EXIT"]     # 8
command_with_response = [0,1,2,3,7,8]

class clientMain:
    def client_run(self):
        # struct
        try:
            signal_pack = struct.Struct('I 512s')
        except struct.error as emsg:
            print("Struct error: ", emsg)
            print("Exiting program ...")
            sys.exit(1)

        # client connection
        serverName = "localhost"
        serverPort = 12000

        try:
            clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            clientSocket.connect((serverName, serverPort))
        except error as emsg:
            print("Socket error: ", emsg)
            print("Exiting program ...")
            sys.exit(1)


        while True:
            command = input("Client: ").split(" ")
            command_sec_arg = ""
            for i in range(len(command) - 1):
                if i == len(command) - 2:
                    command_sec_arg += command[i + 1]
                else:
                    command_sec_arg += command[i + 1] + " "
            if command[0] not in command_list:
                print("Client: Invaild command")
            else:
                command_num = command_list.index(command[0])
                try:
                    packed_command = signal_pack.pack(command_num, bytes(command_sec_arg, encoding='utf-8'))
                except struct.error as emsg:
                    print("Unpack package error: ", emsg)
                    print("Exiting client ...")
                    sys.exit(1)
                try:
                    clientSocket.send(packed_command)
                except error as emsg:
                    print("Send package error: ", emsg)
                    print("Exiting client ...")
                    sys.exit(1)

                if command_num == 4:
                    input_data = None
                    while input_data != ".":
                        input_data = input("Client: ")
                        try:
                            clientSocket.send(bytes(input_data, encoding='utf-8'))
                        except error as emsg:
                            print("Send package error: ", emsg)
                            print("Exiting client ...")
                            sys.exit(1)
                    server_msg = None
                    while server_msg is None:
                        try:
                            data = clientSocket.recv(1024)
                        except error as emsg:
                            print("Recieve error: ", emsg)
                            print("Exiting client ...")
                            sys.exit(1)
                        try:
                            status, arg = signal_pack.unpack(data)
                        except struct.error as emsg:
                            print("Unpack package error: ", emsg)
                            print("Exiting client ...")
                            sys.exit(1)
                        decoded_arg = arg.strip(b'\x00').decode(encoding='utf-8')
                        server_msg = str(status) + " " + decoded_arg
                    print("Server: " + server_msg)
                elif command_num == 5 or command_num == 6:
                    server_msg = None
                    while server_msg is None or server_msg != ".":
                        try:
                            data = clientSocket.recv(1024)
                        except error as emsg:
                            print("Recieve error: ", emsg)
                            print("Exiting client ...")
                            sys.exit(1)
                        server_msg = data.strip(b'\x00').decode(encoding='utf-8')
                        print("Server: " + server_msg)
                else:
                    server_msg = None
                    while server_msg is None:
                        try:
                            data = clientSocket.recv(1024)
                        except error as emsg:
                            print("Recieve error: ", emsg)
                            print("Exiting client ...")
                            sys.exit(1)
                        try:
                            status, arg = signal_pack.unpack(data)
                        except struct.error as emsg:
                            print("Unpack package error: ", emsg)
                            print("Exiting client ...")
                            sys.exit(1)
                        decoded_arg = arg.strip(b'\x00').decode(encoding='utf-8')
                        server_msg = str(status) + " " + decoded_arg
                    print("Server: " + server_msg)

                    if command_num == 8:
                        clientSocket.close()
                        sys.exit(0)

if __name__ == '__main__':
    client = clientMain()
    client.client_run()
