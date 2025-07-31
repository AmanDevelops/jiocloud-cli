import re

import requests

BASE_URL = "https://www.jiocloud.com/"


def get_script_path():
    """
    Fetches the latest main.aabbcd.js file from production environment.

    Returns:
        str: "main.aabbcd.js"

    Raises:
        IndexError: if the regular expression match fails
    """
    main_html = requests.get(BASE_URL)

    # Searches for the 'main.aabbcd.js' using regular expressions.
    main_js = re.findall(r"main\.[a-z0-9]+\.js", main_html.text)
    if not main_js:
        raise IndexError("No main.aabbcd.js file found; Check regex")

    return main_js[0]


def get_app_creds() -> dict:
    """
    Retrieves the most recent X-Api-Key and X-App-Secret values from the production environment.

    Returns:
        dict: {"X-Api-Key": "dfhakfs", "X-App-Secret": "ksdfds"}

    Raises:
        IndexError: if the regular expression match fails
    """

    # Declare App Creds
    app_creds = {}

    # Retrieves the latest main.aabbcd.js file from the production environment.
    script_path = get_script_path()
    js_file_response = requests.get(BASE_URL + script_path)
    js_file = js_file_response.text

    # Searches for the 'X-Api-Key' in the latest main.aabbcd.js file using regular expressions.
    regex = r"production:{\"X-Api-Key\":\"([a-z0-9-]+)\""
    matches = re.search(regex, js_file)
    if not matches or len(matches.groups()) > 2:
        raise IndexError("Could Not Find 'X-Api-Key'")
    app_creds["X-Api-Key"] = matches.group(1)

    # Searches for the 'X-App-Secret' in the latest main.aabbcd.js file using regular expressions.
    regex = r"\"X-App-Secret\":\"([A-Za-z0-9]+)\""
    matches = re.search(regex, js_file)
    if not matches or len(matches.groups()) > 2:
        raise IndexError("Could Not Find 'X-App-Secret'")
    app_creds["X-App-Secret"] = matches.group(1)

    return app_creds


get_app_creds()
