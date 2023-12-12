import os
import traceback
import boto3
import json
from datetime import datetime

from monitor_images import get_driver, monitor_images

from selenium.common import WebDriverException

def run(platforms: list, input_s3_bucket: str, input_s3_filenames: list, output_s3_bucket: str):
    os.makedirs('tmp', exist_ok=True)
    s3_client = boto3.client('s3')
    driver = get_driver()

    local_image_filename = f'{os.getcwd()}/tmp/image.jpg'
    local_output_filename = 'tmp/output.json'
    local_error_output_filename = 'tmp/error.html'

    for input_s3_filename in input_s3_filenames:
        if os.path.isfile(local_image_filename):
            os.remove(local_image_filename)
        s3_client.download_file(input_s3_bucket, input_s3_filename, local_image_filename)

        for platform in platforms:
            # Prepare S3 path with current date
            today = datetime.strftime(datetime.now(), "%Y-%m-%d")
            output_s3_filename = f'raw/{today}/{platform}_{input_s3_filename.split(".")[0].split("/")[-1]}_links.csv'
            error_output_s3_filename = f'errors/{output_s3_filename}'

            print(f''
                  f'platform: {platform}, '
                  f'input s3 bucket name: {input_s3_bucket}, '
                  f'input s3 image filename: {input_s3_filename}, '
                  f'output s3 bucket name: {output_s3_bucket}, '
                  f'output s3 filename: {output_s3_filename}'
                  )

            try:
                links = monitor_images(platform, local_image_filename, driver)

                data = []
                for link in links:
                    data.append({
                        'link': link,
                        'platform': platform,
                        'search_bucket': input_s3_bucket,
                        'search_image_filename': input_s3_filename
                    })
                with open(local_output_filename, 'w') as fp:
                    json.dump(data, fp, indent=4, separators=(',', ': '))

                # Upload output file to s3
                s3_client.upload_file(local_output_filename, output_s3_bucket, output_s3_filename)

            except WebDriverException as e:
                print(f'selenium error! ')
                print(str(e))
                print('stack trace:')
                traceback.print_exc()

                print(f'writing error file to {error_output_s3_filename}')
                with open(local_error_output_filename, "w", encoding='utf-8') as f:
                    f.write(driver.page_source)
                s3_client.upload_file(local_error_output_filename, output_s3_bucket, error_output_s3_filename)

            print()


def main():
    platforms = ['google', 'yandex']
    input_s3_bucket = os.getenv('input_s3_bucket')
    input_s3_files = os.getenv('input_s3_files')
    output_s3_bucket = os.getenv('output_s3_bucket')

    if input_s3_files is None:
        input_s3_files = []
        s3_client = boto3.client('s3')
        paginator = s3_client.get_paginator('list_objects')
        for result in paginator.paginate(Bucket=input_s3_bucket, Prefix='images'):
            for file in result['Contents']:
                s3_image_filename = file['Key']
                input_s3_files.append(s3_image_filename)
    else:
        input_s3_files = input_s3_files.split(',')

    run(platforms, input_s3_bucket, input_s3_files, output_s3_bucket)


if __name__ == "__main__":
    main()
