import boto3
import json
import pandas as pd
from datetime import datetime, timedelta

from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def save_s3(bucket_name, prefix, output_dir='/tmp'):
    print(f'bucket_name: {bucket_name}')
    print(f'prefix: {prefix}')

    output_filename = f'{bucket_name}-{prefix}.csv'.replace('/','_')
    output_filepath = f'{output_dir}/{output_filename}'

    s3 = boto3.client('s3', region_name='us-east-2')  # replace with your preferred region

    files = []

    # list all json files with today's date prefix
    response = s3.list_objects(Bucket=bucket_name, Prefix=prefix)

    for s3_file in response['Contents']:
        s3_object_path = s3_file['Key']

        # get the S3 object
        s3_object = s3.get_object(Bucket=bucket_name, Key=s3_object_path)
        s3_object_body = s3_object['Body'].read().decode('utf-8')

        # append all read JSON data to files list
        files += json.loads(s3_object_body)

    # concatenate all data into one DataFrame
    df = pd.concat([pd.json_normalize(file) for file in files])

    # Write CSV to string and encode to bytes
    df.to_csv(output_filepath, index=False)

    return output_filepath


def send_email(subject, body, sender, recipients, filename=None):
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


def lambda_handler(event, context):
    try:
        start_time = datetime.now()
        print(f'start time: {start_time}')

        # TODO
        #bucket = event['bucket']
        #recipients = event['recipients']

        yesterday = datetime.today() - timedelta(days=1)
        yesterday_str = yesterday.strftime('%Y-%m-%d')

        bucket_name = 'test-monitor-images'
        prefix = f'raw/{yesterday_str}'
        output_filepath = save_s3(bucket_name, prefix)
        subject = f'monitor images output {yesterday_str}'
        body = f'this is the resulting dataset for the data scraped on {yesterday_str}'

        sender = "quest2achiever2000@gmail.com"
        recipients = ['quest2achiever2000@gmail.com', 'avliu@umich.edu']

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
    response = lambda_handler(None, None)
    print(response)
