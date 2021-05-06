import socket
import re
import numpy as np
import time
import signal
import threading
import mysql.connector


mysql_db = mysql.connector.connect(
    user='dev',
    passwd='jointreeGood!@3',
    host='175.201.40.89',
    port=3306,
    db='hyunjin-erp',
    charset='utf8'
)

#tcp port
PORT = 7001
host = '192.168.100.2'
exitThread = False

#쓰레드 종료용 시그널 함수
def handler(signum, frame):
     exitThread = True


def read_register(client):
    '''
        Finally used the ASCII code
    '''

    global exitThread
    global PORT
    global host

    while not exitThread:

        res = client.recv(1024)

        if res is not None:
            print(res)

            code = 1

            try:
                mysql_cursor = mysql_db.cursor(dictionary=True)

                sql = "INSERT INTO assembly_test (product_code, production_qty) VALUES (%s, %s)"
                val = (code, 1)

                mysql_cursor.execute(sql, val)

                mysql_db.commit()
            except Exception as e:
                print(e.message)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, handler)

    re_count = 0

    while True:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except:
            re_count += 1
            print('Reconnect serial port by' + host + ':' + PORT + ' for later 10 sec.\nReconnect count : ' + str(re_count))
            time.sleep(10)
        if client is not None:
            print('connected')
            break
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, PORT))

    thread = threading.Thread(target=read_register, args=(client,))

    thread.start()


