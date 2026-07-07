import cv2
import mediapipe as mp
import random
import time

# ===== MediaPipe setup =====
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

def rounded_rect(img, top_left, bottom_right, color, radius, thickness=cv2.FILLED):
    x1, y1 = top_left
    x2, y2 = bottom_right
    cv2.rectangle(img, (x1 + radius, y1), (x2 - radius, y2), color, thickness, cv2.LINE_AA)
    cv2.rectangle(img, (x1, y1 + radius), (x2, y2 - radius), color, thickness, cv2.LINE_AA)
    cv2.circle(img, (x1 + radius, y1 + radius), radius, color, thickness, cv2.LINE_AA)
    cv2.circle(img, (x2 - radius, y1 + radius), radius, color, thickness, cv2.LINE_AA)
    cv2.circle(img, (x1 + radius, y2 - radius), radius, color, thickness, cv2.LINE_AA)
    cv2.circle(img, (x2 - radius, y2 - radius), radius, color, thickness, cv2.LINE_AA)

def spawn_ball():
    ball_type = random.choices(list(BALL_WEIGHTS.keys()), weights=list(BALL_WEIGHTS.values()))[0]
    return {
        'x': random.randint(ball_radius, frame_width - ball_radius),
        'y': 0,
        'type': ball_type
    }

# ===== Camera + frame dimensions =====
cap = cv2.VideoCapture(0)
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# ===== Box settings =====
box_width = 175
box_height = 130
wall_thickness = 8

# ===== Ball settings =====
ball_radius = 18
max_balls_on_screen = 20
spawn_chance = 0.03

balls = []

BALL_TYPES = {
    'green': {'points': 1, 'color': (100, 220, 100)},
    'blue':  {'points': 2, 'color': (255, 140, 60)},
    'gold':  {'points': 5, 'color': (0, 210, 255)},
    'red':   {'points': -2, 'color': (60, 60, 230)},
}
BALL_WEIGHTS = {'green': 50, 'blue': 25, 'gold': 10, 'red': 15}

score = 0
time_limit = 30  # seconds
game_start_time = time.time()
game_over = False
confetti = []
collected_balls = []  # stores (row, col) grid position of each caught ball
balls_per_row = 5
mini_ball_radius = 10

