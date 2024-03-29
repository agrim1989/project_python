# Create your views here.
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.models import User, Group
from django.template import RequestContext
from django.db.models import Q
from django.db.models import *
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse

from models import *
import sys, traceback
from forms import *
from customer.models import *
from datetime import timedelta
import datetime
import json
import xlrd, xlwt
from service_centre.general_updates import *
from service_centre.models import ReverseShipment, Shipment
from airwaybill.models import AirwaybillNumbers
from xlsxwriter.workbook import Workbook
from utils import history_update
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import simplejson
from service_centre.general_updates import multiple_pickup_creation
import barcode
import urllib2
import urllib
from service_centre.models import Customer
from urllib2 import urlopen, HTTPError
import httplib2
import httplib, urllib
from reports.report_api import ReportGenerator
now = datetime.datetime.now()

Pickup = PickupRegistration

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


#viewing history of all the pending pickups
#def pending_pickup(request):
#    pending_pickup = Pickup.objects.filter(status=0).order_by('-added_on')
#    pickup_info = {}
#    for a in pending_pickup:
#        if not pickup_info.get(a):
#          try:
#            ab = Shipment.objects.filter(pickup_id = a).aggregate(QTY=Sum('quantity'))
#            pickup_info[a] = int(ab['QTY'])
#          except:
#            pickup_info[a] = 0
#    return render_to_response("pickup/pending_pickup.html",
#                              {'pending_pickup':pickup_info},
#                               context_instance=RequestContext(request))

#viewing history of all the completed pickups
#def completed_pickup(request):
#    completed_pickup =Pickup.objects.filter(status=1).order_by('-added_on')
#    return render_to_response("pickup/completed_pickup.html",
#                              {'completed_pickup':completed_pickup},
#                               context_instance=RequestContext(request))

#scheduling a new pickup
#def request_pickup(request):
#
#    if request.POST:
#        form = PickupForm(request.POST)
#        if form.is_valid():
#            form_pickup = form.save(commit=False)
#            form_pickup.customer_id = 1
#            form_pickup.status = 0
#            form_pickup.save()
#            return HttpResponseRedirect('/pickup/pending_pickup/')
#    else:
#      form = PickupForm()
#      return render_to_response("pickup/new_pickup.html",
#                                  {'pickup_form':form
#                                   },context_instance=RequestContext(request))

#cancel pickup

def cancel_pickup(request, id):
    pickup = Pickup.objects.filter(id=id).update(status=3)
    shipment = Shipment.objects.filter(pickup=pickup)
    for a in shipment:
        a.status=0
        a.status_type=0
        a.save()
    return HttpResponseRedirect('/pickup/')


def copy_pickup(request, id):
    pickup = Pickup.objects.get(id=id)
    pickup.id=None
    pickup.save()
    return HttpResponseRedirect('/pickup/')


def pickup_dashboard(request, ptype=0):
    beforem = now - datetime.timedelta(days=30)
    if request.POST:
        q = Q()
        customer = request.POST['cust_id']
        date_from = request.POST['date_from']
        date_to = request.POST['date_to']
        if not date_to:
            date_to = "2050-12-12"

        sc=request.POST['sc']

        if customer == "0":
            customer = None
        else:
            q = q & Q(customer_code__id = int(customer))
        if not (date_from and date_to):
            pass
        else:
            q = q & Q(added_on__range=(date_from,date_to))
        if sc == "0":
            sc = None
        else:
            q = q & Q(service_centre_id=int(sc))
        pickup = PickupRegistration.objects.filter(q).order_by('status')
        a=1
        customer=Customer.objects.all()
        destination= ServiceCenter.objects.all()
        return render_to_response("pickup/pickupdashboard.html",
                              {'pickup':pickup,
                               'a':a,
                               'customer':customer,
                               'sc':destination},
                               context_instance=RequestContext(request))


    else:
        group = Group.objects.get(name="Customer Service")
        a=0
        if request.user.groups.filter(name="Customer Service").exists():
            pickup = PickupRegistration.objects.filter(
                        added_on__range=(beforem, now)
            ).order_by('-added_on')
            a=1
        if request.user.employeemaster.user_type in ["Staff", "Supervisor", "Sr Supervisor"]:
               if ptype:
                    pickup = PickupSchedulerRegistration.objects.filter(
                                 service_centre=request.user.employeemaster.service_centre,
                                 status__in=[0,3])
               else:
                    pickup = PickupRegistration.objects.filter(added_on__range=(beforem, now),
                                 service_centre=request.user.employeemaster.service_centre,
                                 status__in=[0,3])
        else:
               sc = request.user.employeemaster.service_centre
               if ptype:
                    pickup = PickupSchedulerRegistration.objects.filter(
                        service_centre=request.user.employeemaster.service_centre,
                        #added_on__range=(beforem, now), 
                        status__in=[0,3])
               else:
                    pickup = PickupRegistration.objects.filter(
                        service_centre=request.user.employeemaster.service_centre,
                        #added_on__range=(beforem, now), 
                        status__in=[0,3], 
                    ).exclude(reverse_pickup=1).order_by('-added_on')
        #TODO: To be added in cron
        if not ptype:
                t = "pickup/pickupdashboard.html"
		for a in pickup.filter(status=0):
		  if not a.reverse_pickup:
		      shipment_check = Shipment.objects.filter(pickup=a, status=0).only('id','status')
		  else:
		      shipment_check = ReverseShipment.objects.filter(pickup=a, shipment__isnull = True)
		  if not shipment_check:
			  a.status = 1
			  a.save()

        else:
                 t = "pickup/scheduledpickupdashboard.html"
        customer=Customer.objects.all()
        destination= ServiceCenter.objects.all()
        return render_to_response(t,
                              {'pickup':pickup,
              #                 'msg':"test",
                               'a':a,
                               'customer':customer,
                               'sc':destination,
                               'ptype':ptype},
                               context_instance=RequestContext(request))


