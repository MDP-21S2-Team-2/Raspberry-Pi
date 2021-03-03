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

  if (check):
    x_off = y_dir * coef1[idx]
    y_off = -x_dir * coef1[idx]
  else:
    x_off = y_dir * coef2[idx]
    y_off = -x_dir * coef2[idx]

  return (x_off, y_off)

def coordinates(distance,x_dir,y_dir,cur_x_cor,cur_y_cor,x_box):


  if (distance >= 215 ):
    distance -= 215
    conf = distance / 155 
    if (conf > 0.5):
      conf = 1.0
    img_cor = (cur_x_cor + (2*x_dir), cur_y_cor + (2*y_dir))

    if (x_box <= CONST_X11):
      idx = 0
    elif (x_box > CONST_X11 and x_box <= CONST_X21):
      idx = 1
    else:
      idx = 2
    
    (x_off,y_off) = get_offset(x_dir,y_dir,idx,True)
    img_cor = (img_cor[0] + (x_off), img_cor[0] + (y_off))


  elif (distance >= 152.5 and distance < 215):
    distance -= 152.5
    conf = distance / 62.5 
    img_cor = (cur_x_cor + (3*x_dir) , cur_y_cor + (3*y_dir))

    if (x_box <= CONST_X12):
      idx = 0
    elif (x_box > CONST_X12 and x_box <= CONST_X22):
      idx = 1
    else:
      idx = 2
    
    (x_off,y_off) = get_offset(x_dir,y_dir,idx,True)
    img_cor = (img_cor[0] + (x_off), img_cor[0] + (y_off))

  elif (distance >= 126 and distance < 152.5):
    distance -= 126
    conf = distance / 26.5 
    img_cor = (cur_x_cor + (4*x_dir) , cur_y_cor + (4*y_dir))

    if (x_box <= CONST_X13):
      idx = 0
    elif (x_box > CONST_X13 and x_box <= CONST_X23):
      idx = 1
    else:
      idx = 2
    
    (x_off,y_off) = get_offset(x_dir,y_dir,idx,True)
    img_cor = (img_cor[0] + (x_off), img_cor[0] + (y_off))

  elif (distance >= 102.5 and distance < 126):
    distance -= 102.5
    conf = distance / 23.5 
    img_cor = (cur_x_cor + (5*x_dir) , cur_y_cor + (5*y_dir))

    if (x_box <= CONST_X14):
      idx = 0
    elif (x_box > CONST_X14 and x_box <= CONST_X24):
      idx = 1
    elif (x_box > CONST_X24 and x_box <= CONST_X34):
      idx = 2
    elif (x_box > CONST_X34 and x_box <= CONST_X44):
      idx = 3
    else:
      idx = 4
    
    (x_off,y_off) = get_offset(x_dir,y_dir,idx,False)
    img_cor = (img_cor[0] + (x_off), img_cor[0] + (y_off))

  elif (distance >= 88 and distance < 102.5):
    distance -= 88
    conf = distance / 14.5 
    img_cor = (cur_x_cor + (6*x_dir) , cur_y_cor + (6*y_dir))

    if (x_box <= CONST_X15):
      idx = 0
    elif (x_box > CONST_X15 and x_box <= CONST_X25):
      idx = 1
    elif (x_box > CONST_X25 and x_box <= CONST_X35):
      idx = 2
    elif (x_box > CONST_X35 and x_box <= CONST_X45):
      idx = 3
    else:
      idx = 4

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

symb_confidence = {}
main(box_len = 260,img_symb = 6,dir = 'straight',x=5,y=3)

main(box_len = 250,img_symb = 6,dir = 'straight',x=2,y=3)
