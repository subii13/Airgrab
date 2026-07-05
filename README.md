# Ball Catch — Hand-Tracking Arcade Game

A webcam-based arcade game where you control an on-screen basket using real-time hand tracking — no mouse, no keyboard, just your hand in front of the camera.

## How it works

- Your webcam feed is processed live using MediaPipe's hand landmark detection.
- Your index fingertip position controls a basket that moves left and right.
- Balls fall from the top of the screen; catch them in your basket before they hit the bottom.
- Different ball colors are worth different points:
  - 🟢 Green = +1
  - 🔵 Blue = +2
  - 🟡 Gold = +5
  - 🔴 Red = −2
- You have 30 seconds to score as many points as possible. Falling speed increases as your score grows.

## Tech stack

- **Python 3.11**
- **OpenCV** — video capture, rendering, all visual effects (glow, transparency, confetti)
- **MediaPipe** — real-time hand landmark detection

## Setup and running locally

MediaPipe does not currently support Python 3.13+ (no pre-built wheels available), so this project requires **Python 3.11** specifically, run inside a virtual environment.

1. Install [Python 3.11](https://www.python.org/downloads/release/python-3119/) if you don't already have it.

2. Clone this repo and navigate into it:
```bash
   git clone https://github.com/subii13/ball-catch-game.git
   cd ball-catch-game
```

3. Create a virtual environment using Python 3.11 specifically:
```bash
   "C:\path\to\Python311\python.exe" -m venv venv
```

4. Activate it:
   - Command Prompt / PowerShell: `venv\Scripts\activate`
   - Git Bash: `source venv/Scripts/activate`

5. Install dependencies:
```bash
   pip install -r requirements.txt
```

6. Run the game:
```bash
   python ball_catch.py
```

7. Press **Q** to quit at any time.

## Project status

Built as a solo learning project to explore real-time computer vision and hand-tracking with OpenCV and MediaPipe. Currently a complete, playable time-attack mode — future improvements planned include difficulty levels, sound effects, and a proper menu/win-lose screen flow.