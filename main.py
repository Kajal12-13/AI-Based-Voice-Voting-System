import cv2
import face_recognition
import speech_recognition as sr
import os
import firebase_admin
from firebase_admin import credentials, db
import tkinter as tk
import pyttsx3
import time
import re

# -------------------- FIREBASE SETUP --------------------
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://ai-based-voice-voting-system-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

# -------------------- TEXT TO SPEECH --------------------
def speak(text):
    print("SYSTEM:", text)

    engine = pyttsx3.init()
    engine.setProperty("rate", 165)
    engine.setProperty("volume", 1.0)

    voices = engine.getProperty("voices")
    if voices:
        engine.setProperty("voice", voices[0].id)

    engine.say(text)
    engine.runAndWait()
    engine.stop()

    time.sleep(0.5)

# -------------------- FACE VERIFICATION --------------------
def verify_face():
    known_encodings = []
    known_names = []

    # 1. Load faces (Same as before)
    for file in os.listdir("face_data"):
        if file.endswith((".jpg", ".png")):
            try:
                path = os.path.join("face_data", file)
                image = face_recognition.load_image_file(path)
                enc = face_recognition.face_encodings(image)
                if enc:
                    known_encodings.append(enc[0])
                    known_names.append(os.path.splitext(file)[0])
            except:
                continue

    if not known_encodings:
        speak("No voter data found")
        return None

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    speak("Please look at the camera for 5 seconds")
    
    # --- TIMEOUT LOGIC ---
    start_time = time.time()
    timeout = 10  # Seconds to try before giving up

    while True:
        # Check if 10 seconds have passed
        if time.time() - start_time > timeout:
            print("SYSTEM: Verification Timeout.")
            break

        ret, frame = cap.read()
        if not ret: continue

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb)
        face_encodings = face_recognition.face_encodings(rgb, face_locations)

        for face_encoding in face_encodings:
            # Matches using strict tolerance
            matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.45)
            face_distances = face_recognition.face_distance(known_encodings, face_encoding)
            
            if True in matches:
                import numpy as np
                best_match_index = np.argmin(face_distances)
                
                if matches[best_match_index]:
                    name = known_names[best_match_index]
                    cap.release()
                    cv2.destroyAllWindows()
                    return name

        cv2.imshow("Face Verification - Scanning...", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # If the loop breaks without returning a name, it means it failed
    cap.release()
    cv2.destroyAllWindows()
    return None

# -------------------- TAKE VOICE --------------------

def take_voice(attempt_num):
    r = sr.Recognizer()
    
    # Increase sensitivity: lower number = more sensitive
    # If it still doesn't hear you, try 150 or 100.
    r.energy_threshold = 200 
    r.dynamic_energy_threshold = True 

    try:
        with sr.Microphone() as source:
            print(f"Listening... {attempt_num}")
            
            # VERY short adjustment or it will cut off the start of your sentence
            r.adjust_for_ambient_noise(source, duration=0.5)
            
            # Give you more time to speak (10 seconds timeout)
            audio = r.listen(source, timeout=10, phrase_time_limit=6)
            
            try:
                # Primary attempt
                text = r.recognize_google(audio, language="en-IN")
            except:
                # Fallback attempt
                text = r.recognize_google(audio, language="en-US")
                
            print("YOU SAID:", text)
            return text.lower()

    except sr.WaitTimeoutError:
        print(f"Attempt {attempt_num}: No voice detected.")
    except sr.UnknownValueError:
        print(f"Attempt {attempt_num}: Could not understand.")
    except Exception as e:
        print(f"Mic Error: {e}")
        
    return None
# -------------------- PROCESS VOTE --------------------


def process_vote(text):
    if not text:
        return None

    text = text.lower()
    print(f"DEBUG: Processing text -> {text}")

    # This looks for digits (1, 2, 3) or word versions (one, two, three) anywhere in the sentence
    if re.search(r"1|one|first", text):
        return "BJP"
    elif re.search(r"2|two|second", text):
        return "Congress"
    elif re.search(r"3|three|third|none|nota", text):
        return "NOTA"

    return None

# -------------------- BUTTON VOTE UI --------------------
def button_vote_ui():

    result = {"vote": None}

    def choose(v):
        result["vote"] = v
        root.destroy()

    root = tk.Tk()
    root.title("Vote Selection")
    root.geometry("300x250")

    tk.Label(
        root,
        text="Select Your Vote",
        font=("Arial", 14)
    ).pack(pady=10)

    tk.Button(root, text="1 - BJP", width=20,
              command=lambda: choose("BJP")).pack(pady=5)

    tk.Button(root, text="2 - Congress", width=20,
              command=lambda: choose("Congress")).pack(pady=5)

    tk.Button(root, text="3 - NOTA", width=20,
              command=lambda: choose("NOTA")).pack(pady=5)

    root.mainloop()

    return result["vote"]

# -------------------- CONFIRM UI --------------------
def confirm_ui(vote):

    result = {"confirm": False}

    def yes():
        result["confirm"] = True
        root.destroy()

    def no():
        result["confirm"] = False
        root.destroy()

    root = tk.Tk()
    root.title("Confirm Vote")
    root.geometry("300x200")

    tk.Label(
        root,
        text=f"Confirm your vote:\n{vote}",
        font=("Arial", 12)
    ).pack(pady=20)

    tk.Button(root, text="YES", width=10,
              command=yes).pack(pady=5)

    tk.Button(root, text="NO", width=10,
              command=no).pack(pady=5)

    root.mainloop()

    return result["confirm"]

# -------------------- SEND VOTE --------------------
def send_vote(user, vote):

    ref = db.reference("votes")

    if ref.child(user).get():
        speak("You have already voted")
        return False

    ref.child(user).set(vote)

    speak("Vote stored successfully")
    return True

# -------------------- MAIN --------------------
def main():
    speak("Welcome to smart voting system")

    user = verify_face()
    if not user:
        speak("Voter is not verified")
        return

    speak("Face verified successfully")

    speak("Say 1 for BJP")
    speak("Say 2 for Congress")
    speak("Say 3 for NOTA")

    vote = None
    used_button = False

    # Try voice recognition up to 3 times
    for attempt in range(1, 4):
        vote_text = take_voice(attempt)
        vote = process_vote(vote_text)

        if vote:
            # Valid vote found (BJP, Congress, or NOTA)
            break 
        else:
            # If we haven't reached the 3rd attempt yet, give feedback
            if attempt < 3:
                speak("I didn't catch a valid option. Please say the number clearly.")
            else:
                speak("Voice not recognized after 3 attempts. Please use buttons.")
                vote = button_vote_ui()
                used_button = True

    if vote:
        speak(f"You selected {vote}")
        
        # ---------------- CONFIRMATION LOGIC ----------------
        if used_button:
            final_confirm = confirm_ui(vote)
        else:
            speak("Confirm yes or no")
            confirm = take_voice(attempt_num="Confirmation") # Use the same function for "Yes/No"
            
            if confirm and "yes" in confirm:
                final_confirm = True
            elif confirm and "no" in confirm:
                final_confirm = False
            else:
                speak("Confirmation failed")
                final_confirm = False

        # ---------------- SAVE VOTE ----------------
        if final_confirm:
            sent = send_vote(user, vote)
            if sent:
                with open("votes.txt", "a") as f:
                    f.write(f"{user} -> {vote}\n")
                speak("Your vote has been recorded")
        else:
            speak("Vote cancelled")
    else:
        speak("No vote selected")
# -------------------- RUN --------------------
if __name__ == "__main__":
    main()