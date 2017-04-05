# Create your views here.
import os
import sys, traceback
import string, random
import xlrd
import xlwt
import utils
import gzip
#import settings
from subprocess import call
from datetime import timedelta, datetime
import dateutil.parser
from django.core.management import call_command
#from tempfile import TemporaryFile
#from xlrd import open_workbook
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.db.models import *
from django.views.decorators.csrf import csrf_exempt
from django.db.models import get_model
from django.core.management import call_command
from django.core.mail import send_mail
from django.core.files.move import file_move_safe
from django.core import serializers
from django.utils.encoding import smart_str
from models import *
from privateviews.decorators import login_not_required
from reports.views import excel_download
from xlsxwriter.workbook import Workbook
from track_me.models import *
from service_centre.models import *
from location.models import ServiceCenter
from pickup.models import PickupRegistration
import xmldict, xmltodict
from utils import history_update
now = datetime.datetime.now()
monthdir = now.strftime("%Y_%m")




import json
#import csv
from  utils import *
from utils import history_update, price_updated, api_auth
from math import ceil
from django.utils import simplejson
from django.db.models import *
from django.contrib.auth.models import User, Group

from customer.models import *
from ecomm_admin.models import *
from service_centre.models import *
from billing.models import Billing, BillingSubCustomer
from airwaybill.models import AirwaybillNumbers


now = datetime.datetime.now()
to_time_obj = now + datetime.timedelta(days=1)
from_time=now.strftime("%Y-%m-%d")
to_time=to_time_obj.strftime("%Y-%m-%d")
monthdir = now.strftime("%Y_%m")
before = now - datetime.timedelta(days=14)

t8am = now.replace(hour=8, minute=0, second=0, microsecond=0)
t3pm = now.replace(hour=15, minute=0, second=0, microsecond=0)

book = xlwt.Workbook(encoding='utf8')
default_style = xlwt.Style.default_style
datetime_style = xlwt.easyxf(num_format_str='dd/mm/yyyy')
date_style = xlwt.easyxf(num_format_str='dd/mm/yyyy')
header_style = xlwt.XFStyle()
category_style = xlwt.XFStyle()
font = xlwt.Font()
font.bold = True

pattern = xlwt.Pattern()
pattern.pattern = xlwt.Pattern.SOLID_PATTERN
pattern.pattern_fore_colour = 5

borders = xlwt.Borders()
borders.left = xlwt.Borders.THIN
borders.right = xlwt.Borders.THIN
borders.top = xlwt.Borders.THIN
borders.bottom = xlwt.Borders.THIN
header_style.pattern = pattern
header_style.font = font
category_style.font = font
header_style.borders=borders
default_style.borders=borders





before = now - datetime.timedelta(days=7)

#### Folowing are api to fetch details
@login_not_required
@csrf_exempt

#### Folowing are api to fetch details
@login_not_required
@csrf_exempt
def lastmile_outscan_details(request):
    if request.POST or request.GET:
        #return HttpResponse("TRU")
        if request.GET.get('hub_id'):
            shipments = Shipment.objects.filter(service_centre__center_shortcode = request.GET.get('hub_id'), deliveryoutscan__isnull = False, status=7)
        elif request.POST.get('hub_id'):
            shipments = Shipment.objects.filter(service_centre__center_shortcode = request.POST.get('hub_id'), deliveryoutscan__isnull = False, status=7)
        #shipments = []
        shipment_info = {}
        shipments = set(shipments)
        #return HttpResponse("%s----" % shipments.count())
        return render_to_response("api/lastmile/outscanned_details.html",
                                  {'shipments':shipments, 'shipment_info':shipment_info},
                               context_instance=RequestContext(request),
                               mimetype="application/xhtml+xml")
    else:
      return HttpResponse("False")



