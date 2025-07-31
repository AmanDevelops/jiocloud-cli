import requests
from get_api_key import get_app_creds


def send_otp_via_mobile(mobile_number: str) -> bool:
    """
    Sends OTP to the given 10 Digit Mobile Number

    Returns:
        bool:
            True if the OTP (one-time password) is sent successfully
            False in case of rate limiting, bad request, or invalid headers

    Raises:
        ValueError: if the mobile number is not exactly 10 digits
    """

    if len(mobile_number) != 10:
        raise ValueError("Invalid mobile number; must contain exactly 10 digits.")

    headers = get_app_creds()

    json_data = {
        "mobileNumber": f"+91{mobile_number}",
    }

    response = requests.post(
        "https://api.jiocloud.com/account/jioid/sendotp",
        headers=headers,
        json=json_data,
    )

    return response.status_code == 204
