import cv2
import numpy as np
import math
import mediapipe as mp
import serial

#Initialise serial communication
Arduino = serial.Serial("COM8", 9600)
Arduino.timeout = 1

#MediaPipe hand detection
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
claw = "opened"
rotate = ""
elbow = "up"
reset = True

close_claw = 'A'
open_claw = 'B'
turn_right = 'C'
turn_left = 'D'
rotate_right = 'E'
rotate_left = 'F'
adjust_up = 'G'
adjust_down = 'H'
reset_ascii = 'I'
rotate_reset = 'J'
#move_up = 'K'
#move_down = 'L'

#Initialise hands
with mp_hands.Hands(model_complexity=0, min_detection_confidence=0.6, min_tracking_confidence=0.5, max_num_hands = 1) as hands:
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
            original_distance = math.hypot(original[4][1] - original[8][1], original[4][2] - original[8][2])
        
            if distance < 70 and claw != "closed":
                print("close_claw")
                Arduino.write(close_claw.encode())
                claw = "closed"
                
            elif distance > (original_distance - 30) and claw != "opened":
                print("open_claw")
                Arduino.write(open_claw.encode())
                claw = "opened"
        
            x_offset = original[9][1] - landmarks[9][1]

            if x_offset > 300:
                print("turn_right")
                Arduino.write(turn_right.encode())
        
            if x_offset < -300:
                print("turn_left")
                Arduino.write(turn_left.encode())

            #y_offset = original[9][2] - landmarks[9][2]

            #if y_offset > 100:
            #    print("move_up")
            #    Arduino.write("move_up".encode())
        
            #if y_offset < -100:
            #    print("move_down")
            #    Arduino.write("move_down".encode())

            rotation = landmarks[17][2] - landmarks[20][2]

            if rotation < 40 and landmarks[20][1] < landmarks[17][1] and rotate != "right":
                print("rotate_right")
                Arduino.write(rotate_right.encode())
                rotate = "right"

            elif rotation < 40 and landmarks[20][1] > landmarks[17][1] and rotate != "left":
                print("rotate_left")
                Arduino.write(rotate_left.encode())
                rotate = "left"

            elif rotation < 120 and rotation > 80 and rotate != "reset":
                print("rotate_reset")
                Arduino.write(rotate_reset.encode())
                rotate = "reset"

            finger_straightness = abs(landmarks[16][1] - landmarks[14][1])

            if landmarks[16][2] < landmarks[14][2] and finger_straightness < 25 and elbow != "up":
                print("adjust_up")
                Arduino.write(adjust_up.encode())
                elbow = "up"

            if landmarks[16][2] > landmarks[14][2] and finger_straightness < 25 and elbow != "down":
                print("adjust_down")
                Arduino.write(adjust_down.encode())
                elbow = "down"

        cv2.imshow('Output', cv2.flip(image, 1))

        prev_landmarks = landmarks

        if results.multi_hand_landmarks:
            hand_frame += 1
            reset = False

        elif not results.multi_hand_landmarks and not reset:
            hand_frame = 0
            claw = "opened"
            turn = ""
            rotate = ""
            first_elbow = ""
            second_elbow = "up"
            print("reset")
            Arduino.write(reset_ascii.encode())
            reset = True
    
        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

cap.release()
Arduino.close()