# BeyondTouch: A Multimodal Accessibility System for Human–Computer Interaction

## Overview

BeyondTouch is a multimodal human–computer interaction system that enables users to control a computer without using a physical mouse or keyboard. The system integrates hand gestures, eye tracking, and voice commands to create a touchless interface that improves accessibility and interaction flexibility.

Traditional computer interfaces rely heavily on physical devices such as a mouse and keyboard. These devices can be challenging to use for individuals with motor disabilities or in environments where hands-free interaction is required. BeyondTouch addresses this problem by combining computer vision and speech recognition technologies to provide an intuitive alternative interface.

The system allows users to move the cursor, perform clicks, execute commands, and navigate the operating system using natural gestures, eye movements, or voice instructions.

---

## Real World Problem

Millions of users face difficulty interacting with computers due to physical impairments, repetitive strain injuries, or environmental constraints. Standard input devices require precise hand movement and constant physical interaction.

Additionally, in certain environments such as healthcare settings, laboratories, or industrial spaces, touch-based interfaces may not be practical.

BeyondTouch aims to solve these challenges by introducing a multimodal interaction system that allows users to interact with computers using natural human behaviors such as gestures, gaze, and speech.

---

## Key Features

• Touchless computer control using computer vision  
• Cursor movement using hand gestures or eye tracking  
• Mouse click detection using blink gestures  
• Voice commands to open applications and execute tasks  
• Multimodal input combining gesture, gaze, and voice  
• Smooth cursor control using smoothing algorithms  
• Real-time interaction using webcam and microphone  

---

## System Architecture

The system consists of several layers:

### Input Layer
Captures user input through hardware devices.

- Webcam for gesture and eye tracking
- Microphone for voice commands

### Perception Layer
Extracts meaningful data from raw input using computer vision models.

- MediaPipe Hands detects 21 hand landmarks
- MediaPipe FaceMesh detects 468 facial landmarks
- SpeechRecognition converts audio to text

### Interpretation Layer
Processes detected features and interprets gestures or commands.

Examples include:

- Gesture classification based on finger positions
- Blink detection using eye aspect ratio
- Voice command parsing using text pattern matching

### Action Execution Layer
Executes system-level commands using automation libraries.

The PyAutoGUI library performs actions such as:

- Moving the cursor
- Clicking
- Typing text
- Opening applications

### Interface Layer
A simple graphical interface built using Tkinter allows users to select different interaction modes.

---

## Technologies Used

Programming Language:
Python

Libraries:

- OpenCV
- MediaPipe
- NumPy
- PyAutoGUI
- SpeechRecognition
- SoundDevice
- Pyttsx3
- Tkinter

---

## Modules

### Hand Gesture Control

Uses MediaPipe Hands to detect 21 hand landmarks and classify gestures based on finger positions and angles.

Functions include:

- Cursor movement
- Left click
- Right click
- Double click
- Screenshot capture

Gesture recognition is implemented using geometric relationships between landmarks.

---

### Eye Tracking

Uses MediaPipe FaceMesh to detect eye landmarks and estimate gaze direction.

Cursor movement is controlled using the iris position. Blink detection is implemented using the Eye Aspect Ratio (EAR) to trigger mouse clicks.

---

### Voice Command System

Voice commands are captured using a microphone and converted to text using SpeechRecognition.

Commands supported include:

- Opening applications
- Searching the web
- Typing text
- Executing keyboard shortcuts

---

### Action Execution System

An action queue ensures that commands are executed sequentially to avoid conflicts between gesture, gaze, and voice inputs.

---

## Installation

Clone the repository:



git clone [https://github.com/yourusername/BeyondTouch-Multimodal-Accessibility-System.git](https://github.com/yourusername/BeyondTouch-Multimodal-Accessibility-System.git)



Install dependencies:



pip install -r requirements.txt



Run the application:



python gui/main_gui_simple.py



---

## Applications

• Assistive technology for individuals with disabilities  
• Touchless computer interaction  
• Smart environments and automation systems  
• Research in human–computer interaction  

---

## Future Improvements

• Deep learning-based gesture classification  
• Custom wake-word voice assistant  
• Mobile device integration  
• Augmented reality interaction  

---

## Author

Harini V

Computer Science Engineering Student
