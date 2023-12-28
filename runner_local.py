import sys
import os
import time
import random
import logging
from datetime import datetime

from monitor_images import get_driver, monitor_image
from post_hoc import local_compile


def run_local(input_dir: str, output_dir: str, platforms:list = ['google', 'yandex']):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    log_filename = os.path.join(output_dir, "debug.log")
    logging.basicConfig(level=logging.INFO, filename=log_filename, filemode="a+",
                        format="%(asctime)-15s %(levelname)-8s %(message)s")

    logging.info(f'input_dir: {input_dir}')
    logging.info(f'output_dir: {output_dir}')
    logging.info(f'platforms: {platforms}')

    # Get a list of all files in directory
    all_files = os.listdir(input_dir)
    logging.info(f'identified {len(all_files)} input images to process')

    logging.info('\n\n')

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

        images_processed += 1
        logging.info(f'total images processed: {images_processed} / {len(all_files)}')
        time.sleep(random.randint(1, 5))


if __name__ == '__main__':
    env_input_dir = os.environ.get('input_dir')
    env_output_dir = os.environ.get('output_dir')

    input_dir = env_input_dir if env_input_dir else os.path.join(os.getcwd(), 'input')
    output_dir = env_output_dir if env_output_dir else os.path.join(os.getcwd(), 'output')
    temp_output_dir = os.path.join(output_dir, 'temp')

    run_local(input_dir, temp_output_dir)
    local_compile.post_hoc_compile(temp_output_dir, output_dir)
