import sys
import os
import time
import random
from datetime import datetime

from monitor_images import get_driver, monitor_image


def run_local(input_dir: str, output_dir: str, platforms:list = ['google', 'yandex']):
    print(f'input_dir: {input_dir}')
    print(f'output_dir: {output_dir}')
    print(f'platforms: {platforms}')

    # Ensure output_dir exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    log_filename = os.path.join(output_dir, "debug.log")
    log_file = open(log_filename, "w")
    print(f'log output filename: {log_filename}')
    sys.stdout = log_file

    # Get a list of all files in directory
    all_files = os.listdir(input_dir)
    print(f'identified {len(all_files)} input images to process')

    print('\n\n')

    driver = get_driver()
    images_processed = 0
    for image_filename in all_files:
        for platform in platforms:
            image_filepath = os.path.join(input_dir, image_filename)
            monitor_image(
                platform,
                image_filepath,
                output_dir,
                driver,
                extra_data={
                    'source_image_name': image_filename,
                    'scrape_date': datetime.today().strftime('%Y-%m-%d')
                }
            )
            print()

        images_processed += 1
        print(f'total images processed: {images_processed} / {len(all_files)}')
        time.sleep(random.randint(1, 5))

    log_file.close()


if __name__ == '__main__':
    env_input_dir = os.environ.get('input_dir')
    env_output_dir = os.environ.get('output_dir')

    input_dir = env_input_dir if env_input_dir else os.path.join(os.getcwd(), 'input')
    output_dir = env_output_dir if env_output_dir else os.path.join(os.getcwd(), 'output')

    #test_input_dir = f'{os.getcwd()}/tmp/qw_images'
    #test_output_dir = f'{os.getcwd()}/tmp/qw_out'

    # TODO: Use python logging module
    old_stdout = sys.stdout
    run_local(input_dir, output_dir)
    sys.stdout = old_stdout
