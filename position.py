# Function reference: 
# https://github.com/Asadullah-Dal17/Eyes-Position-Estimator-Mediapipe.git

import cv2 as cv
import numpy as np

# colors 
# values =(blue, green, red) opencv accepts BGR values not RGB
BLACK = (0,0,0)
WHITE = (255,255,255)
YELLOW =(0,255,255)
GRAY = (128,128,128)
GREEN = (0,255,0)
ORANGE = (0,165,255)
PINK = (147,20,255)

# Pixel counter
def pixel_count(f_piece, s_piece, t_piece):
    # counting black pixel in each part 
    right_part = np.sum(f_piece<50)
    # print(right_part)

    center_part = np.sum(s_piece<50)
    # print(center_part)

    left_part = np.sum(t_piece<50)
    # print(left_part)

    # creating list of these values
    eye_parts = [right_part, center_part, left_part]

    # getting the index of max values in the list 
    #print(eye_parts)
    max_index = eye_parts.index(max(eye_parts))
    pos_eye ='' 
    
    # Show in screen 
    if max_index==0:
        pos_eye="RIGHT"
        color=[BLACK, GREEN]
    elif max_index == 1:
        pos_eye = 'CENTER'
        color = [YELLOW, PINK]
    elif max_index == 2:
        pos_eye = 'LEFT'
        color = [GRAY, YELLOW]
    else:
        pos_eye="Closed"
        color = [GRAY, YELLOW]
    
    return pos_eye, color

def position(eye_mask, blink):
    # get the height and width of the eye
    h, w, z = eye_mask.shape
    #print(h)
    #print(w)
    # print("--------------------------------------------")

    # remove noise from eye image
    gaussian_blur = cv.GaussianBlur(eye_mask, (9,9),0)
    median_blur = cv.medianBlur(gaussian_blur, 3)

    # threshold to convert binary image
    ret, threshed_eye = cv.threshold(median_blur, 40, 195, cv.THRESH_BINARY)
    #print(f'\n{threshed_eye}\n')
    #print("=======================")

    # create fixd part for eye with 
    piece = int(w/3) 

    # slicing the eyes into three parts 
    right_piece = threshed_eye[0:h, 0:piece]
    center_piece = threshed_eye[0:h, piece:(piece+piece)]
    left_piece = threshed_eye[0:h, (piece + piece):w]
    
    if blink == False:
        # calling pixel counter function
        eye_position, color = pixel_count(right_piece, center_piece, left_piece)

    else:
        eye_position = "Closed"
        color = [GRAY, YELLOW]
    
    return eye_position, color


