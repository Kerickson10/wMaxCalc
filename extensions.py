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
    
    # If the Ext{i} is empty, set Joint{i} to None
    df.loc[df[ext_col].isna(), joint_col] = None

# Round all joint columns to 3 decimals where they are not None
for i in range(1, num_joints + 1):
    joint_col = f'Joint{i}'
    df[joint_col] = df[joint_col].apply(lambda x: round(x, 3) if pd.notna(x) else x)

# Calculate the joint capacity columns
for i in range(1, num_joints + 1):
    ext_col = f'Ext{i}'
    joint_cap_col = f'JointCap{i}'
    
    df[joint_cap_col] = df[ext_col].apply(lambda x: 680000 if x in [9, 12] else (493000 if pd.notna(x) else None))

# Calculate the extension capacity columns
for i in range(1, num_joints + 1):
    ext_col = f'Ext{i}'
    ext_cap_pos_col = f'ExtCapPositive{i}'
    ext_cap_neg_col = f'ExtCapNegative{i}'
    
    df[ext_cap_pos_col] = df[ext_col].apply(lambda x: 1281000 if x == 12 else (908000 if x == 9 else (654000 if pd.notna(x) else None)))
    df[ext_cap_neg_col] = df[ext_col].apply(lambda x: -1089000 if x == 12 else (-666000 if x == 9 else (-580000 if pd.notna(x) else None)))

# Save the modified DataFrame back to the same CSV file
df = df.drop('Joint1', axis=1)
df = df.drop('Joint2', axis=1)
df = df.drop('Joint3', axis=1)
df = df.drop('Joint4', axis=1)

df = df.round(2)
df.to_csv(file_path, index=False)

print("CSV file saved successfully.")
