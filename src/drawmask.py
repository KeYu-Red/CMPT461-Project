import cv2
import numpy as np

class DrawMask:
    def __init__(self, image = None, brush_size = 25):
        self.img = image
        h, w, _ = image.shape
        self.img_mask = np.zeros((h,w), dtype=np.uint8)
        self.brush_size = brush_size
        self.name = "Press Q to quit    |   Press E to exit without saving    |   Press +/- to change the brush size"


    def draw_circle(self, event, x, y, flags, param):
        if flags == cv2.EVENT_FLAG_LBUTTON:
            # For display
            cv2.circle(self.img, (x, y), self.brush_size, (255, 0, 255), -1)

            #For return
            cv2.circle(self.img_mask, (x, y), self.brush_size, (255, 255, 255), -1)
    
    def draw(self):
        cv2.namedWindow(self.name)
        cv2.setMouseCallback(self.name, self.draw_circle)
        isSavedMask = False
        while (1):
            cv2.imshow(self.name, self.img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.imwrite("mask.jpg", self.img_mask)
                isSavedMask = True
                break
            elif cv2.waitKey(1) & 0xFF == ord('e'):
                break
            elif cv2.waitKey(1) & 0xFF == ord('+'):
                self.brush_size += 3
                if self.brush_size > 50: self.brush_size = 50
            elif cv2.waitKey(1) & 0xFF == ord('-'):
                self.brush_size -= 3
                if self.brush_size < 5: self.brush_size = 5

        cv2.destroyAllWindows()
        return [ isSavedMask, self.img_mask ]

