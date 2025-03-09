import cv2
import numpy as np
import mediapipe as mp
from collections import deque

# Color points deque
bpoints = [deque(maxlen=1024)]
gpoints = [deque(maxlen=1024)]
rpoints = [deque(maxlen=1024)]
ypoints = [deque(maxlen=1024)]

blue_index = green_index = red_index = yellow_index = 0
kernel = np.ones((5,5),np.uint8)

colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 255, 255)]
colorIndex = 0

# Canvas setup
paintWindow = np.ones((471, 636, 3), dtype=np.uint8) * 255
buttons = [(40, 1, 140, 65, (0, 0, 0), "CLEAR"),
           (160, 1, 255, 65, (255, 0, 0), "BLUE"),
           (275, 1, 370, 65, (0, 255, 0), "GREEN"),
           (390, 1, 485, 65, (0, 0, 255), "RED"),
           (505, 1, 600, 65, (0, 255, 255), "YELLOW")]

for x1, y1, x2, y2, color, text in buttons:
    cv2.rectangle(paintWindow, (x1, y1), (x2, y2), color, 2)
    cv2.putText(paintWindow, text, (x1 + 10, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, cv2.LINE_AA)

cv2.namedWindow('Paint', cv2.WINDOW_AUTOSIZE)

# Initialize MediaPipe
mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mpDraw = mp.solutions.drawing_utils

# Webcam setup
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        continue  # Skip if frame is not captured

    height, width, _ = frame.shape
    frame = cv2.flip(frame, 1)
    framergb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    for x1, y1, x2, y2, color, text in buttons:
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(frame, text, (x1 + 10, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, cv2.LINE_AA)

    result = hands.process(framergb)

    if result.multi_hand_landmarks:
        for handslms in result.multi_hand_landmarks:
            landmarks = [[int(lm.x * width), int(lm.y * height)] for lm in handslms.landmark]
            
            if len(landmarks) >= 9:  # Ensure landmarks exist
                fore_finger = tuple(landmarks[8])
                thumb = tuple(landmarks[4])

                cv2.circle(frame, fore_finger, 3, (0,255,0), -1)

                if thumb[1] - fore_finger[1] < 30:  # New stroke condition
                    bpoints.append(deque(maxlen=512))
                    gpoints.append(deque(maxlen=512))
                    rpoints.append(deque(maxlen=512))
                    ypoints.append(deque(maxlen=512))

                    blue_index += 1
                    green_index += 1
                    red_index += 1
                    yellow_index += 1

                elif fore_finger[1] <= 65:
                    if 40 <= fore_finger[0] <= 140:  # Clear Button
                        bpoints, gpoints, rpoints, ypoints = [deque(maxlen=512)] * 4
                        blue_index = green_index = red_index = yellow_index = 0
                        paintWindow[67:,:,:] = 255
                    elif 160 <= fore_finger[0] <= 255:
                        colorIndex = 0  # Blue
                    elif 275 <= fore_finger[0] <= 370:
                        colorIndex = 1  # Green
                    elif 390 <= fore_finger[0] <= 485:
                        colorIndex = 2  # Red
                    elif 505 <= fore_finger[0] <= 600:
                        colorIndex = 3  # Yellow
                else:
                    if colorIndex == 0:
                        bpoints[blue_index].appendleft(fore_finger)
                    elif colorIndex == 1:
                        gpoints[green_index].appendleft(fore_finger)
                    elif colorIndex == 2:
                        rpoints[red_index].appendleft(fore_finger)
                    elif colorIndex == 3:
                        ypoints[yellow_index].appendleft(fore_finger)

            mpDraw.draw_landmarks(frame, handslms, mpHands.HAND_CONNECTIONS)

    # Draw on the frame and canvas
    points = [bpoints, gpoints, rpoints, ypoints]
    for i, color in enumerate(colors):
        for j in range(len(points[i])):
            for k in range(1, len(points[i][j])):
                if points[i][j][k - 1] is None or points[i][j][k] is None:
                    continue
                cv2.line(frame, points[i][j][k - 1], points[i][j][k], color, 2)
                cv2.line(paintWindow, points[i][j][k - 1], points[i][j][k], color, 2)

    cv2.imshow("Output", frame)
    cv2.imshow("Paint", paintWindow)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
