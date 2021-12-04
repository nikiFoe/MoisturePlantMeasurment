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

def openSQL():
    connectionSQL = sqlite3.connect("humidity.db")
    cursor = connectionSQL.cursor()
    try:
        cursor.execute("""DROP TABLE humid;""")
    except:
        print("Table not existing")
    #sql_command = """
    #    CREATE TABLE humid (
    #    _number INTEGER PRIMARY KEY,
    #    _time DATE,
    #    _humidity INTEGER);"""

    sql_command = """
        CREATE TABLE humid ( 
        _number INTEGER PRIMARY KEY,
        _time DATE,
        _sensor varchar(255), 
        _humidity INTEGER);"""

    cursor.execute(sql_command)
    return connectionSQL, cursor

def safeSQL(conSQL):
    conSQL.commit()
    conSQL.close()


def receivingDateLoop():
    #ser = serial.Serial('/dev/ttyACM0', 9600)
    ser = serial.Serial('COM5', 9600)
    time.sleep(2)
    runningNumber = 0



    #connectionSQL = sqlite3.connect("humidity.db")
    #cursor = connectionSQL.cursor()
    #shouldRun = True
    #cursor.execute("""DROP TABLE humid;""")

    #sql_command = """
    #CREATE TABLE humid (
    #_number INTEGER PRIMARY KEY,
    #_time DATE,
    #_humidity INTEGER);"""

    #cursor.execute(sql_command)


    connectionSQL, cursor = openSQL()
    runningNumber = runningNumber + 1
    while True:
        try:
            line = ser.readline()  # read a byte
            if line:
                times = datetime.now().strftime('%d.%m-%H:%M:%S')
                string = line.decode()  # convert the byte string to a unicode string
                humidity = int(string[3:])  # convert the unicode string to an int
                sensor = string[0:2]

                format_str = """INSERT INTO humid (_number, _time, _sensor, _humidity)
                            VALUES ("{_number}", "{_time}", "{_sensor}","{_humidity}");"""

                sql_command = format_str.format(_number = runningNumber,  _time = times, _sensor = sensor, _humidity = humidity)
                cursor.execute(sql_command)
                runningNumber = runningNumber + 1

                #print(humidity)
                if runningNumber >= 9:
                    safeSQL(connectionSQL)
                    evaluateData()
                    sendDataMail()
                    connectionSQL, cursor = openSQL()
                    runningNumber = 1

        except gaierror:
            print("Connection to Email-Service lost.")
        except:
            print("Arduino lost.")



def evaluateData():
    con = sqlite3.connect("humidity.db")
    cursor = con.cursor()
    #con = pyodbc.connect("humidity.db")
    query = """SELECT _number, 
                _time,
                _sensor,
                _humidity
               FROM humid;"""
    a = cursor.execute(query)
    TM = pd.read_sql(query, con)

    TM1 = TM.head(100)

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


    plt.scatter(sxAxes[0:len(s1Index)], s1Index)
    plt.scatter(sxAxes[0:len(s2Index)], s2Index)
    plt.scatter(sxAxes[0:len(s3Index)], s3Index)
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
    receivingDateLoop()
    #sendDataMail()
    #evaluateData()
    #readSerialport()