@login_not_required
@csrf_exempt
def lastmile_pod_update(request):
    reason = ""
    #strXML =  request.POST.get("strXML")
    #userID =  request.POST.get("userID")
    api_post = {}
   # strXML = '<?xml version="1.0" encoding="UTF-8" standalone="no"?><DETAILS><DOCKET><DOCKET_NUMBER>100267024</DOCKET_NUMBER><PIECES>0</PIECES><DRS_NUMBER>DS/MUM/1213/014403</DRS_NUMBER><DELIVERY_TIME>2013-10-09 10:30:59.0</DELIVERY_TIME><STATUS>6</STATUS><NEW_DOCKET>DUMMY-9284639</NEW_DOCKET><COMMENTS/><AMT_TOBE_PAD>2699</AMT_TOBE_PAD><ACTUAL_COD_SOD>0</ACTUAL_COD_SOD><AMOUNT_COLLECTABLE>0</AMOUNT_COLLECTABLE><SIGNATURE_LINK>  </SIGNATURE_LINK><CUSTOMER_PHOTO>http://113.19.209.21:8086/fareye_droid/Uploades/customer/cust_1381294857971.jpg</CUSTOMER_PHOTO><CUSTOMER_PHOTO1>  </CUSTOMER_PHOTO1><CUSTOMER_PHOTO2>  </CUSTOMER_PHOTO2><ClS_KLM>100</ClS_KLM><DKT_NT_UPDATED>970</DKT_NT_UPDATED><COD> </COD><Delivery_Person>SACHIN SAXENA</Delivery_Person><LATITUDE>20.2897334</LATITUDE><LONGITUDE>85.8453105</LONGITUDE><LOCATION> </LOCATION><IMEI>911223100108667</IMEI><AUTH_CODE> </AUTH_CODE><SKU_DETAILS><ITEM> </ITEM></SKU_DETAILS><DELIVERED_TO> - </DELIVERED_TO><BIKER_ID>1032510325</BIKER_ID></DOCKET></DETAILS>'
