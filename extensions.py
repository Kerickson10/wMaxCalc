import pandas as pd

# Read data from CSV
file_path = "/home/bpeters2/Indeterminate Beam/wMaxCalc/extensions.csv"
df = pd.read_csv(file_path)

# Define the number of joints
num_joints = 4

# Calculate the joint columns
for i in range(1, num_joints + 1):
    ext_col = f'Ext{i}'
    joint_col = f'Joint{i}'
    
    if i == 1:
        df[joint_col] = df['min'] + df[ext_col].fillna(0) * 3.281
    else:
        prev_joint_col = f'Joint{i-1}'
        df[joint_col] = df[prev_joint_col] + df[ext_col].fillna(0) * 3.281

# Round all joint columns to 3 decimals
for i in range(1, num_joints + 1):
    joint_col = f'Joint{i}'
    df[joint_col] = df[joint_col].round(3)

# Save the modified DataFrame back to the same CSV file
df.to_csv(file_path, index=False)

print("CSV file saved successfully.")
