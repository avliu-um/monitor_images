import csv
import os
import boto3
import json
from datetime import datetime
from monitor_images import get_driver, get_google, get_yandex  # Importing the needed function from your module.


def run(params_list: list):
    s3_client = boto3.client('s3')

    driver = get_driver()
    old_s3_bucket_name = ''
    s3_old_image_filename = ''

    local_image_filename = 'image.jpg'
    local_output_filename = 'output.json'

    for params in params_list:
        platform = params['platform']
        s3_bucket_name = params['s3_bucket_name']
        s3_image_filename = params['s3_image_filename']

        # doanload file locally
        if s3_image_filename != s3_old_image_filename or s3_bucket_name != old_s3_bucket_name:
            os.remove(local_image_filename)
            s3_client.download_file(s3_bucket_name, s3_image_filename, local_image_filename)

        if platform == 'google':
            links = get_google(driver, local_image_filename)
        elif platform == 'yandex':
            links = get_yandex(driver, local_image_filename)
        else:
            print('crying')

        data = []
        for link in links:
            data.append({
                'link': link,
                'platform': platform,
                'search_bucket': s3_bucket_name,
                'search_image_filename': s3_image_filename
            })
        with open(local_output_filename, 'w') as fp:
            json.dump(data, fp, indent=4, separators=(',', ': '))

        # Prepare S3 path with current date
        today = datetime.today()
        s3_output_path = f'raw/{today.isoformat()}/{platform}_{s3_image_filename.split("/")[-1]}_links.csv'
        # Upload output file to s3
        s3_client.upload_file(local_output_filename, s3_bucket_name, s3_output_path)


def main():
    s3_bucket_name = os.getenv('s3_bucket_name')
    s3_client = boto3.client('s3')

    params = []

    paginator = s3_client.get_paginator('list_objects')
    for result in paginator.paginate(Bucket=s3_bucket_name, Prefix='images'):
        for file in result['Contents']:
            s3_image_filename = file['Key']

            for platform in ['google', 'yandex']:
                params.append({
                    'platform': platform,
                    's3_bucket_name': s3_bucket_name,
                    's3_image_filename': s3_image_filename
                })

    run(params)



if __name__ == "__main__":
    main()
