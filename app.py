from flask import Flask,render_template,Response,request,session
import cv2
from imutils.video import VideoStream
from imutils import face_utils
import numpy as np
import time
import dlib
import sqlite3 as sql
from scipy.spatial import distance as dist
import base64
from datetime import datetime,timedelta
import pandas as pd
import csv
import matplotlib.pyplot as plt
import matplotlib 
import squarify

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hdoihsdoivjeiowhfoiqwfqfwegn'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=15)
camera = cv2.VideoCapture(0)
detector = dlib.get_frontal_face_detector()  #initialize dlib
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
matplotlib.use('Agg')

def Roundd(a):
    return round(a,2)

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

def generate_frames(n):
    frameCount = 0
    name=n 
    
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
    mouthsum = 0
    mL=0 #mouth%
    
    ########(T)2022/08/13-1########
    #test store frame:
    sleepFrame = 0
    leaveframe = 0
    blinkframe = 0
    mouthframe = 0
    ##about image
    Pic_byte = None
    ##about time
    currentTime = None
    start_time = None
    end_time = None
    duration_temp = 0
    duration = 0
    datetext = None
    classtime = 20
    d = 0
   
    while True: 
        success,frame = camera.read() #read the camera frame
        
        #以下_曾羽崘_08/11_22:48(這是註解範例)
        start_time = time.time()
        currentTime = datetime.now()
        datetext = str(currentTime)
        timer = datetime.now()
        timerecord = str(timer)
        #以上_曾羽崘_08/11_22:48(這是註解範例)
        
        if not success:
            break
        else:
            frameCount += 1 
            if frameCount%1 == 0:
                with sql.connect("data_test.db") as conl:
                    curl = conl.cursor()
                    curl.execute("INSERT INTO areaTable (id,time,sleep,leave,mouth,blink,normal) VALUES (?,?,?,?,?,?,?)",(name,timerecord,0,0,0,0,1) )
                    conl.commit()   
            cv2.putText(frame, "STATUE:", (20, 65),cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 160, 0), 2)
            cv2.putText(frame, datetext, (880, 20),cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 160, 0), 2)
            
            (left_Start,left_End) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
            (right_Start,right_End) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
            (mStart,mEnd) = (49,68)
            Faces = detector(frame, 0) 

            #TARGET1: whether the user leave: #####22/08/13-4 add 'leaveframe'
            if len(Faces) == 0:
                VRecord += 1
                cv2.putText(frame, "LEAVING!", (20, 90),cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                rL=VRecord/frameCount
                leaveframe += 1
                if frameCount%1 == 0:
                    with sql.connect("data_test.db") as conl:
                        curl = conl.cursor()
                        curl.execute("REPLACE INTO areaTable (id,time,sleep,leave,mouth,blink,normal) VALUES (?,?,?,?,?,?,?)",(name,timerecord,0,1,0,0,0) )
                        conl.commit()
            
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

                #count limit eyes and mouth ratio: #####22/08/13-5 add 'mouth ratio'
                if collectCount < 20:
                    collectCount += 1
                    collectSum += eyeRatioVal
                    mouthsum += mouthMAR
                    startCheck = False
                else:
                    if not startCheck:
                        eyesRatioLimit = (collectSum/(1.0*20))
                        mouthRatioLimit = (mouthsum/(1.0*20))
                    startCheck = True
                    cv2.putText(frame, "User's information:", (20, 650),cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 160, 0), 2)
                    cv2.putText(frame, "Eyes ratio: {:.2f} ".format(eyesRatioLimit), (20, 675),cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 160, 0), 2)
                    cv2.putText(frame, "Mouth ratio: {:.2f}".format(mouthRatioLimit), (20, 705),cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 160, 0), 2)

                #start checking data about eyes:
                if startCheck:
                    cv2.putText(frame, "START", (20, 30),cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 160, 255), 2)
                    
                    #TARGET2: whether the user open his/her mouth(AKA talking):
                    if mar > mouthRatioLimit*1.05:
                        mouth_counter += 1
                    if mouth_counter >= MOUTH_AR_CONSEC_FRAMES:
                        mouth_total += 1
                        mouth_counter = 0
                        mouthframe += 1
                        cv2.putText(frame, "TALKING!", (20, 90),cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                        if frameCount%1 == 0:
                            with sql.connect("data_test.db") as conl:
                                curl = conl.cursor()
                                curl.execute("REPLACE INTO areaTable (id,time,sleep,leave,mouth,blink,normal) VALUES (?,?,?,?,?,?,?)",(name,timerecord,0,0,1,0,0) )
                                conl.commit()
                    mL = mouth_total/frameCount
                    cv2.putText(frame, " / {:.2f}".format(mar), (285, 705),cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 160, 255), 2)
                    
                    #TARGET3: whether the user blink abnormally:
                    if eyeRatioVal <  eyesRatioLimit:
                        blink_counter += 1
                    else:
                        if blink_counter >= EYE_AR_CONSEC_FRAMES:
                            blink_total += 1
                            blinkframe += 1
                        blink_counter = 0   
                        with sql.connect("data_test.db") as conl:
                            curl = conl.cursor()
                            curl.execute("REPLACE INTO areaTable (id,time,sleep,leave,mouth,blink,normal) VALUES (?,?,?,?,?,?,?)",(name,timerecord,0,0,0,1,0) )  
                            conl.commit()
                    bL = blink_total/frameCount
                    
                    #TARGET4: whether the user is asleep:
                    if eyeRatioVal < (eyesRatioLimit*0.9):  #if eyes ratio is less than limit eyes ratio == user close his/her eyes
                        eyesCloseCount += 1
                        eyesOpenCount = 0
                        #user continuously close his/her eyes equal or grater than 20 times:
                        if eyesCloseCount == 20: 
                            cv2.putText(frame, "SLEEP!", (20,90),cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                            sleep = sleep + 20
                            sleepFrame += 1
                            if frameCount%1 == 0:
                                with sql.connect("data_test.db") as conl:
                                    curl = conl.cursor()
                                    curl.execute("REPLACE INTO areaTable (id,time,sleep,leave,mouth,blink,normal) VALUES (?,?,?,?,?,?,?)",(name,timerecord,1,0,0,0,0) )
                                    conl.commit()
                        elif eyesCloseCount > 20:
                            cv2.putText(frame, "SLEEP!!!", (20,90),cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                            sleep += 1
                            sleepFrame += 1
                            if frameCount%1 == 0:
                                with sql.connect("data_test.db") as conl:
                                    curl = conl.cursor()
                                    curl.execute("REPLACE INTO areaTable (id,time,sleep,leave,mouth,blink,normal) VALUES (?,?,?,?,?,?,?)",(name,timerecord,1,0,0,0,0) )
                                    conl.commit()
                    else: 
                        eyesOpenCount += 1
                        if eyesOpenCount > 2:
                            eyesCloseCount = 0
                    cv2.putText(frame, " / {:.2f}".format(eyeRatioVal), (225, 675),cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 160, 0), 2)
                    r = sleep/frameCount
            
            #revert video frame to image:
            ret,buffer = cv2.imencode('.jpg',frame)
            frame = buffer.tobytes()

            #store target image
            if leaveframe == 1:
                currentTime = datetime.now()
                Pic_byte=frame
                content = base64.b64encode(Pic_byte)
                with sql.connect("data_test.db") as c:
                    c2 = c.cursor()
                    sql9 = f"INSERT INTO leaveTable (id,picName,image_bytes) VALUES (?,?,?);"
                    c2.execute(sql9, (name,currentTime,content))
                    c.commit()
                leaveframe = 0
            if mouthframe == 1:
                currentTime = datetime.now()
                Pic_byte=frame
                content = base64.b64encode(Pic_byte)
                with sql.connect("data_test.db") as c:
                    c2 = c.cursor()
                    sql9 = f"INSERT INTO talkTable (id,picName,image_bytes) VALUES (?,?,?) ;"
                    c2.execute(sql9, (name,currentTime,content))
                    c.commit() 
                mouthframe = 0
            if sleepFrame == 1:
                currentTime = datetime.now()
                Pic_byte=frame
                content = base64.b64encode(Pic_byte)
                with sql.connect("data_test.db") as c:
                    c2 = c.cursor()
                    sql9 = f"INSERT INTO sleepTable (id,picName,image_bytes) VALUES (?,?,?);"
                    c2.execute(sql9, (name,currentTime,content))
                    c.commit()
                sleepFrame = 0
        
        yield(b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        #record time
        end_time = time.time()
        duration_temp = end_time-start_time 
        duration += duration_temp
        if d >= 1:
            d = 1
        else:
            d = duration/classtime
        score =( 1 - ((mL + r + rL + bL) / 4) ) * 100 * d
        #record data to database:
        with sql.connect("data_test.db") as con2:
                cur2 = con2.cursor()
                cur2.execute("UPDATE user SET mouth_count=? WHERE user_id=?", (Roundd(mL),name))
                cur2.execute("UPDATE user SET sleep_count=? WHERE user_id=?", (Roundd(r),name))
                cur2.execute("UPDATE user SET leave_count=? WHERE user_id=?",(Roundd(rL),name))
                cur2.execute("UPDATE user SET blink_count=? WHERE user_id=?",(Roundd(bL),name))
                cur2.execute("UPDATE user SET duration=? WHERE user_id=?",(Roundd(d),name))
                cur2.execute("UPDATE user SET score=? WHERE user_id=?",(Roundd(score),name))
                con2.commit()

#首頁的後端程式碼：      
@app.route('/')
def index():
    return render_template('demonstration.html')

##第二頁的後端程式碼：
@app.route('/user',methods = ['POST', 'GET'])
def user():
    if request.method == 'POST':
        try:
          id = request.form['id']
          session['name'] = id ####2022/08/13-9 login
          with sql.connect("data_test.db") as con:
             cur = con.cursor()
             cur.execute("REPLACE INTO user (user_id,mouth_count,sleep_count,leave_count,blink_count) VALUES (?,?,?,?,?)",(id,0,0,0,0) )
             con.commit()
        except:
          con.rollback()
        finally:
          return render_template("user.html")

##第三頁的後端程式碼：
@app.route('/index1') #if use "index" will make collision with demonstration
def index1():
    ###以下不用動###
    d = session['name']
    con = sql.connect("data_test.db")
    con.row_factory= sql.Row
    cur = con.cursor()
    cur.execute("select * from user")
    rows = cur.fetchall()
    cur.execute("select * from user WHERE user_id =?",(d,))
    a = cur.fetchall()
    
    cur.execute("select sleep_count,leave_count,mouth_count,blink_count from user WHERE user_id =?",(d,))
    with open("out.csv", 'w',newline='') as csv_file: 
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow([i[0] for i in cur.description]) 
        csv_writer.writerows(cur)
    cur.execute("select time,sleep,leave,mouth,blink,normal from areaTable WHERE id =?",(d,))
    with open("out2.csv", 'w',newline='') as csv_file: 
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow([i[0] for i in cur.description]) 
        csv_writer.writerows(cur)
    data2 = pd.read_csv("out2.csv")

    rows2 = list(range(0, len(data2)))
    sdata = data2.loc[rows2, 'sleep']
    ldata = data2.loc[rows2,'leave']
    bdata = data2.loc[rows2,'blink']
    mdata = data2.loc[rows2,'mouth']
    ndata = data2.loc[rows2,'normal']
    
    sum_s = round(sum(sdata),2)
    sum_l = round(sum(ldata),2)
    sum_b = round(sum(bdata),2)
    sum_m = round(sum(mdata),2)
    sum_n = round(sum(ndata),2)
    totalSum = (sum_s + sum_b + sum_l +sum_m + sum_n)
    sum_s = Roundd(sum_s/totalSum)
    sum_l = Roundd(sum_l/totalSum)
    sum_b = Roundd(sum_b/totalSum)
    sum_m = Roundd(sum_m/totalSum)
    sum_n = Roundd(sum_n/totalSum)
    if sum_s == 0:
        sum_s = 0.0000001
    if sum_l == 0:
        sum_l = 0.0000001
    if sum_b == 0:
        sum_b = 0.0000001
    if sum_m == 0:
        sum_m = 0.0000001
    if sum_n == 0:
        sum_n = 0.0000001
    now = datetime.now().timestamp()
    ###以上不用動###
    
    #[圖表修外貌]這裡開始是在畫圖，可修改樣式(但勿改的區塊不可改！)：
    volume = [sum_s, sum_l, sum_b, sum_m, sum_n] #NO
    labels = ['', '',
            '', '',
            'Perfect '+str(Roundd(sum_n))]
    color_list = ['#67c29c', '#a06468', '#e4c662',
                '#64a19e', '#F8E8E8']
    plt.rc('font', size=14)
    squarify.plot(sizes=volume, label=labels,
                color=color_list, alpha=0.7)
    plt.axis('off')

    ###以下勿改###
    plt.savefig(
                bbox_inches='tight',              
                pad_inches=0.0,
                fname='static/chart/all'+str(now)+'.png')
    img_a = 'all'+str(now)+'.png'
    return render_template("index.html", rows = rows, img_a = img_a, d = d, a = a)
    ###以上勿改###

#講話指標分頁程式碼：
@app.route('/talking',methods = ['POST','GET'])
def talking():
    ###以下不用改###
    d = session['name'] 
    con = sql.connect("data_test.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("select picName from talkTable WHERE id =?",(d,))
    rows = cur.fetchall();
    data = pd.read_csv("out.csv")
    row = 0
    result_mouth = data.loc[row, 'mouth_count'] #mouth ratio
    other_mouth = (1-result_mouth) #other ratio
    now = datetime.now().timestamp()
    ###以上不用改###

    #[圖表修外貌]以下畫圖區：
    color = ['#64a19e','#D0D0D0']
    plt.figure(figsize=(6,6))    
    labels = 'talk','other'
    size = [result_mouth,other_mouth] #不改
    plt.pie(size , labels = labels,autopct='%1.1f%%',colors = color)
    plt.axis('equal')
    #以上畫圖區#
    
    ###以下勿改###
    plt.savefig(
                bbox_inches='tight',              
                pad_inches=0.0,
                fname='static/chart/mouth'+str(now)+'.png')
    img_m = 'mouth'+str(now)+'.png'
    if request.method == "POST":
        name = request.form['picture name']
        cur.execute("select image_bytes from talkTable WHERE picName = ? ",(name,))
        value = cur.fetchone()
        str_encode = base64.b64decode(value[0])
        nparr1 = np.fromstring(str_encode, np.uint8)
        img_decode = cv2.imdecode(nparr1, cv2.IMREAD_COLOR)
        now = datetime.now().timestamp()
        cv2.imwrite('./static/displayDB/temp'+str(now)+'.png', img_decode)
        time.sleep(2)
        return render_template("talking.html", image='temp'+str(now)+'.png') 
    return render_template("talking.html",rows = rows,d = d,img_m = img_m)
    ###以上勿改###

#眨眼指標分頁程式碼：
@app.route('/blinking')
def blinking():
    ###以下勿改###
    d = session['name']
    data = pd.read_csv("out.csv")
    row = 0
    result_blink = data.loc[row, 'blink_count'] #mouth ratio
    other_blink = (1-result_blink) #other ratio
    now = datetime.now().timestamp()
    ###以上勿改###

    color = ['#e4c662','#D0D0D0']
    #[圖表修外貌]以下畫圖區：
    plt.figure(figsize=(6,6))    
    labels = 'blink','other'
    size = [result_blink,other_blink] #不改
    plt.pie(size , labels = labels,autopct='%1.1f%%', colors = color)
    plt.axis('equal')
    #以上畫圖區#

    ###以下勿改###
    plt.savefig(
                bbox_inches='tight',              
                pad_inches=0.0,
                fname='static/chart/blink'+str(now)+'.png')
    img_b = 'blink'+str(now)+'.png'
    return render_template("blinking.html", img_b = img_b,d = d)
    ###以上勿改###

#睡覺指標分頁程式碼：
@app.route('/sleeping',methods = ['POST','GET'])
def sleeping():
    ###以下勿改###
    d = session['name']
    con = sql.connect("data_test.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("select picName from sleepTable WHERE id = ?",(d,))
    rows = cur.fetchall();
    
    data = pd.read_csv("out.csv")
    row = 0
    result_sleep = data.loc[row, 'sleep_count'] #mouth ratio
    other_sleep = (1-result_sleep) #other ratio
    now = datetime.now().timestamp()
    ###以上勿改###
    color = ['#67c29c','#D0D0D0']
    #[圖表修外貌]以下畫圖區############
    plt.figure(figsize=(6,6))    
    labels = 'sleep','other'
    size = [result_sleep,other_sleep] #不改
    plt.pie(size , labels = labels,autopct='%1.1f%%',colors = color)
    plt.axis('equal')
    #以上畫圖區#############

    ###以下勿改###
    plt.savefig(
                bbox_inches='tight',              
                pad_inches=0.0,
                fname='static/chart/sleep'+str(now)+'.png')
    img_s = 'sleep'+str(now)+'.png'
    if request.method == "POST":
        name = request.form['picture name']
        cur.execute("select image_bytes from sleepTable WHERE picName = ?",(name,))
        value = cur.fetchone()
        str_encode = base64.b64decode(value[0])
        nparr1 = np.fromstring(str_encode, np.uint8)
        img_decode = cv2.imdecode(nparr1, cv2.IMREAD_COLOR)
        now = datetime.now().timestamp()
        cv2.imwrite('./static/displayDB/temp'+str(now)+'.png', img_decode)
        time.sleep(2)
        return render_template("sleeping.html", image='temp'+str(now)+'.png') 
    return render_template("sleeping.html",rows = rows,d = d,img_s = img_s)
    ###以上勿改###

#離開指標分頁程式碼：
@app.route('/appearing',methods = ['POST','GET'])
def appearing():
    ###以下勿改###
    d = session['name']
    con = sql.connect("data_test.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("select picName from leaveTable WHERE id = ?",(d,))
    rows = cur.fetchall();

    data = pd.read_csv("out.csv")
    row = 0
    result_leave = data.loc[row, 'leave_count'] #mouth ratio
    other_leave = (1-result_leave) #other ratio
    now = datetime.now().timestamp()
    ###以上勿改###
    color = ['#a06468','#D0D0D0']
    #[圖表修外貌]以下畫圖區：
    plt.figure(figsize=(6,6))    
    labels = 'leave','other'
    size = [result_leave,other_leave] #不改
    plt.pie(size , labels = labels,autopct='%1.1f%%',colors = color)
    plt.axis('equal')
    #以上畫圖區#

    ###以下勿改###
    plt.savefig(
                bbox_inches='tight',              
                pad_inches=0.0,
                fname='static/chart/leave'+str(now)+'.png')
    img_l = 'leave'+str(now)+'.png'
    if request.method == "POST":
        name = request.form['picture name']
        cur.execute("select image_bytes from leaveTable WHERE picName = ? ",(name,))
        value = cur.fetchone()
        str_encode = base64.b64decode(value[0])
        nparr1 = np.fromstring(str_encode, np.uint8)
        img_decode = cv2.imdecode(nparr1, cv2.IMREAD_COLOR)
        now = datetime.now().timestamp()
        cv2.imwrite('./static/displayDB/temp'+str(now)+'.png', img_decode)
        time.sleep(2)
        return render_template("appearing.html", image='temp'+str(now)+'.png') 
    return render_template("appearing.html",rows = rows,d = d,img_l = img_l)
     ###以上勿改###

#勿改：
@app.route('/video')
def video():
    return Response(generate_frames(session['name']),mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__=="__main__":
    app.run("0.0.0.0", debug=True)

