import cv2
import numpy as np

class CataractDetector:
    def __init__(self):
        pass

    def read_image(self, filepath: str):
        img_bgr = cv2.imread(filepath, cv2.IMREAD_COLOR)
        img_gray = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
        return img_bgr, img_gray

    def detect_eye(self, img_gray):
        eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        eyes = eye_cascade.detectMultiScale(img_gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        return eyes

    def resize_and_preprocess(self, img_gray, img_bgr):
        target_size = (500, 500)
        img_gray = cv2.resize(img_gray, target_size, interpolation=cv2.INTER_CUBIC)
        img_gray = cv2.medianBlur(img_gray, 5)
        img_bgr = cv2.resize(img_bgr, target_size, interpolation=cv2.INTER_CUBIC)
        factor = 300  # This can be adjusted based on the new size if needed
        return img_bgr, img_gray, factor

    def detect_and_draw_circles(self, img_gray, img_bgr, factor):
        circles = cv2.HoughCircles(img_gray, cv2.HOUGH_GRADIENT, 1, factor, param1=50, param2=30, minRadius=0, maxRadius=0)
        if circles is not None:
            circles = np.uint16(np.around(circles))
            for circle in circles[0]:
                # Draw circles
                cv2.circle(img_bgr, (circle[0], circle[1]), circle[2], (0, 255, 0), 2)
                cv2.circle(img_bgr, (circle[0], circle[1]), 2, (0, 0, 255), 3)
        return circles

    def evaluate_cataract(self, img_gray, circles):
        xc, yc, r = circles[0][0]
        y, x = np.ogrid[:img_gray.shape[0], :img_gray.shape[1]]
        mask = (x - xc) ** 2 + (y - yc) ** 2 > r ** 2
        inside = np.ma.masked_where(~mask, img_gray)
        average_color = inside.mean()
        cataract_percentage = (average_color / 255) * 100
        if average_color <= 120:
            return "Not Cataract"
        else:
            return f"Cataract, {cataract_percentage:.2f}%"

    def detect_cataract(self, filepath: str, output_path: str):
        img_bgr, img_gray = self.read_image(filepath)
        img_bgr, img_gray, factor = self.resize_and_preprocess(img_gray, img_bgr)
        eyes = self.detect_eye(img_gray)
        flag = False
        message = "No Eyes Detected"
        if len(eyes) > 0:
            # If eyes are detected, proceed with cataract detection
            circles = self.detect_and_draw_circles(img_gray, img_bgr, factor)
            if circles is not None:
                message = self.evaluate_cataract(img_gray, circles)
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 2  # Increase font scale for larger text
                thickness = 4   # Increase thickness for bolder text
                cv2.putText(img_bgr, message, (10, 50), font, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)
                print(message)
                flag = True
            else:
                print("No circles detected.")
        
        cv2.imwrite(output_path, img_bgr)
        # Removed the lines below to avoid GUI issues in headless environments
        # cv2.imshow('Cataract Detection', img_bgr)
        # cv2.waitKey(0)
        
        return message if flag else "No Eyes Detected"
