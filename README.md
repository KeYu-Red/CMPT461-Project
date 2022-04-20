# CMPT461-Project
This is the project repo for CMPT461
The idea is to create an application that will enable the users to select a video of their choice and interact with that video to select as much as the background possible. 

## Watch our project video
https://www.youtube.com/watch?v=73qDL7ux2JQ

## How to run the application
Please do the following steps to run the program:

1. Install python virtual environment:
pip install --user virtualenv

2. Create and run a virtual environmenet: 
python -m venv ./env
./env/Scripts/activate

3. Install torch libs:
pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu113

4. Install other requirements
pip install -r requirements.txt

5. Run the program:
cd ./src
python main.py