#    strXML = '<?xml version="1.0" encoding="UTF-8" standalone="no"?><DETAILS><DOCKET><DOCKET_NUMBER>100879531</DOCKET_NUMBER><PIECES>0</PIECES><DRS_NUMBER>DS/MUM/1213/014403</DRS_NUMBER><DELIVERY_TIME>2013-10-15 11:11:40.0</DELIVERY_TIME><STATUS>1</STATUS><NEW_DOCKET> </NEW_DOCKET><COMMENTS>219</COMMENTS><AMT_TOBE_PAD>999</AMT_TOBE_PAD><ACTUAL_COD_SOD>0</ACTUAL_COD_SOD><SIGNATURE_LINK>  </SIGNATURE_LINK><CUSTOMER_PHOTO>http://113.19.213.244:8086/fareye_droid/Uploades/customer/cust_1381815696933.jpg</CUSTOMER_PHOTO><CUSTOMER_PHOTO1>  </CUSTOMER_PHOTO1><CUSTOMER_PHOTO2>  </CUSTOMER_PHOTO2><ClS_KLM>100</ClS_KLM><DKT_NT_UPDATED>967</DKT_NT_UPDATED><COD> </COD><Delivery_Person>VYAS KUMAR YADAV</Delivery_Person><LATITUDE>Location Not Available</LATITUDE><LONGITUDE>Location Not Available</LONGITUDE><LOCATION> </LOCATION><IMEI>911223100108667</IMEI><AUTH_CODE/><DELIVERED_TO> - </DELIVERED_TO></DOCKET></DETAILS>'
  #  str#XML = '<?xml version="1.0" encoding="UTF-8" standalone="no"?><DETAILS><DOCKET><DOCKET_NUMBER>100879531</DOCKET_NUMBER><PIECES>0</PIECES><DRS_NUMBER>DS/MUM/1213/014403</DRS_NUMBER><DELIVERY_TIME>2013-10-09 10:30:59.0</DELIVERY_TIME><STATUS>Instant Return (IR)</STATUS><NEW_DOCKET>DUMMY-6336778</NEW_DOCKET><COMMENTS>306</COMMENTS><AMT_TOBE_PAD>2699</AMT_TOBE_PAD><ACTUAL_COD_SOD>0</ACTUAL_COD_SOD><AMOUNT_COLLECTABLE>0</AMOUNT_COLLECTABLE><SIGNATURE_LINK>  </SIGNATURE_LINK><CUSTOMER_PHOTO>http://113.19.213.244:8086/fareye_droid/Uploades/customer/cust_1381294857971.jpg</CUSTOMER_PHOTO><CUSTOMER_PHOTO1>  </CUSTOMER_PHOTO1><CUSTOMER_PHOTO2>  </CUSTOMER_PHOTO2><ClS_KLM>100</ClS_KLM><DKT_NT_UPDATED>970</DKT_NT_UPDATED><COD> </COD><Delivery_Person>SACHIN SAXENA</Delivery_Person><LATITUDE>20.2897334</LATITUDE><LONGITUDE>85.8453105</LONGITUDE><LOCATION> </LOCATION><IMEI>911223100108667</IMEI><AUTH_CODE> </AUTH_CODE><SKU_DETAILS><ITEM> </ITEM></SKU_DETAILS><DELIVERED_TO> - </DELIVERED_TO></DOCKET></DETAILS>'

    #if not strXML or not userID: 
    #    reason = "either of the parameter not found"
    #strxml_parse = request.GET.get("strXML")   
    #return HttpResponse('hi')
    strxml_parse = xmltodict.parse(request.GET.get("strXML"))
    #strxml_parse = xmldict.xml_to_dict(strXML) 
    user_emp = EmployeeMaster.objects.get(employee_code=strxml_parse["DETAILS"]['DOCKET']["BIKER_ID"])
    user = user_emp.user
    #user = User.objects.get(employeemaster__employee_code=10026)

    api_post['delivery_emp'] = strxml_parse["DETAILS"]['DOCKET']["BIKER_ID"]
    #api_post['delivery_emp'] = 10026
    api_post['reason_code'] = strxml_parse["DETAILS"]['DOCKET']["COMMENTS"]
    if api_post['reason_code'] == "999":
        api_post['awbd'] = strxml_parse["DETAILS"]['DOCKET']["DOCKET_NUMBER"]
    else:
        api_post['awbu'] = strxml_parse["DETAILS"]['DOCKET']["DOCKET_NUMBER"]
        api_post['awbd'] = ""
   # api_post['reason_code'] = 10
    api_post['recieved_by'] = strxml_parse["DETAILS"]['DOCKET']["Delivery_Person"]
    #api_post['remarks'] = ""
    api_post['remarks'] = strxml_parse["DETAILS"]['DOCKET']["STATUS"]
    date_time1 = strxml_parse["DETAILS"]['DOCKET']["DELIVERY_TIME"]
    date_time = date_time1.split(".")
    date_time = date_time[0].split(" ")
    api_post['time'] = date_time[1]
    api_post['date'] = date_time[0]

    customer_photo = strxml_parse["DETAILS"]['DOCKET']["CUSTOMER_PHOTO"]
    customer_photo1 = strxml_parse["DETAILS"]['DOCKET']["CUSTOMER_PHOTO1"]
    customer_photo2 = strxml_parse["DETAILS"]['DOCKET']["CUSTOMER_PHOTO2"]
    lat = strxml_parse["DETAILS"]['DOCKET']["LATITUDE"]
    lon = strxml_parse["DETAILS"]['DOCKET']["LONGITUDE"]
    signature_link = strxml_parse["DETAILS"]['DOCKET']["SIGNATURE_LINK"]
    statusapi = strxml_parse["DETAILS"]['DOCKET']["STATUS"]
    location = strxml_parse["DETAILS"]['DOCKET']["LOCATION"]
    actual_cod_sod = strxml_parse["DETAILS"]['DOCKET']["ACTUAL_COD_SOD"]
    cls_klm = strxml_parse["DETAILS"]['DOCKET']["ClS_KLM"]
    drs_number = strxml_parse["DETAILS"]['DOCKET']["DRS_NUMBER"]
    imei = strxml_parse["DETAILS"]['DOCKET']["IMEI"]
    '''Status Update for Shipment'''
    before1 = now - datetime.timedelta(days=1)
    #dest = user.employeemaster.service_centre_id
    dest = user_emp.service_centre_id
    if api_post:
        data_entry_emp = api_post['delivery_emp']
        delivery_emp = api_post['delivery_emp']
        awb = api_post.get('awbu') or api_post.get('awbd')
        reason_code = api_post['reason_code']
        recieved_by = api_post['recieved_by']
        remarks = api_post.get('remarks','')
        time = api_post['time']
        date = api_post['date']
        #ajax_field = api_post['ajax_num']
        pod_reversal = 0
        if not (data_entry_emp and delivery_emp):
             return HttpResponse("<string><root><message>Incorrect Employee Code</message></root></string>", content_type="application/xhtml+xml")

          #   return HttpResponse("Incorrect Employee Code")
        data_entry_emp = EmployeeMaster.objects.filter(employee_code=int(data_entry_emp)).only('id')
        delivery_emp = EmployeeMaster.objects.filter(employee_code=int(delivery_emp)).only('id')
        if delivery_emp and data_entry_emp:
           delivery_emp = delivery_emp[0]
           data_entry_emp = data_entry_emp[0]
        else:
             return HttpResponse("<string><root><message>Incorrect Employee Code</message></root></string>", content_type="application/xhtml+xml")
          # return HttpResponse("Incorrect Employee Code")
        #reason_code=ShipmentStatusMaster.objects.get(id=1)
        reason_code = ShipmentStatusMaster.objects.get(code = int(reason_code))
        dat = dateutil.parser.parse(date)
        date = dat.strftime("%Y-%m-%d")

        ship = Shipment.objects.filter(airwaybill_number = int(awb), status__in = [7,8,9],
                current_sc_id=dest).only('status','status_type','added_on','expected_dod')
        if not ship:
             return HttpResponse("<string><root><message>Incorrect Shipment Number</message></root></string>", content_type="application/xhtml+xml")
            #return HttpResponse("Incorrect Shipment Number")

        shipment = ship[0]
        if not shipment.deliveryoutscan_set.latest("added_on").status:
             return HttpResponse("<string><root><message>Please Close Outscan First</message></root></string>", content_type="application/xhtml+xml")
          #  return HttpResponse("Please Close Outscan First")
        if reason_code.code == 666:
             ship.update(sdl=1)
             sdl_charge(shipment)

        if (api_post['awbd'] <> ""):#Delivered
            if shipment.status <> 7:
                return HttpResponse("<string><root><message>Please Outscan the shipment</message></root></string>", content_type="application/xhtml+xml")   
                #return HttpResponse("Please Outscan the shipment")

            su_status = 2
            shipment_status = 9
            dos_status = 1
        else:
            if shipment.status == 9:#POD reversal
                if reason_code.id <> 44:
                   return HttpResponse("<string><root><message>For updating this shipment enter the reason code as 202</message></root></string>", content_type="application/xhtml+xml") 
                  #  return HttpResponse("For updating this shipment enter the reason code as 202")
                shipment_status =7
                su_status = 1
                dos_status = 0
                pod_reversal = 1
            else:#Undelivered
              su_status = 1
              shipment_status = 8
              dos_status = 2
        #ajax_check = StatusUpdate.objects.filter(ajax_field=ajax_field)
        #if ajax_check:
        #      return HttpResponse("Incorrect Shipment Number")
        su = StatusUpdate.objects.get_or_create(shipment = shipment, data_entry_emp_code = data_entry_emp, delivery_emp_code = delivery_emp, reason_code = reason_code, date = date, time = time, recieved_by = recieved_by, status = su_status, origin = user_emp.service_centre, remarks=remarks)#,ajax_field=ajax_field) #status update

        doss = shipment.doshipment_set.filter(deliveryoutscan__status=1).latest('added_on') #doshipment update
        if doss:
                if pod_reversal:
                   if doss.deliveryoutscan.cod_status == 1:
                        return HttpResponse("COD closed, Please contact Accounts")
                   DeliveryOutscan.objects.filter(id=doss.deliveryoutscan_id).update(collection_status=0)
                DOShipment.objects.filter(id=doss.id).update(status=dos_status, updated_on=now)

        altinstructiawb = InstructionAWB.objects.filter(batch_instruction__shipments__current_sc_id = dest, status = 0, batch_instruction__shipments=shipment).update(status=1)
        if pod_reversal:
           #su_undel = StatusUpdate.objects.filter(shipment=shipment, status=2).update(status=3) #no need to change hist to be maintained
           su_6 = deepcopy(su)
           su_6[0].status = 6
           su_6[0].added_on = now
           su_6[0].save()
