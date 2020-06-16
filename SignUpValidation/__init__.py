import logging
import json
import azure.functions as func
import os
import base64

def main(req: func.HttpRequest) -> func.HttpResponse:  # API version
    API_VERSION = "0.0.1"

    logging.info(
        f"Python HTTP trigger function processed a request, API version: {API_VERSION}")

    # Allowed domains
    allowed_domains = ["fabrikam.com", "fabricam.com"]

    # Check HTTP basic authorization
    if not authorize(req):
        logging.info("HTTP basic authentication validation failed.")
        return func.HttpResponse(status_code=401)

    # Get the request body
    try:
        req_body = req.get_json()
    except:
        return func.HttpResponse(
            json.dumps({"version": API_VERSION, "action": "ShowBlockPage",
                        "code": "SignUp-Validation-01", "userMessage": "There was a problem with your request."}),
            status_code=200,
            mimetype="application/json"
        )

    # Print out the request body
    logging.info(f"Request body: {req_body}")

    # Get the current user language
    language = req_body.get('ui_locales') if 'ui_locales' in req_body and req_body.get(
        'ui_locales') else "default"
    logging.info(f"Current language: {language}")

    # If email claim not found, show block page. Email is required and sent by default.
    if 'email' not in req_body or not req_body.get('email') or "@" not in req_body.get('email'):
        return func.HttpResponse(
            json.dumps({"version": API_VERSION, "action": "ShowBlockPage",
                        "code": "SignUp-Validation-02", "userMessage": "Email is mandatory."}),
            status_code=200,
            mimetype="application/json"
        )

    # Get domain of email address
    domain = req_body.get('email').split('@')[1]
    logging.info(f"Current doamin: {domain}")

    # Check the domain in the allowed list
    if domain.lower() not in allowed_domains:
        s = ", "
        return func.HttpResponse(
            json.dumps({"version": API_VERSION, "action": "ShowBlockPage", "code": "SignUp-Validation-03",
                        "userMessage": f"You must have an account from '{s.join(allowed_domains)}' to register as an external user for Contoso."}),
            status_code=200,
            mimetype="application/json"
        )

    # If jobTitle claim is too short, show validation error message so that user can fix error.
    if ('jobTitle' in req_body and req_body.get('jobTitle')):  # use 'if not' (...) to require Job Title
        if len(req_body.get('jobTitle')) < 5:
            return func.HttpResponse(
                json.dumps({"version": API_VERSION, "status": 400, "action": "ValidationError",
                            "code": "SignUp-Validation-04", "userMessage": "Job Title must contain at least five characters."}),
                status_code=400,
                mimetype="application/json"
            )

    # Input validation passed successfully, return `Allow` response.
    return func.HttpResponse(
        json.dumps({"version": API_VERSION, "action": "Continue"}),
        status_code=200,
        mimetype="application/json"
    )

def authorize(req: func.HttpRequest):

    # Get the environment's credentials 
    username = os.environ["BASIC_AUTH_USERNAME"]
    password = os.environ["BASIC_AUTH_PASSWORD"]

    # Returns authorized if the username is empty or not exists.
    if not username:
        logging.info("HTTP basic authentication is not set.")
        return True

    # Check if the HTTP Authorization header exist
    if not req.headers.get("Authorization"):
        logging.info("Missing HTTP basic authentication header.")
        return False 

    # Read the authorization header
    auth = req.headers.get("Authorization")

    # Ensure the type of the authorization header id `Basic`
    if  "Basic " not in auth:
        logging.info("HTTP basic authentication header must start with 'Basic '.")
        return False  

    # Get the HTTP basic authorization credentials
    auth = auth[6:]
    authBytes = base64.b64decode(auth)
    auth  = authBytes.decode("utf-8")
    cred = auth.split(':')

    # Evaluate the credentials and return the result
    return (cred[0] == username and cred[1] == password)