def reverse_pickup_dashboard(request):
    beforem = now - datetime.timedelta(days=7)
    group = Group.objects.get(name="Customer Service")
    a=0
    if request.user.groups.filter(name="Customer Service").exists():
        pickup = ReversePickupRegistration.objects.filter().order_by('-pickup_date')
        a=1
   # if request.user.employeemaster.user_type in ["Staff", "Supervisor", "Sr Supervisor"]:
   #        pickup = ReversePickupRegistration.objects.filter(service_centre=request.user.employeemaster.service_centre, status=0)
   # else:
    pickup = ReversePickupRegistration.objects.filter(status=0, added_on__range=(beforem,now)).order_by('-pickup_date')
    #TODO: To be added in cron
    for a in pickup:
      if not a.reverse_pickup:
          shipment_check = Shipment.objects.filter(pickup=a, status=0)
          if not shipment_check:
              a.status = 1
              a.save()

    customer = Customer.objects.all()
    destination = ServiceCenter.objects.all()
    return render_to_response("pickup/reverse_pickup_dashboard.html",
                          {'pickup':pickup,
                           'a':a,
                           'customer':customer,
                           'sc':destination},
                           context_instance=RequestContext(request))


def reverse_pickup_download(request, pid, tid):
       q = Q()
       if tid == '2':
             rev_shipment = ReverseShipment.objects.filter(reverse_pickup_id=int(pid))
       elif tid == '1':
            rev_shipment = ReverseShipment.objects.filter(pickup_id=int(pid))
       download_list = []
      
       #return HttpResponse (rev_shipment)
      # sheet = book.add_sheet('Reverse Pickup')
       #sheet.col(1).width = 8000 # 3333 = 1" (one inch).
      # for a in range(10):
          # sheet.col(a).width = 6000
       report = ReportGenerator('Reverse_Pickup.xlsx')
       cols_head = ("Airwaybill Number",
                    "Order Number",
                    "Product",
                    "Shipper",
                    "Pickup Consignee",
                    "Pickup Consignee Address 1",
                    "Pickup Consignee Address 2",
                    "Pickup Consignee Address 3",
                    "Pickup Origin",
                    "Pickup Pincode",
                    "State",
                    "Mobile",
                    "Telephone",
                    "Item Desciption",
                    "Pieces",
                    "Collectable Value",
                    "Declared Value",
                    "Actual Weight",
                    "Volumetric Weight",
                    "Length",
                    "Breadth",
                    "Height",
                    "SubCustomer",
                    "Reverse Shipment ID",
                    "Reverse Pickup Id",
                    "Reason Code")

       #for col,val in enumerate(cols_head):
           #sheet.write(0, col, val, style=header_style)
       reports.write_header(cols_head)
      # for row, rowdata in enumerate(download_list, start=1):
           #for col, val in enumerate(rowdata, start=0):
               # style = default_style
               # if val:
                
               #  val = val.encode('utf-8') if isinstance(val,unicode)  else val
                #  try:
                 #  sheet.write(row, col, str(val), style=style)
                #  except:
                  # pass
       if rev_shipment:
        for a in rev_shipment:
           row = (a.airwaybill_number,
                 a.order_number,
                 "ppd",
                 a.shipper,
                 a.pickup_consignee,
                 a.pickup_consignee_address1,
                 a.pickup_consignee_address2,
                 a.pickup_consignee_address3,
                 a.pickup.service_centre,
                 a.pickup_pincode,
                 a.state,
		 a.mobile,
		 a.telephone,
		 a.item_description,
		 a.pieces,
		 a.collectable_value,
		 a.declared_value,
		 a.actual_weight,
		 a.volumetric_weight,
		 a.length,
		 a.breadth,
		 a.height,
		 a.vendor.id,
		 a.id,
                 pid,
                 #a.shipment.reason_code
                 a.reason_code
           )
           report.write_row(row)
       file_name = report.manual_sheet_close()
       return file_name


def finder_pincode_view(request):
    if request.POST:
      place = pincode = area_code = service_centre = ""
      place = request.POST['place']
      pincode = request.POST['pincode']
      area_code = request.POST['area_code']
      service_centre = request.POST['service_centre']
      pickup = PickupRegistration.objects.filter(pincode = pincode, area_code = area_code, service_centre=service_centre)
      return render_to_response("pickup/finder",
                                {'pincode_pickup':pickup}
                                )
    else:
      sc = ServiceCenter.objects.all()

      return render_to_response("pickup/finders.html",
                                {'sc':sc},
                               context_instance=RequestContext(request))

@csrf_exempt
def transit_time(request):
    origin=request.POST['origin']
    origin = ServiceCenter.objects.get(center_shortcode=origin)
    destination=request.POST['destination']

    if destination == "":
        dest_pincode = request.POST['dest_pincode']
        dest_pincode=Pincode.objects.get(pincode=dest_pincode)
        destination = dest_pincode.service_center

    else:
        destination = ServiceCenter.objects.get(center_shortcode=destination)

    pickup_date = request.POST['pickup_date']
    pickup_time = request.POST['pickup_time']
    if pickup_time:
        pickup_time = datetime.datetime.strptime(pickup_time,"%H%M")

    sctmg = ServiceCenterTransitMasterGroup.objects.get(service_center=origin)
    tt_duration = 0
    try:
       transit_time = TransitMaster.objects.get(transit_master=sctmg.transit_master_group, dest_service_center=destination)
       cutoff = datetime.datetime.strptime(transit_time.cutoff_time,"%H%M")
    except:
       tt_duration = 0
       return HttpResponse("Transit time for the given locations does not exists")
       #TT does not exist
    tt_duration=int(transit_time.duration)
    if pickup_time.time() > cutoff.time():
        tt_duration+=1
    pickup_date = datetime.datetime.strptime(pickup_date, "%Y-%m-%d")
    expected_dod = pickup_date + timedelta(days=int(tt_duration))
    try:
        HolidayMaster.objects.get(date=expected_dod.date())
        expected_dod = expected_dod + datetime.timedelta(days=1)
    except:
        pass
    exp_date =  expected_dod.date()
    return HttpResponse(exp_date)



@csrf_exempt
def pincode_view(request):
        pincode = request.POST['pincode']

        pin_finder = {}
        if pincode:
            q  = Pincode.objects.get(pincode=int(pincode))

        area_code = request.POST['area_code']
        if area_code:
            q  = Pincode.objects.get(area=area_code)

        service_centre = request.POST['service_centre']
        if service_centre:
            sc = ServiceCenter.objects.get(Q(center_name=service_centre) | Q(center_shortcode=service_centre))
            q  = Pincode.objects.get(service_center=sc)

        pin_finder['pincode']=q.pincode
        pin_finder['area']=q.area
        pin_finder['service_centre']=q.service_center.center_shortcode
        pin_json = json.dumps(pin_finder)
        return HttpResponse(pin_json)

