import darknet.darknet as darknet
from cv2 import cv2
import numpy as np
import imutils
import random

#Setup socket for sending of string and receiving of coordinate
import socket

PORT = 5000
FORMAT = 'utf-8'
SERVER = '192.168.2.2'
ADDR = (SERVER, PORT)

ir_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# ir_socket.connect(ADDR)

def getImageString(x_coordinate, y_coordinate, id):
    return str(x_coordinate) + ":" + str(y_coordinate) + ":" + str(id)

def sendAndroidString(resultList):
    string = "IMAGE,"
    for id in resultList:
        image = resultList[id]
        string += getImageString(image[1][0], image[1][1], id)
        string += ","
    resultString = string[0:-1]
    message = resultString.encode(FORMAT)
    ir_socket.send(message)
    return str(resultString)



#Setup path for image recognition
SAVED_IMAGE_PATH = 'D:/Tai_lieu/Academic/Year_3_Semester_2/CZ3004_Multidisciplinary_Design_Project/Image_Recognition_Dependencies/saved_images/'
SOURCE_PATH = 'D:/Tai_lieu/Academic/Year_3_Semester_2/CZ3004_Multidisciplinary_Design_Project/Image_Recognition_Dependencies/darknet/'
WEIGHT_FILE_PATH = SOURCE_PATH + 'backup/yolo-obj_last.weights'
CONFIG_FILE_PATH = SOURCE_PATH + 'cfg/yolo-obj.cfg'
DATA_FILE_PATH = SOURCE_PATH + 'data/obj.data'
RPI_IP = '192.168.2.2'
STREAM_URL = 'http://' + RPI_IP + '/html/cam_pic_new.php'
YOLO_BATCH_SIZE = 4
THRESH = 0.95

def retrieveImg():
    # Captures a frame from video stream and returns an opencv image
    cap = cv2.VideoCapture(STREAM_URL)
    ret, frame = cap.read()
    return frame

def imageDetection(image, network, class_names, class_colors, thresh):
    # Modified from darknet_images.py
    width = darknet.network_width(network)
    height = darknet.network_height(network)
    darknet_image = darknet.make_image(width, height, 3)

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image_resized = cv2.resize(image_rgb, (width, height),
                               interpolation=cv2.INTER_LINEAR)

    darknet.copy_image_from_bytes(darknet_image, image_resized.tobytes())
    detections = darknet.detect_image(network, class_names, darknet_image, thresh=thresh)
    darknet.free_image(darknet_image)
    image = darknet.draw_boxes(detections, image_resized, class_colors)
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB), detections

def saveImage(frame, id):
    frame = imutils.resize(frame, width=500, height=480)
        
    # Saves images to local storage
    cv2.imwrite(SAVED_IMAGE_PATH + 'result_' + str(id) + '.jpeg', frame)
        
def showImages(frame_list):
    for index, frame in enumerate(frame_list):
        frame = imutils.resize(frame, width=500, height=480)
        
        cv2.imshow('Image' + str(index), frame)

    if cv2.waitKey() & 0xFF == ord('q'):
        cv2.destroyAllWindows()

#Position processing
def processPos(string):
    try:
        tokenList = string.split(";")
        stateList = tokenList[0].split(",")
        direction = stateList[-2]
        coorList = stateList[-1].split(":")
        return int(direction), int(coorList[0]), int(coorList[1])
    except Exception as e:
        print("Caught error in processPos:")
        print(str(e))
        raise e

def getPosition():
    try:
        string = ir_socket.recv(1024)
        decodedString = string.decode('utf-8')
        print ("Read from PC: %s" %(decodedString))
        direction, x_coordinate, y_coordinate = processPos(decodedString) 

        return direction, x_coordinate, y_coordinate

    except Exception as e:
        print("Caught error in getPosition:")
        print(str(e))
        raise e


#Distance estimation
symb_confidence = {}

def conf_init():
  confidence = {}
  for i in [0.1,0.2,0.3,0.4,0.5]:
    confidence[i]= i * 2
    confidence[1.0-(i)]= i * 2
  confidence[0.0] = 0.1
  confidence[1.0] = 1.0
  confidence = dict(sorted(confidence.items()))

  return confidence

def get_offset(x_dir,y_dir,idx,check):
  coef1 = [-1,0,1]
  coef2 = [-2,-1,0,1,2]
  coef3 = [-3,-2,-1,0,1,2,3]

  if (check == 1):
    x_off = y_dir * coef1[idx]
    y_off = -x_dir * coef1[idx]
  elif (check ==2):
    x_off = y_dir * coef2[idx]
    y_off = -x_dir * coef2[idx]
  elif (check ==3):
    x_off = y_dir * coef3[idx]
    y_off = -x_dir * coef3[idx]

  print("x_off: " + str(x_off))
  print("y_off: " + str(y_off))
  return (x_off, y_off)


