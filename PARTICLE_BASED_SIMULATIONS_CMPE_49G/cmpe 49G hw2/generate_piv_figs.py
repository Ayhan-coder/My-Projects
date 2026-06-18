import numpy as np
import matplotlib.pyplot as plt

# Fig 1: Sample PIV Velocity Field (Flow past cylinder wake approximation)
x = np.linspace(-2, 5, 30)
y = np.linspace(-2, 2, 20)
X, Y = np.meshgrid(x, y)

# approximate wake
U = 1.0 - 0.5 * np.exp(-(Y**2) / 0.5) * np.exp(-0.2 * np.maximum(X, 0))
V = 0.2 * np.sin(X * 2) * np.exp(-(Y**2) / 0.5) * np.exp(-0.2 * np.maximum(X, 0))
U[X**2 + Y**2 < 0.5**2] = 0
V[X**2 + Y**2 < 0.5**2] = 0

# vorticity
dVdx = np.gradient(V, x, axis=1)
dUdy = np.gradient(U, y, axis=0)
vorticity = dVdx - dUdy
vorticity[X**2 + Y**2 < 0.5**2] = np.nan

plt.figure(figsize=(8, 4))
plt.contourf(X, Y, vorticity, levels=50, cmap='RdBu_r', alpha=0.8)
plt.colorbar(label='Vorticity $\\omega_z$')
# thin out quiver
step = 1
plt.quiver(X[::step, ::step], Y[::step, ::step], U[::step, ::step], V[::step, ::step], 
           scale=20, color='black', alpha=0.8)
circle = plt.Circle((0, 0), 0.5, color='gray')
plt.gca().add_patch(circle)
plt.title("Sample PIV Velocity Field: Wake behind a Cylinder")
plt.xlabel("x / D")
plt.ylabel("y / D")
plt.tight_layout()
plt.savefig(r"c:\Users\Slayer\Desktop\cmpe49g hw2\piv_velocity_field.png", dpi=300)

# Fig 2: Cross-correlation peak
sx = np.linspace(-10, 10, 50)
sy = np.linspace(-10, 10, 50)
SX, SY = np.meshgrid(sx, sy)
# Peak at dx=3.5, dy=-1.2
C = np.exp(-((SX - 3.5)**2 + (SY + 1.2)**2) / 4) + np.random.normal(0, 0.05, SX.shape)
C = np.clip(C, 0, None)

fig = plt.figure(figsize=(6, 5))
ax = fig.add_subplot(111, projection='3d')
surf = ax.plot_surface(SX, SY, C, cmap='viridis', edgecolor='none')
ax.set_title("Cross-Correlation Plane with Sub-pixel Peak")
ax.set_xlabel("Displacement $s_x$ (px)")
ax.set_ylabel("Displacement $s_y$ (px)")
ax.set_zlabel("Correlation $C(\\mathbf{s})$")
# Mark the peak
ax.scatter([3.5], [-1.2], [np.max(C)], color='red', s=50, label='Displacement Peak')
ax.legend()
plt.tight_layout()
plt.savefig(r"c:\Users\Slayer\Desktop\cmpe49g hw2\correlation_peak.png", dpi=300)
