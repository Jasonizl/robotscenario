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
import dance

class Behaivior():
    def __init__(self):
        self.vision = ALProxy('RobocupVision', 'nao5.local', 9559)
        self.motion = ALProxy('ALMotion', 'nao5.local', 9559)
        self.tts = ALProxy('ALTextToSpeech', 'nao5.local', 9559)
        self.motion.wakeUp()
        self.running = True
        self.state = 0
        self.detectet = -1
        self.qrcodes = ['red', 'yellow', 'purple']
        self.hsv_values = [[5, 360], [50], [243, 248, 252]]
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
                    # time.sleep(1000)  # Wait till the body shaking is over for a stable picture

            elif self.state == 1:
                # Move to the colored sheet on the floor
                on_color = False
                while not on_color:
                    # image = cv2.imread("qrRec.png")
                    # rgb_img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    rgb_img = self.getPicture(0)
                    count, pos = self.getColorPose(rgb_img, self.hsv_values[self.detectet])
                    # if not found rotate and search
                    if pos[0] == -1:
                        self.tts.say("No Color")
                        self.motion.moveTo(0, 0, 45 * np.pi / 180)
                        continue
                    # now do some shit if its found orient so the pos is in the middle

                    dist = pos[0] - 320
                    if dist < 50 and dist > -50:
                        self.tts.say("Orientiert")

                        self.motion.moveTo(0.25, 0, 0) # Make a forward movement in the right direction

                        # Take picture from the second camera and if more of 80% is read you are standing right.
                        below_pic = self.getPicture(1)
                        count, pos = self.getColorPose(below_pic, self.hsv_values[self.detectet])
                        saying = str(int((count/(480. * 640.) * 100))) + " Percent."
                        self.tts.say(saying)
                        print(saying)
                        if (count/(480. * 640.)) > 0.60:
                            self.state += 1
                            on_color = True


                    # If the center of mass is left to the middle move right else left
                    elif dist <= -50:
                        if dist <= -160:
                            self.tts.say("Turn Left Big")
                            self.motion.moveTo(0, 0, 16 * np.pi / 180)
                        else:
                            self.tts.say("Turn Left Small")
                            self.motion.moveTo(0, 0, 8 * np.pi / 180)
                    else:
                        if dist >= 160:
                            self.tts.say("Turn Right BIG")
                            self.motion.moveTo(0, 0, - 16 * np.pi / 180)
                        else:
                            self.tts.say("Turn Right SMALL")
                            self.motion.moveTo(0, 0, - 8 * np.pi / 180)

            elif self.state == 2:
	        self.motion.angleInterpolationBezier(dance())
                self.tts.say("finished")
                self.motion.rest()
                return

    def getColorPose(self, rgb_img, searched_h_values):

        posx, posy = 0, 0
        count = 0
        for y in range(480):
            for x in range(640):
                r, g, b = rgb_img[y, x]
                h, s, v = colorsys.rgb_to_hsv(r / 255., g / 255., b / 255.)
                if s < 0.1:
                    rgb_img[y, x] = [0, 0, 0]
                    continue

                found = False
                for h_value in searched_h_values:
                    dist = np.abs(h_value - h * 360)
                    if dist < 5:
                        posx += x
                        posy += y
                        count += 1
                        found = True
                        break

                if not found:
                    rgb_img[y, x] = [0, 0, 0]

        # if more then 50 pixel are in
        if count > 500:
            posx /= count
            posy /= count
            rgb_img[posy, posx] = [0, 255, 0]
            rgb_img[posy, posx + 1] = [0, 255, 0]
            rgb_img[posy, posx - 1] = [0, 255, 0]
            rgb_img[posy + 1, posx] = [0, 255, 0]
            rgb_img[posy - 1, posx] = [0, 255, 0]
        else:
            posx = -1
            posy = -1

        mpimg.imsave("ColoredPicture.png", rgb_img)

        return count, [posx, posy]

    def getPicture(self, cameraId):
        data = self.vision.getBGR24Image(cameraId)
        image = np.fromstring(data, dtype=np.uint8).reshape((480, 640, 3))
        rgb_img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        mpimg.imsave("Current_Picture.png", rgb_img)
        return rgb_img

if __name__ == '__main__':
    agent = Behaivior()
    agent.run()
