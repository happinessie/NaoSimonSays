#A utility program that will help calibrate the boundaries for color filtering: loads a photo and then a range of HSV values 
#can be determined by adjusting the low and high color trackbars until everything in the photo disapperas except the 
# desired color/object, 

#based on docs.opencv.org/3.0-beta/doc/py_tutorials/py_gui/py_trackbar/py_trackbar.html
#based on http://stackoverflow.com/questions/10948589/choosing-correct-hsv-values-for-opencv-thresholding-with-inranges

#################################TO DO ##################################
#1. input verification-->Freezes if the low value greater than high value

import cv2
import numpy as np
from copy import deepcopy
from naoqi import ALProxy
import vision_definitions

def nothing(x):
        pass
    
def main(port,ip):
    #IP address and port number of NAO robot
    IP=ip
    PORT=port
    #establish connection to NAO
    proxy=ALProxy('ALVideoDevice','192.168.1.112',9559)
    #set-up configuration for images
    camera=0 #top camera=0 bottom camera=1
    resolution=vision_definitions.kVGA 
    colorSpace=vision_definitions.kBGRColorSpace
    fps=10
    #subscribe to NAO's camera with given camera configuration
    client=proxy.subscribeCamera("detector", camera, resolution,colorSpace,fps)
    #width and height of the images
    width=640
    height=480
    #image = np.zeros((height,width,3),np.uint8)
    image=None
    #get an image from NAO
    result = proxy.getImageRemote(client)
    #make sure an image was received and it has information
    if result is None:
        print ("cannot get image")
    elif result[6] is None:
        print ("no image data string.")
    else:
        #reshape the image data into a multi-dimensional array 
        img=np.fromstring(result[6],np.uint8).reshape(480,640,3)
        #release the image and unsubscribe from NAO's camera since we won't use it again
        proxy.releaseImage(client)
        proxy.unsubscribe(client)
            
        #create a window with 6 trackbars: H low, H high, S low, S high, V low, and V high
        cv2.namedWindow('result')
        cv2.resizeWindow('result',500,500)
        cv2.createTrackbar('h_low','result',0,179,nothing)
        cv2.createTrackbar('s_low','result',0,255,nothing)
        cv2.createTrackbar('v_low','result',0,255,nothing)

        cv2.createTrackbar('h_high','result',179,179,nothing)
        cv2.createTrackbar('s_high','result',255,255,nothing)
        cv2.createTrackbar('v_high','result',255,255,nothing)

        h,s,v=100,100,100

        #create a loop that will apply filter the image using the values in the trackbars as the boundaries. Display the filtered image.
        while(1):
                h_low=cv2.getTrackbarPos('h_low','result')
                s_low=cv2.getTrackbarPos('s_low','result')
                v_low=cv2.getTrackbarPos('v_low','result')

                h_high=cv2.getTrackbarPos('h_high','result')
                s_high=cv2.getTrackbarPos('s_high','result')
                v_high=cv2.getTrackbarPos('v_high','result')

                #filter the image and draw a rectangle around the largest contour
                lower=np.array([h_low,s_low,v_low])
                upper=np.array([h_high,s_high,v_high])
                hsv=cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
                mask=cv2.inRange(hsv,lower,upper)
                kernel = np.ones((5,5),np.uint8)
                mask=cv2.erode(mask,kernel,iterations=1)
                mask=cv2.dilate(mask,kernel,iterations=1)

                result=cv2.bitwise_and(img,img,mask=mask)
                im2,contours,hierarchy=cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
                areas=[cv2.contourArea(c) for c in contours]
                max_index=np.argmax(areas)
                cnt=contours[max_index]
                        
                x,y,w,h=cv2.boundingRect(cnt)
                cv2.rectangle(result,(x,y),(x+w,y+h),(0,255,0),2)

                cv2.imshow('result',result)
                
                k=cv2.waitKey(5) & 0xFF
                if k==27:
                    break

        cv2.destroyAllWindows()

if __name__ == "__main__" :
    main("192.168.1.112",9559)
