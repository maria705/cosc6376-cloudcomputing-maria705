import json
from healthInsuranceProvider import healthInsuranceProvider
from hospital_patient_satisfaction import hospitalPatientSatisfaction
from diagnosis import PatientDiagnosis
from treatment import treatmentCategory

def lambda_handler(event, context):
    print("event==>", event)
    print("It is from codehook")
    slots = event['sessionState']['intent']['slots']
    intent = event['sessionState']['intent']['name']

    if intent == 'healthInsuranceProvider':
        return healthInsuranceProvider(event, context)
    elif intent == 'hospital_patient_satisfaction':
        print(event)
        return hospitalPatientSatisfaction(event, context)
    elif intent == 'DiagnosisCategory':
        print(event)
        return PatientDiagnosis(event, context)
    elif intent == 'Treatment_Category':
        print(event)
        return treatmentCategory(event, context)

# lambda_handler(event, '')