def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx

def coordinates(distance,x_dir,y_dir,cur_x_cor,cur_y_cor,x_box):
  print("Cur_x_cor: " + str(cur_x_cor))
  print("Cur_y_cor: " + str(cur_y_cor))

  if (distance >= 215 ):
    distance -= 215
    conf = distance / 155 
    if (conf > 0.5):
      conf = 1.0
    img_cor = (cur_x_cor + (2*x_dir), cur_y_cor + (2*y_dir))

    CONST = np.array([92,269.8,447.6])
    
    idx = find_nearest(CONST,x_box)
    (x_off,y_off) = get_offset(x_dir,y_dir,idx,1)
    img_cor = (img_cor[0] + x_off, img_cor[1] + y_off)


  elif (distance >= 152.5 and distance < 215):
    distance -= 152.5
    conf = distance / 62.5 
    img_cor = (cur_x_cor + (3*x_dir) , cur_y_cor + (3*y_dir))

    CONST = np.array([141.45,263.15,384.85])

    # if (x_box <= CONST_X12):
    #   idx = 0
    # elif (x_box > CONST_X12 and x_box <= CONST_X22):
    #   idx = 1
    # else:
    #   idx = 2
    
    idx = find_nearest(CONST,x_box)
    (x_off,y_off) = get_offset(x_dir,y_dir,idx,1)
    img_cor = (img_cor[0] + x_off, img_cor[1] + y_off)

  elif (distance >= 126 and distance < 152.5):
    distance -= 126
    conf = distance / 26.5 
    img_cor = (cur_x_cor + (4*x_dir) , cur_y_cor + (4*y_dir))

    CONST = np.array([69.1,163.6,258.5,352.45,446.95])

    # if (x_box <= CONST_X13):
    #   idx = 0
    # elif (x_box > CONST_X13 and x_box <= CONST_X23):
    #   idx = 1
    # else:
    #   idx = 2

    idx = find_nearest(CONST,x_box)
    (x_off,y_off) = get_offset(x_dir,y_dir,idx,2)
    img_cor = (img_cor[0] + x_off, img_cor[1] + y_off)

  elif (distance >= 102.5 and distance < 126):
    distance -= 102.5
    conf = distance / 23.5 
    img_cor = (cur_x_cor + (5*x_dir) , cur_y_cor + (5*y_dir))

    CONST = np.array([105.95,181.95,258.25,333.1,409.1])

    # if (x_box <= CONST_X14):
    #   idx = 0
    # elif (x_box > CONST_X14 and x_box <= CONST_X24):
    #   idx = 1
    # elif (x_box > CONST_X24 and x_box <= CONST_X34):
    #   idx = 2
    # elif (x_box > CONST_X34 and x_box <= CONST_X44):
    #   idx = 3
    # else:
    #   idx = 4

    idx = find_nearest(CONST,x_box)
    (x_off,y_off) = get_offset(x_dir,y_dir,idx,2)
    img_cor = (img_cor[0] + x_off, img_cor[1] + y_off)

  elif (distance >= 88 and distance < 102.5):
    distance -= 88
    conf = distance / 14.5 
    img_cor = (cur_x_cor + (6*x_dir) , cur_y_cor + (6*y_dir))

    CONST = np.array([59.74,123.7,189.05,252.7,314.8,378.35,442.31])

    # if (x_box <= CONST_X15):
    #   idx = 0
    # elif (x_box > CONST_X15 and x_box <= CONST_X25):
    #   idx = 1
    # elif (x_box > CONST_X25 and x_box <= CONST_X35):
    #   idx = 2
    # elif (x_box > CONST_X35 and x_box <= CONST_X45):
    #   idx = 3
    # else:
    #   idx = 4
    idx = find_nearest(CONST,x_box)
    (x_off,y_off) = get_offset(x_dir,y_dir,idx,3)
    img_cor = (img_cor[0] + x_off, img_cor[1] + y_off)

  else:
    print("Distance: " + str(distance) + ". Image too far.")
    conf = 0.1234567
    img_cor = (cur_x_cor + (6*x_dir) , cur_y_cor + (6*y_dir))

  if (img_cor[0]<0):
    img_cor = (0,img_cor[1])
  elif (img_cor[0]>14):
    img_cor = (14,img_cor[1])
  if (img_cor[1]<0):
    img_cor = (img_cor[0],0)
  elif (img_cor[1]>19):
    img_cor = (img_cor[0],19)

  return (img_cor,conf)

