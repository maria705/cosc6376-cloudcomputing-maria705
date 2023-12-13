import json
import boto3
import time
athena_client = boto3.client('athena')
import json
from openai import OpenAI


def hospitalPatientSatisfaction(event, context):
    slots = event['sessionState']['intent']['slots']
    intent = event['sessionState']['intent']['name']
    city = event['sessionState']['intent']['slots']['city']['value']['originalValue'].upper()

    print("slots", slots)

    print('intent', intent)
    print('insuranceProvider', city)
    open_ai_response = json.loads(queryGeneration(city))
    query_value = open_ai_response.get('query')
    database = 'cloud_project'
    workgroup = 'primary'
    table_name = 'hospital_patient_satisfaction'
    results_bucket = 'cloud-project-bucket-maria'
    query_result = athena_query(query_value, database, results_bucket)
    new_content = "\n".join([f"{i + 1}: {hospital}" for i, hospital in enumerate(query_result)])


    print("query_result", query_result)
    cont = f" The list of hospitals  with star rating in {city} is {new_content} "
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
    # Extract VarCharValue into an array
    varchar_values = [row["Data"][0]["VarCharValue"] for row in results["ResultSet"]["Rows"]]
    varchar_values = varchar_values[1:]
    
    # Print the updated array
    print('varchar_values', varchar_values)

    return varchar_values


def queryGeneration(city):
    client = OpenAI()

    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": '''Given the following SQL tables, your job is to write queries given a user’s request.
CREATE TABLE hospital_patient_satisfaction (
    facility_id STRING,
    facility_name STRING,
    address STRING,
    city STRING,
    state STRING,
    zip_code INT,
    county_name STRING,
    phone_number STRING,
    hcahps_measure_id STRING,
    hcahps_question STRING,
    hcahps_answer_description STRING,
    patient_survey_star_rating STRING,
    patient_survey_star_rating_footnote STRING,
    hcahps_answer_percent STRING,
    hcahps_answer_percent_footnote STRING,
    hcahps_linear_mean_value STRING,
    number_of_completed_surveys STRING,
    number_of_completed_surveys_footnote STRING,
    survey_response_rate_percent STRING,
    survey_response_rate_percent_footnote STRING,
    start_date DATE,
    end_date DATE,
    year STRING,
    hospital_type STRING,
    hospital_ownership STRING,
    emergency_services STRING,
    meets_criteria_for_promoting_interoperability_of_ehrs STRING,
    hospital_overall_rating STRING,
    hospital_overall_rating_footnote INT,
    mortality_national_comparison STRING,
    mortality_national_comparison_footnote INT,
    safety_of_care_national_comparison STRING,
    safety_of_care_national_comparison_footnote INT,
    readmission_national_comparison STRING,
    readmission_national_comparison_footnote INT,
    patient_experience_national_comparison STRING,
    patient_experience_national_comparison_footnote STRING,
    effectiveness_of_care_national_comparison STRING,
    effectiveness_of_care_national_comparison_footnote STRING,
    timeliness_of_care_national_comparison STRING,
    timeliness_of_care_national_comparison_footnote STRING,
    efficient_use_of_medical_imaging_national_comparison STRING,
    efficient_use_of_medical_imaging_national_comparison_footnote STRING
);'''},
            {"role": "system",
             "content": "You are a helpful assistant designed to output JSON. Let the output be in this format {query:""}"},
            {"role": "user",
             "content": f"Write a SQL query which computes the list of hospitals in a city {city} where rating is best. Please send only the sql query in the response"}
        ]
    )
    print(response)
    # print(response.choices[0].message.content)
    return response.choices[0].message.content