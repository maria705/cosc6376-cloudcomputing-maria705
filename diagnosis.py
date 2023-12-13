import json
import boto3
import time
from openai import OpenAI
athena_client = boto3.client('athena')
import json


def PatientDiagnosis(event, context):
    slots = event['sessionState']['intent']['slots']
    intent = event['sessionState']['intent']['name']
    category = event['sessionState']['intent']['slots']['Diagnosis']['value']['originalValue']
    age = event['sessionState']['intent']['slots']['ageSpan']['value']['originalValue']

    print("slots", slots)

    print('intent', intent)
    open_ai_response = json.loads(queryGeneration(age, category))
    query_value = open_ai_response.get('query')
    print("Query:", query_value)
    database = 'cloud_project'
    workgroup = 'primary'
    table_name = 'diagnosis'
    results_bucket = 'cloud-project-bucket-maria'
    query_result = athena_query(query_value, database, results_bucket)
    print("query_result", query_result)
    cont = f" The number of patients daignosed with the {category} disease of age span {age} is {query_result} "
    print(cont)
    return {
        "sessionState": {
            "dialogAction": {
                "type": "Close",
            },
            "intent": {
                "name": "getQuery",
                "state": "Fulfilled"
            }
        },
        "messages": [
            {
                "contentType": "PlainText",
                "content": cont
            }
        ]
    }


def athena_query(query, database, results_bucket):
    response = athena_client.start_query_execution(
        QueryString=query,
        QueryExecutionContext={
            'Database': database
        },
        ResultConfiguration={
            'OutputLocation': 's3://' + results_bucket
        }
    )
    query_execution_id = response["QueryExecutionId"]
    print('query_execution_id', query_execution_id)
    time.sleep(4)
    results = athena_client.get_query_results(QueryExecutionId=query_execution_id)
    print("results", results)
    output = results['ResultSet']['Rows'][1]['Data'][0]['VarCharValue']
    return output


def queryGeneration(age, category):
    client = OpenAI()

    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": '''Given the following SQL tables, your job is to write queries given a user’s request.
CREATE TABLE diagnosis (
    reference_id STRING,
    report_year BIGINT,
    diagnosis_category STRING,
    diagnosis_sub_category STRING,
    treatment_category STRING,
    treatment_sub_category STRING,
    determination STRING,
    type STRING,
    age_range STRING,
    patient_gender STRING,
    findings STRING
);'''},
            {"role": "system",
             "content": "You are a helpful assistant designed to output JSON. Let the output be in this format {query:""}"},
            {"role": "user",
             "content": f"Write a SQL query to nnumber of patiants diagnosed with a particular catogory {category} of an age span {age}. Please send only the sql query in the response"}
        ]
    )
    print(response)
    return response.choices[0].message.content
