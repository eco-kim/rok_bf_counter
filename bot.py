import pyperclip as clip
import pyautogui as auto
import numpy as np
from datetime import datetime
from src.positionInfo import *
from ppadb.client import Client as AdbClient
from config import *
from loc_extract import *
from PIL import Image
from PyQt5.QtTest import QTest
import os

# adb settings
def adb_device(deviceport):
    try:
        os.system('adb server start')
    except:
        pass ##adb server가 이미 켜져있는 경우 말고도 실패할 가능성 체크해야함.
    client = AdbClient(host="127.0.0.1", port=5037)
    client.remote_connect("localhost", deviceport)
    adbdevice = client.device("localhost:"+str(deviceport))
    return adbdevice

def background_screenshot(adb):
    image_bytes = adb.screencap()
    image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)[:,:,::-1]    
    return image

def range_click(adb, pos):
    if type(pos)==str:
        x,y,dx,dy = positions[pos]
    elif type(pos)==tuple:
        x,y,dx,dy = pos
    xx = np.random.randint(x,x+dx)
    yy = np.random.randint(y,y+dy)
    dt = np.random.randint(50,150)
    cmd = f"input swipe {xx} {yy} {xx} {yy} {dt}"
    adb.shell(cmd)

def bias_sleep(low, range0):
    dt = int(np.random.rand()*range0*1000)
    t0 = int(low*1000)
    QTest.qWait(t0+dt)

def go_to_war_page(adb):
    back = background_screenshot(adb)
    temp = auto.locate('./src/rally_1200.png', back, confidence=0.9)
    if temp is not None:
        range_click(adb, (600,360,20,20))

    temp = auto.locate('./src/x_1200.png', back, confidence=0.9)
    if temp is not None:
        print(tuple(temp))
        range_click(adb, tuple(temp))

    temp = auto.locate('./src/aliance_1200.png', back, confidence=0.8)
    if not temp:
        range_click(adb, 'menu')
        bias_sleep(0.3,0.2)
    range_click(adb, 'aliance')
    bias_sleep(0.5,0.2)
    range_click(adb, 'wars')
    bias_sleep(1,0.2)

def bf_check(back):
    temp = auto.locate('./src/bf_1200.png', Image.fromarray(back), confidence=0.95)
    if temp is None:
        return False
    else:
        return True

def rallycount(back):
    temp = auto.locateAll('./src/bf_1200.png', Image.fromarray(back), confidence=0.95)
    if temp is None:
        return 0
    temp = list(temp)
    return min(len(temp),3)

def location_check(back, bf_list):
    nn = rallycount(back)
    if nn == 0:
        return 0
    cc = 0
    for i in range(nn,0,-1):
        _, bf_loc_im = loc_capture(back, i)
        bf_loc = extract(bf_loc_im)
        if bf_loc not in bf_list:
            cc = 1
            break
    if cc == 0:
        return -1
    return i

def locate_n_click(adb, figure):
    back = background_screenshot(adb)
    temp = auto.locate(figure, Image.fromarray(back), confidence=0.9)
    if temp is not None:
        range_click(adb, temp)
        bias_sleep(0.3,0.1)
    else:
        pass

def loc_capture(back, i):
    x,y,w,h = positions[f'loc{i}']
    castle_loc = back[y:y+h,x:x+w]
    bf_loc = back[y:y+h,x+796:x+796+w] ##야도좌표가 성좌표+796에있음, 해상도 바뀔때 확장성떨어짐 나중에 수정
    return Image.fromarray(castle_loc), Image.fromarray(bf_loc)

def get_nickname(adb, nn):
    range_click(adb, f'loc{nn}')
    bias_sleep(2.5,0.5)
    range_click(adb, 'castle')
    bias_sleep(0.5,0.2)
    back = background_screenshot(adb)
    temp = auto.locate('./src/info_1200.png', Image.fromarray(back), confidence=0.9)
    if not temp:
        return 'error'
    pos = (temp[0]-78, temp[1]-229,20,20) ##인포 클릭
    range_click(adb, pos)
    bias_sleep(0.7,0.2)
    back = background_screenshot(adb)
    temp = auto.locate('./src/nick_1200.png', Image.fromarray(back), confidence=0.9)
    if temp is None:
        return 'error'
    range_click(adb, tuple(temp))
    bias_sleep(0.5,0.2)
    nickname = clip.paste()
    range_click(adb, 'info_x')
    bias_sleep(0.5,0.2)
    return nickname
    
def integer_timestamp():
    t0 = datetime.now().timestamp()
    return int(t0)

def bf_count(adb, db, back, alli, i):
    castle_loc_im, bf_loc_im = loc_capture(back, i)
    castle_loc = extract(castle_loc_im)
    bf_loc = extract(bf_loc_im)

    nickname = get_nickname(adb, i)
    data = {'nickname':nickname, 'location':castle_loc, 'alliance':alli}
    user_id = db.insert_user(data)
    
    data = {'user_id':user_id, 'bf_loc':bf_loc, 'timestamp':integer_timestamp()}
    db.insert_rally(data)

    return castle_loc, bf_loc