#      try: #samar: not sure what this is for, will need to check out
#                su_undel = StatusUpdate.objects.filter(shipment=shipment, status=2).update(status=3)
#        except:
#                pass

        s = ship.update(status=shipment_status, reason_code=reason_code, updated_on=now, current_sc=dest) #shipment update
        if s:
           upd_time = shipment.added_on
           monthdir = upd_time.strftime("%Y_%m")
           shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
           shipment_history.objects.create(shipment=shipment, status=shipment_status, employee_code = delivery_emp, current_sc = user_emp.service_centre, expected_dod=shipment.expected_dod, reason_code=reason_code, remarks=remarks)
           ShipmentLastMileUpdate.objects.create(shipment=shipment, delivered_on=date_time1,status=shipment_status, current_sc=user_emp.service_centre, reason_code=reason_code,
                                                 employee_code=delivery_emp, delivered_to = recieved_by, lat =lat , lon=lon, statusapi=shipment_status, imei=imei,
                                                 signature_link=signature_link, customer_photo=customer_photo, customer_photo1=customer_photo1,customer_photo2=customer_photo2,
                                                 location=location, drs_number=drs_number, cls_klm=cls_klm, actual_cod_sod=actual_cod_sod) #cod_method=cod_method,status_text=status_text

       #    history_update(shipment, shipment_status, request, "", reason_code) #history update
           return HttpResponse("<string><root><message>Updated Successfully</message></root></string>", content_type="application/xhtml+xml")
        else:
           return HttpResponse("<string><root><message>Not Updated (%s)</message></root></string>" % reason, content_type="application/xhtml+xml")
           return HttpResponse("Shipment not updated, please contact site admin")
   #     status_update = StatusUpdate.objects.filter(origin_id = dest,date__range=(before,now)).select_related('shipment__airwaybill_number','reason_code').only('id','status','remarks','shipment__airwaybill_number','reason_code')


       #    delivered_count = status_update.filter(date__range=(before1,now)).count()
    #    undelivered_count = status_update.filter().exclude(shipment__rts_status=2).exclude(shipment__rto_status=1).count()
    #    delivered_count = ""
    #    undelivered_count = ""
    #    return HttpResponse("Success")
        #return render_to_response("delivery/status_update_data.html",
        #                              {'status_update':su[0],
        #                               'delivered_count':delivered_count,
        #                               'undelivered_count':undelivered_count,
        #                               },
        #                              )

    else:
           status_update = StatusUpdate.objects.filter(origin_id = dest, date__range=(before,now)).select_related('shipment__airwaybill_number','reason_code').only('id','status','remarks','shipment__airwaybill_number','reason_code').order_by("-id")
           delivered = status_update.filter(date__range=(before1,now)).order_by("-id")
           undelivered = status_update.filter().exclude(shipment__rts_status=2).exclude(shipment__rto_status=1)
           delivered_count = delivered.count()
           undelivered_count = undelivered.count()
           reason_code  =  ShipmentStatusMaster.objects.all()
           return render_to_response("delivery/status_update.html",locals(),
                               context_instance = RequestContext(request))





    #request.user = User.objects.get(employeemaster__employee_code=request.POST.get('BIKER_ID'))
    #return HttpResponse(" --- %s" % request.POST)



    if not reason:
        return HttpResponse("<string><root><message>Updated Successfully</message></root></string>", content_type="application/xhtml+xml")
    else:
        return HttpResponse("<string><root><message>Not Updated (%s)</message></root></string>" % reason, content_type="application/xhtml+xml")

