import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import time
import os
import sys
import requests
import numpy as np
import pymongo
import dns


os.system('cls')
broker_address = "192.168.43.246"

PPGReal = []
PPGImag = []
EKGReal = []
EKGImag = []
EMGReal = []
EMGImag = []
SUHUReal = []
SUHUImag = []
AcceXReal = []
AcceXImag = []
AcceYReal = []
AcceYImag = []
AcceZReal = []
AcceZImag = []

Y = 52
M = 129
N = 256
L = M/N*100
Gaussian = np.loadtxt(fname="Gaussian52x129.txt")

Bstart = False
i = 0


def restart_program():
    """Restarts the current program.
    Note: this function does not return. Any cleanup action (like
    saving data) must be done before calling this function."""
    os.system('cls')
    print("Auto-reconnect")
    python = sys.executable
    os.execl(python, python, * sys.argv)


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("ESP1")


def kirim_():
    dataDocument = {
        "PPG": {
            "real": PPGReal,
            "imag": PPGImag
        },
        "EKG": {
            "real": EKGReal,
            "imag": EKGImag
        },
        "EMG": {
            "real": EMGReal,
            "imag": EMGImag
        },
        "ACCX": {
            "real": AcceXReal,
            "imag": AcceXImag
        },
        "ACCY": {
            "real": AcceYReal,
            "imag": AcceYImag
        },
        "ACCZ": {
            "real": AcceZReal,
            "imag": AcceZImag
        },
        "SUHU": {
            "real": SUHUReal,
            "imag": SUHUImag
        },
    }
    collection.insert_one(dataDocument)


def on_message(client, userdata, msg):
    global real, imag, Bstart, i, sensor, runTime, start, workbook
    item = str(msg.payload.decode("utf-8"))
    if item[:5] == "Start":
        Bstart = True
        if item[6:] == "PPG":
            sensor = 1
        elif item[6:] == "EKG":
            sensor = 2
        elif item[6:] == "AcX":
            sensor = 3
        elif item[6:] == "AcY":
            sensor = 4
        elif item[6:] == "AcZ":
            sensor = 5
        elif item[6:] == "Myo":
            sensor = 6
        elif item[6:] == "Tmp":
            sensor = 7
        else:
            sensor = 0
    elif item == "END":
        startAcc = time.time()
        os.system('cls')
        print('Selesai ESP1')
        kirim_()
        end = time.time()
        runTime = end - startAcc
        print(f"Runtime of the program is {runTime} Second")
        # exit()
    else:
        y1 = item[: item.find(',')]
        y = np.float_(y1.replace(',', ''))
        real = np.append(real, y).tolist()
        o1 = item[item.find(',')+1:]
        o = np.float_(o1.replace(',', ''))
        imag = np.append(imag, o).tolist()
        i += 1


def on_subscribe(client, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))
    L = Y/N*100
    print('%i' % L)
    print('Aktifkan ESP')


def on_disconnect(client, userdata, rc):
    print("Client Disconnect")
    if rc != 0:
        print("Unexpected MQTT disconnection. Will auto-reconnect")
        restart_program()


def data_(real2, imag2):
    global PPGReal, PPGImag, EKGReal, EKGImag, EMGReal, EMGImag, SUHUReal, SUHUImag, AcceXReal, AcceXImag, AcceYReal, AcceYImag, AcceZReal, AcceZImag
    if sensor == 1:
        PPGReal = real2
        PPGImag = imag2
    elif sensor == 2:
        EKGReal = real2
        EKGImag = imag2
    elif sensor == 3:
        EMGReal = real2
        EMGImag = imag2
    elif sensor == 4:
        AcceXReal = real2
        AcceXImag = imag2
    elif sensor == 5:
        AcceYReal = real2
        AcceYImag = imag2
    elif sensor == 6:
        AcceZReal = real2
        AcceZImag = imag2
    elif sensor == 7:
        SUHUReal = real2
        SUHUImag = imag2


try:
    client = pymongo.MongoClient(
        "mongodb+srv://admin:admin@cluster0.eomgz.mongodb.net/Data_alpha001?retryWrites=true&w=majority")
    db = client.Data
    collection = db.Compressed
    print("connect to MongoDB")
except:
    print("Could not connect to MongoDB")
    exit()

client = mqtt.Client()
client.on_message = on_message
client.on_connect = on_connect
client.on_subscribe = on_subscribe
client.on_disconnect = on_disconnect
try:
    client.connect(broker_address)
except:
    restart_program()


if __name__ == '__main__':
    while True:
        client.loop()
        if Bstart == True:
            i = 0
            real = []
            imag = []
            Bstart = False
        elif i >= Y:
            print("CS Start")
            data_(real, imag)
            real = []
            imag = []
            i = 0