@csrf_exempt
def volumetric_calculator(request):
        pieces = request.POST['pieces']
        length=request.POST['length']
        width=request.POST['width']
        height=request.POST['height']
        unit=request.POST['unit']

        lbh = int(length)*int(width)*int(height)
        if unit == "m":
           lbh = lbh * 0.01
        if unit =="in":
            lbh = lbh * 0.3937
        if unit == "mm":
            lbh = lbh * 10
        if unit == "ft":
            lbh = lbh * 0.0328

        volumetric_weight = (lbh*1.0)/5000
        volumetric_weight = volumetric_weight*int(pieces)
        return HttpResponse(volumetric_weight)

def pickup_registration(request):
    if request.POST:
     form = PickupRegistrationForm(request.POST)
     subcustomer_code = form.data['subcustomer_code']
     pickup_time = form.data['pickup_time']
     schedule_uptil = form.data['schedule_date']
     pieces = form.data['pieces']
     if not pieces:
       pieces = 0
     service_centre=form.data['service_centre']
     caller_name = form.data['caller_name'] if form.data['caller_name'] else None
     pickup_sch = PickupScheduler(subcustomer_code_id = subcustomer_code, pickup_time=pickup_time, schedule_uptil = schedule_uptil, pieces=pieces, service_centre_id=service_centre, caller_name = caller_name)
     pickup_sch.save()
     ps = PickupSchedulerRegistration.objects.create(pickup_scheduler = pickup_sch,
               subcustomer_code = pickup_sch.subcustomer_code, pieces = pickup_sch.pieces,
               pickup_date = datetime.datetime.now().date(), pickup_time = pickup_sch.pickup_time,
               service_centre = pickup_sch.service_centre)
     pickup_scheduler = request.POST.getlist('pickup_scheduler')
     if pickup_scheduler:

          for a in pickup_scheduler:
              pickup_time = form.data['pickup_time%s'%a]
              PickupScheduleWeekdays.objects.create(weekday=a, time=pickup_time, pickupscheduler = pickup_sch)
     if form.is_valid():
         form_pikup = form.save(commit=False)
         form_pikup.status=3
         form.save()
         ps.pickup = form_pikup
         ps.save()
         return HttpResponseRedirect("/pickup/")
     else:
      return HttpResponse(str(form.errors))
    else:
     try:
      pur = PickupRegistration.objects.latest("id")
      pur = pur.id
     except:
      pur = 0
     form = PickupRegistrationForm()
     customer = Customer.objects.all()
     area = AreaMaster.objects.all()
     service_centre = ServiceCenter.objects.all()
     subcustomer = Shipper.objects.all()
     mode=Mode.objects.all()
     return render_to_response("pickup/pickup_registration.html",
                                  {'pickup_registration_form':form,
                                   'pur':pur,
                                   'customer':customer,
                                   'subcustomer':subcustomer,
                                   'area':area,
                                   'service_centre':service_centre,
                                   'mode':mode
                                   },context_instance=RequestContext(request))

@csrf_exempt
def update_reason_code(request):
     spickup_id =  request.POST['id']
     reason_code = request.POST['value']
     try:
           res = PickupStatusMaster.objects.get(code=reason_code)
           status = 0 if res.code in [401,402,403,407,408,417] else 1
           spickup = PickupSchedulerRegistration.objects.filter(id=spickup_id).update(reason_code = res, status=status)
     except:
           return HttpResponse("Error")
    # spickup = PickupSchedulerRegistration.objects.filter(id=spickup_id).values_list('id','reason_code')
     ret = spickup_id if status else res
     return HttpResponse(ret)


@csrf_exempt
def update_employee_code(request):
     spickup_id =  request.POST['id']
     employee_code = request.POST['value']
     try:
           emp_code=EmployeeMaster.objects.get(employee_code=employee_code)
           spickup = PickupSchedulerRegistration.objects.filter(id=spickup_id).update(pickedup_by = emp_code)
     except:
           return HttpResponse("Error")
     return HttpResponse("%s"% employee_code)




def edit_pickup(request, id):
    pickup = PickupRegistration.objects.get(id=id)
    if request.method == "POST":
        form = PickupRegistrationForm(request.POST, instance=pickup)
        if form.is_valid():
            form_pikup = form.save(commit=False)
            form_pikup.status=0

            form_pikup.save()
            return HttpResponseRedirect("/pickup/")
        pass
    else:
        form = PickupRegistrationForm(instance=pickup)
        status = "edit"

        return render_to_response("pickup/pickup_edit.html",
                                 {'pickup_registration_form':form,
                                  'status':status,
                                  'id':id
                                  },context_instance=RequestContext(request))

def rev_pickup_download(request, pid):
       rev_shipment = ReverseShipment.objects.filter(pickup_id=int(pid))
       download_list = []
       if rev_shipment:
         for a in rev_shipment:
            u = (a.airwaybill_number,
                 a.order_number,
                 "ppd",
                 a.shipper,
                 a.pickup_consignee,
                 a.pickup_consignee_address1,
                 a.pickup_consignee_address2,
                 a.pickup_consignee_address3,
                 a.pickup.service_centre,
                 a.pickup_pincode,
                 a.state,
                 a.mobile,
                 a.telephone,
                 a.item_description,
                 a.pieces,
                 a.collectable_value,
                 a.declared_value,
                 a.actual_weight,
                 a.volumetric_weight,
                 a.length,
                 a.breadth,
                 a.height,
                 a.vendor.id,
                 a.id,
                 a.reason_code_id
)
            download_list.append(u)
       #return HttpResponse (rev_shipment)
       sheet = book.add_sheet('Reverse Pickup')
       sheet.col(1).width = 8000 # 3333 = 1" (one inch).
       for a in range(10):
           sheet.col(a).width = 6000

       sheet.write(0, 0, "Airwaybill Number", style=header_style)
       sheet.write(0, 1, "Order Number", style=header_style)
       sheet.write(0, 2, "Product", style=header_style)
       sheet.write(0, 3, "Shipper", style=header_style)
       sheet.write(0, 4, "Pickup Consignee", style=header_style)
       sheet.write(0, 5, "Pickup Consignee Address 1", style=header_style)
       sheet.write(0, 6, "Pickup Consignee Address 2", style=header_style)
       sheet.write(0, 7, "Pickup Consignee Address 3", style=header_style)
       sheet.write(0, 8, "Pickup Origin", style=header_style)
       sheet.write(0, 9, "Pickup Pincode", style=header_style)
       sheet.write(0, 10, "State", style=header_style)
       sheet.write(0, 11, "Mobile", style=header_style)
       sheet.write(0, 12, "Telephone", style=header_style)
       sheet.write(0, 13, "Item Desciption", style=header_style)
       sheet.write(0, 14, "Pieces", style=header_style)
       sheet.write(0, 15, "Collectable Value", style=header_style)
       sheet.write(0, 16, "Declared Value", style=header_style)
       sheet.write(0, 17, "Actual Weight", style=header_style)
       sheet.write(0, 18, "Volumetric Weight", style=header_style)
       sheet.write(0, 19, "Length", style=header_style)
       sheet.write(0, 20, "Breadth", style=header_style)
       sheet.write(0, 21, "Height", style=header_style)
       sheet.write(0, 22, "SubCustomer", style=header_style)
       sheet.write(0, 23, "Reverse Shipment ID", style=header_style)
       sheet.write(0, 24, "Reason Code", style=header_style)
       style = datetime_style
       for row, rowdata in enumerate(download_list, start=1):
           for col, val in enumerate(rowdata, start=0):
               style = default_style
               sheet.write(row, col, str(val), style=style)
       response = HttpResponse(mimetype='application/vnd.ms-excel')
       response['Content-Disposition'] = 'attachment; filename=Reverse_Pickup.xls'
       book.save(response)
       return response

