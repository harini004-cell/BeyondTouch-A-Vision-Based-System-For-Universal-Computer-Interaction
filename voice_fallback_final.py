# voice_fallback_final.py
# Improved voice parser: open/close apps, close by process name, search web, type, press keys.
import sounddevice as sd, soundfile as sf, speech_recognition as sr, tempfile, os, time, re, webbrowser
from utils_actions import enqueue
import pyttsx3

engine = pyttsx3.init()
def speak(t):
    try: engine.say(t); engine.runAndWait()
    except: pass

# Detect microphone devices
devs = sd.query_devices()
input_devs = [(i,d['name']) for i,d in enumerate(devs) if d['max_input_channels']>0]
print("Input devices:")
for i,name in input_devs:
    print(i, "-", name)
if input_devs:
    sd.default.device = input_devs[0][0]
else:
    print("No input device. Check microphone permissions.")

r = sr.Recognizer()
DURATION = 4     # longer capture improves accuracy for sentences
FS = 16000
CHANNELS = 1

# friendly name -> process mapping for closing apps
PROCESS_MAP = {
    "chrome": "chrome.exe",
    "google chrome": "chrome.exe",
    "notepad": "notepad.exe",
    "explorer": "explorer.exe",
    "file explorer": "explorer.exe",
    "edge": "msedge.exe",
    "vscode": "Code.exe",
    "code": "Code.exe",
    "spotify": "spotify.exe",
}

def kill_process_by_name(proc_name):
    try:
        os.system(f'taskkill /IM "{proc_name}" /F')
        return True
    except:
        return False

def parse_and_execute(text):
    t = text.lower().strip()
    print("Parsed:", t)
    # Open commands
    if t.startswith("open ") or t.startswith("launch ") or t.startswith("start "):
        for name in PROCESS_MAP:
            if name in t:
                exe = PROCESS_MAP[name]
                try:
                    enqueue(os.startfile, exe)
                    speak(f"Opening {name}")
                    return True
                except Exception:
                    pass
        m = re.match(r"(?:open|launch|start)\s+(.+)", t)
        if m:
            target = m.group(1).strip()
            if "http" in target or "www" in target or "google" in target or "youtube" in target:
                webbrowser.open("https://www.google.com/search?q=" + target.replace(" ", "+"))
                speak("Opening " + target)
                return True
            try:
                enqueue(os.system, f'start "" "{target}"')
                speak("Opening " + target)
                return True
            except:
                pass

    # Close commands
    if t.startswith("close ") or t.startswith("quit ") or t.startswith("terminate "):
        for name, proc in PROCESS_MAP.items():
            if name in t:
                ok = kill_process_by_name(proc)
                if ok:
                    speak(f"Closed {name}")
                    return True
        if "close window" in t or "close this" in t:
            enqueue(__import__('pyautogui').hotkey, 'alt', 'f4'); speak("Closing window"); return True

    # Window actions
    if "minimize" in t:
        enqueue(__import__('pyautogui').hotkey, 'win', 'down'); speak("Minimizing"); return True
    if "maximize" in t or "full screen" in t:
        enqueue(__import__('pyautogui').hotkey, 'win', 'up'); speak("Maximizing"); return True
    if "switch window" in t or "alt tab" in t or "switch" in t:
        enqueue(__import__('pyautogui').hotkey, 'alt', 'tab'); speak("Switching window"); return True

    # Search web
    m = re.match(r"(?:search for|search)\s+(.+)", t)
    if m:
        query = m.group(1)
        webbrowser.open("https://www.google.com/search?q=" + query.replace(" ", "+"))
        speak("Searching for " + query)
        return True

    # Type / write
    m = re.match(r"(?:type|write)\s+(.+)", t)
    if m:
        s = m.group(1)
        enqueue(__import__('pyautogui').write, s, interval=0.03)
        speak("Typing")
        return True

    # Press keys / hotkeys
    m = re.match(r"(?:press|press keys)\s+(.+)", t)
    if m:
        keys = [k.strip() for k in re.split(r'[\+\s]+', m.group(1)) if k.strip()]
        if len(keys) == 1:
            enqueue(__import__('pyautogui').press, keys[0])
        else:
            enqueue(__import__('pyautogui').hotkey, *keys)
        speak("Key pressed")
        return True

    # Clicks & scrolls
    if t in ("click", "single click"):
        enqueue(__import__('pyautogui').click); speak("Clicked"); return True
    if "double click" in t:
        enqueue(__import__('pyautogui').doubleClick); speak("Double clicked"); return True
    if "right click" in t:
        enqueue(__import__('pyautogui').rightClick); speak("Right clicked"); return True
    if "scroll down" in t:
        enqueue(__import__('pyautogui').scroll, -400); speak("Scrolling down"); return True
    if "scroll up" in t:
        enqueue(__import__('pyautogui').scroll, 400); speak("Scrolling up"); return True

    return False

def record_and_recognize():
    try:
        rec = sd.rec(int(DURATION*FS), samplerate=FS, channels=CHANNELS, dtype='int16')
        sd.wait()
        fd, fname = tempfile.mkstemp(suffix=".wav", prefix="vt_")
        os.close(fd)
        sf.write(fname, rec, FS)
        with sr.AudioFile(fname) as source:
            audio = r.record(source)
        try:
            text = r.recognize_google(audio)
            print("Heard:", text)
            ok = parse_and_execute(text)
            if not ok:
                print("Command not recognized; will retry once.")
                # retry once automatically
                time.sleep(0.3)
                rec2 = sd.rec(int(DURATION*FS), samplerate=FS, channels=CHANNELS, dtype='int16')
                sd.wait()
                fd2, fname2 = tempfile.mkstemp(suffix=".wav", prefix="vt2_")
                os.close(fd2)
                sf.write(fname2, rec2, FS)
                with sr.AudioFile(fname2) as source2:
                    audio2 = r.record(source2)
                try:
                    text2 = r.recognize_google(audio2)
                    print("Heard retry:", text2)
                    if parse_and_execute(text2):
                        os.remove(fname2)
                        os.remove(fname)
                        return True
                except:
                    pass
                try: os.remove(fname2)
                except: pass
            try: os.remove(fname)
            except: pass
            return True
        except sr.UnknownValueError:
            print("Could not understand")
            speak("Could not understand, please repeat")
        except Exception as e:
            print("Recognition error:", e)
        try: os.remove(fname)
        except: pass
        return False
    except Exception as e:
        print("Record error:", e); return False

print("Voice fallback running. Speak clearly after the prompt. Press Ctrl+C to stop.")
while True:
    try:
        speak("Listening now")
        record_and_recognize()
        time.sleep(0.3)
    except KeyboardInterrupt:
        break
    except Exception as e:
        print("Runtime error:", e)
        time.sleep(0.5)
