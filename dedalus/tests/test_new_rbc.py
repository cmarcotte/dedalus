

import numpy as np
from dedalus.core import coords, distributor, basis, field, operators

# Parameters
Lx, Ly, Lz = (4, 4, 1)
Nx, Ny, Nz = 16, 16, 16
Prandtl = 1
Rayleigh = 3000

# Bases
c = coords.CartesianCoordinates('x', 'y', 'z')
d = distributor.Distributor((c,))
xb = basis.ComplexFourier(c.coords[0], size=Nx, bounds=(0, Lx))
yb = basis.ComplexFourier(c.coords[1], size=Ny, bounds=(0, Ly))
zb = basis.ChebyshevT(c.coords[2], size=Nz, bounds=(0, Lz))

# Fields
p = field.Field(dist=d, bases=(xb,yb,zb), dtype=np.complex128)
b = field.Field(dist=d, bases=(xb,yb,zb), dtype=np.complex128)
u = field.Field(dist=d, bases=(xb,yb,zb), dtype=np.complex128, tensorsig=(c,))
X = [p, b, u]
ez = field.Field(dist=d, bases=(xb,yb,zb), dtype=np.complex128, tensorsig=(c,))
ez['g'][2] = 1

# Equations [M, L, F]
P = (Rayleigh * Prandtl)**(-1/2)
R = (Rayleigh / Prandtl)**(-1/2)
ghat = - ez
div = operators.Divergence
lap = operators.Laplacian
grad = operators.Gradient
dot = operators.DotProduct
eq0 = [0, div(u,0), 0]
eq1 = [b, -P*lap(b,c), -dot(u,grad(b,c))]
eq2 = [u, -R*lap(u,c) + grad(p,c), -dot(u,grad(u,c)) - b*ghat]
bc1 = [0, u(z=0), 0]
bc2 = [0, u(z=Lz), 0]
bc3 = [0, b(z=0), Lz]
bc4 = [0, b(z=Lz), 0]
# Pressure gauge?
eqs = [eq0, eq1, eq2]
bcs = [bc1, bc2, bc3, bc4]

# Apply conversions
for eq in eqs + bcs:
    M, L, F = eq
    bases = (M + L - F).domain.bases
    if M:
        M = field.Operand.cast(M, d)
        eq[0] = operators.convert(M, bases)
    if L:
        L = field.Operand.cast(L, d)
        eq[1] = operators.convert(L, bases)
    if F:
        F = field.Operand.cast(F, d)
        eq[2] = operators.convert(F, bases)

# Check we can evaluate everything
for eq in eqs + bcs:
    for expr in eq:
        if expr:
            expr.evaluate()

print("All expressions evaluate.")