def pickup_sheet(request):
    now = datetime.datetime.now()
    before = now - datetime.timedelta(days=10)

    emp_code = request.GET['emp_code']
    spid = PickupSchedulerRegistration.objects.filter(added_on__range=(before, now), pickedup_by__employee_code=emp_code)
  #  return HttpResponse(spid)
   #spid = [a.id, a.subcustomer_code, a.subcustomer_code.name, a.subcustomer_code.address for a in PickupSchedulerRegistration.objects.filter(added_on__range=(before, now), pickedup_by__employee_code=emp_code)]
   # spidl = [a[0], a[1], a[2], a.
   # return HttpResponse(spidl)
  #  for a in spidl:
   #     a[3]=a[3]+a[4]
    if not spid:
       return HttpResponse("No Data Available")
    file_name = "/pickup_sheet_%s.xlsx"%(now.strftime("%d%m%Y%H%M%S%s"))
    path_to_save = settings.FILE_UPLOAD_TEMP_DIR+file_name
    workbook = Workbook(path_to_save)
    sheet = workbook.add_worksheet()

#    for a in range(0,9):
    sheet.set_column(0, 3, 12)

    sheet.set_column(4, 4, 60)
    sheet.set_column(5, 9, 12)
    merge_format = workbook.add_format({
        'bold': 1,
        'align': 'center',
        'valign': 'vcenter',
        })
    sheet.write(0, 0, "Employee Code")
    sheet.write(0, 1, spid[0].pickedup_by.employee_code)
    sheet.write(0, 4, "Pickup Sheet", merge_format)
    sheet.write(0, 7, "Date:")
    sheet.write(0, 8, str(now.date()))
    sheet.write(1, 0, "Employee Name")
    sheet.write(1, 1, str(spid[0].pickedup_by.firstname)+" "+str(spid[0].pickedup_by.lastname))
    sheet.write(2, 0, "Sr. No.")
    sheet.write(2, 1, "SPUR ID")
    sheet.write(2, 2, "Customer")
    sheet.write(2, 3, "Customer Name")
    sheet.write(2, 4, "Customer Address")
    sheet.write(2, 5, "No. of Shipments")
    sheet.write(2, 6, "Sign")
    sheet.write(2, 7, "Time")
    counter =1
    for row, rowdata in enumerate(spid, start=4):
        sheet.write(row, 0, counter)
        counter = counter+1

        sheet.write(row, 1, rowdata.id)
        sheet.write(row, 2, str(rowdata.subcustomer_code.customer))
        sheet.write(row, 3, str(rowdata.subcustomer_code.customer))
        sheet.write(row, 4, str(rowdata.subcustomer_code.address))
    #    sval = ""
  #      for col, val in enumerate(rowdata, start=1):
     #       if col == 4:
      #             scol = col

       #            while scol <6:
        #              sval=sval+val   #  return HttpResponse(scol)
         #          sheet.write(row, col, str(sval))
          #  else:
    workbook.close()
    return HttpResponseRedirect("/static/uploads/%s"%(file_name))


def text_pickup_sheet(request):
    now = datetime.datetime.now()
    before = now - datetime.timedelta(days=1)

    emp_code = request.GET['emp_code']
    spid = PickupSchedulerRegistration.objects.filter(
                added_on__range=(before, now),
                pickedup_by__employee_code=emp_code)
    main_output_list = []
    output_list = []
    output_list.append("{0:>50}\n".format('Pickup Sheet'))
    output_list.append("{0:<4}".format(""))
    output_list.append("{0}{1}".format("Employee Code:", emp_code))
    output_list.append("{0:>20}\n".format("Date:"+str(now.date())))
    output_list.append("{0:<4}".format(""))
    output_list.append("Employee Name: {0:>5}\n\n".format(str(spid[0].pickedup_by.firstname)+" "+str(spid[0].pickedup_by.lastname)))

    output_list.append("{0:<4}".format(""))
    output_list.append("{0:<8}".format("Sr No"))
    output_list.append("{0:<8}".format("SPUR ID"))
    output_list.append("{0:<20}".format("Customer"))
    output_list.append("{0:<25}".format("Customer Name"))
    output_list.append("{0:<30}".format("Customer Address"))
    output_list.append("{0:10}".format("Address"))
    output_list.append("{0:16}".format("No.of Shipments"))
    output_list.append("{0:5}".format("Sign"))
    output_list.append("{0:5}".format("Time"))
    row = ''.join(output_list)
    main_output_list.append(row)
    main_output_list.append('-'*130)
    for row, rowdata in enumerate(spid, start=1):
        output_list = []
        output_list.append("{0:<8}".format(row))
        output_list.append("{0:<8}".format(rowdata.id))
        output_list.append("{0:<20}".format(rowdata.subcustomer_code))
        output_list.append("{0:<25}".format(rowdata.subcustomer_code.name))
        output_list.append("{0:<30}\n".format(rowdata.subcustomer_code.address.address1))
        output_list.append("{0:<65}".format(''))
        output_list.append("{0:<30}\n".format(rowdata.subcustomer_code.address.address2))
        output_list.append("{0:<65}".format(''))
        output_list.append("{0:<30}\n".format(rowdata.subcustomer_code.address.address3))
        output_list.append("{0:<65}".format(''))
        output_list.append("{0:<30}\n".format(rowdata.subcustomer_code.address.address4))
        row = ''.join(output_list)
        main_output_list.append(row)

    text =  render_to_string("pickup/pickup_sheet.html",
                              {'contents':main_output_list},
                               context_instance = RequestContext(request))
    response =  HttpResponse("%s"%text, content_type="text/plain", mimetype='text/plain')
    response['Content-Disposition'] = 'attachment; filename=pickup_sheet.txt'
    return response


