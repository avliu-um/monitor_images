import os
import boto3
from datetime import datetime

from monitor_images import get_driver, monitor_image


# Note that this function does NOT run any AWS batch but rather just grabs files from and writes results to AWS
def run(platforms: list, input_s3_bucket: str, input_s3_filenames: list, output_s3_bucket: str):
    s3_client = boto3.client('s3')
    driver = get_driver()

    os.makedirs('tmp', exist_ok=True)
    local_image_filename = f'{os.getcwd()}/tmp/image.jpg'
    local_output_dir = 'tmp'

    images_processed = 1
    for input_s3_filename in input_s3_filenames:
        print(f'processing {images_processed} / {len(input_s3_filenames)} images')

        if os.path.isfile(local_image_filename):
            os.remove(local_image_filename)
        s3_client.download_file(input_s3_bucket, input_s3_filename, local_image_filename)

        for platform in platforms:
            print(f''
                  f'platform: {platform}, '
                  f'input s3 bucket name: {input_s3_bucket}, '
                  f'input s3 image filename: {input_s3_filename}, '
                  f'output s3 bucket name: {output_s3_bucket}, '
                  )

            # Search the image
            success, output_filename = monitor_image(
                platform,
                local_image_filename,
                local_output_dir,
                driver,
                extra_data={
                    'search_s3_bucket': input_s3_bucket,
                    'search_s3_image_filename': input_s3_filename,
                    'scrape_date': datetime.today().strftime('%Y-%m-%d')
                }
            )

            # Prepare S3 path with current date
            today = datetime.strftime(datetime.now(), "%Y-%m-%d")
            output_s3_filename_base = input_s3_filename.split(".")[0].split("/")[-1]
            if success:
                output_s3_filename = f'raw/{today}/{platform}/{output_s3_filename_base}_links.csv'
                s3_client.upload_file(output_filename, output_s3_bucket, output_s3_filename)
            else:
                output_s3_filename = f'errors/{output_s3_filename_base}.html'
                s3_client.upload_file(output_filename, output_s3_bucket, output_s3_filename)

            print(f'output s3 filename: {output_s3_filename}')

        images_processed += 1

def main():
    platforms = ['google', 'yandex']
    #input_s3_bucket = os.getenv('input_s3_bucket')
    #input_s3_prefix = os.getenv('input_s3_prefix')
    #input_s3_files = os.getenv('input_s3_files')
    #output_s3_bucket = os.getenv('output_s3_bucket')
    input_s3_bucket = 'qa-monitor-images'
    input_s3_prefix = 'all_all'
    input_s3_files = None
    output_s3_bucket = 'qa-monitor-images'

    if input_s3_files is None:
        input_s3_files = []
        s3_client = boto3.client('s3')
        paginator = s3_client.get_paginator('list_objects')
        for result in paginator.paginate(Bucket=input_s3_bucket, Prefix=input_s3_prefix):
            for file in result['Contents']:
                s3_image_filename = file['Key']
                input_s3_files.append(s3_image_filename)
    else:
        input_s3_files = input_s3_files.split(',')

    run(platforms, input_s3_bucket, input_s3_files, output_s3_bucket)


if __name__ == "__main__":
    main()
