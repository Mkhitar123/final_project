import cv2
import numpy as np
import htm
import time
import autopy

DrowMode = False

wCam, hCam = 640,  480
frameR = 100     #Frame Reduction
smoothening = 7  #random value


pTime = 0
plocX, plocY = 0, 0
clocX, clocY = 0, 0
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

detector = htm.handDetector(maxHands=1)
wScr, hScr = autopy.screen.size()

# print(wScr, hScr)

while True:
    #  Find the landmarks
    success, img = cap.read()
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img)

    #  Get the tip of the index and middle finger
    if len(lmList) != 0:
        x0, y0 = lmList[12][1:]
        x1, y1 = lmList[4][1:]
        x2, y2 = lmList[8][1:]

        #  Check which fingers are up
        fingers = detector.fingersUp()
        cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR),
                      (255, 0, 255), 2)

        #  Only Index Finger: Moving Mode
        if fingers[1] == 1 or fingers[2] == 1 : #or fingers[1] == 1 and fingers[0] == 1 :

            #  Convert the coordinates
            x3 = np.interp(x1, (frameR, wCam-frameR), (0, wScr))
            y3 = np.interp(y1, (frameR, hCam-frameR), (0, hScr))

            #  Smooth Values
            clocX = plocX + (x3 - plocX) / smoothening
            clocY = plocY + (y3 - plocY) / smoothening

            #  Move Mouse
            autopy.mouse.move(wScr - clocX, clocY)
            cv2.circle(img, (x1, y1), 10, (255, 0, 255), cv2.FILLED)
            plocX, plocY = clocX, clocY

        #  Both Index and middle are up: Clicking Mode
        if fingers[0] == 1 and fingers[1] == 1 and fingers[2] == 0:
            #  Find distance between fingers
            length1, img, lineInfo1 = detector.findDistance(4,8, img)
            #  Click mouse if distance short
            if length1 < 30:
               time.sleep(0.1)
               cv2.circle(img, (lineInfo1[4], lineInfo1[5]), 10, (0, 255, 0), cv2.FILLED)
               autopy.mouse.click(button = autopy.mouse.Button.LEFT )

        elif fingers[0] == 0 and fingers[1] == 1 and fingers[2] == 1:
            length, img, lineInfo = detector.findDistance(12,8, img)
            if length < 30:
               time.sleep(0.3)
               DrowMode = False if DrowMode else True
               cv2.circle(img, (lineInfo[4], lineInfo[5]), 10, (0, 255, 0), cv2.FILLED)
               autopy.mouse.toggle(down =  DrowMode)

        elif fingers[0] == 1 and fingers[1] == 1 and fingers[2] == 1:
            length2, img, lineInfo2 = detector.findDistance(12,4, img)
            length, img, lineInfo = detector.findDistance(4,8, img)
            if length < 30 and length2 < 30 :
               cv2.circle(img, (lineInfo[4], lineInfo[5]), 10, (0, 255, 0), cv2.FILLED)
               cv2.circle(img, (lineInfo2[4], lineInfo2[5]), 10, (0, 255, 0), cv2.FILLED)
               time.sleep(0.2)
               autopy.mouse.click(button = autopy.mouse.Button.RIGHT )
               

    #  Frame rate
    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)), (28, 58), cv2.FONT_HERSHEY_PLAIN, 3, (255, 8, 8), 3)

    #  Display
    im = cv2.resize(img, (650, 500))
    cv2.imshow("Practice", im)
    if cv2.waitKey(1) == ord('q'):
       cv2.destroyAllWindows()
       break
    