import io
import time
import picamera
from PIL import Image
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

imageRatio = 480 / 640
imageWidth = 640
imageHeight = int(imageWidth * imageRatio)

def processImages():
    global numPic
    stream = io.BytesIO()
    for i in range(40):
        yield stream
        stream.seek(0)
        image = Image.open(stream)
        image.save('frame' + str(i), 'jpeg')
        stream.seek(0)
        stream.truncate()
        
with picamera.PiCamera() as camera:
    print("Initialize Camera")
    camera.resolution = (imageWidth, imageHeight)
    camera.framerate = 80
    print("Booting Camera...")
    time.sleep(2)
    print("Booted.")
    outputs = [io.BytesIO() for i in range(40)]
    startTime = time.time()
    camera.capture_sequence(processImages(), 'jpeg', use_video_port=True)
    endTime = time.time()
    print("40 images at ", 40 / (endTime - startTime), "FPS")
