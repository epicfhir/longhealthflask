from flask import Flask, request, redirect
import requests

app = Flask(__name__)

# Replace these values with your actual client information
CLIENT_ID = '19f2216b-cfd4-4d57-bbc3-7068d1a66da5'
# CLIENT_ID = '7d8eb900-8f2c-4683-901d-4e84bc7971b3'
REDIRECT_URI = 'http://localhost:5000/redirect'
EHR_LAUNCH_URL = 'https://app.com/launch'


@app.route('/')
def home():
    # Redirect the user to the EHR launch URL
    return redirect(EHR_LAUNCH_URL)


@app.route('/callback')
def callback():
    # Retrieve parameters from the callback URL
    iss = request.args.get('iss')
    launch = request.args.get('launch')
    # Make an authorization request to retrieve an access token
    authorization_url = 'https://vendorservices.epic.com/interconnect-amcurprd-oauth/oauth2/authorize'
    token_url = 'https://vendorservices.epic.com/interconnect-amcurprd-oauth/oauth2/token'

    redirect_uri = 'http://localhost:5000/redirect'  # Adjust based on your actual redirect URI
    client_id = CLIENT_ID
    scope = 'launch openid fhirUser'  # 'launch/patient patient/*.read launch openid fhirUser'  # Add additional scopes as needed

    authorization_params = {
        'client_id': client_id,
        'scope': scope,
        'response_type': 'code',
        'redirect_uri': redirect_uri,
        'state': 'example-state-value-should-fail',
        'code_challenge_method': 'S256',
        'code_challenge': 'PHHQCoInTVWPbe78fWbQSftF5f6nn7hgskfLfEm4L6s',
        # 'aud': iss,  # Use the iss value from the launch request
        # 'launch': launch  # Use the launch value from the launch request
        # 'launch': 'e0yyMZa5aqjpDhvmIODSJgw3'  # Use the launch value from the launch request
    }

    # Redirect the user to the authorization URL
    authorization_response = requests.get(authorization_url, params=authorization_params)
    return redirect(authorization_response.url)


@app.route('/redirect')
def redirect_take():
    print("Return Method called")
    code = request.args.get('code')

    # Validate the iss, launch, and code parameters (implement your validation logic)

    # Exchange the authorization code for an access token
    token_url = 'https://vendorservices.epic.com/interconnect-amcurprd-oauth/oauth2/token'

    token_params = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
    }
    print("printing code:- ")
    print(code)
    token_response = requests.post(token_url, data=token_params)

    if token_response.status_code == 200:
        # Access token retrieved successfully
        access_token = token_response.json().get('access_token')
        patient = token_response.json().get('patient')
        print("Printing Access Token:- ")
        print(access_token)
        token_data = token_response.json()
        url = f"https://vendorservices.epic.com/interconnect-amcurprd-oauth/api/FHIR/R4/Patient/{patient}"


        payload = {}
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json',
            'Cookie': 'EpicPersistenceCookie=!OrJR/H1Fbazz26TDnBaZuGaSv3+6GKjFSuR+wbear0Klry34om1Pi85rE1I3Cld/8X1pBXSfNC/lRo0=; MyChartLocale=en-US'
        }
        response = requests.request("GET", url, headers=headers, data=payload)


        # Now you can use the access token to make requests to the EHR's FHIR API or perform other actions
        return response.json()

    else:
    # Handle token retrieval failure
        return 'Failed to retrieve access token'

if __name__ == '__main__':
    app.run(debug=True)
