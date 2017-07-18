import numpy as np
import matplotlib.image as mpimg
import os
import sys
import cv2
import time
import colorsys
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
        self.hsv_values = [0, 120, 180]
        self.states = ['Search for QR-Code', 'orientate and move To']

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
                print "Orientate and Move to the Color"
                on_color = False
                while not on_color:
                    count, pos = self.getColorPose(rgb_img, self.hsv_values[self.detectet])
                    # if not found rotate and search
                    if count <= 5:
                        self.motion.moveTo(0, 0, 10 * np.pi / 180)
                        continue
                    # now do some shit if its found orient so the pos is in the middle

                self.motion.rest()
                return
            elif self.state == 2:
                # locate the area
                print "Moving to area"


    def getColorPose(self, rgb_img, searched_h_value):

        posx, posy = 0, 0
        count = 0
        for x in range(480):
            for y in range(640):
                r, g, b = rgb_img[x, y]
                h, s, v = colorsys.rgb_to_hsv(r, g, b)
                if s < 0.05:
                    continue
                dist = np.abs(searched_h_value - h * 360)
                if dist < 5:
                    posx += x
                    posy += y
                    count += 1

        if count > 1:
            posx /= count
            posy /= count

        return count, [posx, posy]

if __name__ == '__main__':
    agent = Behaivior()
    agent.run()
