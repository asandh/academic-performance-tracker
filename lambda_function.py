import json
import boto3
import os
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
sqs = boto3.client('sqs')

study_table = dynamodb.Table('StudySessions')
grade_table = dynamodb.Table('Grades')

QUEUE_URL = os.environ.get("QUEUE_URL")


def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


def lambda_handler(event, context):
    method = event["httpMethod"]
    path = event["resource"]
    body = json.loads(event.get("body") or "{}")

    # POST /study-session
    if path == "/study-session" and method == "POST":
        study_table.put_item(Item=body)
        return {
            "statusCode": 200,
            "body": json.dumps("Study session added")
        }

    # POST /grade
    if path == "/grade" and method == "POST":
        grade_table.put_item(Item=body)
        return {
            "statusCode": 200,
            "body": json.dumps("Grade added")
        }

    # POST /reminder
    if path == "/reminder" and method == "POST":
        sqs.send_message(
            QueueUrl=QUEUE_URL,
            MessageBody=json.dumps(body)
        )
        return {
            "statusCode": 200,
            "body": json.dumps("Reminder sent")
        }

    # GET /summary
    if path == "/summary" and method == "GET":
        study = study_table.scan()["Items"]
        grades = grade_table.scan()["Items"]

        return {
            "statusCode": 200,
            "body": json.dumps({
                "studySessions": study,
                "grades": grades
            }, default=decimal_default)
        }

    return {
        "statusCode": 400,
        "body": json.dumps("Invalid request")
    }
