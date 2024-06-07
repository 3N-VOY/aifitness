# views.py
from django.shortcuts import render
from django.http import StreamingHttpResponse, HttpResponse
import cv2
import numpy as np
import time
import os
from . import posemodule as pm_modified  # Ensure this module is in your project

def generate_deadlift_frames(cap):
    pose_detector = pm_modified.PoseDetectorModified()
    counter = 0
    movement_dir = 0
    correct_form = 0
    exercise_feedback = "Fix Form"
    feedback_list = []
    feedback_display_duration = 3  # seconds
    feedback_timestamps = {}  # To store feedback messages and their timestamps
    reps_start_time = time.time()
    reps_end_time = time.time()
    reps_duration = 0
    speed_threshold = 1.5  # Speed threshold in seconds (adjust as necessary)
    
    

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        video_width = cap.get(3)
        video_height = cap.get(4)

        frame = pose_detector.findPose(frame, False)
        landmarks_list = pose_detector.findPosition(frame, False)

        if len(landmarks_list) != 0:
            hip_angle = pose_detector.findAngle(frame, 11, 23, 25, landmarks_list)  # Left shoulder, left hip, left knee
            knee_angle = pose_detector.findAngle(frame, 23, 25, 27, landmarks_list)  # Left hip, left knee, left ankle
            back_angle = pose_detector.findAngle(frame, 11, 23, 27, landmarks_list)  # Left shoulder, left hip, left ankle

            progress_percentage = np.interp(knee_angle, (125, 150), (0, 100))
            progress_bar = np.interp(knee_angle, (125, 150), (380, 50))
#back_angle > 160
            # Check form
            if hip_angle > 100 and knee_angle > 125 and back_angle > 160:
                correct_form = 1

            if correct_form == 1:
                # Going down
                if progress_percentage == 0:
                    if knee_angle <= 125:
                        exercise_feedback = "Down"
                        reps_end_time = time.time()
                        reps_duration = reps_end_time - reps_start_time
                        reps_start_time = time.time()
                        
                        if movement_dir == 0:
                            counter += 0.5
                            movement_dir = 1

                            if reps_duration < speed_threshold:
                                feedback_list.append("Slow down for better control")
                                feedback_timestamps["Slow down for better control"] = time.time()
                    else:
                        exercise_feedback = "Fix Form"

                # Going up
                if progress_percentage == 100:
                    if knee_angle >= 150:
                        exercise_feedback = "Up"
                        if movement_dir == 1:
                            counter += 0.5
                            movement_dir = 0
                    else:
                        exercise_feedback = "Fix Form"

            # Posture Feedback
            if back_angle > 270:
                feedback_list.append("Keep your back straight")
                feedback_timestamps["Keep your back straight"] = time.time()
            
            # Hip Position Feedback
            if hip_angle < 183:
                feedback_list.append("Hinge at your hips")
                feedback_timestamps["Hinge at your hips"] = time.time()
            
            # Knee Position Feedback
            if knee_angle < 80:
                feedback_list.append("Don't bend your knees too much")
                feedback_timestamps["Don't bend your knees too much"] = time.time()
            
            if correct_form == 1:
                cv2.rectangle(frame, (580, 50), (600, 380), (0, 255, 0), 3)
                cv2.rectangle(frame, (580, int(progress_bar)), (600, 380), (0, 255, 0), cv2.FILLED)
                cv2.putText(frame, f'{int(progress_percentage)}%', (565, 430), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)

            # Draw rep counter
            # cv2.rectangle(frame, (0, 380), (100, 480), (0, 255, 0), cv2.FILLED)
            # cv2.putText(frame, str(int(counter)), (25, 455), cv2.FONT_HERSHEY_PLAIN, 5, (255, 0, 0), 5)

            # # Draw feedback
            # cv2.rectangle(frame, (500, 0), (640, 40), (255, 255, 255), cv2.FILLED)
            # cv2.putText(frame, exercise_feedback, (500, 40), cv2.FONT_HERSHEY_PLAIN, 4, (0, 255, 0), 2)
            
            
            
            
            #other
            # Draw Rep Counter
            # Draw Rep Counter
            cv2.rectangle(frame, (0, 0), (350, 150), (0, 255, 0), -1)  # Enlarged rectangle