def reverse_shipment(request):
    customer = Customer.objects.all()
    sc = ServiceCenter.objects.all()
    st = 0
    if request.GET:
        reverse_ships = ReverseShipment.objects.using('local_ecomm').filter(
        Q(status=0) ).filter(pickup_service_centre__id=request.GET['sc']).exclude(shipment__reason_code__isnull=False,shipment__reason_code__code__in=[420, 419, 418, 416, 415, 414, 413, 411, 406, 405, 404, 400]).order_by('-added_on')
        st = 1
    elif request.user.employeemaster.employee_code in ['124','63392', '11285', '11324','11792','13340','15488']:
        reverse_ships = ReverseShipment.objects.using('local_ecomm').filter(
        Q(status=0) ).exclude( shipment__reason_code__isnull=False, shipment__reason_code__code__in=[420, 419, 418, 416, 415, 414, 413, 411, 406, 405, 404, 400]).order_by('-added_on')[0:100]
        st = 1
    else:
        reverse_ships = ReverseShipment.objects.using('local_ecomm').filter(Q(status=0)).filter(
    	pickup_service_centre=request.user.employeemaster.service_centre).exclude(shipment__reason_code__isnull=False,shipment__reason_code__code__in=[420, 419, 418, 416, 415, 414, 413, 411, 406, 405, 404, 400]).order_by('-added_on')[0:100]
#    paginator = Paginator(reverse_ships, 100) 
#    page = request.GET.get('page')

 #   try:
 #       reverse_shipments = paginator.page(page)
 #   except PageNotAnInteger:
        # If page is not an integer, deliver first page.
 #       reverse_shipments = paginator.page(1)
 #   except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
 #       reverse_shipments = paginator.page(paginator.num_pages)

    #reverse_shipments = ReverseShipment.objects.filter(status=0)[:50]
    return render_to_response("pickup/reverse_shipment_dashboard.html",
                          {'reverse_shipments':reverse_ships,'customer':customer,'sc':sc, 'st':st},
                          context_instance=RequestContext(request))

@csrf_exempt
def rship_update_reason_code(request):
     rev_ship_id =  request.POST['id']
     reason_code = request.POST['value']
     reason_code = reason_code.strip().split(' ')[0]
     rship = ReverseShipment.objects.get(id=rev_ship_id)
     if rship.airwaybill_number:
          return HttpResponse("Error")
     res = PickupStatusMaster.objects.get(code=int(reason_code))
    # if not rship.reason_code:
     rship.reason_code=res
     rship.save()
     return HttpResponse(rship.reason_code.code)

@csrf_exempt
def rship_update_employee_code(request):
     rev_ship_id = request.POST['id']
     employee_code = request.POST['value']
     employee_code = employee_code.strip().split(' ')[0]
     rship = ReverseShipment.objects.get(id=rev_ship_id)
     try:
     	emp_code = EmployeeMaster.objects.get(employee_code=employee_code)
     except EmployeeMaster.DoesNotExist:
        return HttpResponse('Not exist')
     #if not rship.employee_code:
     rship.employee_code=emp_code
     rship.save()
     return HttpResponse(rship.employee_code.employee_code)

@csrf_exempt
def rship_update_awb_number(request):
    rev_ship_id = request.POST['id']
    awb = request.POST['value']
   # awb = awb.strip().split(' ')[0]
    rship = ReverseShipment.objects.get(id=rev_ship_id)
    if rship.actual_weight == 0 or rship.length == 0 or rship.breadth == 0 or rship.height == 0:
       return HttpResponse("Incorrect Weight")
    if not rship.airwaybill_number:
        try:
            awb_from_table = AirwaybillNumbers.objects.get(airwaybill_number=awb)
            awb_from_table.status = 1
            awb_from_table.save()
        except AirwaybillNumbers.DoesNotExist:
            return HttpResponse('Airwaybill Not Generated')
        try:
            ship = Shipment.objects.get(airwaybill_number=awb)
            if ship:
            #if ship.status >=2 or ship.return_shipment > 0:
                return HttpResponse('Used airwaybill Number Entered')
        except Shipment.DoesNotExist:
            pin = rship.pickup.subcustomer_code.address.pincode
            pincode = Pincode.objects.get(pincode=pin)
         #   reason_code = ShipmentStatusMaster.objects.get(id=rship.reason_code.id)
            try:
               origin_service_centre = rship.pickup.service_centre
               sctmg = ServiceCenterTransitMasterGroup.objects.get(service_center=origin_service_centre)
               dest_service_centre = pincode.service_center
               tt_duration = 0

               transit_time = TransitMaster.objects.get(transit_master=sctmg.transit_master_group, dest_service_center=dest_service_centre)
               cutoff = datetime.datetime.strptime(transit_time.cutoff_time,"%H%M")
               tt_duration=int(transit_time.duration)
            except:
               tt_duration=0

            ship = Shipment.objects.create(
                pickup=rship.pickup,
                reverse_pickup=True,
                airwaybill_number=awb,
                order_number=rship.order_number,
                product_type=rship.product_type,
                shipper=rship.shipper,
                consignee=rship.pickup.subcustomer_code.name,
                consignee_address1=rship.pickup.subcustomer_code.address.address1,
                consignee_address2=rship.pickup.subcustomer_code.address.address2,
                consignee_address3=rship.pickup.subcustomer_code.address.address3,
                consignee_address4=rship.pickup.subcustomer_code.address.address4,
                destination_city=rship.pickup.subcustomer_code.address.city,
                pincode=rship.pickup.subcustomer_code.address.pincode,
                service_centre=pincode.service_center,
                current_sc=pincode.service_center,
                state=rship.state,
                mobile=rship.mobile,
                telephone=rship.telephone,
                item_description=rship.item_description,
                pieces=rship.pieces,
                collectable_value=rship.collectable_value,
                declared_value=rship.declared_value,
                actual_weight=rship.actual_weight,
                volumetric_weight=rship.volumetric_weight,
                length=rship.length,
                breadth=rship.breadth,
                height=rship.height,
                status_type=rship.status_type,
          #      reason_code=reason_code,
                remark=rship.remark,
                #expected_dod=rship.expected_dod,
                original_dest=pincode.service_center)
            if tt_duration <> 0:
                         if ship.added_on.time() > cutoff.time():
                             tt_duration+=1
                         expected_dod = ship.added_on + datetime.timedelta(days=tt_duration)
                         try:
                             HolidayMaster.objects.get(date=expected_dod.date())
                             expected_dod = expected_dod + datetime.timedelta(days=1)
                         except:
                             pass
                         ship.expected_dod=expected_dod
                         ship.save()

            history_update(ship, 0, request)
            rship.airwaybill_number=int(awb)
            rship.reason_code = None
            rship.save()
    return HttpResponse(rship.airwaybill_number)

