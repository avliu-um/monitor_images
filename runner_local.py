import os
import time
import random
from datetime import datetime

from monitor_images import get_driver, monitor_image


def run_local(platforms: list, input_dir: str, output_dir: str):
    driver = get_driver()

    # Ensure output_dir exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    images_processed = 0

    # Get a list of all files in directory
    all_files = os.listdir(input_dir)
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


if __name__ == '__main__':
    all_platforms = ['google', 'yandex']
    test_input_dir = f'{os.getcwd()}/tmp/qw_images'
    test_output_dir = f'{os.getcwd()}/tmp/qw_out'
    run_local(all_platforms, test_input_dir, test_output_dir)
