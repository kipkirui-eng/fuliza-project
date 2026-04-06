from django.shortcuts import render, redirect
from .models import BorrowRequest
from django.http import HttpResponse
from datetime import datetime
from requests.auth import HTTPBasicAuth
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
import base64
import requests
def index(request):
    request.session.pop('amount', None)
    request.session.pop('fee', None)

    if request.method == 'POST':
        amount = request.POST.get('amount')

        fee_map = {
            "5000": 99,
            "10000": 250,
            "15000": 500,
            "20000": 1000,
            "25000": 1500,
            "30000": 2500,
            "35000": 3500,
            "45000": 5000
        }
        if not amount:
            return redirect('index')
        
        request.session['amount'] = (amount)
        request.session['fee'] = fee_map.get(amount, 0)
        return redirect('verify') 
    return render(request, 'index.html')
def verify(request):
    amount = request.session.get('amount')
    fee = request.session.get('fee', 0)

    if not amount:
        return redirect('index')
    
    borrow_amount = float(amount)

    if request.method == "POST":
        id_number = request.POST.get('id_number')
        phone = request.POST.get('phone')


        if not id_number or not phone:
            error_message = "ID number and phone number are required"
            return render(request, 'payments/verify.html', {'amount': borrow_amount, 'fee':fee, 'error': error_message})

        borrow_request = BorrowRequest.objects.create(
            id_number=id_number,
            phone_number=phone,
            amount=borrow_amount,
            fee=fee,
            payment_status='PENDING'
        )
        request.session['borrow_request_id'] = borrow_request.id
        return redirect('payment')
    return render(request, 'payments/verify.html', {'amount': amount, 'fee': fee})

def payment(request):
    token = get_access_token()
    print("ACCESS TOKEN:", token)
    borrow_request_id = request.session.get('borrow_request_id')
    if not borrow_request_id:
        return redirect('index')  

    borrow_request = BorrowRequest.objects.get(id=borrow_request_id)
    
    if request.method == "POST":
        phone = borrow_request.phone_number
        if not phone:
            return redirect('payment')
        phone =str(phone).strip()
        if phone.startswith("0"):
            phone = "254" + phone[1:] 
        print("PHONE USED:", phone)
        amount = borrow_request.fee
        
    
        response = stk_push(phone, amount)
        print("STK RESPONSE:",response) 
        if response and response.get("ResponseCode") == "0":
            borrow_request.payment_status = 'PENDING'
        else:
            borrow_request.payment_status = 'FAILED'
        borrow_request.save()
        
        return redirect('result') 

    return render(request, 'payments/payment.html', {
        'amount': borrow_request.amount,
        'fee': borrow_request.fee,
        'phone': borrow_request.phone_number
    })
def result(request):
    borrow_request_id = request.session.get('borrow_request_id')
    if not borrow_request_id:
        return redirect('index')

    borrow_request = BorrowRequest.objects.get(id=borrow_request_id)

    return render(request, 'payments/result.html', {
        'success': borrow_request.payment_status == 'SUCCESS',
        'amount': borrow_request.amount
    })
def stk_push(phone, amount):
    access_token = get_access_token()

    url = "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

    shortcode = "174379" 
    passkey = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"

    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password = base64.b64encode((shortcode + passkey + timestamp).encode()).decode()

    payload = {
        "BusinessShortCode": shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(amount),
        "PartyA": phone,
        "PartyB": shortcode,
        "PhoneNumber": phone,
        "CallBackURL": "https://fuliza-project.onrender.com/callback/",
        "AccountReference": "Fuliza",
        "TransactionDesc": "Payment"
    }

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.post(url, json=payload, headers=headers)

    print("RAW RESPONSE:", response.text)

    try:
        return response.json()
    except:
        print("STK RESPONSE ERROR")
        return None
    
    

def get_access_token():
    consumer_key = "uAXvc84UhbEwlI89sMA6vX8yPFGzdLs6B3Gyn9WdsZm5wfh4"
    consumer_secret = "t5zCG1VT3EMWF87hjA0PiP1gNoZupF75hyAagHe1vBIk9JOFHhzUBkZAUJWT0Bpk"

    url = "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

    response = requests.get(url, auth=HTTPBasicAuth(consumer_key, consumer_secret))

    print("TOKEN RESPONSE:", response.text)
    try:
        return response.json()['access_token'] 
    except:
         print("FAILED TO GET TOKEN")
         return None


@csrf_exempt
def callback(request):
    if request.method == "POST":
        data = json.loads(request.body)
        print("CALLBACK DATA:", data)

        result = data.get("Body", {}).get("stkCallback", {})

        if result.get("ResultCode") == 0:
        
            print("Payment Successful")
        else:
            print("Payment Failed")

        return JsonResponse({"ResultCode": 0, "ResultDesc": "Success"})