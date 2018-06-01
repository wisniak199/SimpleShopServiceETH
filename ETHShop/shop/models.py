from django.db import models

class Session(models.Model):
    session_id = models.CharField(max_length=64)
    etherum_address = models.CharField(max_length=40)
    receipt = models.CharField(max_length=130)
    receipt_value = models.IntegerField()
    expires = models.DateTimeField()
