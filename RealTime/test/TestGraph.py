import numpy as np
import matplotlib.pyplot as plt
import time

# Define the image size
width, height = 100, 100

# Create an initial empty image (random noise)
data = np.random.rand(height, width)

# Set up the figure and imshow
fig, ax = plt.subplots()
im = ax.imshow(data, cmap='viridis', interpolation='nearest')

# Continuously update the image
for _ in range(100):  # Simulating a continuous stream
    data = np.random.rand(height, width)  # New random data
    im.set_data(data)  # Update the imshow data
    plt.draw()  # Redraw the figure
    plt.pause(0.1)  # Pause to allow UI to update
    time.sleep(0.1)  # Simulate data arrival delay

plt.show()
