# UNOX-Hackathon

## The Challenge

Use GenAI to develop or improve functionalities and user experience in at least one of the following platforms:

- [UNOX Website](https://www.unox.com/it_it/)
- [UNOX DDC - Data Driven Cooking](https://demo.datadrivencooking.com/)
- [UNOX Digital.ID ovens](https://www.unox.com/it_it/app-e-sistema-operativo/app/digitalid/)

## What

It's a project developed by Davide Donanzan, Orlando Ferazzani, Nicolò Pellegrinelli, Filippo Rizzolo, Tommaso Terrin, Matteo Tiozzo and Matteo Tonello as part of UNOX S.p.A.'s 24h Hackathon challenge. A(ssistant) C(hatbot) E(xperience) has two main functionalities: it helps customers chosing the oven that suits them best from the context and gives assistance on their model of oven. The chatbot uses GenAI to generate SQL queries from natural language queries. Once generated, the query is executed on a database and the results are reconverted to natural language.

## Requirements

To use this project you need:

- AWS credential and Amazon Bedrock
- Python3
- Pip3

## Configuration

To run this project you need to:

- Remove jq from setup/requirements.txt
- Run: `pip3 install -r setup/requirements.txt`
- Run `aws configure` and enter AWS keys
- Go to [ACE_chatbot](ACE_chatbot) folder
- Run `streamlit run ACE_app.py --server.port 8080`
- If necessary change `credentials_profile_name` and `region_name` in [ACE_lib.py](ACE_chatbot/ACE_lib.py)
