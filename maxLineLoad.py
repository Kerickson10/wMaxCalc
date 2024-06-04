#!/usr/bin/python3
from indeterminatebeam import Beam, Support, DistributedLoad
import numpy as np
import time

def maxMoment(beamLength, supportPositions, lineLoad, printGraphs="No"):
    """
    Analyzes a beam with given length, support positions, and line load.

    Parameters:
    - beamLength: beam length in feet.
    - supportPositions: list of support positions in feet.
    - lineLoad: line load in lbs/ft.
    """
    start_time = time.time()  # Start timing
    
    # Initialize the beam with the given length and modulus of elasticity
    beam = Beam(beamLength, E=29000000)  # E is the modulus of elasticity in psi

    # Update units for the beam analysis
    units = {'length': 'ft', 'force': 'lbf', 'distributed': 'lbf/ft', 
             'moment': 'lbf.ft', 'E': 'lbf/in2', 'I': 'in4', 'deflection': 'in'}
    for key, unit in units.items():
        beam.update_units(key, unit)
    
    # Add supports to the beam
    for position in supportPositions:
        beam.add_supports(Support(position, (1, 1, 0)))  # Defines a pin support
    
    # Add the distributed load to the beam
    beam.add_loads(DistributedLoad(lineLoad, span=(0, beamLength), angle=90))
    
    # Perform beam analysis
    beam.analyse()
    
    # Plot results if requested
    if printGraphs == "Yes":
        beam.plot_beam_external().show()
        beam.plot_beam_internal().show()

    # Calculate and return maximum bending moment and support reactions
    maxCalcMoment = beam.get_bending_moment(return_absmax=True)
    supportLoads = [np.ceil(abs(beam.get_reaction(pos, 'y'))) for pos in supportPositions]
    
    end_time = time.time()  # End timing
    # print(f"maxMoment function execution time: {end_time - start_time:.2f} seconds")
    
    return maxCalcMoment, supportLoads

def maxLineLoadConvergence(beamLength, supportPositions, target, initial_guess, tolerance=1, max_iterations=100):
    """
    Uses the Newton-Raphson method to find the maximum line load that will produce a 
    maximum bending moment close to the target moment.

    Parameters:
    - beamLength: beam length in feet.
    - supportPositions: list of support positions in feet.
    - target: target maximum bending moment in ft-lbs.
    - initial_guess: initial guess for line load in lbs/ft.
    - tolerance: tolerance for convergence. Default is 1 ft-lbs.
    - max_iterations: maximum number of iterations for the algorithm.
    """
    start_time = time.time()  # Start timing
    iterations = 0  # Initialize iteration counter
    lineLoad = initial_guess
    print()

    def f(lineLoad):
        maxCalcMoment, _ = maxMoment(beamLength, supportPositions, lineLoad)
        return maxCalcMoment - target

    def df(lineLoad):
        delta = 1e-5
        return (f(lineLoad + delta) - f(lineLoad)) / delta

    for _ in range(max_iterations):
        iterations += 1
        moment_diff = f(lineLoad)
        if abs(moment_diff) < tolerance:
            break
        lineLoad -= moment_diff / df(lineLoad)
        print(f'Try {lineLoad} lb/ft')
    
    # Final evaluation
    maxCalcMoment, supportLoads = maxMoment(beamLength, supportPositions, lineLoad)
    
    end_time = time.time()  # End timing
    print(f"newton_raphson_optimize function execution time: {end_time - start_time:.2f} seconds")
    print(f"Number of iterations: {iterations}")
    print(f'Max Line Load is {lineLoad} lbs/ft')
    print(f'Maximum Bending Moment is {maxCalcMoment} ft-lbs')

    for pos, load in zip(supportPositions, supportLoads):
        print(f"Support Reaction at {pos}\' is {load} lbs")
    
    return lineLoad, supportLoads


# Example usage
lineLoad, supportLoads = maxLineLoadConvergence(100, [0,50,100], 479000, initial_guess=10000)


