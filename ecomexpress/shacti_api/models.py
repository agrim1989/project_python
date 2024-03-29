from django.db import models
from service_centre.models import Shipment
from location.models import *
from customer.models import Customer
from authentication.models import EmployeeMaster
from ecomexpress import settings
from ecomm_admin.models import *


class ShactiWeigthUpdateHistory(models.Model):
    airwaybill_number=models.BigIntegerField(db_index=True)
    added_on = models.DateTimeField(auto_now_add=True, db_index=True)
    update_date = models.DateField(auto_now_add=True, db_index=True)
    update_time = models.DateTimeField(auto_now_add=True)
    length=models.FloatField(default=0.0, null=True, blank=True)
    breadth=models.FloatField(default=0.0, null=True, blank=True)
    height=models.FloatField(default=0.0, null=True, blank=True) 
    actual_weight=models.FloatField(default=0.0, null=True, blank=True)
    volumetric_weight=models.FloatField(default=0.0, null=True, blank=True)
    volume = models.IntegerField(default=0, null=True, blank=True)
    employee_code = models.CharField(default=0, max_length=100, null=True, blank=True)
    status = models.IntegerField(default=0, null=True, blank=True, db_index=True)


class SchactiFTPDetails(models.Model):
     service_center = models.CharField(default=0, max_length=5, null=True, blank=True) #center shortcode
     ftp_username = models.CharField(default=0, max_length=100, null=True, blank=True) #ftp username
     ftp_password = models.CharField(default=0, max_length=100, null=True, blank=True) #ftp password
     ftp_ip_address = models.CharField(default=0, max_length=100, null=True, blank=True) #authenticated ip address
     hub = models.CharField(default="", max_length=100, null=True, blank=True) #authenticated ip address


class ShactiSortedAwb(models.Model):
    airwaybill_number=models.BigIntegerField(db_index=True)
    added_on = models.DateTimeField(auto_now_add=True, db_index=True)
    update_date = models.DateField(auto_now_add=True, db_index=True)
    update_time = models.DateTimeField(auto_now_add=True)
    length=models.FloatField(default=0.0, null=True, blank=True)
    breadth=models.FloatField(default=0.0, null=True, blank=True)
    height=models.FloatField(default=0.0, null=True, blank=True) 
    actual_weight=models.FloatField(default=0.0, null=True, blank=True)
    volumetric_weight=models.FloatField(default=0.0, null=True, blank=True)
    volume = models.IntegerField(default=0, null=True, blank=True)
    employee_code = models.CharField(default=0, max_length=100, null=True, blank=True)
    reject_status = models.IntegerField(max_length=1, default=0, null=True, blank=True)
    status = models.IntegerField(default=0, null=True, blank=True, db_index=True)
    inscanned_timestamp = models.DateTimeField(auto_now_add=True)	
    primary_sort_timestamp = models.DateTimeField(auto_now_add=True)	
    in_bag_timestamp  = models.DateTimeField(auto_now_add=True) 
    manifested_timestamp  = models.DateTimeField(auto_now_add=True) 
    bag_closed_timestamp  = models.DateTimeField(auto_now_add=True) 
    bag_id = models.CharField(default=0, max_length=100, null=True, blank=True)

