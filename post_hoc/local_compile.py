import pandas as pd
import json
import os


# data dir is where the jsons are stored
# output dir is where we want to put the result
def post_hoc_compile(data_dir, output_dir):
    output_file = os.path.join(output_dir, 'output.csv')

    # Get list of filenames in the directory
    file_list = [f for f in os.listdir(data_dir) if f.endswith('.json')]

    # Initialize an empty DataFrame
    df = pd.DataFrame()

    # Loop through the files
    for filename in file_list:
        with open(os.path.join(data_dir, filename), 'r') as f:
            data = json.load(f)  # Load JSON file
            temp_df = pd.DataFrame(data)  # Convert dictionary to DataFrame
            df = pd.concat([df, temp_df], ignore_index=True)  # Appends all data into a single DataFrame

    df['domain'] = df['link'].apply(lambda x: x[len('https://'):].split('/')[0])

    df = df[['link','domain','platform','source_image_name']]

    # Write the DataFrame to a CSV file
    df.to_csv(output_file, index=False)


if __name__ == '__main__':
    post_hoc_compile('tmp', 'tmp')
