import cv2
import numpy as np
import serial
from time import sleep
from math import trunc

# Establish serial communication
serial_port = "COM4"
baud_rate = 9600
ser_com = serial.Serial(serial_port, baud_rate)
sleep(3)

Kp = 0.06 # Kp degrees of servo response per pixel offset (increased range means decreased Kp)
x_angle = 0
y_angle = 0
tolerance = 30 # Frame's center box is will be (tolerance*2) by (tolerance*2)

# Fuction for setting servo to specific angle
def set_servo_angle(servo, angle):
    if (0 <= angle <= 180):
        ser_com.write(f"{servo}{angle}\n".encode())        
        sleep(0.1)

# Initialize servos' position
set_servo_angle('x', 0)
set_servo_angle('y', 0)

# Initialize video stream
stream = cv2.VideoCapture(0)
if not stream.isOpened():
    print("Frame not opened :(")
    exit()

# Can replace current OpenCV Haar cascade with any .xml file cascade, currently detecting face
object_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 
                        "haarcascade_frontalface_default.xml")

# Loop for analyzing each frame
while True:
    ret, frame = stream.read()
    if not ret:
        print("Frame read failed :(")
        break

    frame_out = frame.copy()    # Separate image for displaying

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    objects = object_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30,30))

    if (len(objects) > 0):  # Check if any objects in frame (rect[2] is width, rect[3] is height)
        largest_object = max(objects, key=(lambda rect: rect[2] * rect[3]))

        x, y, w, h = largest_object

        cv2.rectangle(frame_out, (x, y), (x+w, y+h), (0,255,0), 2)

        # Determine object center
        object_center_x = x + (w // 2)
        object_center_y = y + (h // 2)

        # Obtain frame dimensions and determine frame center
        frame_height, frame_width, _ = frame.shape
        frame_center_x = frame_width // 2
        frame_center_y = frame_height // 2

        # Determine offsets
        offset_x = object_center_x - frame_center_x
        offset_y = object_center_y - frame_center_y

        if (abs(offset_x) > tolerance) or (abs(offset_y) > tolerance):
            # Determine necessary adjustments
            x_adjustment = -Kp * offset_x   # Negative Kp b/c of the nature of my servos' mounted orientations
            y_adjustment = -Kp * offset_y

            x_angle += x_adjustment
            y_angle += y_adjustment

            set_servo_angle('x', x_angle)
            set_servo_angle('y', y_angle)

        # Quadrant lines
        cv2.line(frame_out, (frame_center_x, 0), (frame_center_x, frame_height), (255,0,0), thickness=2)
        cv2.line(frame_out, (0, frame_center_y), (frame_width, frame_center_y), (255,0,0), thickness=2)

        # Draw box on center
        cv2.line(frame_out, (frame_center_x - tolerance, frame_center_y - tolerance), 
                            (frame_center_x + tolerance, frame_center_y - tolerance), (255,0,0), thickness=2)
        cv2.line(frame_out, (frame_center_x - tolerance, frame_center_y - tolerance), 
                            (frame_center_x - tolerance, frame_center_y + tolerance), (255,0,0), thickness=2)
        cv2.line(frame_out, (frame_center_x + tolerance, frame_center_y - tolerance), 
                            (frame_center_x + tolerance, frame_center_y + tolerance), (255,0,0), thickness=2)
        cv2.line(frame_out, (frame_center_x - tolerance, frame_center_y + tolerance), 
                            (frame_center_x + tolerance, frame_center_y + tolerance), (255,0,0), thickness=2)
        
        # Display diagnostic information
        cv2.putText(frame_out, f"Kp value: {Kp}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,100,255), 2)
        cv2.putText(frame_out, f"x_servo angle: {trunc(x_angle)}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,100,255), 2)
        cv2.putText(frame_out, f"y_servo angle: {trunc(y_angle)}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,100,255), 2)
        

    cv2.imshow("Frame", frame_out)

    if cv2.waitKey(1) == ord('q'):
        break

# End program
ser_com.close()
stream.release()
cv2.destroyAllWindows()