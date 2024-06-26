import os
import boto3
import json
import pandas as pd
from datetime import datetime, timedelta

from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def save_s3(bucket_name, prefix, local_output_dir='/tmp'):
    print(f'saving s3 files locally into csv')
    print(f'bucket_name: {bucket_name}')
    print(f'prefix: {prefix}')
    print(f'local output_dir: {local_output_dir}')

    output_filename = f'{bucket_name}-{prefix}.csv'.replace('/','_')
    output_filepath = f'{local_output_dir}/{output_filename}'

    s3 = boto3.client('s3', region_name='us-east-2')  # replace with your preferred region

    files = []

    # list all json files with today's date prefix
    response = s3.list_objects(Bucket=bucket_name, Prefix=prefix)

    print(f'identiied {len(response["Contents"])} files in this bucket with this prefix')

    for s3_file in response['Contents']:
        s3_object_path = s3_file['Key']

        # get the S3 object
        s3_object = s3.get_object(Bucket=bucket_name, Key=s3_object_path)
        s3_object_body = s3_object['Body'].read().decode('utf-8')

        # hacky way to get the date in there, for the runs pre-january that didn't have the scrape_date explicitly
        json_object = json.loads(s3_object_body)
        for item in json_object:
            item['s3_key'] = s3_object_path

        # append all read JSON data to files list
        files += json_object

    # concatenate all data into one DataFrame
    df = pd.concat([pd.json_normalize(file) for file in files])

    # Write CSV to string and encode to bytes
    df.to_csv(output_filepath, index=False)

    return output_filepath


def send_email(subject, body, sender, recipients, filename=None):
    print(f'sending email')
    print(f'sender: {sender}')
    print(f'recipients: {recipients}')
    print(f'filename: {filename}')

    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = sender

    # Set message body
    body = MIMEText(body, "plain")
    msg.attach(body)

    if filename:
        with open(filename, "rb") as attachment:
            part = MIMEApplication(attachment.read())
            part.add_header("Content-Disposition",
                            "attachment",
                            filename=filename)
        msg.attach(part)

    # Convert message to string and send
    ses_client = boto3.client("ses", region_name="us-east-2")
    response = ses_client.send_raw_email(
        Source=sender,
        Destinations=recipients,
        RawMessage={"Data": msg.as_string()}
    )
    print(response)


# TODO: Abstract out to an output s3 bucket and prefix (and label existing bucket and prefix as "raw")
def lambda_handler(event, context):
    try:
        start_time = datetime.now()
        print(f'start time: {start_time}')

        bucket_name = event['bucket']
        local_output_dir = event['local_output_dir'] if 'local_output_dir' in event.keys() else None

        if 'prefix' in event.keys():
            prefix = event['prefix']
            subject = f'monitor images output for prefix {prefix}'
        else:
            yesterday = datetime.today() - timedelta(days=1)
            yesterday_str = yesterday.strftime('%Y-%m-%d')
            prefix = f'raw/{yesterday_str}'
            subject = f'monitor images output for {yesterday_str}'

        output_filepath = save_s3(bucket_name, prefix, local_output_dir)

        sender = "quest2achiever2000@gmail.com"
        recipients = event['recipients']
        body = f'this email was automatically generated'
        send_email(subject, body, sender, recipients, output_filepath)

        end_time = datetime.now()
        print(f'end time: {end_time}')
        print(f'total time: {(end_time - start_time).total_seconds()} seconds')

        return {
            'statusCode': 200,
            'body': json.dumps('success')
        }

    except Exception as e:
        return {
            'status': 'Failed',
            'message': str(e)
        }


if __name__ == '__main__':
    event = {
        'bucket': 'qa-monitor-images',
        'prefix': 'raw/2024-04-06',
        'local_output_dir': os.getcwd()+'/tmp',
        'recipients': []
    }
    response = lambda_handler(event, None)
    print(response)
