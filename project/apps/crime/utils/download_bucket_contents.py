import boto3
import os
import csv
aak = os.environ.get('CRIME_AWS_ACCESS_KEY')
ask = os.environ.get('CRIME_AWS_SECRET_KEY')
client = boto3.client('s3',aws_access_key_id=aak, aws_secret_access_key=ask)
mine = client.list_objects_v2(Bucket='njsp-crime-reports')
mycsv = mine['Contents']

with open('s3_listing.csv', 'w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=mycsv[0].keys())
    writer.writeheader()
    for row in mycsv:
        writer.writerow(row)