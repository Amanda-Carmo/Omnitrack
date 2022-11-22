#================================================ Imports =================================================

import cv2 as cv 
import numpy as np
import mediapipe as mp 
from eye_contour import *
from position import pixel_count, position
import utils
import webbrowser
from blink import blinkRatio
import pyautogui

# from interface import build_interface
import os
# import streamlit.bootstrap
import sys
# from streamlit import cli as stcli

from streamlit import config as _config

import streamlit as st
from streamlit_option_menu import option_menu

mp_face_mesh = mp.solutions.face_mesh
chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'
url_netflix = 'https://www.netflix.com/browse'
url_spotify = 'https://open.spotify.com'

global global_var
global_var = 0

# Colors to use (maybe use from another file)
GREEN = (0,255,0)
BLUE = (245, 56, 129)
YELLOW =(0,255,255)
PINK = (147,20,255)


# left eyes indices
LEFT_EYE =[ 362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385,384, 398 ]

# right eyes indices
RIGHT_EYE=[ 33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161 , 246 ] 

# irises Indices list
LEFT_IRIS = [474,475, 476, 477]
RIGHT_IRIS = [469, 470, 471, 472]

FONTS = cv.FONT_HERSHEY_COMPLEX

CEF_COUNTER = 0
TOTAL_BLINKS = 0
CLOSED_EYES_FRAME =  15 # need to be closed during 5 frames
OPEN = False



selected = option_menu(
    
    menu_title = None,
    options = ['Home', 'Apps', 'Messages'],
    icons = ['home', 'apps', 'message'],
    menu_icon = 'menu',
    default_index = 0,
    orientation = 'horizontal',
)

if selected == 'Apps':
    global_var = 1


if selected == 'Messages':
    # st.experimental_rerun()
    global_var = 2
    


#================================================ main =================================================
cap = cv.VideoCapture(0)

