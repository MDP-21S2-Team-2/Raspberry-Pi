import darknet.darknet as darknet
from cv2 import cv2
import numpy as np
import imutils
import random

SAVED_IMAGE_PATH = 'D:/Tai_lieu/Academic/Year_3_Semester_2/CZ3004_Multidisciplinary_Design_Project/Image_Recognition_Dependencies/saved_images/'
SOURCE_PATH = 'D:/Tai_lieu/Academic/Year_3_Semester_2/CZ3004_Multidisciplinary_Design_Project/Image_Recognition_Dependencies/darknet/'
WEIGHT_FILE_PATH = SOURCE_PATH + 'backup/yolo-obj_last.weights'
CONFIG_FILE_PATH = SOURCE_PATH + 'cfg/yolo-obj.cfg'
DATA_FILE_PATH = SOURCE_PATH + 'data/obj.data'
RPI_IP = '192.168.2.2'
STREAM_URL = 'http://' + RPI_IP + '/html/cam_pic_new.php'
YOLO_BATCH_SIZE = 4
THRESH = 0.95

def retrieve_img():
    # Captures a frame from video stream and returns an opencv image
    cap = cv2.VideoCapture(STREAM_URL)
    ret, frame = cap.read()
    return frame

def image_detection(image, network, class_names, class_colors, thresh):
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

def save_image(frame, id):
    frame = imutils.resize(frame, width=500, height=480)
        
    # Saves images to local storage
    cv2.imwrite(SAVED_IMAGE_PATH + 'result_' + str(id) + '.jpeg', frame)
        
def show_images(frame_list):
    for index, frame in enumerate(frame_list):
        frame = imutils.resize(frame, width=500, height=480)
        
        # Saves images to local storage
        # cv2.imwrite(SAVED_IMAGE_PATH + 'result_' + str(index) + '.jpeg', frame)
        cv2.imshow('Image' + str(index), frame)

    if cv2.waitKey() & 0xFF == ord('q'):
        cv2.destroyAllWindows()

def format_string(i, x_coor, y_coor):
    if int(i) < 10:
        i = '0' + i
    if int(x_coor) < 10:
        x_coor = '0' + x_coor
    if int(y_coor) < 10:
        y_coor = '0' + y_coor
    
    return 'ID' + i + x_coor +y_coor

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
            frame = retrieve_img()
            image, detections = image_detection(frame, network, class_names, class_colors, THRESH)
            
            #structure: list
            #element structure: (id, confidence, (bbox))
            #bbox: x, y, w, h
            for i in detections:
                id = i[0]
                confidence = i[1]
                bbox = i[2]
                print('ID detected: ' + id, ', confidence: ' + confidence)
                if id in results:
                    print('ID has been detected before')
                    if float(confidence) > float(results[id][1]):
                        print('Higher confidence. Replacing existing image.')
                        # Removes existing result from dict
                        del results[id]
                        # Removes existing img from dict
                        del images[id]
                        # Adds new result to dict
                        results[id] = i
                        # Adds new result to dict
                        images[id] = image
                        save_image(image, id)
                    else:
                        print('Lower confidence. Keeping existing image.')
                        pass
                else:
                    print('New ID. Saving to results and images dict.')
                    results[id] = i
                    images[id] = image
                    save_image(image, id)
    except KeyboardInterrupt:
        print('Image recognition ended')
    
    result_string = '{'
    print("Results:")
    
    for i in results:
        x_coordinate = random.randint(0,14)
        y_coordinate = random.randint(0,19)
        id_coordinate_str = '(' + i + ',' + str(x_coordinate) + ',' + str(y_coordinate) + '),'
        result_string += id_coordinate_str

        # String format: IDABXXYY
        android_string = format_string(i, str(x_coordinate), str(y_coordinate))
        print(android_string)
        # send string to android

        print('ID: ' + i + ', Coordinates: (' + str(x_coordinate) +',' + str(y_coordinate) + ')' + ', Confidence: ' + results[i][1])

    if result_string[-1] == ',':
        result_string = result_string[:-1]
    result_string += '}'
    print(result_string)

    #generate image mosaic
    result_list = list(images.values())
    show_images(result_list)

if __name__ == "__main__":
    detect()