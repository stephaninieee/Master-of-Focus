import fractions
from flask import Flask,render_template,Response,redirect,request,session,url_for
import cv2
from imutils.video import VideoStream
from imutils import face_utils
import imutils
import numpy as np
import time
import dlib
import sqlite3 as sql
from scipy.spatial import distance as dist
app = Flask(__name__)
camera = cv2.VideoCapture(0)
detector = dlib.get_frontal_face_detector()  #initialize dlib
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

def eyesRatio(eye): #define eyes ratio
    hight1 = np.linalg.norm(eye[1] - eye[5])
    hight2 = np.linalg.norm(eye[2] - eye[4])
    width = np.linalg.norm(eye[0] - eye[3])
    return  (hight1+hight2) / (2.0*width)  

def mouth_aspect_ratio(mouth): #define mouth ratio
    A = dist.euclidean(mouth[2], mouth[10]) 
    B = dist.euclidean(mouth[4], mouth[8]) 
    C = dist.euclidean(mouth[0], mouth[6]) 
    mar = (A + B) / (2.0 * C)
    return mar

def generate_frames():
    frameCount = 0
    
    ################
    name='108403000' #lazy login AKA fake login (just for demo, it's ok)
    ################
    
    #about eyes
    eyesRatioLimit = 0  #user's limit eyes ratio
    collectCount = 0  
    collectSum = 0  
    startCheck = False  #whether program start check
    eyesCloseCount = 0  
    eyesOpenCount = 0 

    #about sleep count:#
    sleep = 0
    r = 0 #sleep%

    #about leave count:
    VRecord = 0  #leave count
    rL = 0 #leave%
    
    #about blink count:
    EYE_AR_CONSEC_FRAMES = 3
    blink_counter = 0
    blink_total = 0
    bL = 0 #blink%
    
    #about nouth count:
    MOUTH_AR_THRESH = 0.7 #standard mouth ratio
    MOUTH_AR_CONSEC_FRAMES = 3
    mouth_counter=0
    mouth_total=0
    mL=0 #mouth%
    
    while True: 
        success,frame = camera.read() #read the camera frame
        
        if not success:
            break
        else:
            frameCount += 1 
            
            (left_Start,left_End) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
            (right_Start,right_End) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
            (mStart,mEnd) = (49,68)
            Faces = detector(frame, 0) 
            
            #TARGET1: whether the user leave:
            if len(Faces) == 0:
                VRecord += 1
                cv2.putText(frame, "DON'T LEAVE ME!!! PLEASE COME BACK", (580, 30),cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                rL=VRecord/frameCount
            
            for ff in Faces:
                shape = predictor(frame, ff)  
                shape = face_utils.shape_to_np(shape)  
                
                #variables about eyes:
                leftEye = shape[left_Start:left_End]
                rightEye = shape[right_Start:right_End]
                leftEyesVal = eyesRatio(leftEye)
                rightEyesVal = eyesRatio(rightEye)
                leftEyeHull = cv2.convexHull(leftEye)
                rightEyeHull = cv2.convexHull(rightEye)
                eyeRatioVal = (leftEyesVal + rightEyesVal) / 2.0
                
                #variables abount mouth:
                mouth = shape[mStart:mEnd]
                mouthHull = cv2.convexHull(mouth)
                mouthMAR = mouth_aspect_ratio(mouth)
                mar = mouthMAR
                
                #draw contour(eyes & mouth):
                cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
                cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)
                cv2.drawContours(frame,[mouthHull], -1,(0, 255, 0), 1 )
                
                #TARGET2: whether the user open his/her mouth(AKA talking):
                if mar > MOUTH_AR_THRESH:
                     mouth_counter += 1
                if mouth_counter >= MOUTH_AR_CONSEC_FRAMES:
                    mouth_total += 1
                    mouth_counter = 0
                    cv2.putText(frame, "STOP TALKING!!!", (580, 50),cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 160, 255), 2)
                mL = mouth_total/frameCount

                #count limit eyes ratio:
                if collectCount < 20:
                    collectCount += 1
                    collectSum += eyeRatioVal
                    startCheck = False
                else:
                    if not startCheck:
                        eyesRatioLimit = (collectSum/(1.0*20))
                    startCheck = True
                    cv2.putText(frame, "YOUR STANDARD EYES RATIO: {:.2f}".format(eyesRatioLimit), (20, 20),cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 160, 0), 2)
                
                #start checking data about eyes:
                if startCheck:
                    cv2.putText(frame, "WE GOT YOUR EYES!!!", (580, 80),cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 160, 255), 2)
                   
                    #TARGET3: whether the user blink abnormally:
                    if eyeRatioVal <  eyesRatioLimit:
                        blink_counter += 1
                    else:
                        if blink_counter >= EYE_AR_CONSEC_FRAMES:
                            blink_total += 1
                        blink_counter = 0
                    bL = blink_total/frameCount
                    
                    #TARGET4: whether the user is asleep:
                    if eyeRatioVal < eyesRatioLimit:  #if eyes ratio is less than limit eyes ratio == user close his/her eyes
                        eyesCloseCount += 1
                        eyesOpenCount = 0
                        #user continuously close his/her eyes equal or grater than 20 times:
                        if eyesCloseCount == 20: 
                            cv2.putText(frame, "SLEEP!!!", (580, 30),cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                            sleep = sleep + 20
                        elif eyesCloseCount > 20:
                            cv2.putText(frame, "SLEEP!!!", (580, 30),cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                            sleep += 1
                    else: 
                        eyesOpenCount += 1
                        if eyesOpenCount > 1:
                            eyesCloseCount = 0
                    cv2.putText(frame, "EYES_RATIO: {:.2f}".format(eyeRatioVal), (20, 50),cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 160, 0), 2)
                    cv2.putText(frame,"EYES_COLSE: {}".format(eyesCloseCount),(320,50),cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,160,0),2)
                    r = sleep/frameCount
            
            #revert video frame to image:
            ret,buffer = cv2.imencode('.jpg',frame)
            frame = buffer.tobytes()
        yield(b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        
        #record data to database:
        with sql.connect("data_test.db") as con2:
                cur2 = con2.cursor()
                cur2.execute("UPDATE user SET mouth_count=? WHERE user_id=?", (mL,name))
                cur2.execute("UPDATE user SET sleep_count=? WHERE user_id=?", (r,name))
                cur2.execute("UPDATE user SET leave_count=? WHERE user_id=?",(rL,name))
                cur2.execute("UPDATE user SET blink_count=? WHERE user_id=?",(bL,name))
                con2.commit()
        
@app.route('/')
def index():
    return render_template('demonstration.html')

@app.route('/user',methods = ['POST', 'GET'])
def user():
    if request.method == 'POST':
        try:
          id = request.form['id']
          with sql.connect("data_test.db") as con:
             cur = con.cursor()
             cur.execute("INSERT INTO user (user_id,mouth_count,sleep_count,leave_count,blink_count) VALUES (?,?,?,?,?)",(id,0,0,0,0) )
             con.commit()
        except:
          con.rollback()
        finally:
          return render_template("user.html")
#take data from db
@app.route('/index1') #if use "index" will make collision with demonstration
def index1():
    con = sql.connect("data_test.db")
    con.row_factory= sql.Row
    cur = con.cursor()
    cur.execute("select * from user")
    rows = cur.fetchall()
    return render_template("index.html", rows = rows)

@app.route('/talking')
def talking():
    con = sql.connect("data_test.db")
    con.row_factory= sql.Row
    cur = con.cursor()
    cur.execute("select user_id,mouth_count from user")
    rows = cur.fetchall()
    return render_template("talking.html", rows = rows)

@app.route('/blinking')
def blinking():
    con = sql.connect("data_test.db")
    con.row_factory= sql.Row
    cur = con.cursor()
    cur.execute("select user_id,blink_count from user")
    rows = cur.fetchall()
    return render_template("blinking.html", rows = rows)

@app.route('/sleeping')
def sleeping():
    con = sql.connect("data_test.db")
    con.row_factory= sql.Row
    cur = con.cursor()
    cur.execute("select user_id,sleep_count from user")
    rows = cur.fetchall()
    return render_template("sleeping.html", rows = rows)

@app.route('/appearing')
def appearing():
    con = sql.connect("data_test.db")
    con.row_factory= sql.Row
    cur = con.cursor()
    cur.execute("select user_id,leave_count from user")
    rows = cur.fetchall()
    return render_template("appearing.html", rows = rows)
#end         
@app.route('/video')
def video():
    return Response(generate_frames(),mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__=="__main__":
    app.run("0.0.0.0", debug=True)

