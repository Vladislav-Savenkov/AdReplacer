import cv2
import numpy as np

class AdDetecter:
    def __init__(self, image):
        self.input_image = cv2.imread(image)
        self.grey_img = cv2.cvtColor(self.input_image, cv2.COLOR_BGR2GRAY)
        self.detected_ad = 0

    def detect_ad(self, ads):
        for ad in ads:
            possible_ad = cv2.imread(ad, 0)
            w, h = possible_ad.shape[::-1]

            res = cv2.matchTemplate(self.grey_img, possible_ad, cv2.TM_CCOEFF_NORMED)
            #print(res)
            threshold = 0.8;
            loc = np.where(res >= threshold)
            #print(loc)
            if len(loc) > 1:
                self.detected_ad = 1
            for pt in zip(*loc[::-1]):
                cv2.rectangle(self.input_image, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)

        cv2.imshow("img", self.input_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()