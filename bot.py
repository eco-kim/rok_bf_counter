import pyperclip as clip
import pyautogui as auto
import numpy as np
import time
from datetime import datetime
import pandas as pd
from src.positionInfo import *
from window_setup import bluestackWindow
from ppadb.client import Client as AdbClient
from config import *
from loc_extract import *
import pickle
import subprocess
from PIL import Image
from db import Database
from PyQt5.QtTest import QTest

# adb settings
client = AdbClient(host="127.0.0.1", port=5037)
client.remote_connect("localhost", int(deviceport))
adbdevice = client.device("localhost:"+str(deviceport))

positions = position()
scRegions = sc_region()

b_window = bluestackWindow()
b_window.windowFind()
b_window.win.activate()
time.sleep(1)
x0, y0, x1, y1 = b_window.position

def background_screenshot():
    #back = auto.screenshot(region = (x0,y0+32,x1-x0,y1-y0-32))
    pipe = subprocess.Popen("adb shell screencap -p",
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE, shell=True)
    image_bytes = pipe.stdout.read().replace(b'\r\n', b'\n')
    image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)[:,:,::-1]
    return image

def range_click(pos):
    if type(pos)==str:
        x,y,dx,dy = positions[pos]
    elif type(pos)==tuple:
        x,y,dx,dy = pos
    xx = np.random.randint(x,x+dx)
    yy = np.random.randint(y,y+dy)
    dt = np.random.randint(50,150)
    cmd = f"input swipe {xx} {yy} {xx} {yy} {dt}"
    adbdevice.shell(cmd)

def bias_sleep(low, range0):
    dt = int(np.random.rand()*range0*1000)
    t0 = int(low*1000)
    QTest.qWait(t0+dt)
#    time.sleep(low + dt)

def go_to_war_page():
    back = background_screenshot()
    temp = auto.locate(f'{basedir}src/aliance_1200.png', back, confidence=0.8)
    print(temp)
    if not temp:
        range_click('menu')
        bias_sleep(0.3,0.2)
    range_click('aliance')
    bias_sleep(0.5,0.2)
    range_click('wars')
    bias_sleep(1,0.2)

def bf_check():
    back = background_screenshot()
    temp = auto.locate(f'{basedir}src/bf_1200.png', Image.fromarray(back), confidence=0.95)
    if temp is None:
        return False
    else:
        return True

def rallycount():
    back = background_screenshot()
    temp = auto.locateAll(f'{basedir}src/bf_1200.png', Image.fromarray(back), confidence=0.95)
    if temp is None:
        return False
    temp = list(temp)
    return len(temp)

def loc_capture(i):
    x,y,w,h = positions[f'loc{i}']
    im = background_screenshot()
    castle_loc = im[y:y+h,x:x+w]
    bf_loc = im[y:y+h,x+796:x+796+w] ##야도좌표가 성좌표+796에있음, 해상도 바뀔때 확장성떨어짐 나중에 수정
    return Image.fromarray(castle_loc), Image.fromarray(bf_loc)

def get_nickname(nn):
    range_click(f'loc{nn}')
    bias_sleep(2.5,0.5)
    range_click('castle')
    bias_sleep(0.5,0.2)
    back = background_screenshot()
    temp = auto.locate(f'{basedir}src/info_1200.png', Image.fromarray(back), confidence=0.9)
    if not temp:
        dx = 190
        dy = 140
        pos0 = positions['castle']
        cc = 0
        for i in [-1,0,1]:
            for j in [-1,0,1]:
                pos = (pos0[0]+dx*i, pos0[1]+dy*j, pos0[2], pos0[3])
                range_click(pos)
                bias_sleep(0.3,0.2)
                back = background_screenshot()
                temp = auto.locate(f'{basedir}src/info_1200.png', Image.fromarray(back), confidence=0.9)
                if temp is not None:
                    cc = 1
                    break
            if cc==1:
                break

    pos = (temp[0]-78, temp[1]-229,20,20)
    range_click(pos)
    bias_sleep(0.7,0.2)
    back = background_screenshot()
    temp = auto.locate(f'{basedir}src/nick_1200.png', Image.fromarray(back), confidence=0.95)
    range_click(tuple(temp))
    nickname = clip.paste()
    range_click('info_x')
    bias_sleep(0.5,0.2)
    return nickname
    
def integer_timestamp():
    t0 = datetime.now().timestamp()
    return int(t0)

if adbdevice is not None:
    print("Adb detected")
else:
    print("Adb not detected")
    exit(0)

def bf_count(db, rally=0, castle=None, bf=None):
    nn = rallycount()
   
    if rally==0: #집결이 없었다가 생긴 경우
        castle_loc_im, bf_loc_im = loc_capture(nn)
        castle_loc = extract(castle_loc_im)
        i = nn
    else:
        for i in range(nn,0,-1):
            castle_loc_im, bf_loc_im = loc_capture(i)
            castle_loc = extract(castle_loc_im)
            if castle_loc != castle:
                break

    nickname = get_nickname(i)
    data = {'nickname':nickname, 'location':castle_loc}
    user_id = db.insert_user(data)

    bf_loc = extract(bf_loc_im)
    data = {'user_id':user_id, 'bf_loc':bf_loc, 'timestamp':integer_timestamp()}
    db.insert_rally(data)

    return castle_loc, bf_loc
#    elif rally==1:
        

if __name__=='__main__':
    bf_count(Database())