# CMPT461-Project - Background Selection Application
This is the project repo for CMPT461

![alt text](https://github.com/KeYu-Red/CMPT461-Project/blob/main/images/app_sample.jpg?raw=true)

### Approach
The idea is to create an application that will enable the users to select a video of their choice and interact with that video to select as much as the background possible. The user pauses the video at their desired frame and uses the brush to paint over the background. This will generate an image with as many background images as the user selects. When the user is happy with the result shown on the right-hand side, they can press “Done” and let the Background Matting V2 model (https://arxiv.org/abs/2012.07810) take care of generating two videos, one with a green screen and one with a background image of a road.

## Watch our project video
https://www.youtube.com/watch?v=73qDL7ux2JQ

## What our demos
There are two demos of the use case of the application, which can be downloaded and watched:
https://drive.google.com/drive/folders/1TNt7uIxVBlv5aQSx-PjTGojLMrrpr9EA?usp=sharing

## How to run the application
Please do the following steps to run the program:

1. Install python virtual environment:
```
pip install --user virtualenv
```

2. Create and run a virtual environmenet:
```
python -m venv ./env
./env/Scripts/activate
```

3. Install torch libs:
```
pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu113
```

4. Install other requirements
```
pip install -r requirements.txt
```

5. Run the program:
```
cd ./src
python main.py
```


