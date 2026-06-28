# NotSoIntelligentCCTV

NOTE: This repo is a copy of [this](https://github.com/Nishchay-Bhudia/Intelligent-Office-Surveillance-System) (**Also made by me**), a school project which I added updates to for [stardance](https://stardance.hackclub.com/home). This copy will allow me to add my own features and updates without interferring with the original project

## Context
This is a python script that you can keep running while you leave your computer. It's purpose is to be a light-weight *motion-detection* program that will save low framerate footage, designed to be extremely simple.

## Usage
You can choose to download the bundled .exe file in the releases as a windows user, or you can choose to run **GUI1.py**, aslong as the other files, systemArmed.py and clearMedia.py lie in the same folder as GUI1. Doing so will require you to install openCV, customtkinter and pillow packages.

<img width="520" height="547" alt="image" src="https://github.com/user-attachments/assets/9b7a298a-ff57-4552-b960-3c16839aaf30" />

The ***ARM SYSTEM*** button will turn on actual motion detection and logging. Motion is "detected" if the next image taken differs from the previous, and for the next 30s, images will be taken at 2fps, before going back to 1fps when motion is no longer detected.
***View events*** will open the folder containing these images taken during motion, and for ease of use, images within an event will be bundled into a video (this may come in handy if motion was detected for a while and you dont want to flick thhrough tons of images.
The ***Clear all media*** button will remove all images and videos, this is if you know nothing of interest has taken place while the program was on
The ***Toggle Camera*** button will change between cameras, upto 3 of them.  
Note that it may take some time for the GUI window to open.
Please ensure all cameras to be used are connected and not already in use **before** starting the program, and **toggle the camera** to "camera in use: 1" before clicking arm system.
## ToDo
To add preview for camera so you know which one is in use. *(The code for this is done, yet to implement)*
To double check if openCV's CAP_MSMF works in other operating systems apart from windows
To add functionality for masking (adding black boxes in areas where we dont want to detect motion) *(The code for this is done, yet to implement)*

##Update
While this is meant to be used with a real modern camera (most almost always use windows MSMF backend), virtual cameras are known not to be exposed to its device enumeration properly. Therefore i switched back to DSHOW and added MSMF as a fallback, so virtual cameras like OBS's virtual camera should be detected. (Only tested using droidcam, but it should work). Sorry shipwrighters, never occured to me that people testing this would defo not want to use their own camera due to privacy :(

