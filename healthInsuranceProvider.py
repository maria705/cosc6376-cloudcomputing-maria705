import json
import boto3
client = boto3.client('athena')
from openai import OpenAI
import os
import mysql.connector

def healthInsuranceProvider(event, context):
    slots = event['sessionState']['intent']['slots']
    intent = event['sessionState']['intent']['name']
    insuranceProvider = event['sessionState']['intent']['slots']['insuranceProvider']['value']['originalValue']
    print('insuranceProvider', insuranceProvider)
    open_ai_response = json.loads(queryGeneration(insuranceProvider))
    query_value = open_ai_response.get('query')
    print("Query:", query_value)
    query_result = process_rds_query(query_value)
    cont = f" The number of patients for insuranceProvider {insuranceProvider} is {query_result} "
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


def process_rds_query(query_value):
    try:
        # Establish a connection to the RDS instance
        connection = connect_to_rds()
        print('query_value', query_value)
        rds_results = execute_query(connection, query_value)
        print('rds_results', rds_results)
        return rds_results

    except Exception as e:
        return str(e)


def queryGeneration(insuranceProvider):
    client = OpenAI()

    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": '''Given the following SQL tables, your job is to write queries given a user’s request.
create table health_data (
Name text,
Age int,
Gender text,
Blood_Type text,
Medical_Condition text,
Date_of_Admission date,
Doctor text,
Hospital text,
Insurance_Provider text,
Billing_Amount double,
Room_Number int,
Admission_Type text,
Discharge_Date date,
Medication text,
Test_Results text
);'''},
            {"role": "system",
             "content": "You are a helpful assistant designed to output JSON. Let the output be in this format {query:""}"},
            {"role": "user",
             "content": f"Write a SQL query which computes the total number of patiants under this insurance Provider {insuranceProvider} . Please send only the sql query in the response"}
        ]
    )
    print(response)
    # print(response.choices[0].message.content)
    return response.choices[0].message.content


def connect_to_rds():
    print("INSIDE connect_to_rds")
    # Retrieve RDS connection details from environment variables
    rds_host = 'cloud-project-2.cjfmao9x7ji6.us-east-1.rds.amazonaws.com'
    rds_port = 3306
    rds_user = 'admin'
    rds_password = os.environ.get('RDS_PASSWORD')
    rds_database = 'project1'

    # Establish a connection to the RDS instance
    connection = mysql.connector.connect(
        host=rds_host,
        port=rds_port,
        user=rds_user,
        password=rds_password,
        database=rds_database
    )
    print(connection)
    return connection


def execute_query(connection, query):
    try:
        cursor = connection.cursor()

        # Execute the SQL query
        cursor.execute(query)

        # Fetch all rows
        result = cursor.fetchall()
        print(result)
        if 'COUNT' in query:
            cursor.close()
            return result[0][0]

        else:

            # Convert result to a list of dictionaries
            rows = [{'column1': row[0], 'column2': row[1], 'column3': row[2]} for row in result]

            print(rows)
            return rows
        # Close cursor


    except Exception as e:
        raise e

    finally:
        # Close connection
        connection.close()
