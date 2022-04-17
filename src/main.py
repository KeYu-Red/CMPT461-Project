import PySimpleGUI as sg
import cv2
import os.path
import drawmask as dm
import os.path
import numpy as np
import torch
from torchvision.transforms.functional import to_tensor, to_pil_image

def run_model(background_image = None):
    device = torch.device('cpu')

    vid = cv2.VideoCapture("../video/vid_use.mp4")
    ret, frame = vid.read()
    h, w, l = frame.shape
    frame_rate = vid.get(cv2.CAP_PROP_FPS)

    cv2.destroyAllWindows()
    vid.release()

    vid = cv2.VideoCapture("../video/vid_use.mp4")

    new_vid = cv2.VideoWriter("final_vid.avi", 0, frame_rate, (w, h))
    new_vid2 = cv2.VideoWriter("final_vid_green_screen.avi", 0, frame_rate, (w, h))
    run = True

    model = torch.jit.load("../model/torchscript_resnet50_fp32.pth").to(torch.device('cpu')).eval()
    model.backbone_scale = 0.25
    model.refine_mode = 'sampling'
    model.refine_sample_pixels = 80_000
    bkg = cv2.imread("background.jpg")
    new_bkg = None
    if background_image == None:
        new_bkg = cv2.imread("new_background.jpg")
    else:
        new_bkg = background_image.copy()


    while run:
        ret, frame = vid.read()
        if ret:
            src = frame.copy()
            new_bkg = cv2.resize(new_bkg, (src.shape[1], src.shape[0]))
            src = to_tensor(src).to(torch.device('cpu')).unsqueeze(0)
            bkg = to_tensor(bkg).to(torch.device('cpu')).unsqueeze(0)
            new_bkg = to_tensor(new_bkg).to(torch.device('cpu')).unsqueeze(0)
            # print(src.shape)

            if src.shape[1] <= 2048 and src.shape[2] <= 2048:
                model.backbone_scale = 1 / 4
                model.refine_sample_pixels = 80_000
            else:
                model.backbone_scale = 1 / 8
                model.refine_sample_pixels = 320_000

            model = model.to(device)

            pha, fgr = model(src, bkg)[:2]

            com = pha * fgr + (1 - pha) * new_bkg
            fnl = to_pil_image(com[0].cpu())
            open_cv_image = np.array(fnl)
            new_vid.write(open_cv_image)

            com2 = pha * fgr + (1 - pha) * torch.tensor([120 / 255, 255 / 255, 155 / 255], device='cuda').view(1, 3, 1,
                                                                                                               1)
            fnl2 = to_pil_image(com2[0].cpu())
            open_cv_image2 = np.array(fnl2)
            new_vid2.write(open_cv_image2)

        else:
            break



