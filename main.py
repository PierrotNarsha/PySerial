 #-*- coding: utf-8 -*-
import serial
import time
import signal
import threading
import mysql.connector
import datetime

mysql_db = mysql.connector.connect(
    user='lautec',
    passwd='jointreeGood!@3',
    host='175.201.40.89',
    port=3306,
    db='lautec-erp',
    charset='utf8'
)

global ser
global pVal, hVal
global select_type

recv_data = [] #라인 단위로 데이터 가져올 리스트 변수

port = 'COM3' # 시리얼 포트
baud = 19200 # 시리얼 보드레이트(통신속도)

exitThread = False   # 쓰레드 종료용 변수


#쓰레드 종료용 시그널 함수
def handler(signum, frame):
     exitThread = True

#본 쓰레드
def readThread():
    global recv_data
    global exitThread
    global ser
    global mysql_db
    global pVal
    global hVal
    global select_type

    # 쓰레드 종료될때까지 계속 돌림
    while not exitThread:
        #데이터가 있있다면

        time.sleep(2)

        # for c in ser.read():
        #     recv_data.append(str(chr(c)))
        #
        #     if recv_data[-1] == '&': #라인의 끝을 만나면..
        #         #데이터 처리 함수로 호출
        #
        #         test = str(recv_data)
        #
        #         if recv_data[0] == 'P':
        #             # f = int(recv_data[2]) * 1000
        #             # s = int(recv_data[3]) * 100
        #             # t = int(recv_data[4]) * 10
        #             # fo = int(recv_data[5])
        #             # hap = f + s + t + fo
        #             code = 1
        #         elif recv_data[0] == 'H':
        #             code = 2

        if select_type == '1':

            print()

            try:
                mysql_cursor = mysql_db.cursor(dictionary=True)

                sql = "INSERT INTO assembly_test (product_code, production_qty) VALUES (%s, %s)"
                val = (select_type, 1)

                mysql_cursor.execute(sql, val)

                mysql_db.commit()

                recv_data = []
            except Exception as e:
                print(e)

    mysql_db.close()


if __name__ == "__main__":
    #종료 시그널 등록

    global ser
    global pVal
    global hVal
    global select_type

    select_type = input("type : ")

    dt = str(datetime.date.today())

    data_list = []

    try:
        mysql_cursor = mysql_db.cursor(buffered=True, dictionary=True)

        sql = "SELECT input_date , product_code, sum(production_qty) FROM assembly_work_results where input_date='"+dt+"' group by input_date, product_code;"

        mysql_cursor.execute(sql)

        for ddd in mysql_cursor:
            data_list.append(ddd)

        mysql_db.commit()

        if data_list == []:
            pVal = 0
            hVal = 0
        else:
            for data in data_list:
                if data['product_code'] == 1:
                    pVal = data['sum(production_qty)']
                else:
                    hVal = data['sum(production_qty)']

    except Exception as e:
        print(e)

    signal.signal(signal.SIGINT, handler)

    re_count = 0

    #시리얼 열기
    while True:
        try:
            ser = serial.Serial(port=port, baudrate=baud, stopbits=1, timeout=0)
            if ser is not None:
                print('connected')
                break
        except:
            re_count += 1
            print('Reconnect serial port by' + port + 'for later 10 sec.\nReconnect count : ' + str(re_count))
            time.sleep(10)

    #시리얼 읽을 쓰레드 생성
    thread = threading.Thread(target=readThread)

    #시작!
    thread.start()