def dist_est(box_len,img_symb,dir,x,y,x_box):
  distance =  int(round(box_len))
  print("Distance: ",distance)
  
  if (int(dir) == 0):
    (img_cor,conf) = coordinates(distance, -1, 0, x, y, x_box)
  elif (int(dir) == 90):
    (img_cor,conf) = coordinates(distance, 0, 1, x, y, x_box)
  elif (int(dir) == 270):
    (img_cor,conf) = coordinates(distance, 0, -1, x, y, x_box)
  elif (int(dir) == 180):
    (img_cor,conf) = coordinates(distance, 1, 0, x, y, x_box)

  print("Image Coordinates: ",img_cor)


  conf_lookup = conf_init()

  confidence = round(conf,1)
  if (conf != 0.1234567):
    try:
      for key in symb_confidence[img_symb]:
        alr_conf = key
      if (alr_conf<confidence):
        symb_confidence[img_symb] = {conf_lookup[confidence] : img_cor}
    except:
        symb_confidence[img_symb] = {conf_lookup[confidence] : img_cor}

  print(symb_confidence)


def detect():
    results = {}
    images = {}
    network, class_names, class_colors = darknet.load_network(
        CONFIG_FILE_PATH,
        DATA_FILE_PATH,
        WEIGHT_FILE_PATH,
        YOLO_BATCH_SIZE
    )
    try:
        print('Image recognition started!')
        while True:
            # cv2.waitKey(50)
            direction, x_coordinate , y_coordinate = 0, 0, 0
            frame = retrieveImg()
            image, detections = imageDetection(frame, network, class_names, class_colors, THRESH)
            
            #structure: list
            #element structure: (id, confidence, (bbox))
            #bbox: x, y, w, h
            for i in detections:
                id = i[0]
                confidence = i[1]
                bbox = i[2]
                
                #Code for evaluating bbox area


                print('ID detected: ' + id, ', confidence: ' + confidence)
                print('Bounding box: x = ' + str(bbox[0]) + ' y = ' + str(bbox[1]) + ' Width = ' + str(bbox[2]) + ' Height =' + str(bbox[3]))
                dist_est(bbox[3], id, direction, x_coordinate, y_coordinate, int(bbox[0]))
                if id in symb_confidence:
                    if id in results:
                        print('ID has been detected before')
                        # if float(confidence) > float(results[id][1]):
                        if float(confidence) > float(results[id][0][1]) and max(symb_confidence[id].keys()) >= max(results[id][1].keys()):
                            print('Higher confidence. Replacing existing image.')
                            # Removes existing result from dict
                            del results[id]
                            # Removes existing img from dict
                            del images[id]
                            # Adds new result to dict
                            # results[id] = i
                            # results[id] = [i, symb_confidence[id][max(symb_confidence[id].keys())]]
                            results[id] = [i, symb_confidence[id]]
                            # Adds new result to dict
                            images[id] = image
                            # saveImage(image, id)
                            # sendAndroidString(results)
                        else:
                            print('Lower confidence. Keeping existing image.')
                            pass
                    else:
                        print('New ID. Saving to results and images dict.')
                        # results[id] = i
                        # results[id] = [i, symb_confidence[id][max(symb_confidence[id].keys())]]
                        results[id] = [i, symb_confidence[id]]
                        images[id] = image
                        # saveImage(image, id)
                        # sendAndroidString(results)
    except KeyboardInterrupt:
        print('Image recognition ended')
    
    result_string = '{'
    print("Results:")
    
    for id in results:
        x_coordinate , y_coordinate = results[id][1][max(symb_confidence[id].keys())][0], results[id][1][max(symb_confidence[id].keys())][1]
        id_coordinate_str = '(' + id + ',' + str(x_coordinate) + ',' + str(y_coordinate) + '),'
        result_string += id_coordinate_str

        print('ID: ' + id + ', Coordinates: (' + str(x_coordinate) +',' + str(y_coordinate) + ')' + ', Confidence: ' + results[id][1])

    if result_string[-1] == ',':
        result_string = result_string[:-1]
    result_string += '}'
    print(result_string)

    # android_full_string = sendAndroidString(results)
    # print('Sent ' + android_full_string + ' to Android.')

    #generate image mosaic
    result_list = list(images.values())
    showImages(result_list)

if __name__ == "__main__":
    detect()