import random
import requests

def generate_otp():
    """Generates a 6-digit OTP code."""
    return str(random.randint(100000, 999999))

def format_ghana_phone(phone_number):
    """Formats 024XXXXXXX, 020XXXXXXX, or 027XXXXXXX to international format 23324XXXXXXX."""
    cleaned = ''.join(filter(str.isdigit, str(phone_number)))
    if cleaned.startswith('0') and len(cleaned) == 10:
        return '233' + cleaned[1:]
    elif cleaned.startswith('233') and len(cleaned) == 12:
        return cleaned
    return cleaned

import requests

def send_otp_sms(phone_number, otp_code, api_key="YOUR_ARKESEL_API_KEY"):
    """Sends OTP via Arkesel v2 SMS API and prints exact response."""
    formatted_phone = format_ghana_phone(phone_number)
    
    url = "https://sms.arkesel.com/api/v2/sms/send"
    headers = {
        "api-key": api_key
    }
    payload = {
        "sender": "AnchorCrest",
        "message": f"Your Anchor Crest verification code is: {otp_code}. Do not share this code.",
        "recipients": [formatted_phone]
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        print("--- ARKESEL API RESPONSE ---")
        print(response.status_code)
        print(response.text)
        print("----------------------------")
        
        res_json = response.json()
        return res_json.get("status") == "success" or response.status_code == 200
    except Exception as e:
        print(f"SMS Sending Exception: {e}")
        return False