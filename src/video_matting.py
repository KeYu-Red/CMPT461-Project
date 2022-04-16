from pip import main
import pygame
import cv2
from matplotlib import pyplot as plt
import numpy as np
 
def get_bkgr():
    image = cv2.imread("frame1.jpg")
    mask = cv2.imread("mask.jpg")
    grayImage = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
    (thresh, blackAndWhiteImage) = cv2.threshold(grayImage, 127, 255, cv2.THRESH_BINARY)
    bkgr = cv2.bitwise_and(image, image, mask=blackAndWhiteImage)
 
    cv2.imwrite("bgr.jpg", bkgr)
 
def video_play():
    pygame.display.init()
    pygame.display.update()
    print("=================================")
    video = cv2.VideoCapture("./video/vid_use.mp4")
    success, video_image = video.read()
    print(video_image)
    cv2.imwrite("frame1.jpg", video_image)
    frame1 = cv2.imread("frame1.jpg")
    h, w, l = video_image.shape
    img_mask = np.zeros((h,w), dtype=np.uint8)
    temp_mask = np.zeros((h,w), dtype=np.uint8)
    fps = video.get(cv2.CAP_PROP_FPS)
    RED = (255, 0, 0)
    window = pygame.display.set_mode(video_image.shape[1::-1])
    clock = pygame.time.Clock()
    run = success
    brush = None
    paused = False
    brush_size = 50
    

    print("=================================")
    print("Press left mouse button and hold to color the background and let go when done")
    print("Press the PLUS or MINUS key to increase or decrease the size of the brush (respectively)")
    print("=================================")
    while run:
        clock.tick(fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # print("Mouse buton Down")
                paused = True
                if event.button == 1:  # left button pressed
                    brush = event.pos
            elif event.type == pygame.MOUSEBUTTONUP:
                # print("Mouse buton Up")
                # cv2.add(img_mask, temp_mask)
                paused = False
                temp_mask = np.zeros((h,w), dtype=np.uint8)
                if event.button == 1:  # left button released
                    brush = None
            elif event.type == pygame.MOUSEMOTION:
                if brush:  # left button still pressed
                    paused = True
                    brush = event.pos
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_KP_MINUS:
                    print("Brush Size: ", brush_size)
                    brush_size = brush_size - 10
                if event.key == pygame.K_KP_PLUS:
                    print("Brush Size: ", brush_size)
                    brush_size = brush_size + 10
                if event.key == pygame.K_SPACE:
                    if paused == False:
                        paused = True
                    else:
                        paused = False
        # draw brush in bufor
        if brush:
            pygame.draw.circle(window, RED, (brush[0], brush[1]), brush_size)
            # cv2.circle(video_image, (brush[0], brush[1]), 10, (255, 0, 0, 0), -1)
            cv2.circle(temp_mask, (brush[0], brush[1]), brush_size, (255, 255, 255), -1)
            # temp_mask[brush[0], brush[1]] = 255
            temp_mask = cv2.add(temp_mask, temp_mask)
            img_mask = cv2.add(img_mask, temp_mask)
            # plt.imshow(temp_mask)
            # plt.show()
        # send bufor on the screen
        pygame.display.flip()
 
        if not paused:
            success, video_image = video.read()
 
            video_surf = None
            if success:
                h, w, l = video_image.shape
                video_surf = pygame.image.frombuffer(
                    video_image.tobytes(), video_image.shape[1::-1], "BGR")
            else:
                break
            window.blit(video_surf, (0, 0))
            pygame.display.flip()
 
    pygame.quit()
 
    cv2.imwrite("mask.jpg", img_mask)
    get_bkgr()
    plt.figure()
    plt.imshow(img_mask)
    plt.show()
    

video_play()