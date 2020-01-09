import cv2
import os
import ntpath

def create_thumbnail(filepath):

    os.mkdir("media/thumbnails")

    img = cv2.imread(filepath)
    img = cv2.resize(img, (300, 200), interpolation=cv2.INTER_NEAREST)
    cv2.imwrite('media/thumbnails/thumb_{}'.format(ntpath.basename(filepath)), img)
    print("Thumbnail created!")



path = 'media/full/2020-01-04/2020-01-04_14-30-13.jpg'

create_thumbnail(path)