@csrf_exempt
def rship_update_etc(request, param):
     rev_ship_id =  request.POST['id']
     value = request.POST['value']
    # value = rvalue.strip().split(' ')[0]
     rship = ReverseShipment.objects.get(id=rev_ship_id)
     if param == 'length':
       #  if not rship.length:
             rship.length = value
             if rship.airwaybill_number:
                Shipment.objects.filter(airwaybill_number=rship.airwaybill_number, status__lte = 2).update(length=rship.length)
             rship.save()
             return HttpResponse(rship.length)
     elif param == 'breadth':
        # if not rship.breadth:
             rship.breadth = value
             if rship.airwaybill_number:
                Shipment.objects.filter(airwaybill_number=rship.airwaybill_number, status__lte = 2).update(breadth=rship.breadth)
             rship.save()
             return HttpResponse(rship.breadth)
     elif param == 'height':
        # if not rship.height:
             rship.height = value
             if rship.airwaybill_number:
                Shipment.objects.filter(airwaybill_number=rship.airwaybill_number, status__lte = 2).update(height=rship.height)
             rship.save()
             return HttpResponse(rship.height)
    # elif param == 'volumetric_weight':
     #    if not rship.volumetric_weight:
      #       rship.volumetric_weight = value
       #      rship.save()
        # return HttpResponse(rship.volumetric_weight)
     elif param == 'actual_weight':
         #if not rship.actual_weight:
             rship.actual_weight = value
             if rship.airwaybill_number:
                Shipment.objects.filter(airwaybill_number=rship.airwaybill_number, status__lte = 2).update(actual_weight=rship.actual_weight)
             rship.save()
             return HttpResponse(rship.actual_weight)
     else:
         return HttpResponse('Error')

def rship_revert(request):
    q = Q()
    if request.user.employeemaster.employee_code in ['63392', '11285', '11324']:
       pass
    else:
       q = q & Q(pickup_service_centre=request.user.employeemaster.service_centre)
   
    ReverseShipment.objects.filter(
        q, status=0
    ).filter(~Q(airwaybill_number=None) & ~Q(actual_weight=0) & \
        ~Q(breadth=0) & ~Q(height=0) & ~Q(length=0)|\
        ~Q(reason_code=None)
    ).exclude(reason_code__code__in=[401,402,403,407,408,417]).update(status=1, updated_on=datetime.datetime.now())
    ReverseShipment.objects.filter(
        q, status=0
    ).filter(~Q(airwaybill_number=None) & ~Q(actual_weight=0) & \
        ~Q(breadth=0) & ~Q(height=0) & ~Q(length=0) &\
        ~Q(reason_code=None)
    ).exclude(reason_code__code__in=[401,402,403,407,408,417]).update(status=1, updated_on=datetime.datetime.now())
    return HttpResponseRedirect(reverse('pickup.views.reverse_shipment'))



def reverse_shipment_report(request):
  load_report_fields = (
      'Airwaybill Number',
      'Order ID',
      'Reverse Pickup ID',
      'Reverse Shipment ID',
      'Registered Date',
      'Pickup Location',
      'Destination',
      'Customer Name',
      'Shipper Name',
      'Shipper Address',
      'Phone Number',
      'Item Description',
      'Current Status',
      'Reason Code',
      'Remark',
      'Updated On',
      'Number of Outscans')

  if request.POST:
    customer = request.POST['cust_id']
    date_from = request.POST['date_from']
    date_to = request.POST['date_to']
    origin = request.POST['sc']
    q = Q()
    if customer == "0":
      customer = None
    else:
      q = q & Q(shipper__id = int(customer))
    if date_from and date_to:
      t = datetime.datetime.strptime(date_to, "%Y-%m-%d") + datetime.timedelta(days=1)
      date_to = t.strftime("%Y-%m-%d")
      q = q & Q(added_on__range=(date_from, date_to))
    if origin == "0":
      origin = None
    else:
      q = q & Q(pickup__service_centre__id=int(origin))

    reverse_shipments = ReverseShipment.objects.using('local_ecomm').filter(q)
    report = ReportGenerator("reverseshipment_report_%s.xlsx"%(now.strftime("%d%m%Y%H%M%S%s")))
    report.write_header(load_report_fields)

    for row, reverse_shipment in enumerate(reverse_shipments, start=3):
      ad1 = reverse_shipment.pickup_consignee_address1 if reverse_shipment.pickup_consignee_address1 else u''
      ad2 = reverse_shipment.pickup_consignee_address2 if reverse_shipment.pickup_consignee_address2 else u''
      ad3 = reverse_shipment.pickup_consignee_address3 if reverse_shipment.pickup_consignee_address3 else u''
      ad4 = reverse_shipment.pickup_consignee_address4 if reverse_shipment.pickup_consignee_address4 else u''
      address = ad1 + ad2 + ad3 + ad4

      if reverse_shipment.shipment:
          supd = reverse_shipment.shipment.statusupdate_set.filter()
          if supd:
             su = supd.latest('added_on')
             remarks=su.remarks
          else:
              remarks=''
          if reverse_shipment.shipment.reason_code:
             desc = str(reverse_shipment.shipment.reason_code)
          else:
             desc=''
          ot_count = reverse_shipment.shipment.deliveryoutscan_set.filter().only('id').count()
      else:
          desc = ''
          remarks=''
          ot_count = 0
      added_date = reverse_shipment.added_on.strftime('%Y/%m/%d') if reverse_shipment.added_on else ''
      updated_date = reverse_shipment.updated_on.strftime('%Y/%m/%d') if reverse_shipment.updated_on else ''
      if reverse_shipment.vendor:
          try: 
             dest = Pincode.objects.using('local_ecomm').get(pincode=reverse_shipment.vendor.address.pincode).service_center.center_name
          except:
             dest = ''
      else:
          dest = ''
      rsc = reverse_shipment.pickup_service_centre.center_name if reverse_shipment.pickup_service_centre else ''
      cs = 'Pending' if reverse_shipment.status == 0 else 'Completed'
    
      row_data = (reverse_shipment.airwaybill_number, reverse_shipment.order_number,
             reverse_shipment.reverse_pickup.id, reverse_shipment.id,
             added_date, rsc, dest, reverse_shipment.pickup_consignee,
             reverse_shipment.shipper.name, address, reverse_shipment.mobile,
             reverse_shipment.item_description, cs, desc, reverse_shipment.remark, updated_date)
      report.write_row(row_data)
    file_name = report.manual_sheet_close()
  return HttpResponseRedirect('/static/uploads/reports/' + file_name)


