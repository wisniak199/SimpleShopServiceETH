from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions, status
from shop.models import Session
from django.utils import timezone
from django.conf import settings
from shop.utils import is_valid_receipt
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponseBadRequest
from web3 import Web3

w3 = Web3()


def welcome(request):
    return render(request, 'welcome.html')


@login_required
def start_session(request):
    if Session.objects.filter(user=request.user, expires__gt=timezone.now()).count() > 0:
        return redirect('shop')

    if request.method == 'POST':
        receipt = request.POST['receipt']
        etherum_address = request.POST['etherum_address']
        session_id = request.POST['session_id']
        transaction_hash = request.POST['transaction_hash']
        # input: session_id, adres etherum, podpis rachunku na 0, podtwierdzenie przelewu na kontrakt
        if not is_valid_receipt(receipt, etherum_address, session_id, 0):
            return HttpResponseBadRequest()
        expires = timezone.now() + timezone.timedelta(**settings.SESSION_TIME)
        Session.objects.create(user=request.user, session_id=session_id[2:], etherum_address=etherum_address[2:],
                               receipt=receipt[2:], receipt_value=0,
                               expires=expires, tx_hash=transaction_hash[2:])
        return redirect('shop')

    return render(request, 'start_session.html', {'contract_address': settings.ETHERUM_CONTRACT_ADDRESS})


@login_required
def shop(request):
    session = Session.objects.filter(user=request.user, expires__gt=timezone.now()).first()
    if session is None:
        return redirect('start-session')
    msg = ''
    can_buy = True
    auto_refresh = False
    new_receipt_value = session.receipt_value + settings.CONTENT_PRICE
    if not session.confirmed:
        can_buy = False
        msg = 'Please wait for your session to be confirmed by our system'
        auto_refresh = True
    elif new_receipt_value > settings.MAX_SESSION_RECEIPT_VALUE:
        can_buy = False
        msg = "You spend all the money, end current session and start a new one"
    elif request.method == 'POST':
        new_receipt = request.POST['receipt']

        if not is_valid_receipt(new_receipt, '0x' + session.etherum_address, '0x' + session.session_id, w3.toWei(new_receipt_value, 'Finney')):
            return HttpResponseBadRequest()

        session.receipt = new_receipt[2:]
        session.receipt_value = new_receipt_value
        session.save()
        new_receipt_value = session.receipt_value + settings.CONTENT_PRICE
        msg = "Thanks for buying item"
        if new_receipt_value > settings.MAX_SESSION_RECEIPT_VALUE:
            can_buy = False
            msg = msg + "\nYou spend all the money, end current session and start a new one"

    return render(request, 'shop.html', {
        'session_id': '0x' + session.session_id,
        'new_receipt_value': new_receipt_value,
        'can_buy': can_buy,
        'msg': msg,
        'auto_refresh': auto_refresh
    })


@login_required
def end_session(request):
    Session.objects.filter(user=request.user).update(expires=timezone.now() - timezone.timedelta(hours=1))
    return redirect('start-session')
