import os
import time
import shutil
from PIL import Image, ImageChops, ImageStat, ImageDraw
import cv2

#https://docs.python.org/3/library/shutil.html, https://docs.python.org/3/library/os.html
#   looked for rmtree, move, path, makedir, remove
#https://stackoverflow.com/questions/595305/how-do-i-get-the-path-of-the-python-script-i-am-running-in
#https://stackoverflow.com/questions/4934806/how-can-i-find-scripts-directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Import directory constants from GUI (set at app startup)
# These are set to None initially; GUI1.py will update them before starting the motion thread
TEMP_DIR = None
SAVE_DIR = None
EVENTS_DIR = None
EVENTS2_DIR = None

MAX_TEMP_IMAGES = 3000
SAVE_DURATION = 60 # 300 fiels saved at 0.1img/s = 30s of 10fps footage, returns to 1fps during inactivity
THRESHOLD = 15.0    #will inc or dec when testing diff door open/close
keep_running = True  # Flag to control main loop
camToUse = 0

def init_camera(camToUse): #fixes issue where camera was reopened each time image was taken, which didnt meet the "change sensitivity req)"
    cap = cv2.VideoCapture(camToUse, cv2.CAP_MSMF)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return None

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    for _ in range(5):
        cap.read()

    return cap


def capture_image(cap, filename):
    if cap is None or not cap.isOpened():
        print("Error: camera is not opened.")
        return False

    ret, frame = cap.read()
    if ret:
        cv2.imwrite(filename, frame)
        #applying black mask
        tempimg = Image.open(filename)
        draw = ImageDraw.Draw(tempimg)
        x1, y1 = 950, 80
        x2, y2 = 950, 300
        x3, y3 = 1280, 350
        x4, y4 = 1280, 550
#        draw.polygon([(x1, y1), (x2, y2), (x4, y4), (x3, y3)], fill="black")
        tempimg.save(filename)
        return True
    else:
        print("Error: Failed to grab frame.")
        return False


def get_image_list():
    files = [os.path.join(TEMP_DIR, f) for f in os.listdir(TEMP_DIR) if f.endswith(('.jpg', '.png'))]
    return sorted(files, key=os.path.getmtime)

def clean_temp_folder():
    images = get_image_list()
    while len(images) > MAX_TEMP_IMAGES:
        oldest_image = images.pop(0)
        try:
            os.remove(oldest_image)
        except OSError:
            pass

#https://www.geeksforgeeks.org/python/python-create-video-using-multiple-images-using-opencv/
def generate_video_from_event(image_folder):
    images = [img for img in os.listdir(image_folder) if img.lower().endswith((".jpg", ".jpeg", ".png"))]
    if not images:
        print(f"No images found")
        return

    def image_mtime(name):
        return os.path.getmtime(os.path.join(image_folder, name))

    images = sorted(images, key=image_mtime)
    first_frame_path = os.path.join(image_folder, images[0])
    frame = cv2.imread(first_frame_path)
    if frame is None:
        print(f"Error: failed to read first image")
        return

    height, width = frame.shape[:2]
    event_name = os.path.basename(image_folder.rstrip("\\/")) #https://docs.python.org/3.13/library/os.path.html
    video_path = os.path.join(EVENTS2_DIR, f"{event_name}.avi")
    video = cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc(*'DIVX'), 2, (width, height))#2fps

    for image_name in images:
        image_path = os.path.join(image_folder, image_name)
        frame = cv2.imread(image_path)
        if frame is None:
            print(f"Warning: could not read {image_path}, skipping")
            continue
        if frame.shape[:2] != (height, width):
            frame = cv2.resize(frame, (width, height))
        video.write(frame)

    video.release()
    print(f"Video generated successfully: {video_path}")

def detect_motion(imgPath1, imgPath2):
    try:
        img1 = Image.open(imgPath1).convert("L")
        img2 = Image.open(imgPath2).convert("L")
        
        diff = ImageChops.difference(img1, img2)
        stat = ImageStat.Stat(diff)
        
        rms = stat.rms[0]
        return rms > THRESHOLD
    except Exception:
        return False

def bundle_motion_event():
    stagedFiles = [os.path.join(SAVE_DIR, f) for f in os.listdir(SAVE_DIR) if f.endswith(('.jpg', '.png'))]
    if not stagedFiles:
        return
    folder_timestamp = time.strftime("%Y-%m-%d_%H-%M-%S") #Converts a time tuple to a string
    eventFolderPath = os.path.join(EVENTS_DIR, f"event_{folder_timestamp}")
    os.makedirs(eventFolderPath, exist_ok=True)
    for filePath in stagedFiles:
        filename = os.path.basename(filePath) # Returns the final component of a pathname, taken from python docu
        destination = os.path.join(eventFolderPath, filename)
        try:
            shutil.move(filePath, destination)
        except OSError:
            pass      
    generate_video_from_event(eventFolderPath)
    print(f"--> Successfully bundled {len(stagedFiles)} images into: {eventFolderPath}")

def main():
    print("Starting motion detection loop...")
    prevImagePath = None
    saveCounter = 0
    event_active = False

    cap = init_camera(camToUse)
    if cap is None:
        return

    try:
        while keep_running:
            startTime = time.time()
            timestamp = int(startTime)
            currentImagePath = os.path.join(TEMP_DIR, f"cap_{timestamp}.jpg")
            capture_image(cap, currentImagePath)
            
            if prevImagePath and os.path.exists(prevImagePath):
                if detect_motion(prevImagePath, currentImagePath):
                    print(f"[{timestamp}] Motion detected!")
                    saveCounter = SAVE_DURATION
                    event_active = True

            if saveCounter > 0:
                savedPath = os.path.join(SAVE_DIR, os.path.basename(currentImagePath))
                shutil.copy2(currentImagePath, savedPath) # copies with meta data, though filename alrdy has date so not needed.
                saveCounter -= 1
                if saveCounter == 0:
                    print("Finished saving motion sequence.")
                    if event_active:
                        print("Motion sequence finished recording, making event...")
                        bundle_motion_event()
                        event_active = False
            
            clean_temp_folder()
            
            prevImagePath = currentImagePath
            if saveCounter > 0:
                time.sleep(0.5)
            else:
                elapsed = time.time() - startTime
                sleepTime = max(0, 1.0 - elapsed)
                time.sleep(sleepTime)
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