# REPS Label and Counter
            cv2.putText(frame, 'REPS', (15, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 3, cv2.LINE_AA)  # Adjusted position, font scale, and thickness
            cv2.putText(frame, str(int(counter)), (15, 120), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 0), 5, cv2.LINE_AA)  # Adjusted position, font scale, and thickness

# STAGE Label and Value
            cv2.putText(frame, 'STAGE', (180, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 3, cv2.LINE_AA)  # Adjusted position, font scale, and thickness
            cv2.putText(frame,  exercise_feedback, (180, 120), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 0), 5, cv2.LINE_AA)   # Adjusted position, font scale, and thickness



            #oter

            current_time = time.time()
            feedback_to_display = []
            for feedback, timestamp in feedback_timestamps.items():
                if current_time - timestamp < feedback_display_duration:
                    feedback_to_display.append(feedback)
            
            if feedback_to_display:
                feedback_text = " | ".join(set(feedback_to_display))
                cv2.putText(frame, feedback_text, (150, 450), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 2)
            
            feedback_list.clear()

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()

def generate_bicep_curl_frames(cap):
    pose_detector = pm_modified.PoseDetectorModified()
    counter = 0
    movement_dir = 0
    correct_form = 0
    exercise_feedback = "Fix Form"
    feedback_list = []
    feedback_display_duration = 3  # seconds
    feedback_timestamps = {}  # To store feedback messages and their timestamps
    reps_start_time = time.time()
    reps_end_time = time.time()
    reps_duration = 0
    speed_threshold = 1.0  # Speed threshold in seconds (adjust as necessary)
    incorrect_curl_counter = 0
    incorrect_extension_counter = 0

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        video_width = cap.get(3)
        video_height = cap.get(4)

        frame = pose_detector.findPose(frame, False)
        landmarks_list = pose_detector.findPosition(frame, False)
        
        if len(landmarks_list) != 0:
            elbow_angle = pose_detector.findAngle(frame, 11, 13, 15, landmarks_list)
            shoulder_angle = pose_detector.findAngle(frame, 23, 11, 13, landmarks_list)

            progress_percentage = np.interp(elbow_angle, (50, 160), (100, 0))
            progress_bar = np.interp(elbow_angle, (50, 160), (50, 380))

            if elbow_angle < 150 and shoulder_angle > 150:
                correct_form = 1
            elif elbow_angle > 190:
                counter += 0
                correct_form == 0
            if correct_form == 1:
                
                if progress_percentage == 100:
                    if elbow_angle < 50 and shoulder_angle > 150:
                        exercise_feedback = "Up"
                        if movement_dir == 1:
                            counter += 1
                            movement_dir = 0
                    else:
                        exercise_feedback = "Fix Form"
                if progress_percentage == 0:
                    if elbow_angle >= 160:
                        exercise_feedback = "Down"
                        reps_end_time = time.time()
                        reps_duration = reps_end_time - reps_start_time
                        reps_start_time = time.time()
                        
                        if movement_dir == 0:
                            # counter += 0.5
                            movement_dir = 1

                            if reps_duration < speed_threshold:
                                feedback_list.append("Slow down for better control")
                                feedback_timestamps["Slow down for better control"] = time.time()
                    else:
                        exercise_feedback = "Fix Form"


            # Range of Motion Feedback
            if elbow_angle > 200:
                incorrect_extension_counter += 1
            else:
                incorrect_extension_counter = 0

            if incorrect_extension_counter > 3:
                feedback_list.append("Try to fully extend your arm")
                feedback_timestamps["Try to fully extend your arm"] = time.time()
                incorrect_extension_counter = 0
                counter -1
            if exercise_feedback == "Fix Form":
                feedback_list.append("Keep your elbows close to your body")
                feedback_timestamps["Keep your elbows close to your body"] = time.time()
                
            # Elbow Position Feedback
            if elbow_angle > 190:
                feedback_list.append("Keep your elbows close to your body")
                feedback_timestamps["Keep your elbows close to your body"] = time.time()
            
            # Shoulder Position Feedback
            if shoulder_angle < 150:
                feedback_list.append("Keep your shoulders stable and back")
                feedback_timestamps["Keep your shoulders stable and back"] = time.time()

            if correct_form == 1:
                cv2.rectangle(frame, (580, 50), (600, 380), (0, 255, 0), 3)
                cv2.rectangle(frame, (580, int(progress_bar)), (600, 380), (0, 255, 0), cv2.FILLED)
                cv2.putText(frame, f'{int(progress_percentage)}%', (565, 430), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)

