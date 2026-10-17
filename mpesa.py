# Mpesa Payment Route 
import requests
import datetime
import base64
from requests.auth import HTTPBasicAuth

# @app.route('/api/mpesa_payment', methods=['POST'])
def mpesa_payment():
    # if request.method == 'POST':
        # Extract POST Values sent
        amount = "1"
        phone = "254790061452"

        # Provide consumer_key and consumer_secret provided by safaricom
        consumer_key = "GTWADFxIpUfDoNikNGqq1C3023evM6UH"
        consumer_secret = "amFbAoUByPV2rM5A"

        # Authenticate Yourself using above credentials to Safaricom Services, and Bearer Token this is used by safaricom for security identification purposes - Your are given Access
        api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"  # AUTH URL
        # Provide your consumer_key and consumer_secret 
        response = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))
        # Get response as Dictionary
        data = response.json()
        # Retrieve the Provide Token
        # Token allows you to proceed with the transaction
        access_token = "Bearer" + ' ' + data['access_token']

        #  GETTING THE PASSWORD
        timestamp = datetime.datetime.today().strftime('%Y%m%d%H%M%S')  # Current Time
        passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'  # Passkey(Safaricom Provided)
        business_short_code = "174379"  # Test Paybile (Safaricom Provided)
        # Combine above 3 Strings to get data variable
        data = business_short_code + passkey + timestamp
        # Encode to Base64
        encoded = base64.b64encode(data.encode())
        password = encoded.decode()

        # BODY OR PAYLOAD
        payload = {
            "BusinessShortCode": "174379",
            "Password":password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,  # use 1 when testing
            "PartyA": phone,  # change to your number
            "PartyB": "174379",
            "PhoneNumber": phone,
            "CallBackURL": "https://mku.ac.ke",
            "AccountReference": "SokoGarden Online",
            "TransactionDesc": "Payments for Products"
        }

        # POPULAING THE HTTP HEADER, PROVIDE THE TOKEN ISSUED EARLIER
        headers = {
            "Authorization": access_token,
            "Content-Type": "application/json"
        }

        # Specify STK Push  Trigger URL
        url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"  
        # Create a POST Request to above url, providing headers, payload 
        # Below triggers an STK Push to the phone number indicated in the payload and the amount.
        response = requests.post(url, json=payload, headers=headers)
        print(response.text) # 
        # Give a Response
        return ("An MPESA Prompt has been sent to Your Phone, Please Check & Complete Payment")


# ======================================================================
# NEW: make_payment(phone, amount)
# Same STK Push logic as mpesa_payment() above, but the phone number and
# the amount are passed in as parameters (from the booking dialog) instead
# of being hard-coded. Returns a dict so the booking route knows whether the
# prompt was really sent to the phone.
# ======================================================================
def make_payment(phone, amount):
    try:
        phone = str(phone).strip()
        amount = str(int(float(amount)))  # M-Pesa wants whole shillings

        # Provide consumer_key and consumer_secret provided by safaricom
        consumer_key = "GTWADFxIpUfDoNikNGqq1C3023evM6UH"
        consumer_secret = "amFbAoUByPV2rM5A"

        # Authenticate to get the access token
        api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        response = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret), timeout=30)
        data = response.json()
        access_token = "Bearer" + ' ' + data['access_token']

        # Password = base64(shortcode + passkey + timestamp)
        timestamp = datetime.datetime.today().strftime('%Y%m%d%H%M%S')
        passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
        business_short_code = "174379"
        data = business_short_code + passkey + timestamp
        password = base64.b64encode(data.encode()).decode()

        payload = {
            "BusinessShortCode": "174379",
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,   # amount passed in from the booking dialog
            "PartyA": phone,    # phone number passed in from the booking dialog
            "PartyB": "174379",
            "PhoneNumber": phone,
            "CallBackURL": "https://mku.ac.ke",
            "AccountReference": "DOCCONNECT Booking",
            "TransactionDesc": "Payment for doctor appointment"
        }

        headers = {
            "Authorization": access_token,
            "Content-Type": "application/json"
        }

        url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        print(response.text)
        result = response.json()

        if str(result.get("ResponseCode")) == "0":
            return {"success": True, "message": "An MPESA Prompt has been sent to Your Phone, Please Check & Complete Payment"}

        return {"success": False,
                "message": result.get("errorMessage") or result.get("ResponseDescription") or "M-Pesa could not send the payment prompt."}

    except Exception as e:
        print("MPESA ERROR:", e)
        return {"success": False, "message": "Could not reach M-Pesa. Please check the number and try again."}
