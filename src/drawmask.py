import cv2
import numpy as np

class DrawMask:
    def __init__(self, image = None, brush_size = 25):
        self.img = image
        h, w, _ = image.shape
        self.img_mask = np.zeros((h,w), dtype=np.uint8)
        self.brush_size = brush_size


    def draw_circle(self, event, x, y, flags, param):
        if flags == cv2.EVENT_FLAG_LBUTTON:
            # For display
            cv2.circle(self.img, (x, y), self.brush_size, (255, 0, 255), -1)

            #For return
            cv2.circle(self.img_mask, (x, y), self.brush_size, (255, 255, 255), -1)
    
    def draw(self):
        cv2.namedWindow('image')
        cv2.setMouseCallback('image', self.draw_circle)

        while (1):
            cv2.imshow('image', self.img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.imwrite("mask.jpg", self.img_mask)
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
        return self.img_mask

