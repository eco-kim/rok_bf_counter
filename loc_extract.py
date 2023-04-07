import cv2
import pytesseract
import re

def transform(im):
    im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    _, im = cv2.threshold(im, 0, 200, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
    return im

def extract(im):
    text = pytesseract.image_to_string(im, lang='eng',config='--psm 6')
    loc = list(map(int, re.findall(r'[0-9]+', text)))
    return loc[0]*10000+loc[1]