import os
from monitor_images import get_driver, monitor_image


def run_local(platforms: list, input_dir: str, output_dir: str):
    driver = get_driver()

    # Ensure output_dir exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Get a list of all files in directory
    for image_filename in os.listdir(input_dir):
        for platform in platforms:
            image_filepath = os.path.join(input_dir, image_filename)
            monitor_image(
                platform,
                image_filepath,
                output_dir,
                driver,
                extra_data={'query_type': 'local'}
            )
            print()


if __name__ == '__main__':
    all_platforms = ['google', 'yandex']
    test_input_dir = f'{os.getcwd()}/images'
    test_output_dir = f'{os.getcwd()}/tmp'
    run_local(all_platforms, test_input_dir, test_output_dir)
