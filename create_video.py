import cv2
import numpy as np

width, height = 1280, 720
fps = 30
duration = 10  # seconds

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('backend/sample_traffic.mp4', fourcc, fps, (width, height))

num_cars = 5
cars = []
for _ in range(num_cars):
    cars.append({
        'x': np.random.randint(0, width),
        'y': np.random.randint(0, height),
        'w': np.random.randint(50, 150),
        'h': np.random.randint(30, 80),
        'speed': np.random.randint(5, 15)
    })

for i in range(fps * duration):
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    frame[:] = (128, 128, 128)  # Gray background

    for car in cars:
        car['x'] = (car['x'] + car['speed']) % width
        cv2.rectangle(frame, (car['x'], car['y']), (car['x'] + car['w'], car['y'] + car['h']), (0, 0, 255), -1)

    out.write(frame)

out.release()
print("Video created successfully.")
