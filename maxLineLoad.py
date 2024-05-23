#!/usr/bin/python3
from indeterminatebeam import Beam, Support, DistributedLoad, PointLoad
import numpy as np
import math
import matplotlib.pyplot as plt
import sympy as sp
import pandas as pd
import os
import re

def maxMoment(beamLength,supportPositions,lineLoad,maxAllowMoment, printGraphs="No"):
    """
    Analyzes a corner post with given sheeted height and tributary width.

    Parameters:
    - beamlLength: beam length in feet.
    - supportPositions: tributary width in feet.
    - maxAllowMoment: maximum allowable moment in ft-lbs/ft.
    """
    #initialize variables
    supportLoads = []
    beam = Beam(beamLength, E=29000000)  # E is the modulus of elasticity in psi
    # Update units for the beam analysis
    beam.update_units(key='length', unit='ft')
    beam.update_units('force', 'lbf')
    beam.update_units('distributed', 'lbf/ft')
    beam.update_units('moment', 'lbf.ft')
    beam.update_units('E', 'lbf/in2')
    beam.update_units('I', 'in4')
    beam.update_units('deflection', 'in')
    # Add supports to the beam
    
    for position in supportPositions:
        support = Support(position, (1, 1, 0))  # Defines a pin support
        beam.add_supports(support)
    load = DistributedLoad(lineLoad, span=(0, beamLength), angle=90)
    # Add the load to the beam
    beam.add_loads(load)
    # Perform beam analysis
    beam.analyse()
    # print("Beam Analysis Complete")
    # Plot results
    fig_1 = beam.plot_beam_external()
    # fig_1.show()
    fig_2 = beam.plot_beam_internal()
    # fig_2.show()

    if printGraphs == "Yes":
        fig_1.show()
        fig_2.show()

    # Calculate and print maximum bending moment and support reactions
    maxCalcMoment = beam.get_bending_moment(return_absmax=True)

    # lineLoad = convergence(beamLength,supportPositions,lineLoad,maxAllowMoment, 0, 100000)
    print(f'Max Line Load is {lineLoad} lbs/ft')
    print(f'Maximum Bending Moment is {np.ceil(maxCalcMoment)} ft-lbs')
    
    for position in supportPositions:
        print(f"Support Reaction at {position}\' is {np.ceil(abs(beam.get_reaction(position, 'y')))} lbs")
        supportLoads.append(np.ceil(abs(beam.get_reaction(beamLength, 'y'))))

    return maxCalcMoment, supportLoads

def convergence(beamLength,supportPositions, target, low, high, tolerance=.01):
    
    for _ in range(100):
        lineLoad = (low + high) / 2
        print(lineLoad)
        maxCalcMoment, supportLoads = maxMoment(beamLength,supportPositions,lineLoad, target)

        if abs(maxCalcMoment - target)/100 < tolerance:
            return lineLoad, supportLoads

        if maxCalcMoment < target:
            low = lineLoad
        else:
            high = lineLoad
    
    raise ValueError("Convergence not found")
    
lineLoad, supportLoads = convergence(20,[0,10,20],479000, 0, 50000)

# maxCalcMoment = maxLineLoad(20,[0,10,20],479000)