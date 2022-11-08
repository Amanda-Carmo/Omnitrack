import cv2 as cv
import numpy as np

# landmark detection function 
def landmarksDetection(img, results, draw=False):
    img_height, img_width= img.shape[:2]
    # list[(x,y), (x,y)....]
    mesh_coord = [(int(point.x * img_width), int(point.y * img_height)) for point in results.multi_face_landmarks[0].landmark]
    if draw :
        [cv.circle(img, p, 2, (0,255,0), -1) for p in mesh_coord]

    # returning the list of tuples for each landmarks 
    return mesh_coord

def eye_contour(img, re_coord, le_coord):
    # converting color image to scale image
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    rgb_frame = cv.cvtColor(img, cv.COLOR_BGR2RGB)

    # dimension of image
    dim = gray.shape

    # creating mask
    mask = np.zeros(dim, dtype=np.uint8)

    # drawing Eyes Shape on mask with white color 
    cv.fillPoly(mask, [np.array(re_coord, dtype=np.int32)], 255)
    cv.fillPoly(mask, [np.array(le_coord, dtype=np.int32)], 255)

    # showing the mask 
    cv.imshow('mask', mask)

    # draw eyes image on mask, where white shape is 
    eyes = cv.bitwise_and(rgb_frame, rgb_frame, mask=mask)
    # change black color to gray other than eys 
    cv.imshow('eyes draw', eyes)
    eyes[mask==0]=155
    
    # getting minium and maximum x and y  for right and left eyes 
    # For Right Eye 
    r_max_x = (max(re_coord, key=lambda item: item[0]))[0]
    r_min_x = (min(re_coord, key=lambda item: item[0]))[0]
    r_max_y = (max(re_coord, key=lambda item : item[1]))[1]
    r_min_y = (min(re_coord, key=lambda item: item[1]))[1]

    # For LEFT Eye
    l_max_x = (max(le_coord, key=lambda item: item[0]))[0]
    l_min_x = (min(le_coord, key=lambda item: item[0]))[0]
    l_max_y = (max(le_coord, key=lambda item : item[1]))[1]
    l_min_y = (min(le_coord, key=lambda item: item[1]))[1]

    # croping the eyes from mask 
    cropped_right = eyes[r_min_y: r_max_y, r_min_x: r_max_x]
    cropped_left = eyes[l_min_y: l_max_y, l_min_x: l_max_x]

    # returning the cropped eyes 
    return cropped_right, cropped_left