@csrf_exempt
def create_shipment(request):
    error_list = {}
    print " inside "
    pid=1
    dup_awb = []
    awb_overweight=[]
    subCustomers_list=[]
 
    if request.POST:
        capi =  api_auth(request)
        if not capi:
            return HttpResponse("%s"%"Unauthorised Request")
 
    if request.POST:
            if not request.FILES:
                return HttpResponse("%s"%"Invalid Request")
            if not request.FILES.get('upload_file'):
                return HttpResponse("%s"%"Invalid Request")

            upload_file = request.FILES['upload_file']
            file_contents = upload_file.read()
            if file_contents:
                import_wb = xlrd.open_workbook(file_contents=file_contents)
                import_sheet = import_wb.sheet_by_index(0) 
                for a in range(1, import_sheet.nrows):
                   airwaybill_num = import_sheet.cell_value(rowx=a, colx=0)
                   if not error_list.get(airwaybill_num):
                       error_list[airwaybill_num] = {}
                   for field in [3,4,5,8,9,10,11,13,17,19,20,21]:
                       field_data = import_sheet.cell_value(rowx=a, colx=field)
                       val = field_data.encode('utf-8') if isinstance(field_data,unicode)  else field_data
                       if field == 17:
                          if float(val) <= 0.0:
                             #return HttpResponse("Airwaybill with incorrect weight found %s-%s"%(a,field)) 
                             error_list[airwaybill_num]["weight"] = "incorrect weight"
                       if not val:
                             #return HttpResponse("Field left blank - file could not be uploaded %s-%s"%(a,field))
                             error_list[airwaybill_num]["empty_fields"] = "there are some empty fields"
                   airwaybill_num = import_sheet.cell_value(rowx=a, colx=0)
                   coll_val = import_sheet.cell_value(rowx=a, colx=15)
                 #  return HttpResponse("Field left blank - file could not be uploaded %s-%s"%(airwaybill_num,coll_val)) 
                   if airwaybill_num:
                     if str(airwaybill_num)[0] in ['7','8','9'] and float(coll_val) <= 0.0:
                            #return HttpResponse("COD shipment found with 0 collectible value")
                            error_list[airwaybill_num]["cod_value"] = "COD shipment found with 0 collectible value"
                     if Shipment.objects.filter(airwaybill_number=airwaybill_num):
                       awb_num = Shipment.objects.get(airwaybill_number=airwaybill_num)
                       #if (awb_num.status <> 0 and awb_num.status <> 1 and awb_num.return_shipment <> 0):
                       if (awb_num.status >=2 or awb_num.return_shipment > 0):
                            error_list[airwaybill_num]["awb_used"] = "Airwaybill already in use"
                            #return HttpResponse("Used Air waybill entered, please recheck file before uploading.")
                       #return HttpResponse("-----%s" % (awb_num.return_shipment <> 0))
                   #except:
                   #     pass

                   if airwaybill_num not in dup_awb:
                          dup_awb.append(airwaybill_num)
                   else:
                       error_list[airwaybill_num]["awb_used"] = "Airwaybill already in use"
                       #return HttpResponse("Recheck file, duplicate airwaybill number found")  
                
                reverse_pickup=0  
                
                for rx in range(1, import_sheet.nrows):
                    airwaybill_num = import_sheet.cell_value(rowx=rx, colx=0)
                    sub_customer_id = import_sheet.cell_value(rowx=rx, colx=22)
                    if Shipper.objects.filter(id=sub_customer_id, customer = capi.customer):
                        sub_customer = Shipper.objects.get(id=sub_customer_id)
                        if not sub_customer in subCustomers_list:
                            subCustomers_list.append(sub_customer)
                    else:
                        #return HttpResponse("Subcustomer not found! Please check again.")    
                        error_list[airwaybill_num]["cod_value"] = "COD shipment found with 0 collectible value"

                #subCustomers_list=[]
       
                #json = simplejson.dumps({'subcustomers':subCustomers_list})
                #return HttpResponse(json, mimetype='application/json')
                #for i in enumerate(subCustomers_list):
                #    print "Submerchants are",i 
                pickup_dict = {}

                for rx in range(1, import_sheet.nrows):
                    airwaybill_num = import_sheet.cell_value(rowx=rx, colx=0)
                    try:
                       awb_num = AirwaybillNumbers.objects.get(airwaybill_number=airwaybill_num)
                    except:
                        return HttpResponse("Wrong airwaybill Number")
                        error_list[airwaybill_num]["airwaybill"] = "wrong Airwaybill number"

                    if awb_num.awbc_info.get().customer.code <> "32012":
                       if capi.customer <> awb_num.awbc_info.get().customer:
                         #return HttpResponse("Airwaybill does not belong to this Customer, please recheck")
                         error_list[airwaybill_num]["airwaybill"] = "wrong Airwaybill number"
                
                #for subcust in subCustomers_list:
                     #try:   
                       #pincode = Pincode.objects.get(pincode = int(subcust.address.pincode))
                     #except:
                       #return HttpResponse("Pincode does not exists for this subcustomer")
                       #error_list[airwaybill_num]["pincode"] = "pincode does not exists"


                #if error_list:
                    #error_list['name']='PRTouch'
                    #json = simplejson.dumps(error_list)
                    #return HttpResponse(json, mimetype='application/json')
                    #return render_to_response("api/creat_shipment_errors.html",
                                  #{'error_list':error_list},
                               #mimetype="application/xhtml+xml")

                for subcust in subCustomers_list:
                     try:   
                       pincode = Pincode.objects.get(pincode = int(subcust.address.pincode))
                     except:
                      return HttpResponse("Pincode does not exists for this subcustomer")
                     print "pincode",pincode.service_center
                     pickup = PickupRegistration.objects.filter(customer_code = subcust.customer,subcustomer_code=subcust).filter(Q(pickup_time__gte="07:00:00", pickup_date=from_time) & Q(pickup_time__lte="07:00:00", pickup_date=to_time)).order_by("-pickup_date", "-pickup_time")

                     if pickup:
                         pickup = pickup[0]
                     else:
                         pickup = PickupRegistration(customer_code=subcust.customer,subcustomer_code=subcust,pickup_time=now,pickup_date=now,mode_id=1,customer_name=subcust.name,address_line1=subcust.address.address1,address_line2=subcust.address.address2,pincode=subcust.address.pincode,address_line3=subcust.address.address3,address_line4=subcust.address.address4,mobile=0,telephone=0,pieces=4,actual_weight=1.2,volume_weight=2.1,service_centre=pincode.service_center)
                     pickup.save()
                     pickup_dict[subcust.id] = pickup
                     subcus = pickup_dict.keys()
                     #code for matching with scheduled
                     scheduled_pickup = PickupSchedulerRegistration.objects.filter(status = 0, service_centre = request.user.employeemaster.service_centre, subcustomer_code__id__in=subcus)
                     for a in scheduled_pickup:
                         a.status =1
                         a.save()                    

                error_awbs = error_list.keys()
                skip_awbs = [int(float(awb)) for awb in error_awbs if len(error_list[awb]) > 0]
                for rx in range(1, import_sheet.nrows):
                    airwaybill_num = import_sheet.cell_value(rowx=rx, colx=0)
                    if int(float(airwaybill_num)) in skip_awbs:
                        continue
                    pickup = pickup_dict.get(int(import_sheet.cell_value(rowx=rx, colx=22)))
                    if not pickup:
                        continue
                    try:
                       awb_num = AirwaybillNumbers.objects.get(airwaybill_number=airwaybill_num)
                       awb_num.status=1
                       awb_num.save()
                    except:
                        return HttpResponse("Wrong airwaybill Number")    
                    order_num = import_sheet.cell_value(rowx=rx, colx=1)
                    product_type = import_sheet.cell_value(rowx=rx, colx=2)
                    product_type = product_type.lower()
                    if str(airwaybill_num)[0] in ["1","2","3"]:
                           product_type="ppd"
                    elif str(airwaybill_num)[0] in ["7","8","9"]:
                           product_type="cod"

                    shipper = import_sheet.cell_value(rowx=rx, colx=3)
                    shipper = pickup.customer_code
                    if awb_num.awbc_info.get().customer.code <> "32012":
                       if shipper <> awb_num.awbc_info.get().customer:
                         return HttpResponse("Airwaybill does not belong to this Customer, please recheck")

                    consignee = import_sheet.cell_value(rowx=rx, colx=4)
                    consignee_address1 = import_sheet.cell_value(rowx=rx, colx=5)
                    consignee_address2 = import_sheet.cell_value(rowx=rx, colx=6)
                    consignee_address3 = import_sheet.cell_value(rowx=rx, colx=7)
                            
                    destination_city = import_sheet.cell_value(rowx=rx, colx=8)
                    pincode = import_sheet.cell_value(rowx=rx, colx=9)
                    state = import_sheet.cell_value(rowx=rx, colx=10)
                    mobile = import_sheet.cell_value(rowx=rx, colx=11)
                    telephone = import_sheet.cell_value(rowx=rx, colx=12)
                    item_description = import_sheet.cell_value(rowx=rx, colx=13)
                    pieces = import_sheet.cell_value(rowx=rx, colx=14)
                    collectable_value=import_sheet.cell_value(rowx=rx, colx=15)
                    declared_value=import_sheet.cell_value(rowx=rx, colx=16)
                    actual_weight = import_sheet.cell_value(rowx=rx, colx=17)
                    volumetric_weight = import_sheet.cell_value(rowx=rx, colx=18)
                    length = import_sheet.cell_value(rowx=rx, colx=19)
                    breadth = import_sheet.cell_value(rowx=rx, colx=20)
                    height = import_sheet.cell_value(rowx=rx, colx=21)
                    order_num = repr(import_sheet.cell_value(rowx=rx, colx=1))
                    if order_num.replace(".", "", 1).isdigit():
                       order_num = int(float(order_num))
                    elif 'e+' in str(order_num):
                       order_num = int(float(order_num))
                    else:
                       order_num = import_sheet.cell_value(rowx=rx, colx=1)

                    if length == "":
                       length = 0.0
                    if breadth == "":
                       breadth = 0.0
                    if height == "":
                       height = 0.0
                    if actual_weight == "":
                       actual_weight = 0.0
                    if not (isinstance(volumetric_weight, float) or isinstance(volumetric_weight, int)):
                      if volumetric_weight.strip() == "":
                   
                         volumetric_weight = 0.0
                    if ((actual_weight > 10.0) or (volumetric_weight > 10.0)):
                            a = str(airwaybill_num)+"("+str(max(actual_weight,volumetric_weight))+"Kgs)"
                            awb_overweight.append(a)
                    if collectable_value == "":
                       collectable_value = 0.0
                    else:
                        try:
                            int(collectable_value)
                        except ValueError:
                            collectable_value = collectable_value.replace(",", "")  
                    if declared_value == "":    
                       declared_value = 0.0
                    else:
                       try:
                            int(declared_value)
                       except ValueError:
                            declared_value = declared_value.replace(",", "")    
                    if mobile == "":
                       mobile = 0
                       
                    if pincode == "":
                       pincode = 0.0
                       tt_duration = 0
                    else:
                        
                        origin_pincode=pickup.pincode
                        if not Pincode.objects.filter(pincode=pincode):
                            pincode = 0.0
                            tt_duration = 0
                        try:                    
                            pincode1 = Pincode.objects.get(pincode=origin_pincode)
                            origin_service_centre = pickup.service_centre
                            sctmg = ServiceCenterTransitMasterGroup.objects.get(service_center=origin_service_centre)
                            dest_pincode=Pincode.objects.get(pincode=pincode)
                            dest_service_centre = dest_pincode.service_center
                            tt_duration = 0
                   
                            transit_time = TransitMaster.objects.get(transit_master=sctmg.transit_master_group, dest_service_center=dest_service_centre)
                            cutoff = datetime.datetime.strptime(transit_time.cutoff_time,"%H:%M")
                            tt_duration=int(transit_time.duration)
                        except:
                            tt_duration=0        
                    
                         
                    try:
                     shipment = Shipment.objects.filter(airwaybill_number=airwaybill_num, status__in=[0,1]).update(order_number=str(order_num), current_sc=pickup.service_centre,product_type=product_type, shipper=shipper, pickup=pickup, reverse_pickup=reverse_pickup, consignee=consignee, consignee_address1 = consignee_address1, consignee_address2 = consignee_address2 , consignee_address3 = consignee_address3, destination_city=destination_city, pincode=pincode, state=state, mobile=mobile, telephone=telephone, item_description=item_description, pieces=pieces, collectable_value=collectable_value, declared_value=declared_value, actual_weight=actual_weight, volumetric_weight=volumetric_weight, length=length, breadth=breadth, height=height)
                     shipment = Shipment.objects.get(airwaybill_number=airwaybill_num)
                    except: 
                      shipment = Shipment(airwaybill_number=int(airwaybill_num), current_sc=pickup.service_centre, order_number=str(order_num), product_type=product_type, shipper=shipper, pickup=pickup, reverse_pickup=reverse_pickup, consignee=consignee, consignee_address1 = consignee_address1, consignee_address2 = consignee_address2 , consignee_address3 = consignee_address3, destination_city=destination_city, pincode=pincode, state=state, mobile=mobile, telephone=telephone, item_description=item_description, pieces=pieces, collectable_value=collectable_value, declared_value=declared_value, actual_weight=actual_weight, volumetric_weight=volumetric_weight, length=length, breadth=breadth, height=height)
                      shipment.save()
                    if pincode: 
                        try:
                          pincode = Pincode.objects.get(pincode=shipment.pincode)
                          servicecentre = pincode.service_center
                          shipment.service_centre = servicecentre
                          shipment.original_dest = servicecentre
                          shipment.save()
                        except:
                          pincode = ""  
                     
                    if tt_duration <> 0:
                         if shipment.added_on.time() > cutoff.time():
                             tt_duration+=1 
                         expected_dod = shipment.added_on + datetime.timedelta(days=tt_duration)
                         try:
                             HolidayMaster.objects.get(date=expected_dod.date())
                             expected_dod = expected_dod + datetime.timedelta(days=1)
                         except:
                             pass   
                         shipment.expected_dod=expected_dod
                         shipment.save()
                    if shipment:
                         history_update(shipment, 0, request)
                    tmp_count=Shipment.objects.filter(pickup=pickup.id).count()
                    pickup.pieces=tmp_count;
                    pickup.status=0 
                    pickup.save() 
            else:
              pass
                
            group = Group.objects.get(name="Customer Service")
            a=0
            if request.user.groups.filter(name="Customer Service").exists():
              pickup = PickupRegistration.objects.filter().order_by('-added_on')
              a=1
            if request.user.employeemaster.user_type in ["Staff", "Supervisor", "Sr Supervisor"]:
               pickup = PickupRegistration.objects.filter(service_centre=request.user.employeemaster.service_centre, status=0)
            else:
               pickup = PickupRegistration.objects.filter(status=0).order_by('-added_on')
            msg = ""
            if awb_overweight:
              msg = "Following Air Waybills have weight more than 10 kgs, PLEASE CONFIRM !!!, and incase of mismatch re-upload the file:\n"+"\n".join(['%s' % ship for ship in awb_overweight])
            customer=Customer.objects.all()
            destination= ServiceCenter.objects.all()
            json = simplejson.dumps(error_list)
            return HttpResponse(json, mimetype='application/json')

            #return HttpResponse("Request Updated successfully")
    else:
     return HttpResponse("Invalid request")

def api_form(request):                                                                                                                          
    return render_to_response('api/api_form.html')                   
