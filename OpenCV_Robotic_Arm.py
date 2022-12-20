import cv2
import numpy as np
import math
import mediapipe as mp
import serial
import time

#Initialise serial communication
##Arduino = serial.Serial("<port>", 9600)
##Arduino.timeout = 1

#mediapipe hand detection
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

#Configure video capture
cap = cv2.VideoCapture(0)
height = 720
width = 1280
cap.set(4, height)
cap.set(3, width)

hand_frame = 0
claw = ""
turn = ""
rotate = ""
first_elbow = ""
second_elbow = "up"
reset = True

#Initialise hands
with mp_hands.Hands(model_complexity=0, min_detection_confidence=0.8, min_tracking_confidence=0.5) as hands:
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue

        # To improve performance, mark the image as not writeable to pass by reference
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(image)

        # Draw the hand annotations on the image
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        landmarks = []

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style())
        
                for index, landmark in enumerate(hand_landmarks.landmark):
                    cx, cy = int(landmark.x * width), int(landmark.y * height)
                    landmarks.append([index, cx, cy])

        if hand_frame == 30:
            original = landmarks
            print("Hand registered")

        if hand_frame > 30 and results.multi_hand_landmarks:

            distance = math.hypot(landmarks[4][1] - landmarks[8][1], landmarks[4][2] - landmarks[8][2])
        
            if distance < 70 and claw != "closed":
                print("close_claw")
                claw = "closed"
                ##Arduino.write(command.encode())
                
            elif distance > 220 and claw != "opened":
                print("open_claw")
                claw = "opened"
                ##Arduino.write(command.encode())
        
            x_offset = original[9][1] - landmarks[9][1]

            if x_offset > 300 and turn != "right":
                print("turn_right")
                turn = "right"
        
            if x_offset < -300 and turn != "left":
                print("turn_left")
                turn = "left"

            y_offset = original[9][2] - landmarks[9][2]

            if y_offset > 100 and first_elbow != "up":
                print("move_up")
                first_elbow = "up"
        
            if y_offset < -100 and first_elbow != "down":
                print("move_down")
                first_elbow = "down"

            rotation = landmarks[17][2] - landmarks[20][2]

            if rotation < 80 and landmarks[20][1] < landmarks[17][1] and rotate != "right":
                print("rotate_right")
                rotate = "right"

            elif rotation < 80 and landmarks[20][1] > landmarks[17][1] and rotate != "left":
                print("rotate_left")
                rotate = "left"

            finger_straightness = abs(landmarks[16][1] - landmarks[14][1])

            if landmarks[16][2] > landmarks[14][2] and finger_straightness < 25 and second_elbow != "down":
                print("adjust_down")
                second_elbow = "down"

            if landmarks[16][2] < landmarks[14][2] and finger_straightness < 25 and second_elbow != "up":
                print("adjust_up")
                second_elbow = "up"

        cv2.imshow('Output', cv2.flip(image, 1))

        prev_landmarks = landmarks

        if results.multi_hand_landmarks:
            hand_frame += 1
            reset = False

        elif not results.multi_hand_landmarks and not reset:
            hand_frame = 0
            claw = ""
            turn = ""
            rotate = ""
            first_elbow = ""
            second_elbow = "up"
            print("reset")
            reset = True
    
        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

cap.release()