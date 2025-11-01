# 🕵️‍♂️ Q-Search  
A smart and interactive desktop browser built using **Python (PyQt5)** with integrated **Virtual Mouse Control** powered by **Computer Vision**.  
Users can browse the web, manage bookmarks, view history, and even control the browser using **hand gestures** detected by the webcam.

---

## 🚀 Features

### 🌐 Browser Features
- Modern GUI using **PyQt5**
- User authentication (Register / Login)
- Save and manage **bookmarks**
- View and clear **search history**
- Multiple search engine support: *Google*, *Bing*, *DuckDuckGo*
- Quick access to **YouTube**, **Instagram**, **LinkedIn**, **Facebook**, and **Twitter**

### ✋ Virtual Mouse (AI Integration)
- Uses **OpenCV** and **MediaPipe** for hand-tracking.
- Control the cursor, click, scroll, adjust system volume, and brightness using **hand gestures**.
- Gesture-based actions include:
  - ✊ Fist → Click/Drag  
  - ✌️ V-Gesture → Move Cursor  
  - 👌 Pinch → Adjust Brightness or Volume  
  - ✋ Palm → Neutral / Stop  

---

## 🧩 Tech Stack

| Component | Technology Used |
|------------|----------------|
| GUI | PyQt5 |
| Browser Engine | QWebEngineView |
| Gesture Recognition | OpenCV, MediaPipe |
| Virtual Mouse Control | PyAutoGUI, PyCAW, ScreenBrightnessControl |
| Authentication | bcrypt, JSON-based storage |
| Backend Files | Python (.py) |
| Data Storage | JSON (users, bookmarks, history) |

---

## 📁 Project Structure

```
Q-Search/
│
├── browser.py         # Main browser and UI logic
├── main.py            # Virtual mouse gesture controller
├── logo5.png          # Application logo
├── users.json         # User database (login info)
├── <username>_history.json   # User browsing history
├── <username>_bookmarks.json # User bookmarks
└── README.md          # Project documentation
```

---

## ⚙️ Installation & Setup

### Step 1: Clone Repository
```bash
git clone https://github.com/<your-username>/Q-Search.git
cd Q-Search
```

### Step 2: Install Dependencies
Make sure you have Python 3.9+ installed.
```bash
pip install pyqt5 pyqtwebengine opencv-python mediapipe pyautogui pycaw screen-brightness-control bcrypt pillow comtypes
```

### Step 3: Run the Application
```bash
python browser.py
```

---

## 🧠 How It Works

1. **Login / Register**  
   - User credentials are stored securely (hashed with bcrypt) in `users.json`.
2. **Browsing**  
   - Search or visit websites using the integrated web engine.
3. **Bookmark & History Management**  
   - Automatically saves visited URLs and allows adding favorites.
4. **Virtual Mouse Mode**  
   - Click “Virtual Mouse → Start” to activate hand gesture control using your webcam.

---

## 🖼️ Application Logo
![Q-Search Logo](logo5.png)

---

## 🧑‍💻 Author
**Md Rasheed**  
Institute of Aeronautical Engineering (IARE)  
Department of Computer Science & Machine Learning  

---

## 📜 License
This project is open-source and available under the **MIT License**.
