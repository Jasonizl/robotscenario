import numpy as np
import matplotlib.pyplot as plt
import os
import sys
import cv2
sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'qr'))
sys.path.append('/home/blaxzter/Documents/robo/nao/pynaoqi-python2.7-2.1.2.17-linux64/')
from naoqi import ALProxy
from QRHandler import decodeImage


class Behaivior():
    def __init__(self):
        self.cameraId = 0  # 0 for
        self.vision = ALProxy('RobocupVision', 'nao1.local', 9559)
        self.motion = ALProxy('ALMotion', 'nao1.local', 9559)
        self.run = True
        self.states = ['search', 'locateArea', 'movingToArea'] # TODO more States here
        self.state = 1
        self.qrcodes = ['red', 'blue', 'green']


    def run(self):
        while (self.run):
            # Say State
            # TODO SAY State with states[state] and ttls bla from naoqi
            if self.state == 1:
                # turn around
                self.motion.moveto(0, 0, 2)

                # take pic and process
                data = self.vision.getBGR24Image(self.cameraId)
                image = np.fromstring(data, dtype=np.uint8).reshape((480, 640, 3))
                rgb_img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                plt.matshow(rgb_img)
                plt.savefig('qrRec.png')
                qrcode = decodeImage(os.path.dirname(__file__) + "/qrRec.png")

                # process qrcode
                if qrcode in self.qrcodes:
                    self.state += 1

            elif self.state == 2:
                # locate the area
                print "Locate the area"
            elif self.state == 3:
                # locate the area
                print "Moving to area"

if __name__ == '__main__':
    agent = Behaivior()
    agent.run()
