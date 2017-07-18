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
        self.vision = ALProxy('RobocupVision', 'nao3.local', 9559)
        self.motion = ALProxy('ALMotion', 'nao3.local', 9559)
        self.tts = ALProxy('ALTextToSpeech', 'nao3.local', 9559)
        self.motion.wakeUp()
        self.running = True
        self.state = 0
        self.detectet = -1
        self.qrcodes = ['red', 'blue', 'green']
        self.hsv_values = [[0, 360], [240], [120]]
        self.states = ['Search for QR-Code', 'orientate and move To', 'Dancing']

    def run(self):
        while (self.running):
            # Say State
            say = self.states[self.state]
            say += " " + self.qrcodes[self.detectet] if self.detectet != -1 else ""
            self.tts.say(say)

            if self.state == 0:

                # take pic and process
                rgb_img = self.getPicture(0)

                # Process the picture for qr_codes
                mpimg.imsave("qrRec.png", rgb_img)
                qrcode = decodeImage(os.path.dirname(__file__) + "/qrRec.png")

                # If the qr-code is in the qr-code list change state else turn around
                if qrcode in self.qrcodes:
                    self.detectet = self.qrcodes.index(qrcode)
                    self.state += 1
                else:
                    self.motion.moveTo(0, 0, 10 * np.pi / 180)
                    time.sleep(1000)  # Wait till the body shaking is over for a stable picture

            elif self.state == 1:
                # Move to the colored sheet on the floor
                on_color = False
                while not on_color:
                    count, pos = self.getColorPose(rgb_img, self.hsv_values[self.detectet])
                    on_color = True
                    # if not found rotate and search
                    if pos[0] == -1:
                        self.motion.moveTo(0, 0, 10 * np.pi / 180)
                        continue
                    # now do some shit if its found orient so the pos is in the middle

                    dist = np.abs(pos[0] - 240)
                    if dist < 50:
                        print "Oriented"

                        self.motion.moveTo(1, 0, 0) # Make a forward movement in the right direction

                        # Take picture from the second camera and if more of 80% is read you are standing right.
                        below_pic = self.getPicture(0)
                        count, pos = self.getColorPose(rgb_img, self.hsv_values[self.detectet])
                        if count/(480. * 640.) > 0.8:
                            self.state += 1

                    # If the center of mass is left to the middle move right else left
                    elif pos[0] - 240 < 0:
                        self.motion.moveTo(0, 0, - 5 * np.pi / 180)
                    else:
                        self.motion.moveTo(0, 0, 5 * np.pi / 180)

            elif self.state == 2:
                # TODO make some dacing stuff
                self.motion.rest()
                return

    def getColorPose(self, rgb_img, searched_h_values):

        posx, posy = 0, 0
        count = 0
        for x in range(480):
            for y in range(640):
                b, g, r = rgb_img[y, x]
                h, s, v = colorsys.rgb_to_hsv(r / 255., g / 255., b / 255.)
                if s < 0.1:
                    continue
                for h_value in searched_h_values:
                    dist = np.abs(h_value - h * 360)
                    if dist < 5:
                        posx += x
                        posy += y
                        count += 1

        # if more then 50 pixel are in
        if count > 50:
            posx /= count
            posy /= count
        else:
            posx = -1
            posy = -1

        return count, [posx, posy]

    def getPicture(self, cameraId):
        data = self.vision.getBGR24Image(cameraId)
        image = np.fromstring(data, dtype=np.uint8).reshape((480, 640, 3))
        rgb_img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return rgb_img

if __name__ == '__main__':
    agent = Behaivior()
    agent.run()
