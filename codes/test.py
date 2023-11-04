import socket, time
from random import randint 
import xml.etree.ElementTree as ET

from models.account import Account, account_exists
from models.base import Session, engine, Base


def receive_connection():
    newline_rec = False
    buffer = ''
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client_socket.bind(('localhost', 12345))
    client_socket.listen(5)
    c, addr = client_socket.accept()
    while not newline_rec:
        xml_size_bytes = c.recv(1)
        xml_size_str = xml_size_bytes.decode()
        if xml_size_str == '\n':
            newline_rec = True
        else:
            buffer += xml_size_str

    xml_size = int(buffer)
    action_xml = c.recv(xml_size)
    try:
        xml_tree = ET.fromstring(action_xml)
    except:
        print("XML was malformatted")
        return
    if xml_tree.tag == 'create':
        for entry in xml_tree:
            session = Session()
            if entry.tag == 'account':
             
                id = entry.attrib.get('id')
                balance = entry.attrib.get('balance')
                print(balance)
                if not account_exists(session, id):
                    newAcc = Account(id=id, balance=balance)
                    session.add(newAcc)
                    session.commit()
                else:
                    print("account alread exists error")
                return
            elif entry.tag == 'symbol':
      
                sym = entry.attrib.get('sym')
                for e in entry:
                    account = e.attrib.get('id')
                    amt = int(e.text)
                    print(sym)
                  
                pass
            else:
                raise Exception("Malformatted xml in create")
      
        return
    elif xml_tree.tag == 'transactions':

        account = xml_tree.attrib.get('id')
        for entry in xml_tree:
            if entry.tag == 'order':
                sym = entry.attrib.get('sym')
                amt = entry.attrib.get('amount')
                limit = entry.attrib.get('limit')
             
                order_id = randint(100, 1000000000)
               
                order_type = None
              
                print(account)
                pass
            elif entry.tag == 'cancel':
                id = entry.attrib.get('id')
              
                pass
            elif entry.tag == 'query':
                id = entry.attrib.get('id')
             
                pass
            else:
                raise Exception("Malformatted xml in transaction")
    else:
        raise Exception("Got an XML that did not follow format")

if __name__ == "__main__":
    receive_connection()