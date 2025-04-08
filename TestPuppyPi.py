import base64
import cv2  # pip install opencv-python
import numpy as np  # pip install numpy
from PuppyPi import PuppyPi
import time


class Test:
    def __init__(self, ip):
        self.puppy = PuppyPi(ip)

    def finish(self):
        self.puppy.finish()
        cv2.destroyAllWindows()

    def processImage(self, result):
        # los datos de la imagen
        h = result["height"]
        w = result["width"]
        enc = result["encoding"]
        img = result["data"].encode("ascii")

        # viene en base 64
        img = base64.b64decode(img)

        # la necesitamos como BGR para opencv
        img = np.frombuffer(img, np.uint8)
        img = img.reshape((h, w, 3))
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        # la mostramos
        cv2.imshow("USB CAM", img)
        k = cv2.waitKey(1)

    def doActions(self):
        self.puppy.runActionGroup(PuppyPi.ACTION_PEE, pause=4)
        self.puppy.runActionGroup(PuppyPi.ACTION_SIT, pause=4)
        self.puppy.runActionGroup(PuppyPi.ACTION_STAND_4_LEGS, pause=4)

    def doPose(self):
        self.puppy.setPoseLieDown()
        self.puppy.setPose(roll=0, pitch=0, height=70)

    def doMovements(self):
        self.puppy.setPoseStand()

        self.puppy.move(x=5.0, yaw_rate=-5)
        time.sleep(2)
        self.puppy.move_stop()
        time.sleep(1)

    def run(self):
        self.puppy.imageRaw_start(self.processImage)

        self.doActions()
        self.doPose()
        self.doMovements()
        
        self.puppy.setPoseLieDown()
        self.puppy.imageRaw_stop()
        self.finish()


#
test = Test("192.168.149.1")
test.run()