def main():
    title = [sg.Text("CMPT461 Project", size=(60, 1), justification="center")]
    file_list_column = [
        [
            sg.Text("Image Folder"),
            sg.In(size=(25, 1), enable_events=True, key="-FOLDER-"),
            sg.FolderBrowse(),
            sg.Listbox(values=[], enable_events=True, size=(20, 5), key="-FILE LIST-")
        ]
    ]

    playVideo = [sg.Radio("Play Video", "Radio", size=(10, 1), default=True, key="-PLAY-")]
    pauseVideo = [
        [sg.Radio("Pause Video", "Radio", size=(10, 1), key="-PAUSE-"), sg.Button("Mask Edit", size=(10, 1), key="-DRAW-MASK-")],
        [sg.Text("Brush Size", key="-BRUSH-SIZE-TEXT-"), sg.Slider(range=(5,45), default_value= 20, resolution=5, orientation="h", size=(20, 15), key="-BRUSH-SIZE-")],
        [sg.Text("1: Draw  2:Erase"), sg.Slider(range=(1,2), default_value= 1, resolution=1, orientation="h", size=(20, 15), key="-BRUSH-OPTION-")],
        [sg.Button("Done", size=(10, 1), key="-DONE-")],

    ]

    ## diplay size
    display_size = (600, 400)
    displaySection =[[ [sg.Text("Playing Video(Left)"), sg.VSeperator(),sg.Text("Background (Right)")],
                       [sg.Image(filename="", key="-IMAGE-"), sg.VSeperator(), sg.Image(filename="", key="-BG-")]
        ]]
    #sg.Column(file_list_column)

    layout = [
        [title,
        file_list_column,
        playVideo,
        pauseVideo,
        displaySection]
    ]

    window = sg.Window("Background Generator", layout)

    ##################################################
    displayVideo = False
    displayNewVideo = False
    drawBGMask = False
    captured = False
    allowDrawMask = False
    firstMaskDrawing = True
    currentFrame = []
    backgroundMask = []
    new_background = []
    temp_bkgr = []


    ############################################################
    video_filename = ""
    cap = None

    while True:
        if video_filename != "" and displayNewVideo and displayVideo:
            cap = cv2.VideoCapture(video_filename)
            displayNewVideo = False
            captured = True

        event, values = window.read(timeout=20)
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        if event == "-FOLDER-":
            folder = values["-FOLDER-"]
            try:
                # Get list of files in folder
                file_list = os.listdir(folder)
            except:
                file_list = []

            fnames = [
                f
                for f in file_list
                if os.path.isfile(os.path.join(folder, f))
                and f.lower().endswith((".mp4", ".avi", ".mov"))
            ]
            window["-FILE LIST-"].update(fnames)
        elif event == "-FILE LIST-":  # A file was chosen from the listbox
            try:
                filename = os.path.join(
                    values["-FOLDER-"], values["-FILE LIST-"][0]
                )
                displayVideo = True
                displayNewVideo = True
                video_filename = filename

            except:
                pass
        elif event == "-DRAW-MASK-":
            if allowDrawMask:
                drawBGMask = True

        elif event == "-DONE-":
            run_model()
            print("Final video created as final_vid.mp4 with background image given or the road background")
            print("Final video also created with a green screen")
            break

        elif values["-PAUSE-"]:
            displayVideo = False
            allowDrawMask = True

        elif values["-PLAY-"]:
            allowDrawMask = False
            displayVideo = True

        if displayVideo == True and captured == True:
            ret, frame = cap.read()
            if ret:
                # currentFrame = frame
                if len(new_background) != 0:
                    frame[new_background > 0] = frame[new_background > 0] + 20
                currentFrame = frame
                frame = cv2.resize(frame, (600, 400))

                imgbytes = cv2.imencode(".png", frame)[1].tobytes()
                cap.get(cv2.CAP_PROP_POS_FRAMES)
                window["-IMAGE-"].update(data=imgbytes)
            else:
                cap = cv2.VideoCapture(video_filename)
                displayNewVideo = False
                captured = True

        if drawBGMask == True:
            drawBGMask = False
            # BG Mask from current frame
            backgroundMask = dm.DrawMask(image=currentFrame.copy(), brush_size=int(values["-BRUSH-SIZE-"])).draw()
            # Get current BG
            (thresh, blackAndWhiteImage) = cv2.threshold(backgroundMask, 127, 255, cv2.THRESH_BINARY)
            temp_bkgr = cv2.bitwise_and(currentFrame, currentFrame, mask=blackAndWhiteImage)

            if firstMaskDrawing:
                firstMaskDrawing = False
                new_background = temp_bkgr.copy()
            else:
                overall_background = cv2.imread("background.jpg")
                if values["-BRUSH-OPTION-"] == 2:
                    overall_background[temp_bkgr > 0] = 0
                    new_background = overall_background.copy()
                else:
                    overall_background[temp_bkgr > 0] = 0
                    new_background = cv2.add(overall_background, temp_bkgr)

            cv2.imwrite("background.jpg", new_background)

        if len(new_background) != 0:
            # Display on APP
            backgrounddisplay = cv2.resize(new_background, display_size)
            imgbytes = cv2.imencode(".png", backgrounddisplay)[1].tobytes()
            cap.get(cv2.CAP_PROP_POS_FRAMES)
            window["-BG-"].update(data=imgbytes)

        #Debugging

    window.close()


main()
