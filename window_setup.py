import pyautogui as auto
import pygetwindow as gw

class bluestackWindow:
    def __init__(self, res=None, name=None):
        if name is not None:
            self.name = name
        else:
            self.name = 'BlueStacks for RoK BFcounter'

        if res is not None:
            self.res = res
        else:
            self.res = (1280,720)
        self.win = gw.getWindowsWithTitle(self.name)[0]
    def windowFind(self):
        win = self.win
        x1, y1, x2, y2 = win.left, win.top, win.right, win.bottom
        if x1<0:
            print('Bluestack 창을 띄워주세요 (최소화 상태에선 작동하지 않음)')
            return False
        else:
            self.position = [x1,y1,x2,y2]
            return True
        
    def windowSize(self):
        resX = self.res[0]
        x1,y1,x2,y2 = self.position
        dx = resX-(x2-x1)
        auto.moveTo(x2-1,(y1+y2)/2)
        auto.drag(dx,0,0.5)