# ===== Main loop =====
while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    # Hand tracking + box control
    paddle_x = frame_width // 2  # default if no hand detected this frame

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            index_tip = hand_landmarks.landmark[8]
            cx, cy = int(index_tip.x * frame_width), int(index_tip.y * frame_height)
            cv2.circle(frame, (cx, cy), 10, (0, 255, 0), cv2.FILLED, cv2.LINE_AA)
            paddle_x = cx

    # Box position, following fingertip horizontally
    box_left = paddle_x - box_width // 2
    box_right = paddle_x + box_width // 2
    box_top = frame_height - box_height - 10
    box_bottom = frame_height - 10

    # Glowing outline behind the box
    glow_overlay = frame.copy()
    rounded_rect(glow_overlay, (box_left - 6, box_top - 6), (box_right + 6, box_bottom + 6), (180, 220, 60), 18)
    frame = cv2.addWeighted(glow_overlay, 0.2, frame, 0.8, 0)

    glass_overlay = frame.copy()
    rounded_rect(glass_overlay, (box_left, box_top), (box_right, box_bottom), (70, 60, 20), 16)
    frame = cv2.addWeighted(glass_overlay, 0.35, frame, 0.65, 0)

    # Walls
    cv2.rectangle(frame, (box_left, box_top), (box_left + wall_thickness, box_bottom), (180, 220, 60), cv2.FILLED, cv2.LINE_AA)
    cv2.rectangle(frame, (box_right - wall_thickness, box_top), (box_right, box_bottom), (180, 220, 60), cv2.FILLED, cv2.LINE_AA)
    cv2.rectangle(frame, (box_left, box_bottom - wall_thickness), (box_right, box_bottom), (180, 220, 60), cv2.FILLED, cv2.LINE_AA)

    # Draw stacked/collected balls inside the box
    for (row, col) in collected_balls:
        sx = box_left + wall_thickness + mini_ball_radius + col * (mini_ball_radius * 2 + 4)
        sy = box_bottom - wall_thickness - mini_ball_radius - row * (mini_ball_radius * 2 + 4)
        cv2.circle(frame, (int(sx), int(sy)), mini_ball_radius, (100, 90, 255), cv2.FILLED, cv2.LINE_AA)
        cv2.circle(frame, (int(sx), int(sy)), mini_ball_radius, (255, 255, 255), 1, cv2.LINE_AA)

    # ---- Timer check ----
    elapsed = time.time() - game_start_time
    remaining = max(0, time_limit - elapsed)

    if remaining <= 0 and not game_over:
        game_over = True
        confetti = [
            {
                'x': random.randint(0, frame_width),
                'y': random.randint(-frame_height, 0),
                'speed': random.randint(4, 10),
                'color': random.choice([(255,80,180),(255,180,60),(80,255,120),(255,60,220),(0,210,255)]),
                'size': random.randint(4, 8)
            }
            for _ in range(150)
        ]

    # ---- Gameplay only runs while time remains ----
    if not game_over:
        current_speed = min(7 + score // 5, 18)

        if len(balls) < max_balls_on_screen and random.random() < spawn_chance:
            balls.append(spawn_ball())

        balls_to_remove = []

        for ball in balls:
            ball['y'] += current_speed
            color = BALL_TYPES[ball['type']]['color']

            overlay = frame.copy()
            for i in range(3, 0, -1):
                glow_radius = ball_radius + (i * 8)
                cv2.circle(overlay, (ball['x'], ball['y']), glow_radius, color, cv2.FILLED, cv2.LINE_AA)
            frame = cv2.addWeighted(overlay, 0.15, frame, 0.85, 0)

            cv2.circle(frame, (ball['x'], ball['y']), ball_radius, color, cv2.FILLED, cv2.LINE_AA)
            cv2.circle(frame, (ball['x'], ball['y']), ball_radius, (255, 255, 255), 2, cv2.LINE_AA)

            if box_top < ball['y'] + ball_radius < box_bottom:
                if box_left + wall_thickness < ball['x'] < box_right - wall_thickness:
                    points_earned = BALL_TYPES[ball['type']]['points']
                    score += points_earned
                    score = max(score, 0)

                    if points_earned > 0:
                        for _ in range(points_earned):
                            if len(collected_balls) < balls_per_row * 4:
                                row = len(collected_balls) // balls_per_row
                                col = len(collected_balls) % balls_per_row
                                collected_balls.append((row, col))
                    else:
                        for _ in range(abs(points_earned)):
                            if collected_balls:
                                collected_balls.pop()

                    balls_to_remove.append(ball)

            elif ball['y'] - ball_radius > frame_height:
                balls_to_remove.append(ball)

        for ball in balls_to_remove:
            balls.remove(ball)

    # Score + timer panel background
    overlay = frame.copy()
    cv2.rectangle(overlay, (10, 10), (260, 60), (20, 20, 20), cv2.FILLED)
    frame = cv2.addWeighted(overlay, 0.6, frame, 0.4, 0)
    cv2.putText(frame, f"Score: {score}", (25, 45), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(frame, f"{int(remaining)}s", (190, 45), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 210, 255), 2, cv2.LINE_AA)

    # ---- Time's up screen ----
    if game_over:
        for piece in confetti:
            piece['y'] += piece['speed']
            if piece['y'] > frame_height:
                piece['y'] = random.randint(-50, 0)
                piece['x'] = random.randint(0, frame_width)
            cv2.circle(frame, (piece['x'], int(piece['y'])), piece['size'], piece['color'], cv2.FILLED, cv2.LINE_AA)

        overlay = frame.copy()
        cv2.rectangle(overlay, (frame_width//2 - 220, frame_height//2 - 60), (frame_width//2 + 220, frame_height//2 + 60), (20, 20, 20), cv2.FILLED)
        frame = cv2.addWeighted(overlay, 0.7, frame, 0.3, 0)

        cv2.putText(frame, "Time's Up!", (frame_width//2 - 130, frame_height//2 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.1, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(frame, f"Final Score: {score}", (frame_width//2 - 130, frame_height//2 + 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 220, 255), 2, cv2.LINE_AA)

    cv2.imshow("Ball Catch", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()