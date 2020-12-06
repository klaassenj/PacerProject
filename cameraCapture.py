import io
import time
import picamera
from PIL import Image
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
numCycles = 0

imageRatio = 480 / 640
imageWidth = 640
imageHeight = 480
capturesPerCycle = 40

def processImages():
    global numCycles
    stream = io.BytesIO()
    for i in range(capturesPerCycle):
        yield stream
        stream.seek(0)
        image = Image.open(stream)
        image.save('outdoorsSunny/collect2frame' + str(numCycles) + 'split' + str(i) + '.jpeg', 'jpeg')
        stream.seek(0)
        stream.truncate()
    numCycles += 1
        
with picamera.PiCamera() as camera:
    print("Initialize Camera")
    camera.resolution = (imageWidth, imageHeight)
    camera.color_effects = (128, 128)
    camera.framerate = 80
    print("Booting Camera...")
    time.sleep(2)
    print("Booted.")
    try:
        while True:
            outputs = [io.BytesIO() for i in range(capturesPerCycle)]
            startTime = time.time()
            camera.capture_sequence(processImages(), 'jpeg', use_video_port=True)
            endTime = time.time()
            print(str(capturesPerCycle) + " images at ", capturesPerCycle / (endTime - startTime), "FPS")
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("Completed")
