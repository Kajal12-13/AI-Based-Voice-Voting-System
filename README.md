# AI-Based-Voice-Voting-System
# Mini Voting System Using C and IOT

An intelligent, secure, and multi-platform voting system that integrates **Artificial Intelligence** for voter verification and **IOT principles** for data management. This project was developed as part of a research paper exploring the intersection of biometric security and embedded systems.

## 🚀 Key Features
*   **Face Verification:** Uses AI-based face recognition to authenticate voters against a local dataset.
*   **Voice Integration:** Interactive voice-guided voting process for accessibility using Text-to-Speech (TTS) and Speech Recognition.
*   **Hybrid Backend:** Utilizes a **C-based logic module** for efficient data handling and a **Python-based front-end** for high-level AI integration.
*   **Real-time Database:** Integrated with **Firebase** to store and sync voting results securely across sessions.
*   **Modular Security:** Implements Environment Variables and Secrets management to ensure credentials remain private.

## 🛠️ Tech Stack
*   **Languages:** Python (AI & Logic), C (Backend Processing)
*   **AI/ML:** OpenCV, Face-Recognition
*   **Cloud:** Firebase Realtime Database
*   **UI/UX:** Tkinter (Python)
*   **IOT:** Integrated voice and sensor logic simulation

## 📁 Project Structure
```text
├── main.py                # Main application entry point
├── backend.c              # C logic for vote processing
├── speak.py               # Voice and speech modules
├── .gitignore             # Git security configuration
├── requirements.txt       # Project dependencies
└── README.md              # Documentation
