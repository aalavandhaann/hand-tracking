import time

import cv2
import mediapipe as mp
import numpy as np


class HandTracker():
    def __init__(self, *, static_image_mode: bool = False, maxHands: int = 1, detectionConfidence: float = 0.5, trackingConfidence: float = 0.5):
        self._mode = static_image_mode
        self._maxHands = maxHands
        self._detectionConfidence = detectionConfidence
        self._trackingConfidence = trackingConfidence
        
        self._mpHands = mp.solutions.hands
        self._hands = self._mpHands.Hands(
            static_image_mode = self._mode,
            max_num_hands = self._maxHands,
            min_detection_confidence = self._detectionConfidence,
            min_tracking_confidence = self._trackingConfidence
            )
        self._mpDraw = mp.solutions.drawing_utils
        self._results = None
    
    
    def findHands(self, img: np.ndarray, *, needs_bgr2rgb: bool = True, draw: bool = True)->np.ndarray:
        if(needs_bgr2rgb):
            imageRGB: np.ndarray = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        else:
            imageRGB: np.ndarray = np.copy(img)
            
        self._results = self._hands.process(imageRGB)
        if(self._results and self._results.multi_hand_landmarks):
            for handLMS in self._results.multi_hand_landmarks:
                if (draw):
                    self._mpDraw.draw_landmarks(img, handLMS, self._mpHands.HAND_CONNECTIONS)
        
        return img


    def findHandLandmarks(self, img: np.ndarray, *, hand_index: int = 0, draw: bool = True)->list:
        landmarks_list: list = []
        
        if(self._results and self._results.multi_hand_landmarks):
            try:
                hand = self._results.multi_hand_landmarks[hand_index]
            except:
                return landmarks_list
            
            for id, landmark in enumerate(hand.landmark):
                height, width, _ = img.shape
                x, y = int(landmark.x * width), int(landmark.y * height)
                landmarks_list.append((id, x, y))
                if draw:
                    cv2.circle(img, (x, y), 3, (255, 0, 255), cv2.FILLED)
        
        return landmarks_list
        

if __name__ == '__main__':
    previousTimestamp = 0
    currentTimestamp = 0
    cap = cv2.VideoCapture(0)    
    detector = HandTracker()
    
    while (True):
        success, img = cap.read()
        
        image = detector.findHands(img)
        landmark_list = detector.findHandLandmarks(img)
        
        currentTimestamp = time.time()
        fps = 1 / (currentTimestamp - previousTimestamp)
        previousTimestamp = currentTimestamp
        
        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)
        cv2.imshow('Hand Tracking', img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break