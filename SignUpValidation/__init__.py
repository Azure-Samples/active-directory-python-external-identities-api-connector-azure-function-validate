import logging
import json
import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:  # API version
    API_VERSION = "0.0.1"

    logging.info(
        f"Python HTTP trigger function processed a request, API version: {API_VERSION}")

    # Allowed domains
    allowed_domains = ["fabrikam.com", "fabricam.com"]

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
