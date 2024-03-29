import numpy as np
import cv2
import numpy as np
import os

def img_stitch(path):
  imgs = []
  for i in os.listdir(path):
    img = cv2.imread(path + i)
    print(img)
    imgs.append(img)
  im_f = cv2.hconcat([imgs[0], imgs[1], imgs[2], imgs[3], imgs[4]])
  cv2.imwrite(path + 'fin.jpg', im_f)
  
def conf_init():
  confidence = {}
  for i in [0.1,0.2,0.3,0.4,0.5]:
    confidence[i]= i * 2
    confidence[1.0-(i)]= i * 2
  confidence[0.0] = 0.1
  confidence[4.5] = 0.9
  confidence[1.0] = 1.0
  confidence[0.01] = 0.0
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

  return (x_off, y_off)


def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx

def coordinates(distance,x_dir,y_dir,cur_x_cor,cur_y_cor,x_box):
  if (distance >= 95.5 ):
    distance -= 95.5
    conf = distance / 23.75 #changed from 68.5 to 55
    conf = round(conf,1)
    if (conf > 0.5):
      conf = 1.0
    img_cor = (cur_x_cor + (2*x_dir), cur_y_cor + (2*y_dir))

    CONST = np.array([92,269.8,447.6])
    
    idx = find_nearest(CONST,x_box)
    (x_off,y_off) = get_offset(x_dir,y_dir,idx,1)
    img_cor = (img_cor[0] + x_off, img_cor[1] + y_off)


  elif (distance >= 67.7 and distance < 95.5):
    distance -= 67.7
    conf = distance / 27.8 
    conf = round(conf,1)
    if conf==0.5:
      conf = 4.5
    img_cor = (cur_x_cor + (3*x_dir) , cur_y_cor + (3*y_dir))

    CONST = np.array([141.45,263.15,384.85])
    
    idx = find_nearest(CONST,x_box)
    (x_off,y_off) = get_offset(x_dir,y_dir,idx,1)
    img_cor = (img_cor[0] + x_off, img_cor[1] + y_off)

  elif (distance >= 56 and distance < 67.7):
    distance -= 56
    conf = distance / 11.7 
    conf = round(conf,1)
    if conf==0.5:
      conf = 4.5
    img_cor = (cur_x_cor + (4*x_dir) , cur_y_cor + (4*y_dir))

    CONST = np.array([69.1,163.6,258.5,352.45,446.95])

    idx = find_nearest(CONST,x_box)
    (x_off,y_off) = get_offset(x_dir,y_dir,idx,2)
    img_cor = (img_cor[0] + x_off, img_cor[1] + y_off)

  elif (distance >= 45.5 and distance < 56):
    distance -= 45.5
    conf = distance / 10.5 
    conf = round(conf,1)
    if conf==0.5:
      conf = 4.5
    img_cor = (cur_x_cor + (5*x_dir) , cur_y_cor + (5*y_dir))

    CONST = np.array([105.95,181.95,258.25,333.1,409.1])

    idx = find_nearest(CONST,x_box)
    (x_off,y_off) = get_offset(x_dir,y_dir,idx,2)
    img_cor = (img_cor[0] + x_off, img_cor[1] + y_off)

  elif (distance >= 39 and distance < 45.5):
    distance -= 39
    conf = distance / 6.5 
    conf = round(conf,1)
    if conf==0.5:
      conf = 4.5
    img_cor = (cur_x_cor + (6*x_dir) , cur_y_cor + (6*y_dir))

    CONST = np.array([59.74,123.7,189.05,252.7,314.8,378.35,442.31])

    idx = find_nearest(CONST,x_box)
    (x_off,y_off) = get_offset(x_dir,y_dir,idx,3)
    img_cor = (img_cor[0] + x_off, img_cor[1] + y_off)

  else:
    print("Distance: " + str(distance) + ". Image too far.")
    conf = 0.01
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

def main(box_len,img_symb,dir,x,y,x_box):
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

  # if (conf != 0.1234567):
  try:
    for key in symb_confidence[img_symb]:
      alr_conf = key
      # print(key)
    if (alr_conf<conf_lookup[conf]):
      symb_confidence[img_symb] = {conf_lookup[conf] : img_cor}
      # print("First ")
      # print(symb_confidence)
    else:
      print("High Confidence value not replaced")
  except:
      symb_confidence[img_symb] = {conf_lookup[conf] : img_cor}
      # print("Second ")
      # print(symb_confidence)

  print(symb_confidence)