# Draw Rep Counter
            # Draw Rep Counter
            cv2.rectangle(frame, (0, 0), (350, 150), (0, 255, 0), -1)  # Enlarged rectangle

# REPS Label and Counter
            cv2.putText(frame, 'REPS', (15, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 3, cv2.LINE_AA)  # Adjusted position, font scale, and thickness
            cv2.putText(frame, str(counter), (15, 120), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 0), 5, cv2.LINE_AA)  # Adjusted position, font scale, and thickness

# STAGE Label and Value
            cv2.putText(frame, 'STAGE', (180, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 3, cv2.LINE_AA)  # Adjusted position, font scale, and thickness
            cv2.putText(frame, exercise_feedback, (180, 120), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 0), 5, cv2.LINE_AA)  # Adjusted position, font scale, and thickness



            # cv2.rectangle(frame, (500, 0), (640, 40), (255, 255, 255), cv2.FILLED)
            # cv2.putText(frame, exercise_feedback, (700, 450), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
            
            current_time = time.time()
            feedback_to_display = []
            for feedback, timestamp in feedback_timestamps.items():
                if current_time - timestamp < feedback_display_duration:
                    feedback_to_display.append(feedback)
            
            if feedback_to_display:
                feedback_text = " | ".join(set(feedback_to_display))
                cv2.putText(frame, feedback_text, (50, 350), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 2)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()

def generate_pushup_frames(cap):
    pose_detector = pm_modified.PoseDetectorModified()
    counter = 0
    stage = None
    rep_started = False

    # Feedback parameters
    exercise_feedback = "Fix Form"
    feedback_list = []
    feedback_display_duration = 3  # seconds
    feedback_timestamps = {}  # To store feedback messages and their timestamps

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        frame = pose_detector.findPose(frame, False)
        landmarks_list = pose_detector.findPosition(frame, False)

        if len(landmarks_list) != 0:
            # Coordinates of shoulder, elbow, and wrist
            shoulder = [landmarks_list[11][1], landmarks_list[11][2]]
            elbow = [landmarks_list[13][1], landmarks_list[13][2]]
            wrist = [landmarks_list[15][1], landmarks_list[15][2]]

            # Coordinates of hip and ankle for posture feedback
            hip = [landmarks_list[23][1], landmarks_list[23][2]]
            ankle = [landmarks_list[27][1], landmarks_list[27][2]]
        

            # Angles
            elbow_angle = pose_detector.findAngle(frame, 11, 13, 15, landmarks_list)
            shoulder_angle = pose_detector.findAngle(frame, 13, 11, 23, landmarks_list)
            back_angle = pose_detector.findAngle(frame, 11, 23, 27, landmarks_list)

            # Progress percentage for the push-up
            progress_percentage = np.interp(elbow_angle, (190, 262), (0, 100))
            progress_bar = np.interp(elbow_angle, (190, 262), (380, 50))

            if elbow_angle > 262:
                if not rep_started:
                    stage = "down"
                    rep_started = True
            if elbow_angle < 190 and stage == 'down':
                stage = "up"
                counter += 1
                rep_started = False

            # Posture Feedback
            if back_angle < 150:
                feedback_list.append("Keep your back straight")
                feedback_timestamps["Keep your back straight"] = time.time()
            
            if back_angle > 210:
                feedback_list.append("Keep your back straight")
                feedback_timestamps["Keep your back straight"] = time.time()

            # Elbow Position Feedback
            if shoulder_angle < 20:
                feedback_list.append("Don't lower too much")
                feedback_timestamps["Don't lower too much"] = time.time()
            
            if shoulder_angle > 320 and back_angle > 200:
                feedback_list.append("Your shoulders are not aligned with your back")
                feedback_timestamps["Your shoulders are not aligned with your back"] = time.time()
                

            # Draw Progress Bar
# Draw Progress Bar
            cv2.rectangle(frame, (580, 100), (600, 380), (0, 255, 0), 3)  # Adjusted position for the progress bar
            cv2.rectangle(frame, (580, int(progress_bar)), (600, 380), (0, 255, 0), cv2.FILLED)
            cv2.putText(frame, f'{int(progress_percentage)}%', (565, 430), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)

            # Draw Rep Counter
