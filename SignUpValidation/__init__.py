import logging
import json
import azure.functions as func
import os
import base64

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request v1.0.')

    # Allowed domains
    allowedDomain = ["fabrikam.com" ,"contoso.com"];

    # Check HTTP basic authorization
    if not authorize(req):
        logging.info("HTTP basic authentication validation failed.")
        return func.HttpResponse(status_code=401)

    # Get the request body
    try:
        req_body = req.get_json()
    except:
        return func.HttpResponse(
            json.dumps({"version": "1.0.0", "status": 200, "action": "ShowBlockPage", "code": "SingUp-Validation-01", "userMessage": "Invalid input data."}),
            status_code=200,
            mimetype="application/json"
         )

    # Print out the request body
    logging.info(f"Request body: {req_body}")

    # Get the current user language
    language = req_body.get('ui_locales') if 'ui_locales' in req_body and req_body.get('ui_locales') else "default" 
    logging.info(f"Current language: {language}")

    # If email claim not found, show validation error message. So, user can fix the input data
    if 'email' not in req_body or not req_body.get('email') or "@" not in req_body.get('email'):
        return func.HttpResponse(
            json.dumps({"version": "1.0.0", "status": 200, "action": "ShowBlockPage", "code": "SingUp-Validation-02", "userMessage": "Email is mandatory."}),
            status_code=200,
            mimetype="application/json"
        )

    # Get domain of email address
    domain = req_body.get('email').split('@')[1]
    logging.info(f"Current doamin: {domain}")

    # Check the domain in the allowed list
    if domain not in allowedDomain:
        s = ", "
        return func.HttpResponse(
            json.dumps({"version": "1.0.0", "status": 200, "action": "ShowBlockPage", "code": "SingUp-Validation-02", "userMessage": f"You must have an account from '{s.join(allowedDomain)}' to register as an external user for Contoso."}),
            status_code=200,
            mimetype="application/json"
        )

    # If jobTitle claim not found, show validation error message. So, user can fix the input data
    if 'jobTitle' not in req_body or not req_body.get('jobTitle'):
        return func.HttpResponse(
            json.dumps({"version": "1.0.0", "status": 200, "action": "ShowBlockPage", "code": "SingUp-Validation-02", "userMessage": "Display name is mandatory."}),
            status_code=200,
            mimetype="application/json"
         )

    # # If jobTitle claim is too short, show validation error message. So, user can fix the input data.
    if len(req_body.get('jobTitle')) < 4:
        return func.HttpResponse(
            json.dumps({"version": "1.0.0", "status": 200, "action": "ShowBlockPage", "code": "SingUp-Validation-03", "userMessage": "Display name must contain at least four characters."}),
            status_code=200,
            mimetype="application/json"
         )
    
    # Input validation passed successfully, return `Allow` response.
    return func.HttpResponse("Ok")

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