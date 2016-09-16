import cv2
import numpy as np
import math
import time
from socketIO_client import SocketIO, LoggingNamespace

def createParams(num) :
  payload = {
    'type': 'keypress',
    'value': num,
    'clientid': 'gesture',
    'timestamp': time.time()
  }
  return payload

with SocketIO('https://<servernamegoes here>.herokuapp.com', 443, LoggingNamespace, verify=False) as socketIO:

    cap = cv2.VideoCapture(0)
    while(cap.isOpened()):
        ret, img = cap.read()
        cv2.rectangle(img,(300,300),(100,100),(0,255,0),0)
        crop_img = img[100:300, 100:300]
        grey = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
        value = (35, 35)
        blurred = cv2.GaussianBlur(grey, value, 0)
        _, thresh1 = cv2.threshold(blurred, 127, 255,
                                   cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
        cv2.imshow('Thresholded', thresh1)

        # uncomment the lines below(17-18) if using OpenCV 3+ and remove lines 21-22
        image, contours, hierarchy = cv2.findContours(thresh1.copy(), \
                cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

        # works only for OpenCV 2.4.x
        # contours, hierarchy = cv2.findContours(thresh1.copy(),cv2.RETR_TREE, \
        #        cv2.CHAIN_APPROX_NONE)

        max_area = -1
        for i in range(len(contours)):
            cnt=contours[i]
            area = cv2.contourArea(cnt)
            if(area>max_area):
                max_area=area
                ci=i
        cnt=contours[ci]
        x,y,w,h = cv2.boundingRect(cnt)
        cv2.rectangle(crop_img,(x,y),(x+w,y+h),(0,0,255),0)
        hull = cv2.convexHull(cnt)
        drawing = np.zeros(crop_img.shape,np.uint8)
        cv2.drawContours(drawing,[cnt],0,(0,255,0),0)
        cv2.drawContours(drawing,[hull],0,(0,0,255),0)
        hull = cv2.convexHull(cnt,returnPoints = False)
        defects = cv2.convexityDefects(cnt,hull)
        count_defects = 0
        cv2.drawContours(thresh1, contours, -1, (0,255,0), 3)
        for i in range(defects.shape[0]):
            s,e,f,d = defects[i,0]
            start = tuple(cnt[s][0])
            end = tuple(cnt[e][0])
            far = tuple(cnt[f][0])
            a = math.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
            b = math.sqrt((far[0] - start[0])**2 + (far[1] - start[1])**2)
            c = math.sqrt((end[0] - far[0])**2 + (end[1] - far[1])**2)
            angle = math.acos((b**2 + c**2 - a**2)/(2*b*c)) * 57
            if angle <= 90:
                count_defects += 1
                cv2.circle(crop_img,far,1,[0,0,255],-1)
            #dist = cv2.pointPolygonTest(cnt,far,True)
            cv2.line(crop_img,start,end,[0,255,0],2)
            #cv2.circle(crop_img,far,5,[0,0,255],-1)
        curr_command = 0
        if count_defects == 1:
            cv2.putText(img,"LEFT", (50,50), cv2.FONT_HERSHEY_SIMPLEX, 2, 2)
            print("1 defect")
            curr_command = 37
        elif count_defects == 2:
            cv2.putText(img, "RIGHT", (5,50), cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
            print("2 defects")
            curr_command = 39
        elif count_defects == 3:
            cv2.putText(img,"UP", (50,50), cv2.FONT_HERSHEY_SIMPLEX, 2, 2)
            print("3 defects")
            curr_command = 38
        elif count_defects == 4:
            cv2.putText(img, "DOWN", (50,50), cv2.FONT_HERSHEY_SIMPLEX, 2, 2)
            curr_command = 40
            print("4 defects")
        elif count_defects == 5:
            cv2.putText(img, "5555555", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, 2)
            print("5 defects")
            curr_command = 32
        elif count_defects == 6:
            cv2.putText(img, "66666", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, 2)
            print("6 defects")
            curr_command = 71
        else:
            cv2.putText(img,"Hello World!!!", (50,50),\
                    cv2.FONT_HERSHEY_SIMPLEX, 2, 2)
            print("None detected")

        if count_defects != current_defects:
            current_defects = count_defects
            socketIO.emit('keypress', createParams(curr_command))
            print("emitting to the socket")

        #cv2.imshow('drawing', drawing)
        #cv2.imshow('end', crop_img)
        cv2.imshow('Gesture', img)
        all_img = np.hstack((drawing, crop_img))
        cv2.imshow('Contours', all_img)
        k = cv2.waitKey(10)
        if k == 27:
            break
