import shutil
import os
import cv2
import gdown
import numpy as np
import torch
from torchvision.transforms.functional import to_tensor, to_pil_image

class Model:
    def __init__(self, workspace_path = "../workspace/"):
 
        self.workspace_path = workspace_path
        self.saved_background = workspace_path + "background.jpg"
        self.new_background   = workspace_path + "new_background.jpg"
        self.final_video = workspace_path + "final_vid.avi"
        self.final_video_with_green_screen = workspace_path + "final_vid_green_screen.avi"
        
    def get_models(self):
        model_folder = "../model/"
        if os.path.exists(model_folder):
            shutil.rmtree(model_folder)
        os.mkdir(model_folder)

        url = "https://drive.google.com/drive/folders/1fMl7qepWqWvROlWvwLyr9TFGaAUBIYtW?usp=sharing"
        gdown.download_folder(url, output=model_folder)

    def run_model(self, video_path, background_image = None):
        #device = torch.device('cpu')
        
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        vid = cv2.VideoCapture(video_path)
        ret, frame = vid.read()
        h, w, l = frame.shape
        frame_rate = vid.get(cv2.CAP_PROP_FPS)

        cv2.destroyAllWindows()
        vid.release()

        vid = cv2.VideoCapture(video_path)

        new_vid = cv2.VideoWriter(self.final_video, 0, frame_rate, (w, h))
        new_vid2 = cv2.VideoWriter(self.final_video_with_green_screen, 0, frame_rate, (w, h))
        run = True

        if not os.path.exists("../model/torchscript_resnet50_fp32.pth"):
            print("Model Not Found!! Clearing directory and downloading models again")
            self.get_models()

        model = torch.jit.load("../model/torchscript_resnet50_fp32.pth").to(device).eval()
        model.backbone_scale = 0.25
        model.refine_mode = 'sampling'
        model.refine_sample_pixels = 80_000
        bkg = cv2.imread(self.saved_background)
        new_bkg = None
        if background_image == None:
            new_bkg = cv2.imread(self.new_background )
        else:
            new_bkg = background_image.copy()

        #Resizing to frame size
        new_bkg = cv2.resize(new_bkg, (w, h))

        bkg = to_tensor(bkg).to(device).unsqueeze(0)
        new_bkg = to_tensor(new_bkg).to(device).unsqueeze(0)

        count = 1
        while run:
            print(count)
            count = count + 1
            ret, frame = vid.read()
            if ret:
                src = frame.copy()
                # print(src.dtype)
                src = to_tensor(src).to(device).unsqueeze(0)
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

                com2 = pha * fgr + (1 - pha) * torch.tensor([120 / 255, 255 / 255, 155 / 255], device=device).view(1, 3, 1,
                                                                                                                1)
                fnl2 = to_pil_image(com2[0].cpu())
                open_cv_image2 = np.array(fnl2)
                new_vid2.write(open_cv_image2)

            else:
                break
