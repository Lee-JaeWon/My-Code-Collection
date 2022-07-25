"""
author : 이재원
email : jawwoni@naver.com
GitHub : Lee-JaeWon
"""

import cv2
import glob
import numpy as np

class calibration():

    def __init__(self):
        self.cam = 'usb0'
        self.run_flag = True
        self.images = glob.glob('./checkerboard_img/*.png')
        # print(self.images)
        self.cnt = 0

        # 체커보드 행과 열, 내부 코너 수
        self.wc = 8
        self.hc = 6

        self.objpoints = []
        self.imgpoints = []

        self.criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

        self.objp = np.zeros((self.hc * self.wc, 3), np.float32)
        self.objp[:,:2] = np.mgrid[0:self.wc, 0:self.hc].T.reshape(-1,2)

        # 아래 mtx와 dist는 calibrate_image 메소드를 통해 구한 값입니다. 테스트를 위한 용도로 적어두었습니다.
        self.mtx = np.array(
            [[556.57522722, 0., 290.64160574],
             [0., 557.99058274, 155.17902656],
             [0., 0., 1.]])

        self.dist = np.array(
            [-0.75414008,  0.53645432,  0.00640072,  0.02310201, -0.06336218])

    def capture_camera(self, cam):
        self.cam = cam

        print(f"Camera is {self.cam}")

        if self.cam == 'usb0':
            cap = cv2.VideoCapture(0)
        elif self.cam == 'ip0':
            cap = cv2.VideoCapture('http://192.168.66.1:9527/videostream.cgi?loginuse=admin&loginpas=admin')

        while self.run_flag:
            success, self.image = cap.read()

            if success is True:

                cv2.imshow('image', self.image)

                if cv2.waitKey(1) == ord('c'):
                    self.cnt += 1
                    path = './checkerboard_img/'+str(self.cnt)+'.png'
                    print(path)
                    cv2.imwrite(path, self.image)

                elif cv2.waitKey(1) == 27:
                    break
            else:
                print("image is None")

    def open_camera(self, cam):
        self.cam = cam

        print(f"Camera is {self.cam}")

        if self.cam == 'usb0':
            cap = cv2.VideoCapture(0)
        elif self.cam == 'ip0':
            cap = cv2.VideoCapture('http://192.168.66.1:9527/videostream.cgi?loginuse=admin&loginpas=admin')

        while self.run_flag:
            success, self.image = cap.read()

            if success is True:
                cv2.imshow('image', self.image)

                if cv2.waitKey(1) == 27:
                    break
            else:
                print("image is None")

    def find_corner(self):
        
        print(self.images)

        for fname in self.images:
            img = cv2.imread(fname)
            self.gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            ret, corners = cv2.findChessboardCorners(self.gray,(self.wc, self.hc),None)
            print(ret, img.shape)

            if ret == True:
                self.objpoints.append(self.objp)

                corners_ = cv2.cornerSubPix(self.gray, corners, (11,11), (-1,-1), self.criteria)
                
                self.imgpoints.append(corners_)

                img = cv2.drawChessboardCorners(img, (self.wc, self.hc), corners_, ret)

            cv2.imshow('img', img)

            cv2.waitKey(10)

        cv2.destroyAllWindows()

    def calibrate_image(self):
        _, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(self.objpoints, self.imgpoints, self.gray.shape[::-1],None,None)
        print(mtx) # Camera Matrix
        print(dist) # distortion_coefficients

        test_img = cv2.imread('./checkerboard_img/20.png')
        h, w = test_img.shape[:2]
        
        new_cam_mat, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h))

        dst = cv2.undistort(test_img, mtx, dist, None, new_cam_mat)

        x_,y_,w_,h_ = roi

        dst = dst[y_:y_+h_, x_:x_+w_]

        tot_error = 0
        for i in range(len(self.objpoints)):
            imgpoints2, _ = cv2.projectPoints(self.objpoints[i], rvecs[i], tvecs[i], mtx, dist)
            error = cv2.norm(self.imgpoints[i],imgpoints2, cv2.NORM_L2)/len(imgpoints2)
            tot_error += error
            print("total error: ", tot_error/len(self.objpoints))

        cv2.imwrite('calibrate_result.png',dst)

        while self.run_flag:
            cv2.imshow('calibrate', dst)
            if cv2.waitKey(1) == 27:
                    break

    def test_image(self):
        mtx = self.mtx
        dist = self.dist

        test_img = cv2.imread('./checkerboard_img/45.png')
        h, w = test_img.shape[:2]
        
        new_cam_mat, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h))

        dst = cv2.undistort(test_img, mtx, dist, None, new_cam_mat)

        x_,y_,w_,h_ = roi

        dst = dst[y_:y_+h_, x_:x_+w_]

        while self.run_flag:
            cv2.imshow('calibrate', dst)
            if cv2.waitKey(1) == 27:
                    break

    def calibrate_video(self, cam):
        self.cam = cam

        print(f"Camera is {self.cam}")

        if self.cam == 'usb0':
            cap = cv2.VideoCapture(0)
        elif self.cam == 'ip0':
            cap = cv2.VideoCapture('http://192.168.66.1:9527/videostream.cgi?loginuse=admin&loginpas=admin')

        while self.run_flag:
            success, self.image = cap.read()

            if success is True:
                cv2.imshow('image', self.image)

                h, w = self.image.shape[:2]
        
                new_cam_mat, roi = cv2.getOptimalNewCameraMatrix(self.mtx, self.dist, (w,h), 1, (w,h))

                dst = cv2.undistort(self.image, self.mtx, self.dist, None, new_cam_mat)

                x_,y_,w_,h_ = roi

                dst = dst[y_:y_+h_, x_:x_+w_]

                cv2.imshow('calibrate', dst)

                if cv2.waitKey(1) == 27:
                    break
            else:
                print("image is None")


    def stop(self):
        cv2.destroyAllWindows()
        self.run_flag = False
        
if __name__ == "__main__":
    cali_ = calibration()

    # cali_.open_camera(cam='ip0') # Just Open a web cam

    # cali_.capture_camera(cam='ip0')
    # cali_.find_corner() # find corner from saved image
    # cali_.calibrate_image() # calibrate with camera matrix and distortion matrix
    # cali_.stop() # all process stop
    # cali_.test_image()
    cali_.calibrate_video('ip0')