with mp_face_mesh.FaceMesh(
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
) as face_mesh:

    while True:
        
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv.flip(frame, 1)
        # frame = cv.resize(frame, None, fx=1, fy=1, interpolation=cv.INTER_CUBIC)

        rgb_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        img_h, img_w = frame.shape[:2]
        results = face_mesh.process(rgb_frame)
        mask = np.zeros((img_h, img_w), dtype=np.uint8)

        if results.multi_face_landmarks:
            # print((results.multi_face_landmarks[0]))
            
            mesh_points=np.array([np.multiply([p.x, p.y], [img_w, img_h]).astype(int) 
            for p in results.multi_face_landmarks[0].landmark])

            mesh_coords = landmarksDetection(frame, results, False)
            
            cv.polylines(frame, [mesh_points[LEFT_IRIS]], True, (0,255,0), 1, cv.LINE_AA)
            cv.polylines(frame, [mesh_points[RIGHT_IRIS]], True, (0,255,0), 1, cv.LINE_AA)
            
            (l_cx, l_cy), l_radius = cv.minEnclosingCircle(mesh_points[LEFT_IRIS])
            (r_cx, r_cy), r_radius = cv.minEnclosingCircle(mesh_points[RIGHT_IRIS])
            
            center_left = np.array([l_cx, l_cy], dtype=np.int32)
            center_right = np.array([r_cx, r_cy], dtype=np.int32)

            cv.circle(frame, center_left, int(l_radius), (180,240,10), 1, cv.LINE_AA)
            cv.circle(frame, center_right, int(r_radius), (245,170,20), 1, cv.LINE_AA)

            cv.circle(frame, center_left, 1, (255,0,0), -1, cv.LINE_AA)
            cv.circle(frame, center_right, 1, (255,0,0), -1, cv.LINE_AA)

            # drawing on the mask 
            cv.circle(mask, center_left, int(l_radius), (255,255,255), -1, cv.LINE_AA)
            cv.circle(mask, center_right, int(r_radius), (255,255,255), -1, cv.LINE_AA)

            # -----------------------------------------------------------------------------------
            # Contour 

            # Mask
            cv.polylines(frame,  [np.array([mesh_coords[p] for p in LEFT_EYE ], dtype=np.int32)], True, BLUE, 1, cv.LINE_AA)
            cv.polylines(frame,  [np.array([mesh_coords[p] for p in RIGHT_EYE ], dtype=np.int32)], True, BLUE, 1, cv.LINE_AA)
            
            left_coords = [mesh_coords[p] for p in LEFT_EYE]
            right_coords = [mesh_coords[p] for p in RIGHT_EYE]
            crop_right, crop_left = eye_contour(frame, right_coords, left_coords)
            
            # cv.imshow('left', crop_left)
            # cv.imshow('right', crop_right)

            # print(crop_left.shape)

            #-------------------------------------------------------------------------------------
            # Position
            # print(crop_left.shape)
            eye_position_right, color = position(crop_right)
            utils.colorBackgroundText(frame, f'R: {eye_position_right}', FONTS, 1.0, (40, 220), 2, color[0], color[1], 8, 8)
            eye_position_left, color = position(crop_left)
            utils.colorBackgroundText(frame, f'L: {eye_position_left}', FONTS, 1.0, (40, 320), 2, color[0], color[1], 8, 8)
            
            
            # -----------------------------------------------------------------------------------
            # Blink detection

            ratio = blinkRatio(frame, mesh_coords, RIGHT_EYE, LEFT_EYE)
            utils.colorBackgroundText(frame,  f'Ratio : {round(ratio,2)}', FONTS, 0.7, (30,100),2, PINK, YELLOW)
            
            if ratio > 5.5:
                CEF_COUNTER += 1
                # cv.putText(frame, 'Blink', (200, 50), FONTS, 1.3, utils.PINK, 2)
                utils.colorBackgroundText(frame,  f'Blink', FONTS, 1.7, (int(img_h/2), 100), 2, YELLOW, pad_x=6, pad_y=6, )

            else:
                if CEF_COUNTER > CLOSED_EYES_FRAME:
                    TOTAL_BLINKS += 1
                    CEF_COUNTER = 0
                    
                    if TOTAL_BLINKS == 3 and OPEN == False:
                        
                        # dirname = os.path.dirname(__file__)
                        # filename = os.path.join(dirname, 'interface.py')

                        # _config.set_option("server.headless", True)
                        # args = []

                        # #streamlit.cli.main_run(filename, args)
                        # streamlit.bootstrap.run(filename,'',args)
                        # if __name__ == '__main__':
                        #     sys.argv = ["streamlit", "run", "APP_NAME.py"]
                        #     sys.exit(stcli.main())

                        if global_var == 0:
                            st.title("Omnitrack Interface")
                            st.write("This is the interface for Omnitrack.")

                        if global_var == 1:
                            st.title("Your Apps")
                            app1 = st.button("Netflix")
                            app2 = st.button("Spotify")

                            st.write(app1, app2)

                            if app1:
                                st.write("Openning Netflix...")
                                webbrowser.get(chrome_path).open(url_netflix)

                            if app2:
                                st.write("Openning Spotify...")
                                webbrowser.get(chrome_path).open(url_spotify)

                        if global_var == 2:
                            st.title("Choose a message")
                            msg1 = st.button("Call caregiver")
                            msg2 = st.button("Message caregiver")
                            msg3 = st.button("Call doctor")

                            st.write(msg1)
                            st.write(msg2)
                            st.write(msg3)

                            if msg1:
                                st.write("Calling caregiver...")
                            if msg2:
                                st.write("Messaging caregiver...")
                            if msg3:
                                st.write("Calling doctor...")
                        
                        mouse_position = pyautogui.moveTo(578, 365)
                        # open_browser(url_2)
                        TOTAL_BLINKS = 0
                    
                        global_var = 0
                        OPEN = True
                    
                    #move to next button
                    if CEF_COUNTER == 17:
                        pyautogui.moveTo(1328, 338)

            # cv.putText(frame, f'Total Blinks: {TOTAL_BLINKS}', (100, 150), FONTS, 0.6, utils.GREEN, 2)
            utils.colorBackgroundText(frame,  f'Total Blinks: {TOTAL_BLINKS}', FONTS, 0.7, (30,150),2)


            # open web page if right
            # if eye_position_right == 'RIGHT':
                # webbrowser.get(chrome_path).open(url)
                # break


        # cv.imshow('Mask_pupil', mask)     
        cv.imshow('img', frame)
        key = cv.waitKey(1)
        if key == ord('q'): # off pressing "q"
            break

cap.release()
cv.destroyAllWindows()