import numpy as np
import time
from indeterminatebeam import Beam, Support, DistributedLoad

def maxMoment(beamLength, supportPositions, lineLoad, printGraphs="No"):
    """
    Analyzes a corner post with given sheeted height and tributary width.

    Parameters:
    - beamLength: beam length in feet.
    - supportPositions: list of support positions in feet.
    - lineLoad: line load in lbs/ft.
    - maxSupportReaction: maximum allowable support reaction in lbs.
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
    beam.add_loads(DistributedLoad(lineLoad * -1, span=(0, beamLength), angle=90))  # Adjusted for negative load
    
    # Perform beam analysis
    beam.analyse()
    
    # Plot results if requested
    if printGraphs == "Yes":
        beam.plot_beam_external().show()
        beam.plot_beam_internal().show()

    # Calculate and return maximum and minimum bending moments and support reactions
    maxCalcMoment = beam.get_bending_moment(return_max=True)
    minCalcMoment = beam.get_bending_moment(return_min=True)
    
    supportLoads = [np.ceil(abs(beam.get_reaction(pos, 'y'))) for pos in supportPositions]
    
    # Check if any support reaction exceeds the maximum allowable value
    
    return maxCalcMoment, minCalcMoment, supportLoads

def maxLineLoadConvergence(beamLength, supportPositions, positiveTarget, negativeTarget, initial_guess, maxSupportReaction, tolerance=1, max_iterations=100):
    start_time = time.time()  # Start timing
    
    # Function to find the line load for positive target moment
    def findLineLoadForPositiveTarget(lineLoad):
        def f(lineLoad):
            maxCalcMoment, _, _ = maxMoment(beamLength, supportPositions, lineLoad)
            return maxCalcMoment - positiveTarget
        
        def df(lineLoad):
            delta = 1e-5  # Adjust delta for better numerical stability
            return (f(lineLoad + delta) - f(lineLoad)) / delta
        
        for _ in range(max_iterations):
            moment_diff = f(lineLoad)
            if abs(moment_diff) < tolerance:
                return lineLoad
            lineLoad -= moment_diff / df(lineLoad)
        
        return lineLoad
    
    # Function to find the line load for negative target moment
    def findLineLoadForNegativeTarget(lineLoad):
        def f(lineLoad):
            _, minCalcMoment, _ = maxMoment(beamLength, supportPositions, lineLoad)
            return negativeTarget - minCalcMoment
        
        def df(lineLoad):
            delta = 1e-2  # Adjust delta for better numerical stability
            return (f(lineLoad + delta) - f(lineLoad)) / delta
        
        for _ in range(max_iterations):
            moment_diff = f(lineLoad)
            if abs(moment_diff) < tolerance:
                return lineLoad
            lineLoad -= moment_diff / df(lineLoad)
        
        return lineLoad
    
    # Find line loads for positive and negative target moments
    lineLoadPositive = findLineLoadForPositiveTarget(initial_guess)
    lineLoadNegative = findLineLoadForNegativeTarget(initial_guess)
    
    # Determine the smaller line load
    if lineLoadPositive < lineLoadNegative:
        finalLineLoad = lineLoadPositive
    else:
        finalLineLoad = lineLoadNegative

    # Check if any support reaction exceeds the maximum allowable value
    maxCalcMoment, minCalcMoment, supportLoads = maxMoment(beamLength, supportPositions, finalLineLoad)
    if max(supportLoads) > maxSupportReaction:
        # Adjust the line load to ensure that support reactions remain within the limit
        finalLineLoad *= maxSupportReaction / max(supportLoads)
        # Recalculate moments and support reactions with the adjusted line load
        maxCalcMoment, minCalcMoment, supportLoads = maxMoment(beamLength, supportPositions, finalLineLoad)

    end_time = time.time()  # End timing

    # Final evaluation    
    maxCalcMoment, minCalcMoment, supportLoads = maxMoment(beamLength, supportPositions, finalLineLoad, maxSupportReaction)

    end_time = time.time()  # End timing

    print(f"maxLineLoadConvergence function execution time: {end_time - start_time:.2f} seconds")
    print(f'Minimum Line Load is {finalLineLoad} lbs/ft')
    print(f'Maximum Positive Bending Moment is {maxCalcMoment} ft-lbs')
    print(f'Maximum Negative Bending Moment is {minCalcMoment} ft-lbs')
    for pos, load in zip(supportPositions, supportLoads):
        print(f"Support Reaction at {pos}\' is {load} lbs")

    return finalLineLoad

# Example usage
# lineLoad = maxLineLoadConvergence(100, [0,50,100], 654000, -590000, initial_guess=10000)

# lineLoad = maxLineLoadConvergence(60, [0,30,60], 654000, -590000, 10000, 330000)