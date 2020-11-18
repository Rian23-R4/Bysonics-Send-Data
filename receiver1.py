import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import time
import os
import sys
import requests
import numpy as np
from sklearn.linear_model import OrthogonalMatchingPursuit
from sklearn.linear_model import OrthogonalMatchingPursuitCV
import multiprocessing

broker_address = "192.168.43.246"

Y = 52
M = 129
N = 256
L = Y/N*100
row = 1
col = 1
Q = [[0], [0]]
Bstart = False
sensor = 1
real = []
imag = []
realZ = []
imagZ = []
array = []
z = 0
i = 0
col = 0
urlSensor = ''
id_rompi: ""
id_sensor: ""
id_pasien: ""
data: ""
AcceX = []
AcceY = []
AcceZ = []
start = time.time()

for x in range(Y-2):
    Q.append([0])
for x in range(Y):
    for y in range(M-1):
        Q[x].append(0)

Log = 0
# Gaussian = np.loadtxt(fname="Gaussian26x65.txt")
Gaussian = np.loadtxt(fname="Gaussian52x129.txt")

for x in range(Y):
    for y in range(M):
        Q[x][y] = Gaussian[Log]
        Log += 1


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
        os.system('cls')
        print('Selesai ESP1')
        exit()

    else:
        y1 = item[: item.find(',')]
        y = np.float_(y1.replace(',', ''))
        real = np.append(real, y)
        o1 = item[item.find(',')+1:]
        o = np.float_(o1.replace(',', ''))
        imag = np.append(imag, o)
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


def print_square(num, AcceX2, AcceY2, data):
    arr = []
    arr = np.array(data.real)
    arr2 = []
    arr2 = arr.tolist()
    myList = [int(x) for x in arr2]
    if num == 1 or num == 2 or num == 6 or num == 7:
        start = time.time()
        if num == 1:
            data = {
                "id_rompi": "001",
                "id_sensor": "PPG01",
                "id_pasien": "000003",
                "dataPPG": myList
            }
            url_POST = ('https://bysonics-alpha001.herokuapp.com/dataPPG/save')
        elif num == 2:
            data = {
                "id_rompi": "001",
                "id_sensor": "EKG01",
                "id_pasien": "000003",
                "dataEKG": myList
            }
            url_POST = ('https://bysonics-alpha001.herokuapp.com/dataEKG/save')
        elif num == 6:
            data = {
                "id_rompi": "001",
                "id_sensor": "EMG01",
                "id_pasien": "000003",
                "dataEMG": myList
            }
            url_POST = ('https://bysonics-alpha001.herokuapp.com/dataEMG/save')
        elif num == 7:
            data = {
                "id_rompi": "001",
                "id_sensor": "Tmp01",
                "id_pasien": "000003",
                "dataSuhu": myList
            }
            url_POST = (
                'https://bysonics-alpha001.herokuapp.com/dataSuhu/save')
        # response = requests.post(
        #     "https://bysonics-alpha001.herokuapp.com/recording/start")
        # print(f"Request returned {response.status_code} : '{response.reason}'")
        # payload = response.content
        # import pprint
        # pp = pprint.PrettyPrinter(indent=1)
        # pp.pprint(payload)
        response = requests.post(url_POST, None, data)
        print(f"Request returned {response.status_code} : '{response.reason}'")
        payload = response.content
        import pprint
        pp = pprint.PrettyPrinter(indent=1)
        pp.pprint(payload)
        end = time.time()
        runTime = end - start
        print(f"Runtime of the program is {runTime} Second")
    else:
        # response = requests.post(
        #     "https://bysonics-alpha001.herokuapp.com/recording/start")
        # print(f"Request returned {response.status_code} : '{response.reason}'")
        # payload = response.content
        # import pprint
        # pp = pprint.PrettyPrinter(indent=1)
        # pp.pprint(payload)
        if num == 5:
            startAcc = time.time()
            AcceZ = myList
            data = {
                "id_rompi": "001",
                "id_sensor": "Acc01",
                "id_pasien": "000003",
                "dataAccelerometer_X": AcceX2,
                "dataAccelerometer_Y": AcceY2,
                "dataAccelerometer_Z": AcceZ
            }
            url_POST = (
                'https://bysonics-alpha001.herokuapp.com/dataAccelerometer/save')
            response = requests.post(url_POST, None, data)
            print(
                f"Request returned {response.status_code} : '{response.reason}'")
            payload = response.content
            import pprint
            pp = pprint.PrettyPrinter(indent=1)
            pp.pprint(payload)
            end = time.time()
            runTime = end - startAcc
            print(f"Runtime of the program is {runTime} Second")


def CS_():
    global array, real, imag, realZ, imagZ, sensor, runTime, z, AcceX, AcceY, myList, Q
    print(sensor)

    omp1 = OrthogonalMatchingPursuit(n_nonzero_coefs=M)
    omp1.fit(Q, real)
    coefreal = omp1.coef_

    omp2 = OrthogonalMatchingPursuit(n_nonzero_coefs=M)
    omp2.fit(Q, imag)
    coefimag = omp2.coef_

    realZ = []
    realQ = coefreal[0]
    realW = coefreal[M-1]
    realX = coefreal[1:M-1]
    realY = realX[::-1]
    realZ = np.append(realZ, realQ)
    realZ = np.append(realZ, realX)
    realZ = np.append(realZ, realW)
    realZ = np.append(realZ, realY)

    imagZ = []
    imagQ = coefimag[0]
    imagW = coefimag[M-1]
    imagX = coefimag[1:M-1]
    imagY = imagX[::-1]*-1
    imagZ = np.append(imagZ, imagQ)
    imagZ = np.append(imagZ, imagX)
    imagZ = np.append(imagZ, imagW)
    imagZ = np.append(imagZ, imagY)

    array = []
    for x in range(N):
        com = complex(realZ[x], imagZ[x])
        array = np.append(array, com)

    ftx = []
    ftx = np.fft.ifft(array)

    if sensor == 3:
        arr = []
        arr = np.array(ftx.real)
        arr2 = []
        arr2 = arr.tolist()
        myList = [int(x) for x in arr2]
        AcceX = myList
    elif sensor == 4:
        arr = []
        arr = np.array(ftx.real)
        arr2 = []
        arr2 = arr.tolist()
        myList = [int(x) for x in arr2]
        AcceY = myList

    p1 = multiprocessing.Process(
        target=print_square, args=(sensor, AcceX, AcceY, ftx,))
    p1.start()


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
            CS_()
            real = []
            imag = []
            i = 0
