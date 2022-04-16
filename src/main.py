import PySimpleGUI as sg
import cv2
import os.path
import drawmask as dm

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

    window = sg.Window("WOOOOOOOOOOOW", layout)

    ##################################################
    displayVideo = False
    displayNewVideo = False
    drawBGMask = False
    captured = False
    allowDrawMask = False
    firstMaskDrawing = True
    currentFrame = []
    backgroundMask = []
    globalBackgroundMask = []
    bkgr = []


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

                # window["-IMAGE-"].update(filename=filename)

            except:
                pass
        elif event == "-DRAW-MASK-":
            if allowDrawMask: 
                drawBGMask = True

        elif values["-PAUSE-"]:
            displayVideo = False
            allowDrawMask = True

        elif values["-PLAY-"]:
            allowDrawMask = False
            displayVideo = True

        if displayVideo == True and captured == True:
            ret, frame = cap.read()
            currentFrame = frame
            frame = cv2.resize(frame, (600, 400))
            imgbytes = cv2.imencode(".png", frame)[1].tobytes()
            cap.get(cv2.CAP_PROP_POS_FRAMES)
            window["-IMAGE-"].update(data=imgbytes)
        
        if drawBGMask == True:
            drawBGMask = False
            backgroundMask = dm.DrawMask(image=currentFrame.copy(), brush_size=int(values["-BRUSH-SIZE-"])).draw()
            if firstMaskDrawing:
                globalBackgroundMask = backgroundMask.copy()
                firstMaskDrawing = False
            else:
                if values["-BRUSH-OPTION-"] == 2: 
                    globalBackgroundMask = cv2.subtract(globalBackgroundMask, backgroundMask )
                else:
                    globalBackgroundMask = cv2.add(globalBackgroundMask, backgroundMask )
            
        if globalBackgroundMask != []:
            (thresh, blackAndWhiteImage) = cv2.threshold(globalBackgroundMask, 127, 255, cv2.THRESH_BINARY)
            bkgr = cv2.bitwise_and(currentFrame, currentFrame, mask=blackAndWhiteImage)
            cv2.imwrite("background.jpg", bkgr)
            # Display on APP
            backgroundMaskdisplay = cv2.resize(bkgr, display_size)
            imgbytes = cv2.imencode(".png", backgroundMaskdisplay)[1].tobytes()
            cap.get(cv2.CAP_PROP_POS_FRAMES)
            window["-BG-"].update(data=imgbytes)

        #Debugging
            
    window.close()


main()