def reverse_order_slip(request, sid):
    rv = ReverseShipment.objects.get(id=sid)
    pin = rv.pickup.subcustomer_code.address.pincode
    pincode = Pincode.objects.get(pincode=pin)
    dest = pincode.service_center
    #text = render_to_string("hub/manifest_txt.html",
     #                             {'bags':bags,
     #                              'dec_value':dec_value,
     #                              'weight':weight,
     #                              'shipments':shipments},
     #                              context_instance=RequestContext(request))
    text = render_to_string("pickup/order_slip.html",
                            {'rv':rv,
                             'dest':dest },context_instance=RequestContext(request))
    response = HttpResponse("%s"%text, content_type="text/plain", mimetype="text/plain")
    response['content-Disposition']='attachment; filename=order_slip.txt'
    return response

@csrf_exempt
def update_reverse_shipment(request):
     if request.POST:
        #datastring=request.POST['datastring']
	id=request.POST['id']
        remark=request.POST['remark']      
        ReverseShipment.objects.filter(id=id).update(remark=remark, updated_on=datetime.datetime.now())
        data={'success':True,'remark':remark,'id':id}
        
        json=simplejson.dumps(data)
        return HttpResponse(json,mimetype='application/json')
     else:
        pass

def bulk_pickup_registration(request):
    if request.POST:
        upload_file = request.FILES['upload_file']
        file_contents = upload_file.read()
        if file_contents:
            import_wb = xlrd.open_workbook(file_contents=file_contents)
            import_sheet = import_wb.sheet_by_index(0)
            for rx in range(1, import_sheet.nrows):
                subcustomer_code = import_sheet.cell_value(rowx=rx, colx=0) if import_sheet.cell_value(rowx=rx, colx=0) else None
                #alias_code = import_sheet.cell_value(rowx=rx, colx=1) if import_sheet.cell_value(rowx=rx, colx=1) else None
                num_ships = import_sheet.cell_value(rowx=rx, colx=1) if import_sheet.cell_value(rowx=rx, colx=1) else 0
                multiple_pickup_creation(subcustomer_code, None, num_ships, 0)
    return HttpResponseRedirect("/pickup/")

def reverse_pickup_sheet(request):
    pass
def reverse_outscan(request):
    pass	


def reverse_shipment_print(request):
    customer = Customer.objects.all()
    sc = ServiceCenter.objects.all()
    st = 0
    if request.GET.get('awb'):
         reverse_ships = ReverseShipment.objects.filter(airwaybill_number=request.GET.get('awb'),
            status=0).exclude(airwaybill_number=None,shipment__reason_code__code__in=[420, 419, 418, 416, 415, 414, 413, 411, 406, 405, 404, 400])

    else:
        reverse_ships = ReverseShipment.objects.filter(
            pickup_service_centre__id=request.GET.get('sc'),
            status=0).exclude(airwaybill_number=None,shipment__reason_code__code__in=[420, 419, 418, 416, 415, 414, 413, 411, 406, 405, 404, 400]).order_by('-added_on')
        st = 1
        if request.user.employeemaster.employee_code in ['124','63392', '11285', '11324','13340','11792','15488']:
            reverse_ships = ReverseShipment.objects.filter(
                status=0).exclude(airwaybill_number=None,shipment__reason_code__code__in=[420, 419, 418, 416, 415, 414, 413, 411, 406, 405, 404, 400]).order_by('-added_on')[0:100]
            st = 1
        else:
            reverse_ships = ReverseShipment.objects.filter(
                pickup_service_centre=request.user.employeemaster.service_centre,
                status=0).order_by('-added_on').exclude(airwaybill_number=None,shipment__reason_code__code__in=[420, 419, 418, 416, 415, 414, 413, 411, 406, 405, 404, 400])

    for ship in reverse_ships:
         #import barcode
         if ship.airwaybill_number:
             EAN = barcode.get_barcode_class('code128')
             ean = EAN(str(ship.airwaybill_number),writer=barcode.writer.ImageWriter())
             ean.default_writer_options['module_height'] = 4.0
             ean.default_writer_options['module_width'] = 0.1  
             ean.save('/home/web/ecomm.prtouch.com/ecomexpress/static/airwaybill/{0}'.format(ship.airwaybill_number))
     
    return render_to_response(
         "pickup/reverse_pickup_sheet.html",
         {'shipment':reverse_ships}, 
         context_instance=RequestContext(request))


def reverse_shipment_single_print(request, awb):
    sh = Shipment.objects.filter(airwaybill_number=int(awb))
    if sh:
        ship =  sh[0]
        EAN = barcode.get_barcode_class('code128')
        ean = EAN(str(ship.airwaybill_number),writer=barcode.writer.ImageWriter())
        ean.default_writer_options['module_height'] = 4.0
        ean.default_writer_options['module_width'] = 0.1
        ean.save('/home/web/ecomm.prtouch.com/ecomexpress/static/airwaybill/{0}'.format(ship.airwaybill_number))
        return render_to_response("pickup/reverse_pickup_sheet.html",
            {'shipment':sh},context_instance=RequestContext(request))
    else:
        return HttpResponse("Invalid AWB")


