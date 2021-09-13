"""
File contains functions and constants used in TFLink post-processing.

Edits:
 - 3/24/21, M. Lavell. Created File.
"""
import numpy as np
import matplotlib
matplotlib.use('qt5agg')

import matplotlib.pyplot as plt

# constants (mks)
Mi = 1.67262192e-27
Me = 9.10938356e-31
qe = 1.60217663e-19
MH = 1  # atomic number hydrogen
MC = 6  # carbon
MO = 16  # oxygen
Kb = 1.38064852e-23
eps0 = 8.8541878128e-12
tol = 1e-27


# function returns temperature and velocity drift
def getTempDrift(velx, mass):
    nparts = np.shape(velx)[0]
    sumV2 = 0;
    sumVDrift = np.zeros(3)
    for p in range(nparts):
        sumV2 += np.sum(velx[p] ** 2)
        sumVDrift += velx[p]
    temp = mass / (3 * Kb) * abs(sumV2 / nparts - np.sum((sumVDrift / nparts) ** 2))
    vdrift = sumVDrift / nparts
    return temp, vdrift


# function returns Debye length for single species
def getDebyeLength(ndens, atomNum, temp):
    rmin = (4.0 * np.pi * ndens / 3.0) ** (-1 / 3)  # min mean interatomic distance
    debyelength = (ndens * (qe * atomNum) ** 2 / (eps0 * Kb * temp)) ** (-0.5)
    return max(rmin, debyelength)


# function returns Debye length for two species
def getDebyeLengthTwoSpecies(ndens1, atomNum1, temp1, ndens2, atomNum2, temp2):
    # min mean interatomic distance
    rmin = (4.0 * np.pi * max(ndens1, ndens2) / 3.0) ** (-1 / 3)
    ldm2 = (ndens1 * (qe * atomNum1) ** 2 / (eps0 * Kb * temp1) + ndens2 * (qe * atomNum2) ** 2 / (eps0 * Kb * temp2))
    return max(rmin, ldm2 ** (-0.5))


# function returns plasma frequency
def getPlasmaFrequency(ndens, chrg, mass):
    return (ndens * (qe * chrg) ** 2 / (eps0 * mass)) ** 0.5


# function returns array of velocity norms
def getVelocityNorm(vec3, nsteps):
    vnorm = np.zeros(nsteps)
    for s in range(nsteps):
        vnorm[s] = np.linalg.norm(vec3[s, :])
    return vnorm


# function returns thermal velocity
def getThermalVelocity(temperature, mass):
    return np.sqrt(Kb * temperature / mass)
