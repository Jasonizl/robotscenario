import numpy as np
import matplotlib.image as mpimg
import os
import sys
import cv2
import time
sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'qr'))
sys.path.append('/home/blaxzter/Documents/robo/nao/pynaoqi-python2.7-2.1.2.17-linux64/')
from naoqi import ALProxy
from QRHandler import decodeImage


class Behaivior():
    def __init__(self):
        self.cameraId = 0  # 0 for
        self.vision = ALProxy('RobocupVision', 'nao3.local', 9559)
        self.motion = ALProxy('ALMotion', 'nao3.local', 9559)
        self.tts = ALProxy('ALTextToSpeech', 'nao3.local', 9559)
        self.motion.wakeUp()
        self.running = True
        self.state = 0
        self.detectet = -1
        self.qrcodes = ['red', 'blue', 'green']
        self.states = ['Search for QR-Code', 'Locate Area ', 'moving to Area' ]

    def run(self):
        while (self.running):
            # Say State
            # TODO SAY State with states[state] and tts from naoqi
            say = self.states[self.state]
            say += self.qrcodes[self.detectet] if self.detectet != -1 else ""
            self.tts.say(say)
            if self.state == 0:
                # turn around
                self.motion.moveTo(0, 0, 10 * np.pi/180)
                time.sleep(1000)
                # take pic and process
                data = self.vision.getBGR24Image(self.cameraId)
                image = np.fromstring(data, dtype=np.uint8).reshape((480, 640, 3))
                rgb_img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                mpimg.imsave("qrRec.png", rgb_img)
                qrcode = decodeImage(os.path.dirname(__file__) + "/qrRec.png")
                print qrcode
                # process qrcode
                if qrcode in self.qrcodes:
                    self.detectet = self.qrcodes.index(qrcode)
                    self.state += 1

            elif self.state == 1:
                # locate the area
                print "Locate the area"
                self.motion.rest()
                return
            elif self.state == 2:
                # locate the area
                print "Moving to area"

if __name__ == '__main__':
    agent = Behaivior()
    agent.run()
