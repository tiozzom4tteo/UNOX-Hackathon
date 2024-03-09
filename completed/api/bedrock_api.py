import os
import json
import boto3

#
session = boto3.Session(
    profile_name=os.environ.get("default")
)  # sets the profile name to use for AWS credentials

bedrock = session.client(
    service_name='bedrock-runtime',  # creates a Bedrock client
    region_name='us-east-1',
)

#
bedrock_model_id = "ai21.j2-ultra-v1"  # set the foundation model

# the prompt to send to the model
prompt = "What is the largest city in New Hampshire?"

body = json.dumps({
    "prompt": prompt,  # AI21
    "maxTokens": 1024,
    "temperature": 0,
    "topP": 0.5,
    "stopSequences": [],
    "countPenalty": {"scale": 0},
    "presencePenalty": {"scale": 0},
    "frequencyPenalty": {"scale": 0}
})  # build the request payload

#
response = bedrock.invoke_model(body=body, modelId=bedrock_model_id, accept='application/json',
                                contentType='application/json')  # send the payload to Bedrock

#
response_body = json.loads(response.get('body').read())  # read the response

response_text = response_body.get("completions")[0].get(
    "data").get("text")  # extract the text from the JSON response

print(response_text)