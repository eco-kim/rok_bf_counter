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
    dt = np.random.rand()*range0
    time.sleep(low + dt)

def go_to_war_page():
    temp = auto.locateOnScreen('./src/aliance_1200.png',confidence=0.9)
    print(temp)
    if not temp:
        range_click('menu')
        bias_sleep(0.5,0.2)
    range_click('aliance')
    bias_sleep(0.5,0.2)
    range_click('wars')
    bias_sleep(1,0.2)

def bf_check():
    back = background_screenshot()
    temp = auto.locate('./src/bf_1200.png', Image.fromarray(back), confidence=0.95)
    if temp is None:
        return False
    else:
        return True

def rallycount():
    back = background_screenshot()
    temp = auto.locateAll('./src/bf_1200.png', Image.fromarray(back), confidence=0.95)
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

def get_nickname():
    back = background_screenshot()
    temp = auto.locate('./src/nick_1200.png', Image.fromarray(back), confidence=0.95)
    range_click(tuple(temp))
    nickname = clip.paste()
    return nickname
    
def data_load():
    try:
        with open('./data/users','rb') as f:
            user = pickle.loads(f)
    except:
        user = pd.DataFrame(columns=['id','nickname','location'])
    
    try:
        with open('./data/timeline','rb') as f:
            timeline = pickle.loads(f)
    except:
        timeline = pd.DataFrame(columns=['id','user_id','bf_loc','timestamp'])

    return user, timeline

if adbdevice is not None:
    print("Adb detected")
else:
    print("Adb not detected")
    exit(0)

if __name__=='__main__':
    ##df들 불러오기 or 만들기
    user, timeline = data_load()

    #전쟁 페이지로 가기
    go_to_war_page()
    
    #야도집결 걸릴때까지 대기 (3초마다 체크, 야간에는 한 10초로 늘려야할듯.)
    cc = bf_check()
    while not cc:
        time.sleep(3)
        cc = bf_check()
    
    nn = rallycount()
    castle_loc, bf_loc = loc_capture(nn)
    loc = extract(castle_loc)

    if loc not in user.location.values:
        range_click(f'loc{nn}')
        bias_sleep(2.5,0.5)
        range_click('castle')
        bias_sleep(0.5,0.2)
        range_click('info')
        bias_sleep(0.7,0.2)
        nickname = get_nickname()
        user_id = user.shape[0]+1
        data = pd.DataFrame([[user_id,nickname,loc]], columns=user.columns)
        user = pd.concat([user,data],ignore_index=True)

        bf_loc = extract(bf_loc)
        idx = timeline.shape[0]+1
        data = pd.DataFrame([[idx,user_id,bf_loc, datetime.now()]], columns=timeline.columns)
        timeline = pd.concat([timeline, data], ignore_index=True)
        print(timeline.head())

