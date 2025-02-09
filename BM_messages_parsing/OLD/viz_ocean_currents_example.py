# example code, see a vector field plotted on a 2D plane with arrows showing direction and magnitude
import numpy as np
import matplotlib.pyplot as plt

# Create pseudo data for the vector field
x = np.linspace(0, 10, 10)  # X coordinates
y = np.linspace(0, 10, 10)  # Y coordinates
X, Y = np.meshgrid(x, y)

# Simulate current magnitude and direction
U = np.sin(Y)  # X component (magnitude and direction in X)
V = np.cos(X)  # Y component (magnitude and direction in Y)

# Plot the vector field
plt.figure(figsize=(10, 8))
plt.quiver(X, Y, U, V, angles='xy', scale_units='xy', scale=1, color='blue')
plt.title('2D Vector Field Representation of Ocean Currents')
plt.xlabel('X Coordinate (Longitude)')
plt.ylabel('Y Coordinate (Latitude)')
plt.grid(True)
plt.show()