# Draw Rep Counter
            # Draw Rep Counter
            cv2.rectangle(frame, (0, 0), (350, 150), (0, 255, 0), -1)  # Enlarged rectangle

# REPS Label and Counter
            cv2.putText(frame, 'REPS', (15, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 3, cv2.LINE_AA)  # Adjusted position, font scale, and thickness
            cv2.putText(frame, str(counter), (15, 120), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 0), 5, cv2.LINE_AA)  # Adjusted position, font scale, and thickness

# STAGE Label and Value
            cv2.putText(frame, 'STAGE', (180, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 3, cv2.LINE_AA)  # Adjusted position, font scale, and thickness
            cv2.putText(frame, stage, (180, 120), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 0), 5, cv2.LINE_AA)  # Adjusted position, font scale, and thickness



            # Render feedback
            current_time = time.time()
            feedback_to_display = []
            for feedback, timestamp in feedback_timestamps.items():
                if current_time - timestamp < feedback_display_duration:
                    feedback_to_display.append(feedback)

            if feedback_to_display:
                feedback_text = " | ".join(set(feedback_to_display))
                cv2.putText(frame, feedback_text, (100, 240), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 2)

            feedback_list.clear()

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()

def generate_squat_frames(cap):
    pose_detector = pm_modified.PoseDetectorModified()
    counter = 0
    stage = None
    rep_started = False
    correct_form = 0
    exercise_feedback = "Fix Form"

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        frame = pose_detector.findPose(frame, False)
        landmarks_list = pose_detector.findPosition(frame, False)

        if len(landmarks_list) != 0:
            hip = [landmarks_list[23][1], landmarks_list[23][2]]  # Left hip
            knee = [landmarks_list[25][1], landmarks_list[25][2]]  # Left knee
            ankle = [landmarks_list[27][1], landmarks_list[27][2]]  # Left ankle

            angle = pose_detector.calculateAngle(hip, knee, ankle)

            # Calculate progress percentage and bar
            progress_percentage = np.interp(angle, (60, 160), (0, 100))
            progress_bar = np.interp(angle, (60, 160), (380, 50))

            # Check form
            if angle > 160:
                correct_form = 1
                exercise_feedback = "Good Form"

            if correct_form == 1:
                # Down phase
                if angle < 90:
                    exercise_feedback = "Down"
                    if stage == 'up' or stage is None:
                        stage = "down"
                        counter += 0.5
                        rep_started = False

                # Up phase
                if angle > 160 and stage == "down":
                    exercise_feedback = "Up"
                    stage = "up"
                    counter += 0.5
                    rep_started = True

            # Visualize the angle
            cv2.putText(frame, str(int(angle)),
                        tuple(np.multiply(knee, [640, 480]).astype(int)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)

            # Draw progress bar
            cv2.rectangle(frame, (580, 50), (600, 380), (0, 255, 0), 3)
            cv2.rectangle(frame, (580, int(progress_bar)), (600, 380), (0, 255, 0), cv2.FILLED)
            cv2.putText(frame, f'{int(progress_percentage)}%', (565, 430), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)

        # Squat Counter render
        cv2.rectangle(frame, (0, 0), (255, 73), (245, 117, 16), -1)

        # Rep data
        cv2.putText(frame, 'REPS', (15, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(frame, str(counter), (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)

        # Stage data
        cv2.putText(frame, 'STAGE', (65, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(frame, stage, (60, 60), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)

        # Feedback data
        cv2.rectangle(frame, (500, 0), (640, 40), (255, 255, 255), cv2.FILLED)
        cv2.putText(frame, exercise_feedback, (700, 40), cv2.FONT_HERSHEY_PLAIN, 4, (0, 255, 0), 2)

        # Render detections
        pose_detector.drawLandmarks(frame, landmarks_list)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()


def generate_crunch_frames(cap):
    pose_detector = pm_modified.PoseDetectorModified()
    counter = 0
    movement_dir = 0
    correct_form = 0
    exercise_feedback = "Fix Form"
    feedback_list = []
    feedback_display_duration = 3  # seconds
    feedback_timestamps = {}  # To store feedback messages and their timestamps

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        video_width = cap.get(3)
        video_height = cap.get(4)

        frame = pose_detector.findPose(frame, False)
        landmarks_list = pose_detector.findPosition(frame, False)

        if len(landmarks_list) != 0:
            shoulder = [landmarks_list[11][1], landmarks_list[11][2]]
            hip = [landmarks_list[23][1], landmarks_list[23][2]]
            knee = [landmarks_list[25][1], landmarks_list[25][2]]

            angle = pose_detector.findAngle(frame, 11, 23, 25)

            progress_percentage = np.interp(angle, (90, 120), (0, 100))
            progress_bar = np.interp(angle, (90, 120), (380, 50))

            if angle > 120:
                correct_form = 1

            if correct_form == 1:
                if angle <= 90:
                    exercise_feedback = "Up"
                    if movement_dir == 0:
                        counter += 0.5
                        movement_dir = 1
                if angle >= 120:
                    exercise_feedback = "Down"
                    if movement_dir == 1:
                        counter += 0.5
                        movement_dir = 0

            if correct_form == 1:
                cv2.rectangle(frame, (580, 50), (600, 380), (0, 255, 0), 3)
                cv2.rectangle(frame, (580, int(progress_bar)), (600, 380), (0, 255, 0), cv2.FILLED)
                cv2.putText(frame, f'{int(progress_percentage)}%', (565, 430), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)

            cv2.rectangle(frame, (0, 380), (100, 480), (0, 255, 0), cv2.FILLED)
            cv2.putText(frame, str(int(counter)), (25, 455), cv2.FONT_HERSHEY_PLAIN, 5, (255, 0, 0), 5)

            cv2.rectangle(frame, (500, 0), (640, 40), (255, 255, 255), cv2.FILLED)
            cv2.putText(frame, exercise_feedback, (500, 40), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)

            current_time = time.time()
            feedback_to_display = []
            for feedback, timestamp in feedback_timestamps.items():
                if current_time - timestamp < feedback_display_duration:
                    feedback_to_display.append(feedback)

            if feedback_to_display:
                feedback_text = " | ".join(set(feedback_to_display))
                cv2.putText(frame, feedback_text, (50, 50), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)

            feedback_list.clear()

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()
    
    
def video_feed(request):
    exercise = request.GET.get('exercise')
    if request.GET.get('source') == 'upload':
        return HttpResponse("Invalid source for live feed.")
    cap = cv2.VideoCapture(0)
    if exercise == 'deadlift':
        return StreamingHttpResponse(generate_deadlift_frames(cap), content_type='multipart/x-mixed-replace; boundary=frame')
    elif exercise == 'bicep_curl':
        return StreamingHttpResponse(generate_bicep_curl_frames(cap), content_type='multipart/x-mixed-replace; boundary=frame')
    elif exercise == 'pushup':
        return StreamingHttpResponse(generate_pushup_frames(cap), content_type='multipart/x-mixed-replace; boundary=frame')
    elif exercise == 'squat':
        return StreamingHttpResponse(generate_squat_frames(cap), content_type='multipart/x-mixed-replace; boundary=frame')
    else:
        return HttpResponse("Invalid exercise selected.")

def upload_video(request):
    if request.method == 'POST':
        video_file = request.FILES.get('video-file')
        exercise = request.POST.get('exercise')
        
        if video_file and exercise:
            video_path = os.path.join('media', video_file.name)
            with open(video_path, 'wb+') as destination:
                for chunk in video_file.chunks():
                    destination.write(chunk)
            cap = cv2.VideoCapture(video_path)
            if exercise == 'deadlift':
                return StreamingHttpResponse(generate_deadlift_frames(cap), content_type='multipart/x-mixed-replace; boundary=frame')
            elif exercise == 'bicep_curl':
                return StreamingHttpResponse(generate_bicep_curl_frames(cap), content_type='multipart/x-mixed-replace; boundary=frame')
            elif exercise == 'pushup':
                return StreamingHttpResponse(generate_pushup_frames(cap), content_type='multipart/x-mixed-replace; boundary=frame')
            elif exercise == 'squat':
                return StreamingHttpResponse(generate_squat_frames(cap), content_type='multipart/x-mixed-replace; boundary=frame')
            else:
                return HttpResponse("Invalid exercise selected.")
        else:
            return HttpResponse("Invalid form submission.")
    return HttpResponse("No video uploaded.")

def index(request):
    return render(request, 'base/index.html')

