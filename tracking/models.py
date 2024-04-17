from django.db import models
from django.db.models import DateTimeField
from django.utils import timezone
from django.contrib.auth.models import User
import datetime

# Create your models here.

class Types(models.Model):
    type_name = models.CharField(max_length=100)
    def __str__(self):
        return self.type_name


class ActionTaken(models.Model):
    action_taken = models.CharField(max_length=100)

    def __str__(self):
        return self.action_taken


def pdf_file_name(instance, filename):
    return '/'.join(['media', instance.code + instance.sender, filename])

def approved_file_name(instance, filename):
    return '/'.join(['sent', instance.code + instance.sender, filename])

def attach_file_name(instance, filename):
    return '/'.join(['attached', instance.code + instance.sender, filename])

def attach_file(instance, filename):
    return '/'.join(['outgoing', instance.doc_code, filename])

def qrcode_file_name(instance, filename):
    return '/'.join(['qrcode_images', instance.code + instance.sender, filename])

def counter():
    dt = datetime.date.today()
    dtt = datetime.datetime.today()
    count = str(dt.year) + "" + str(dt.month) + "" + str(dt.day) + "" + str(dtt.second) + "" + str(round(dtt.timestamp()))
    #count = str(dt.year) + "" + str(dt.month) + "" + str(dt.day) + "" + str(dtt.second)
    return count


class Document(models.Model):
    TYPE = (('Incoming-Ext','Incoming-Ext'),
            ('Outgoing-Ext','Outgoing-Ext'),
            ('Incoming-Int', 'Incoming-Int'),
            ('Outgoing-Int', 'Outgoing-Int'),
            )
    code = models.CharField(max_length=100,default=counter)
    category = models.CharField(max_length=100,choices=TYPE,null=True)
    type = models.ForeignKey(Types,null=True,on_delete=models.SET_NULL)
    route = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    subject = models.CharField(max_length=500)
    description = models.CharField(max_length=500)
    sender = models.CharField(max_length=100)
    contact = models.BigIntegerField()
    date_received = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    action_taken = models.ForeignKey(ActionTaken, null=True, on_delete=models.SET_NULL)
    deadline = models.DateField(default=timezone.now() + timezone.timedelta(days=24))
    online = models.BooleanField(default=True)
    complete = models.BooleanField(default=True)
    for_release = models.BooleanField(default=False) # served as acted docs ignore the label, kapoy lang usab
    urgent = models.BooleanField(default=False)
    process = models.BooleanField(default=False)
    multiple_route = models.BooleanField(default=False)
    pdf_file = models.FileField(upload_to=pdf_file_name,max_length=500)
    send_file = models.FileField(upload_to=approved_file_name,max_length=500)
    #qrcode_file = models.FileField(upload_to=qrcode_file_name)
    date_sent = models.DateTimeField(auto_now=False,auto_now_add=True)
    remark = models.TextField(max_length=300,null=True)
    acted_release = models.BooleanField(default=False)
    division = models.TextField(max_length=300, null=True)
    my_copy = models.TextField(max_length=300, null=True)
    confidential = models.BooleanField(default=False)

    def __str__(self):
        return self.code


class Routed(models.Model):
    comment = models.CharField(max_length=300)
    action = models.ForeignKey(ActionTaken, null=True, on_delete=models.SET_NULL)
    routed_to = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    date_rcv = models.DateTimeField(auto_now=True)
    sender = models.CharField(max_length=100)
    attach_file = models.FileField(upload_to=attach_file_name,max_length=500)
    # doc_code = models.BigIntegerField()
    doc_code = models.CharField(max_length=250)

    def __str__(self):
        return self.comment


class Outgoing(models.Model):
    doc_code = models.CharField(max_length=300)
    subject = models.CharField(max_length=500)
    date_upload = models.DateTimeField(auto_now=True)
    doc_type = models.CharField(max_length=300)
    doc_to = models.CharField(max_length=300)
    doc_from = models.CharField(max_length=300)
    #attach_file = models.FileField(upload_to=attach_file, max_length=500)

    def __str__(self):
        return self.doc_code


class Carboncopy(models.Model):
    routed_to = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    date_rcv = models.DateTimeField(auto_now=True)
    doc_code = models.CharField(max_length=250, default=None, null=True)

    class Meta:
        ordering = ('-date_rcv',)

    def __str__(self):
        return self.doc_code
