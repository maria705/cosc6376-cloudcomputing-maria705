Project Name: Chat2Query
Overview
This project integrates Amazon Lex, a conversational interface for chatbots, with AWS Lambda functions to create a robust healthcare-oriented conversational system. The project includes predefined intents for health insurance providers, hospital patient satisfaction, patient diagnosis, and treatment categories.

Setup Instructions
1. Lex Chatbot Configuration
    Download the provided Lex chatbot configuration zip file from the repository.

    Upload the zip file to an S3 bucket.

    In the Lex console, use the "Import" feature to import the configurations from the uploaded zip file. This will create the necessary intents and configurations for the healthcare chatbot.

2: OPEN AI Account Setup:
    Create a new access key in the Open AI account and use that token to make open AI API calls to generate the SQL queries.

3: You need to create an rds cluster and Athena tables for the CSV dataset provided and need to pass its connection values accordingly to connect to rds and Athena.

4. Lambda Local Testing:
    Ensure you have Python 3.8 or above installed on your local machine.

    Install required Python packages:

    pip install boto3
    pip install openai
    pip install mysql.connector
    Test the Lambda code locally by passing a sample event which is provided in the file (sample_event.json). Execute the lambda_function.py file and pass the event provided in sample_event.json as a sample input.

5. AWS Lambda Deployment
    Zip the Lambda code files.

    Upload the zip file to AWS Lambda.

    Create a new Lambda function and associate the uploaded zip file.

    Lambda Layer
    Create a Lambda Layer containing all required dependencies (boto3, openai, mysql.connector).

    Attach this layer to the Lambda function created above.

Usage :
Once both Lex, Open AI, rds, and Athena Lambda, are set up, the chatbot is ready to use. Users can interact with the healthcare chatbot through the configured Lex interface, and Lambda functions will process the intents and provide appropriate responses.

Contributors :
Maria Ann Toms
Arti Patel
Aishwarya Chitrakumar
