import base64
import json
import os

import requests

from utils.get_api_key import get_app_creds

HEADERS = get_app_creds()
LOGIN_DETAILS_PATH = "login_details.json"


def check_auth_state() -> bool:
    """
    Checks if the user is logged in or not
    """
    return os.path.exists(LOGIN_DETAILS_PATH)


def send_otp_to_mobile(mobileNumber: str) -> bool:
    """
    Sends OTP to the given 10 Digit Mobile Number

    Returns:
        - bool:
            True if the OTP (one-time password) is sent successfully
            False in case of rate limiting, bad request, or invalid headers

    Raises:
        - ValueError: if the mobile number is not exactly 10 digits
    """

    if len(mobileNumber) != 10:
        raise ValueError("Invalid mobile number; must contain exactly 10 digits.")

    headers = HEADERS.copy()

    json_data = {
        "mobileNumber": f"+91{mobileNumber}",
    }

    response = requests.post(
        "https://api.jiocloud.com/account/jioid/sendotp",
        headers=headers,
        json=json_data,
    )

    return response.status_code == 204


def verify_otp(otp: str, mobileNumber: str) -> dict:
    """
    Verifies the OTP

    Returns:
        - userId: the userId of the given user

    Raises:
        - ValueError: Invalid OTP
    """

    headers = HEADERS.copy()

    json_data = {"mobileNumber": f"+91{mobileNumber}", "otp": otp}

    response = requests.post(
        "https://api.jiocloud.com/account/jioid/verifyotp",
        headers=headers,
        json=json_data,
    )

    user_response = response.json()

    userId = None

    if user_response.get("userAccounts") is not None:
        userId = user_response.get("userAccounts")[0].get("userId")

    user_info = {
        "requestId": user_response.get("requestId"),
        "userId": userId,
    }

    return user_info


def user_login_via_mobile(args: str) -> None:
    """
    User Login Functionality via mobile
        - Sends the OTP
        - Verify the OTP
        - Fetches Credentials
        - Saves Credentials

    Args:
        - Mobile Number: str

    Return:
        - None

    Raises:
        -
    """

    if check_auth_state():
        print("[Status]: User Already Logged in")
        return

    mobileNumber = args.number
    print(f"[Log]: Sending OTP to {mobileNumber}")
    send_otp_to_mobile(mobileNumber)

    while True:
        otp = input("[Input]: Enter OTP: ")

        if len(otp) != 6:
            continue

        user_info = verify_otp(otp=otp, mobileNumber=mobileNumber)

        userId = user_info.get("userId")
        requestId = user_info.get("requestId")

        if userId is not None and requestId is not None:
            break

        print("[Error]: Invalid OTP, Try Again")

    cookies = {
        "G_ENABLED_IDPS": "google",
    }

    headers = HEADERS.copy()

    json_data = {
        "userId": userId,
        "requestId": requestId,
        "deviceType": "W",
        "mobileNumber": f"+91{mobileNumber}",
        "deviceInfo": {
            "model": "JioCloud CLI",
            "deviceName": "JioCloud CLI",
            "platformType": "JioCloud CLI",
            "platformVersion": "1.0",
            "type": "JioCloud CLI",
            "isWebClient": True,
        },
        "isStaySignIn": True,
    }

    response = requests.post(
        "https://www.jiocloud.com/account/jioid/useridlogin",
        cookies=cookies,
        headers=headers,
        json=json_data,
    )

    login_details = response.json()

    auth_token = login_details.get("authToken").get("accessToken")

    base64_login_token = base64.b64encode(auth_token.encode("utf-8")).decode("ascii")

    user_creds = {
        "userId": userId,
        "Authorization": f"Bearer {base64_login_token}",
        "X-Device-Key": login_details.get("deviceKey"),
    } | HEADERS

    with open(LOGIN_DETAILS_PATH, "w") as f:
        json.dump(user_creds, f)

    print("[Success]: User Logged in Succesfully...")
