import pandas as pd
import json
import os

output_dir = 'tmp'
output_file = os.path.join(output_dir, 'out.csv')

# Get list of filenames in the directory
file_list = [f for f in os.listdir(output_dir) if f.endswith('.json')]

# Initialize an empty DataFrame
df = pd.DataFrame()

# Loop through the files
for filename in file_list:
    with open(os.path.join(output_dir,filename), 'r') as f:
        data = json.load(f)  # Load JSON file
        temp_df = pd.DataFrame(data)  # Convert dictionary to DataFrame
        df = pd.concat([df, temp_df], ignore_index=True)  # Appends all data into a single DataFrame

df['domain'] = df['link'].apply(lambda x: x[len('https://'):].split('/')[0])

df = df[['link','domain','platform','source_image_name']]

# Write the DataFrame to a CSV file
df.to_csv(out_file, index=False)