@csrf_exempt
def update_employee(request):
     if request.POST:
        pickup_id = request.POST['pickup_id']
        employee_code = request.POST['emp_code']
        emp=EmployeeMaster.objects.filter(employee_code=employee_code)
        if emp:
            pickup=PickupRegistrationEmployee.objects.filter(pickup_id=pickup_id)
            if pickup:
                      pickup.update(employee_code=employee_code)
            else:
                      PickupRegistrationEmployee.objects.create(employee_code=employee_code,pickup_id=pickup_id)
            ships=Shipment.objects.filter(pickup_id=pickup_id)
            ships_records=[]
            for s in ships:
                if s.product_type<>"cod":
                   prod_type="N"
                else:
                   prod_type="Y"
                cust=s.shipper
                email=cust.email
                city=s.pickup.service_centre.city.city_name
                try:
                  op=s.order_price_set.get()
                  frt=op.freight_charge
                except:
                  frt=0
                #user=emp[0].email.split("@")
                if emp[0].email:
                    user=emp[0].email.split("@")
                    email=user[0]
                else:
                    email=""
                con_email=""
                record={"AssignmentNo":s.airwaybill_number,"AssignmentType":"E","NoOfPcs":s.pieces,"PickupTime":s.pickup.added_on.strftime("%d-%m-%Y %H:%M"),"Weight":s.chargeable_weight,"ShipperAccNo":cust.code,"PickUpID":s.pickup.id,"ShipperName":s.pickup.customer_name,"ShipperAddress1":s.pickup.address_line1,"ShipperAddress2":s.pickup.address_line2,"ShipperCity":city,"ShipperPincode":s.pickup.customer_code.address.pincode,"ShipperEmail":con_email,"ShipperContactNo":s.pickup.mobile,"isFreight":"Y","Freight AMT":frt,"UserName":email}
                ships_records.append(record)
        #return HttpResponse(len(ships_record))
        resp_dict={}
        resp_dict["shipments"]=ships_records
        #return HttpResponse(ships_records)
        response=simplejson.dumps(resp_dict)
        #response=(simplejson.dumps(pickup_dict),content_type="application/json")
        #return HttpResponse(response)
        #data={'success':True,'remark':pickup_id,'id':employee_code}
        code="C00000002"
        password="traconmobi@123"
        data="""<?xml version="1.0" encoding="utf-8"?>
                 <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                 <soap:Body>
                  <TOM_PCK_IMPORT xmlns="http://navatech.cloudapp.net/TOMWS/">
                  <objValue>
                     <customerCode>"""+code+"""</customerCode>
                     <Password>"""+password+"""</Password>
                     <JsonPickupData>"""+str(response)+"""</JsonPickupData>
                  </objValue>
                  </TOM_PCK_IMPORT>
                  </soap:Body>
                  </soap:Envelope>"""
        headers = {
    'Host': 'navatech.cloudapp.net',
    'Content-Type': 'text/xml; charset=utf-8',
    'Content-Length': len(data),
    'SOAPAction': "http://navatech.cloudapp.net/TOMWS/TOM_PCK_IMPORT"
    }
        #return HttpResponse(data)
        site="http://navatech.cloudapp.net/TOMWS/Pickup.asmx?op=TOM_PCK_IMPORT"
        auth_handler = urllib2.HTTPBasicAuthHandler()
        opener = urllib2.build_opener(auth_handler)
        urllib2.install_opener(opener)
        page = urllib2.urlopen(site)
        req = urllib2.Request(site, data, headers)
        resp = urllib2.urlopen(req)
        the_page = resp.read()
        print "response is "
        print (the_page)
        #response = the_page
        return HttpResponse(the_page,response)
        return True
       
        #return the_page

def download_xcl(request):
    file_name = 'pickup_file.xlsx'
    report = ReportGenerator(file_name)
    col_heads = ('Air Waybill number','Order Number','Product','Shipper','Consignee','Consignee Address1','Consignee Address2','Consignee Address3','Destination City','Pincode','State','Mobile','Telephone','Item Description','Pieces','Collectable Value','Declared value','Actual Weight','Volumetric Weight','Length(cms)','Breadth(cms)','Height(cms)','sub customer id','Pickup name','Pickup Address','Pickup Phone','Pickup Pincode','Return name','Return Address','Return Phone','Return Pincode')
    report.write_header(col_heads)
    file_name = report.manual_sheet_close()
    excel_file = open(settings.FILE_UPLOAD_TEMP_DIR + '/reports/' + file_name, "rb").read()
    response = HttpResponse(excel_file, mimetype='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=%s' %  file_name
    return response
 
def mass_upload(request):
    return render_to_response(
          "pickup/reverse/mass_upload.html",
           context_instance=RequestContext(request))

@csrf_exempt
def multiple_rvp(request):
    if request.POST:
         ship_file = request.FILES['upload_file']
         content = ship_file.read()       
         wb = xlrd.open_workbook(file_contents=content)
         sheetnames = wb.sheet_names()
         sh = wb.sheet_by_name(sheetnames[0])
         awbs= sh.col_values(0)[1:]
            
         rc = None
         for awb in awbs:
             rvp = ReverseShipment.objects.get(airwaybill_number=int(awb))
             ship = rvp.shipment
             if rc:
                 reason_code = ShipmentStatusMaster.objects.get(code=rc)
             else:
                 reason_code = None
             ship.reason_code=reason_code
             ship.save()
             rvp.status=0
             rvp.save()
             emp = EmployeeMaster.objects.get(employee_code=124)
             update_shipment_history(ship, reason_code=reason_code, status=31, sc=rvp.pickup_service_centre,employee_code=emp, remarks="Shipment reopened")

    return HttpResponseRedirect("/pickup/reverse_shipment/")

@csrf_exempt
def multiple_rvp_remove(request):
    if request.POST:
         ship_file = request.FILES['upload_file']
         content = ship_file.read()
         wb = xlrd.open_workbook(file_contents=content)
         sheetnames = wb.sheet_names()
         sh = wb.sheet_by_name(sheetnames[0])
         awbs= sh.col_values(0)[1:]

         rc = None
         for awb in awbs:
	     rvp = ReverseShipment.objects.get(airwaybill_number=awb)
             ship = rvp.shipment
             if rc:
                  reason_code = ShipmentStatusMaster.objects.get(code=rc)
             else:
                  reason_code = ShipmentStatusMaster.objects.get(code=404)
             ship.reason_code=reason_code
             ship.save()
             rvp.status=2
             rvp.save()
             emp = EmployeeMaster.objects.get(employee_code=124)
             update_shipment_history(ship, reason_code=reason_code, status=33, sc=rvp.pickup_service_centre,
                  employee_code=emp, remarks="Shipment removed from dashboard")

    return HttpResponseRedirect("/pickup/reverse_shipment/")

