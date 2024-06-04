import pandas as pd
import numpy as np

def calculate_moment_at_point(UDL, span, x):
    """
    Calculate the bending moment at any point along a simply supported beam
    with a central support under a uniformly distributed load (UDL).

    Parameters:
    - UDL: Uniformly distributed load in units of force per length (e.g., N/m or lb/ft)
    - span: Length of one span in the beam
    - x: Distance from the left end of the beam to the point where the moment is calculated

    Returns:
    - Moment at the specified point
    """
    # print(f'Try {x} ft')
    # Reactions at supports
    R_A = R_C = 3 * UDL * span / 8
    R_B = 10 * UDL * span / 8

    # Central support moment
    M_B = -0.125 * UDL * span**2

    if 0 <= x <= span:
        # Calculate moment in the left span (0 to L)
        M = R_A * x - (UDL * x**2) / 2
    elif span < x <= 2 * span:
        # Calculate moment in the right span (L to 2L), mirroring the left span
        x_prime = x - span
        M = R_C * (span - x_prime) - (UDL * (span - x_prime)**2) / 2
    else:
        raise ValueError("The point x is outside the length of the beam.")

    return M

def maxLineLoadCentralStrut(beamLength,HD="No"):
    """
    Find the maximum allowable distributed load on a beam given the length and available extensions

    Parameters:
    - beamLength: Length of the beam in feet.
    - HD: If HD extensions are available.
    """
    span = beamLength/2

    file_path = "/home/bpeters2/Indeterminate Beam/wMaxCalc/extensions.csv"
    df = pd.read_csv(file_path)

    filtered_df = df[(df['min'] <= beamLength) & (df['max'] >= beamLength)]

    if HD == "No":
        filtered_df = filtered_df[~filtered_df['Ext1'].isin([9.0, 12.0])]
        filtered_df = filtered_df[~filtered_df['Ext2'].isin([9.0, 12.0])]
        filtered_df = filtered_df[~filtered_df['Ext3'].isin([9.0, 12.0])]
        filtered_df = filtered_df[~filtered_df['Ext4'].isin([9.0, 12.0])]
        negativeExtCap = -590000
        positiveExtCap = 654000
    
    filtered_df = filtered_df.drop('min', axis=1)
    filtered_df = filtered_df.drop('max', axis=1)

    filtered_df['Joint1'] = beamLength - 1.88 - (filtered_df['total'] * 3.281)
    filtered_df['Joint2'] = 0.0
    filtered_df['Joint3'] = 0.0
    filtered_df['Joint4'] = 0.0

    for index, row in filtered_df.iterrows():
        if pd.notnull(row['Ext2']):
            filtered_df.at[index, 'Joint2'] = row['Joint1'] + (row['Ext1'] * 3.281)
        if pd.notnull(row['Ext3']) and filtered_df.at[index, 'Joint2'] != 0:
            filtered_df.at[index, 'Joint3'] = filtered_df.at[index, 'Joint2'] + (row['Ext2'] * 3.281)
        if pd.notnull(row['Ext4']) and filtered_df.at[index, 'Joint3'] != 0:
            filtered_df.at[index, 'Joint4'] = filtered_df.at[index, 'Joint3'] + (row['Ext3'] * 3.281)

    

    maxLineLoadHydraulic = np.floor(110000*8/(3*span))
    maxLineLoadStrut = np.floor(330000*8/(10*span))
    maxLineLoadNegativeExtension = np.floor(negativeExtCap/(-.125*span**2))
    maxLineLoadPositiveExtensioin = np.floor(positiveExtCap*128/(9*span**2))

    maxLineLoad = min(maxLineLoadHydraulic, maxLineLoadStrut, maxLineLoadNegativeExtension, maxLineLoadPositiveExtensioin)

    filtered_df = filtered_df.fillna(0)

    # Calculate the moment at each joint
    filtered_df['Joint1_Moment'] = filtered_df['Joint1'].apply(lambda x: calculate_moment_at_point(maxLineLoad, span, x))
    filtered_df['Joint2_Moment'] = filtered_df['Joint2'].apply(lambda x: calculate_moment_at_point(maxLineLoad, span, x))
    filtered_df['Joint3_Moment'] = filtered_df['Joint3'].apply(lambda x: calculate_moment_at_point(maxLineLoad, span, x))
    filtered_df['Joint4_Moment'] = filtered_df['Joint4'].apply(lambda x: calculate_moment_at_point(maxLineLoad, span, x))

    df = filtered_df

    # Remove configurations where the moment exceeds the capacity of the joint or is negative
    filtered_df = filtered_df[
    (filtered_df['Joint1_Moment'] >= 0.0) & (filtered_df['Joint1_Moment'] <= filtered_df['JointCap1']) &
    (filtered_df['Joint2_Moment'] >= 0.0) & (filtered_df['Joint2_Moment'] <= filtered_df['JointCap2']) &
    (filtered_df['Joint3_Moment'] >= 0.0) & (filtered_df['Joint3_Moment'] <= filtered_df['JointCap3']) &
    (filtered_df['Joint4_Moment'] >= 0.0) & (filtered_df['Joint4_Moment'] <= filtered_df['JointCap4'])]
    
    filtered_df = filtered_df.drop(columns=['Combo'])

    filtered_df = filtered_df.round(2)
    
    sorted_df = filtered_df.assign(num_extensions=(filtered_df[['Ext1', 'Ext2', 'Ext3', 'Ext4']] != 0).sum(axis=1)).sort_values(by='num_extensions')
    print(sorted_df)
    UDL = maxLineLoad  # Load in lb/ft or N/m
    span = beamLength/2  # Span in ft or meters
    step = .01 # Step size for calculating moments
    x_points = np.arange(start=0, stop=span*2+step, step=step)  # List of points at which to calculate the moment

    # Calculate moments for all points in x_points
    moments = [calculate_moment_at_point(UDL, span, x) for x in x_points]

    # Create a DataFrame to store points and their corresponding moments
    data = {'Point': x_points, 'Moment': moments}
    moment_df = pd.DataFrame(data)
    moment_df = moment_df.round(2)
    # print(moment_df)
    # Save the DataFrame to a .csv file
    moment_df.to_csv('momentTable.csv')
    sorted_df.to_csv('finalExtensionTable.csv')

    # Concatenate extension configurations for the first row
    extConfig = ' + '.join(
        f"{sorted_df.iloc[0][col]}m" 
        for col in ['Ext1', 'Ext2', 'Ext3', 'Ext4']
        if pd.notnull(sorted_df.iloc[0][col]) and sorted_df.iloc[0][col] != 0.0)


    return maxLineLoad,extConfig

beamLength = 80  # Example beam length
HD = "No"  # Example HD setting
max_load, extension_config = maxLineLoadCentralStrut(beamLength, HD)
print(f'Length: {beamLength} ft')
print(f"Max Line Load Load: {int(max_load)} lb/ft")
print(f"Extension Configuration: {extension_config}")
