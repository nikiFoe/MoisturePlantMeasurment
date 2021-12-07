from datetime import datetime
import random
import sqlite3
import time
import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from socket import gethostbyname, gaierror

import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import serial

import schedule
from threading import Thread

global connectionSQL
global cursor

def evaluationThread(time):
    try:
        evaluateData(time)
        sendDataMail()
        print('thread is done.')
    except Exception as e:
        print(str(e))

def do_something(time):
    thread = Thread(target = evaluationThread, args = time)
    thread.start()

def test(sql, cursos):
    sql.close()
    evaluateData()
    sendDataMail()

def creatNewSQLTable(last_time, first_iteration):
    try:
        if first_iteration:
            new_time = last_time
        else:
            new_time = datetime.now().strftime('%H_%M')

        sql_command = """CREATE TABLE {0} ( 
                        _number INTEGER PRIMARY KEY, 
                        _time DATE, 
                        _sensor varchar(255), 
                        _humidity INTEGER);""".format(str(new_time))


        cursor.execute(sql_command)
        if first_iteration:
            do_something(last_time)

        connectionSQL.commit()
        return new_time #, connectionSQL, cursor
    except sqlite3.OperationalError:
        print("Table already existing")
        return new_time




def openSQL():
    connectionSQL = sqlite3.connect("humidity.db")
    cursor = connectionSQL.cursor()
    try:
        sql_command = """
                                        CREATE TABLE humid ( 
                                        _number INTEGER PRIMARY KEY,
                                        _time DATE,
                                        _sensor varchar(255), 
                                        _humidity INTEGER);"""

        cursor.execute(sql_command)
    except sqlite3.OperationalError:
        print("Table already existing")

    statement = "SELECT _number AS names FROM humid ORDER BY _number DESC LIMIT 1"
    element = cursor.execute(statement)
    lastEntry = element.fetchone()[0]
    return connectionSQL, cursor, lastEntry

def safeSQL(conSQL):
    conSQL.commit()


def receivingDateLoop():
    #ser = serial.Serial('/dev/ttyACM0', 9600)
    ser = serial.Serial('COM5', 9600)
    time.sleep(2)
    runningNumber = 0
    last_time= creatNewSQLTable(datetime.now().strftime('%H_%M'), True)
    print(last_time)
    schedule.every(2).minutes.do(creatNewSQLTable, time = last_time, first_iteration = False)
    runningNumber = runningNumber + 1
    #print(runningNumber)
    while True:
        #try:
        line = ser.readline()  # read a byte
        if line:
            times = datetime.now().strftime('%d.%m-%H:%M:%S')
            string = line.decode()  # convert the byte string to a unicode string
            humidity = int(string[3:])  # convert the unicode string to an int
            sensor = string[0:2]
            print(last_time)
            format_str_v1 = """INSERT INTO {time} """.format(time = last_time)
            format_str_v2 = """"(_number, _time, _sensor, _humidity) 
                            VALUES ("{_number}", "{_time}", "{_sensor}","{_humidity}");"""

            print(format_str_v1)

            sql_command = format_str_v2.format(_number = runningNumber,  _time = times, _sensor = sensor, _humidity = humidity)
            cursor.execute(format_str_v1 + sql_command)
            runningNumber = runningNumber + 1
            schedule.run_pending()

            #print(humidity)
            if runningNumber%30 == 0:
                safeSQL(connectionSQL)
                #if runningNumber%30==0:
                #    test(connectionSQL, cursor)
                #evaluateData()
                #sendDataMail()
                #connectionSQL, cursor, runningNumber = openSQL()
                runningNumber = runningNumber + 1


        """except gaierror:
            print("Connection to Email-Service lost.")
        except Exception as e:
            #ser = serial.Serial('COM5', 9600)
            #time.sleep(2)
            print(str(e))
            print("SEL")"""



def evaluateData(time):
    #con = sqlite3.connect("humidity.db")
    #cursor = con.cursor()
    #con = pyodbc.connect("humidity.db")
    query = """SELECT _number, 
                _time,
                _sensor,
                _humidity
               FROM {};""".format(time)
    a = cursor.execute(query)




    TM1 = pd.read_sql(query, connectionSQL)

    #TM1 = TM.head(100)

    s1Index = []
    s2Index = []
    s3Index = []
    sxAxes = []

    count = 0
    for count, item in enumerate(TM1['_sensor'].str.findall('s1'), start = 0):
        if item:
            s1Index.append(TM1['_humidity'][count])
            sxAxes.append(TM1['_time'][count])

    count = 0
    for count, item in enumerate(TM1['_sensor'].str.findall('s2'), start = 0):
        if item:
            s2Index.append(TM1['_humidity'][count])

    count = 0
    for count, item in enumerate(TM1['_sensor'].str.findall('s3'), start = 0):
        if item:
            s3Index.append(TM1['_humidity'][count])

    plt.scatter(sxAxes[:len(s1Index)], s1Index)
    plt.scatter(sxAxes[:len(s2Index)], s2Index)
    plt.scatter(sxAxes[:len(s3Index)], s3Index)
    #plt.scatter( TM1['_number'], TM1['_humidity'])
    plt.xlabel("Timer", fontsize = 16)
    plt.ylabel("Moisture Value", fontsize = 16)
    plt.title("Moisture", fontsize = 25)
    plt.xticks(rotation = 45)
    plt.tight_layout()
    plt.savefig("Moisture.jpg")
    plt.close()



def sendDataMail():
    mail_content = '''Hello'''
    sender_address = 'moisture.sensorumea@gmail.com'
    sender_pass = '43A7BC_A'
    receiver_address = 'foerster.niklas96@gmx.de'
    # Setup the MIME
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = receiver_address
    message['Subject'] = 'A test mail sent by Python. It has an attachment.'
    # The subject line
    # The body and the attachments for the mail
    message.attach(MIMEText(mail_content, 'plain'))
    attach_file_name = 'Moisture.jpg'
    #attach_file = open(attach_file_name, 'rb')  # Open the file as binary mode
    with open(attach_file_name, 'rb') as fp:
        payload = MIMEImage(fp.read())
        #payload = MIMEImage('application', 'octate-stream')
        #payload.set_payload((attach_file).read())
        #encoders.encode_base64(payload)  # encode the attachment
        # add payload header with filename
        payload.add_header('Content-Decomposition', 'attachment', filename = attach_file_name)
        message.attach(payload)
    # Create SMTP session for sending the mail
    session = smtplib.SMTP('smtp.gmail.com', 587)  # use gmail with port
    session.starttls()  # enable security
    session.login(sender_address, sender_pass)  # login with mail_id and password
    text = message.as_string()
    session.sendmail(sender_address, receiver_address, text)
    session.quit()


if __name__ == "__main__":
    connectionSQL = sqlite3.connect("humidity.db")
    cursor = connectionSQL.cursor()
    receivingDateLoop()
    #sendDataMail()
    #evaluateData()
    #readSerialport()


