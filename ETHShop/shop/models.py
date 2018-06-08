from django.db import models
from django.contrib.auth.models import User

class Session(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    session_id = models.CharField(max_length=64)
    etherum_address = models.CharField(max_length=40)
    receipt = models.CharField(max_length=130)
    receipt_value = models.IntegerField()
    expires = models.DateTimeField()
    tx_hash = models.CharField(max_length=64)
    confirmed = models.BooleanField(default=False)
