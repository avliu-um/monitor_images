import csv
import os
import boto3
from datetime import datetime
from monitor_images import get_driver, get_google, get_yandex  # Importing the needed function from your module.


def run():
    s3_bucket_name = os.getenv('s3_bucket_name')
    s3_client = boto3.client('s3')

    paginator = s3_client.get_paginator('list_objects')
    for result in paginator.paginate(Bucket=s3_bucket_name, Prefix='images'):
        for file in result['Contents']:
            file_name = file['Key']

            # Download the file
            s3_client.download_file(s3_bucket_name, file_name, "photo.jpg")

            for platform, rmi_function in [('google',get_google), ('yandex',get_yandex)]:
                # Process the file
                driver = get_driver()
                links = rmi_function(driver, "photo.jpg")

                # Prepare S3 path with current date
                today = datetime.today()
                s3_output_path = f"links/{today.isoformat()}/{platform}links.csv"

                # Write output_links to a local CSV file
                with open('output_links.csv', 'w') as file:
                    writer = csv.writer(file)
                    for row in links:
                        writer.writerow([row])

                # Upload output file to s3
                s3_client.upload_file('output_links.csv', s3_bucket_name, s3_output_path)

            # Delete the file
            os.remove("photo.jpg")


if __name__ == "__main__":
    run()
