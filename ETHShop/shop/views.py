from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from shop.serializers import UserSerializer, GroupSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions, status
from shop.models import Session
from django.utils import timezone
from django.conf import settings
from shop.utils import is_valid_receipt


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def shop_details(request):
    return Response({
        'etherum_contract_address': settings.ETHERUM_CONTRACT_ADDRESS,
        'content_price': settings.CONTENT_PRICE
    })


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def start_session(request):
    receipt = request.data['receipt']
    etherum_address = request.data['etherum_address']
    session_id = request.data['session_id']
    # input: session_id, adres etherum, podpis rachunku na 0, podtwierdzenie przelewu na kontrakt
    if not is_valid_receipt(receipt, etherum_address, session_id, 0):
        return Response(status=status.HTTP_400_BAD_REQUEST)

    expires = timezone.now() + timezone.timedelta(**settings.SESSION_TIME)

    Session.objects.create(session_id=session_id[2:], etherum_address=etherum_address[2:],
                           receipt=receipt[2:], receipt_value=0,
                           expires=expires)

    return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def buy_content(request):
    new_receipt = request.data['receipt']
    # for now we dont have login
    # check for expiration
    session = Session.objects.filter(expires__gt=timezone.now()).select_for_update().first()
    if session is None:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    new_receipt_value = session.receipt_value + settings.CONTENT_PRICE

    if new_receipt_value > settings.MAX_SESSION_RECEIPT_VALUE:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    if not is_valid_receipt(new_receipt, '0x' + session.etherum_address, '0x' + session.session_id, new_receipt_value):
        return Response(status=status.HTTP_400_BAD_REQUEST)

    session.receipt = new_receipt[2:]
    session.receipt_value = new_receipt_value
    session.save()
    return Response(status=status.HTTP_200_OK)
