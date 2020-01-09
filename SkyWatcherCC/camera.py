import cv2


class VideoCamera(object):
    """
    Props for https://github.com/electrocoder/Django-Webcam-Streaming
    Uses OpenCV to create image-stream from '/dev/video2'
    """
    def __init__(self):
        # Using OpenCV to capture from device 2
        self.video = cv2.VideoCapture(2)

    def __del__(self):
        self.video.release()
    
    def get_frame(self):
        success, image = self.video.read()
        # We are using Motion JPEG, but OpenCV defaults to capture raw images,
        # so we must encode it into JPEG in order to correctly display the
        # video stream.
        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()


def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
