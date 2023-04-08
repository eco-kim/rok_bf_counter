import pyperclip as clip
import pyautogui as auto
import numpy as np
import time
from datetime import datetime
from src.positionInfo import *
from window_setup import bluestackWindow
from ppadb.client import Client as AdbClient
from config import *
from loc_extract import *
from PIL import Image
from PyQt5.QtTest import QTest

# adb settings
def adb_device(deviceport):
    client = AdbClient(host="127.0.0.1", port=5037)
    client.remote_connect("localhost", deviceport)
    adbdevice = client.device("localhost:"+str(deviceport))

    if adbdevice is not None:
        print("Adb detected")
    else:
        print("Adb not detected")
    return adbdevice

#b_window = bluestackWindow()
#b_window.windowFind()
#b_window.win.activate()
#time.sleep(1)

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
    temp = auto.locate(f'{basedir}src/aliance_1200.png', back, confidence=0.8)
    if not temp:
        range_click(adb, 'menu')
        bias_sleep(0.3,0.2)
    range_click(adb, 'aliance')
    bias_sleep(0.5,0.2)
    range_click(adb, 'wars')
    bias_sleep(1,0.2)

def bf_check(adb):
    back = background_screenshot(adb)
    temp = auto.locate(f'{basedir}src/bf_1200.png', Image.fromarray(back), confidence=0.95)
    if temp is None:
        return False
    else:
        return True

def location_check(adb, castle_list, bf_list):
    nn = rallycount()
    cc = 0
    back = background_screenshot(adb)
    for i in range(nn,0,-1):
        castle_loc_im, bf_loc_im = loc_capture(back, i)
        castle_loc = extract(castle_loc_im)
        bf_loc = extract(bf_loc_im)
        if castle_loc not in castle_list and bf_loc not in bf_list:
            cc = 1
            break
    if cc == 0:
        return False
    return i

def rallycount(adb):
    back = background_screenshot(adb)
    temp = auto.locateAll(f'{basedir}src/bf_1200.png', Image.fromarray(back), confidence=0.95)
    if temp is None:
        return False
    temp = list(temp)
    return len(temp)

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
    temp = auto.locate(f'{basedir}src/info_1200.png', Image.fromarray(back), confidence=0.9)
    if not temp:
        dx = 190
        dy = 140
        pos0 = positions['castle']
        cc = 0
        for i in [-1,0,1]:
            for j in [-1,0,1]:
                pos = (pos0[0]+dx*i, pos0[1]+dy*j, pos0[2], pos0[3])
                range_click(adb, pos)
                bias_sleep(0.3,0.2)
                back = background_screenshot(adb)
                temp = auto.locate(f'{basedir}src/info_1200.png', Image.fromarray(back), confidence=0.9)
                if temp is not None:
                    cc = 1
                    break
            if cc==1:
                break

    pos = (temp[0]-78, temp[1]-229,20,20)
    range_click(adb, pos)
    bias_sleep(0.7,0.2)
    back = background_screenshot(adb)
    temp = auto.locate(f'{basedir}src/nick_1200.png', Image.fromarray(back), confidence=0.95)
    range_click(adb, tuple(temp))
    try:
        nickname = clip.waitForNewPaste(1)
    except:
        return 'error'
    range_click(adb, 'info_x')
    bias_sleep(0.5,0.2)
    return nickname
    
def integer_timestamp():
    t0 = datetime.now().timestamp()
    return int(t0)

def bf_count(adb, db, i):
    back = background_screenshot(adb)
    castle_loc_im, bf_loc_im = loc_capture(back, i)
    castle_loc = extract(castle_loc_im)
    bf_loc = extract(bf_loc_im)

    nickname = get_nickname(adb, i)
    data = {'nickname':nickname, 'location':castle_loc}
    user_id = db.insert_user(data)
    
    data = {'user_id':user_id, 'bf_loc':bf_loc, 'timestamp':integer_timestamp()}
    db.insert_rally(data)

    return castle_loc, bf_loc
