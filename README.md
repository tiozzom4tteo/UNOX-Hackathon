# Team1-UNOX-Hackathon

Gang of ++Four+=2

## The Challenge

Use GenAI to develop or improve functionalities and user experience at least one of the following platforms:

- [UNOX Website](https://www.unox.com/it_it/)
- [UNOX DDC - Data Driven Cooking](https://demo.datadrivencooking.com/)
- [UNOX Digital.ID ovens](https://www.unox.com/it_it/app-e-sistema-operativo/app/digitalid/)

## Requirements

To use this project you need to:

- Have AWS credential
- Amazon Bedrock
- Python3 installed
- Pip3 installed

## Configuration

To run this project you need to:

- Download the zip
- Extract the zip and enter the folder
- Remove jq from setup/requirements.txt
- Open window terminal and run this command: 'pip3 install -r setup/requirements.txt'
- Open completed/api/bedrock_api.py and make the following changes:
  - profile_name="default"
  - region_name="us-east-1"
  - endpoint_url → remove row
- Run 'aws configure' and AWS keys
- Try to run 'python completed/api/bedrock_api.py'
