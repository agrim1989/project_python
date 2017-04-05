# Create your views here.
import datetime
import xlwt
import json
from decimal import *
from xlsxwriter.workbook import Workbook
from collections import defaultdict

from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils import simplejson
from django.views.decorators.csrf import csrf_exempt
from django.db.models import get_model
from django.core.management import call_command
from django.db.models import Q
from django.conf import settings
from jsonview.decorators import json_view

from billing.models import *
from customer.models import Customer
from location.models import ServiceCenter, Region, State
from service_centre.models import *
from track_me.models import *
from reports.noinfo_report import generate_noinfo_report
from reports.cod_collection_pod_report import CodCollectionPodReport
from reports.cash_tally_reports import scwise_daily_cash_tally_report
from reports.correction_report import generate_correction_report
from reports.telecalling_report import *
from reports.pickup_report import *
from reports.overage_report import *
from reports.Invoice_Trf_eepl_to_Tally import generate_invoicetrfreport
from reports.invoice_xml import *
from reports.wb_entry_tax  import generate_wbtax_report
from reports.bag_reports import bag_exception_inbound_report, bag_exception_outbound_report
from reports.bag_reports import unconnected_bag_report, bag_inscan_unconnected_report
from reports.bag_reports import bag_hub_inscan_report
from reports.report_api import ReportGenerator
from reports.daywise_charge_misc import get_daywise_charge_report
from reports.forms import ReportSearchForm

count = 1

def removeNonAscii(s): return "".join(i for i in s if ord(i)<128)

now = datetime.datetime.now()
monthdir = now.strftime("%Y_%m")
nextmonth = now + datetime.timedelta(days=1)
nextmonth = nextmonth.strftime("%Y_%m")


book = xlwt.Workbook(encoding='utf8')
default_style = xlwt.Style.default_style
datetime_style = xlwt.easyxf(num_format_str='dd/mm/yyyy')
date_style = xlwt.easyxf(num_format_str='dd/mm/yyyy')
header_style = xlwt.XFStyle()
status_style = xlwt.XFStyle()
category_style = xlwt.XFStyle()
font = xlwt.Font()
font.bold = True

pattern = xlwt.Pattern()
pattern.pattern = xlwt.Pattern.SOLID_PATTERN
pattern.pattern_fore_colour = 5

pattern1 = xlwt.Pattern()
pattern1.pattern = xlwt.Pattern.SOLID_PATTERN
pattern1.pattern_fore_colour = 0x0A

borders = xlwt.Borders()
borders.left = xlwt.Borders.THIN
borders.right = xlwt.Borders.THIN
borders.top = xlwt.Borders.THIN
borders.bottom = xlwt.Borders.THIN
header_style.pattern = pattern
status_style.pattern = pattern1
header_style.font = font
category_style.font = font
header_style.borders=borders
default_style.borders=borders

'''
def get_morn_time_added_date(date_str):
    dt = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    return dt.strftime('%Y-%m-%d 07:00:00')

def get_today_str():
    d = datetime.date.today()
    return d.strftime('%Y-%m-%d')

def get_last_date_str():
    d = datetime.date.today() - datetime.timedelta(days=1)
    return d.strftime('%Y-%m-%d')

def query(customer, date_from, date_to, sc):
        q = Q()
        if customer == "0":
            customer = None
        else:
            q = q & Q(shipper_id = int(customer))
        if not (date_from and date_to):
            pass
        else:
            t = datetime.datetime.strptime(date_to, "%Y-%m-%d") + datetime.timedelta(days=1)
            date_to = t.strftime("%Y-%m-%d")
            q = q & Q(expected_dod__range=(date_from,date_to))
        if sc == "0":
            sc = None
        else:
            q = q & Q(service_centre_id=int(sc))
        shipments = Shipment.objects.using('local_ecomm').filter(q).exclude(status_type=5, reason_code__id = 1)
        return shipments


def query_cod(customer, date_from, date_to, sc):
        q = Q()
        if customer == "0":
            customer = None
        else:
            q = q & Q(shipper_id = int(customer))
        if not (date_from and date_to):
            pass
        else:
            t = datetime.datetime.strptime(date_to, "%Y-%m-%d") + datetime.timedelta(days=1)
            date_to = t.strftime("%Y-%m-%d")
            q = q & Q(expected_dod__range=(date_from,date_to))
        if sc == "0":
            sc = None
        else:
            q = q & Q(service_centre_id=int(sc))
        #shipments = Shipment.objects.using('local_ecomm').filter(q).exclude(status_type=5)
        shipments = Shipment.objects.using('local_ecomm').filter(q)
        return shipments

def excel_download(distinct_list, rtype):

    sheet = book.add_sheet(rtype)
    sheet.write(0, 2, "%s Report"%(rtype), style=header_style)
    for a in range(9):
        sheet.col(a).width = 6000
    sheet.write(3, 0, "Origin Service Centre", style=header_style)
    sheet.write(3, 1, "Pickup Date", style=header_style)
    sheet.write(3, 2, "Destination Service Centre", style=header_style)
    sheet.write(3, 3, "Air waybill Number", style=header_style)
    sheet.write(3, 4, "Order Number", style=header_style)
    sheet.write(3, 5, "Shipper", style=header_style)
    sheet.write(3, 6, "Consignee", style=header_style)
    sheet.write(3, 7, "Collectable Value", style=header_style)
    sheet.write(3, 8, "Reason Code", style=header_style)
    sheet.write(3, 9, "Status Updated On", style=header_style)
    sheet.write(3, 10, "Mobile Number", style=header_style)
    sheet.write(3, 11, "Remarks", style=header_style)

    for row, rowdata in enumerate(distinct_list, start=4):
        for col, val in enumerate(rowdata, start=0):
                     style = datetime_style
		     try:
	                sheet.write(row, col, str(val), style=style)
		     except:
			pass
    response = HttpResponse(mimetype='application/vnd.ms-excel')
    return response

def reports_dashboard(request):
    form = ReportSearchForm(request.user)
    return render_to_response("reports/reports-dashboard.html", {'form': form},context_instance=RequestContext(request))

'''
def get_report(report_type, customer, origin_city, dest_city, origin_state, dest_state, origin_region, dest_region, from_date, to_date):

    q = Q()
    #return HttpResponse(origin_city)
    if not origin_city and not origin_region and not origin_state:
        city = ServiceCenter.objects.all()
        q = q & Q(pickup__service_centre__in=city)
    if not dest_city and not dest_region and not dest_state:
        city = ServiceCenter.objects.all()
        q = q & Q(original_dest__in=city)
    if origin_city:
        city = ServiceCenter.objects.filter(id__in=origin_city)
        q = q & Q(pickup__service_centre__in=city)
    if dest_city:
        city = ServiceCenter.objects.filter(id__in=dest_city)
        q = q & Q(original_dest__in=city)
    if origin_state:
        if origin_state != "0":
            state_id=State.objects.filter(id__in=origin_state)
            q = q & Q(pickup__service_centre__city__state_id__in=state_id)
    if dest_state:
        if dest_state != "0":
            state_id=State.objects.filter(id__in=dest_state)
            q = q & Q(original_dest__service_centre__city__state_id__in=state_id)
    if origin_region:
        if origin_region != "0":
            region_id=Region.objects.filter(id__in=origin_region)
            q = q & Q(pickup__service_centre__city__region_id__in=region_id)
    if dest_region:
        if dest_region != "0":
            region_id=Region.objects.filter(id__in=dest_region)
            q = q & Q(original_dest__service_centre__city__region_id___in=region_id)
       
    date_from = datetime.datetime.strptime(from_date, "%Y-%m-%d")
    t = datetime.datetime.strptime(to_date, "%Y-%m-%d") + datetime.timedelta(days=1)
    date_from = date_from.strftime("%Y-%m-%d")
    date_to = t.strftime("%Y-%m-%d")
    q = q & Q(added_on__range=(date_from,date_to))
    if report_type == "1":
        shipments = Shipment.objects.filter(q,status__in=[7,8]).exclude(reason_code=5).exclude(reason_code__code__in=[216,208,202,311,200,111, 777, 999, 888, 333, 310,213]).exclude(reason_code__in=[52,4]).exclude(rts_status__gte=1)
        #return HttpResponse(shipments)
        shipment_info={}
        download_list = []

        for a in shipments:
            if a.reason_code_id != 1:
           # if a.reason_code_id != 1 and a.reason_code_id !=34 and a.reason_code_id !=5 and a.ref_airwaybill_number !="" and a.return_shipment !=2:
                teleList = TeleCallingReport.objects.using('local_ecomm').filter(shipment__airwaybill_number=a.airwaybill_number)
                tele = ''
                if teleList:
                  tele = teleList.latest('id')
                comment =''
                if tele:
                    comment = tele.comments

                if not shipment_info.get(a):
                    upd_time = a.added_on
                    monthdir = upd_time.strftime("%Y_%m")
                    shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
                    history = shipment_history.objects.using('local_ecomm').filter(shipment=a)
                    upd_date = history.latest('updated_on').updated_on.date() if history.exists() else ''
                    supd = a.statusupdate_set.filter()
                    if supd:
                       su = supd.latest('added_on')
                       rs = su.reason_code.code
                       rsd = su.reason_code.code_description
                       remarks = su.remarks
                    else:
                       continue
                       rs = ""
                       rsd = ""
                       remarks = ""
                    sc = a.original_dest
                    if a.ref_airwaybill_number and Shipment.objects.using('local_ecomm').filter(airwaybill_number = a.ref_airwaybill_number):
                                    rts_shipment = Shipment.objects.using('local_ecomm').get(airwaybill_number = a.ref_airwaybill_number)
                                    try:
                                        rts_history = shipment_history.objects.using('local_ecomm').filter(shipment=rts_shipment).latest('updated_on')
                                    except:
                                        rts_history = ""
                       # rts_updated_on = rts_history
                                    if rts_history:
                                        rts_updated_on = rts_history.updated_on.strftime("%d-%m-%Y")
                                    else:
                                        rts_updated_on = ""
                                    u = (a.airwaybill_number, a.order_number, a.added_on.date(), a.pickup.service_centre.center_name, sc,
                                         a.pickup.service_centre.city.region.region_name, a.pickup.service_centre.city.state.state_name,
                                         a.shipper, a.consignee, a.collectable_value, upd_date, a.mobile, rs, rsd, remarks,
                                         a.deliveryoutscan_set.filter().only('id').count(),comment,a.current_sc, a.status)
                    else:
                        u = (a.airwaybill_number, a.order_number, a.added_on.date(), a.pickup.service_centre.center_name, sc,
                             a.pickup.service_centre.city.region.region_name, a.pickup.service_centre.city.state.state_name, 
                             a.shipper, a.consignee, a.collectable_value, upd_date, a.mobile, rs, rsd, remarks,
                             a.deliveryoutscan_set.filter().only('id').count(),comment,a.current_sc, a.status)

                    download_list.append(u)
                    shipment_info[a]=history
        report = ReportGenerator('NDR_report.xlsx')
        col_heads = ('Airwaybill no', 'Order no', 'Pickup Date', 'Origin SC', 'Destination SC', 'Origin Region', 'Origin State',
                     'Shipper', 'Consignee', 'Collectable Value', 'Mobile no', 'Reason Code', 'Reason Code Description', 
                     'Remarks', 'No. of attempts', 'Comment', 'Current SC','Status')
        report.write_header(col_heads)
        report.write_body(download_list)
        file_name = report.manual_sheet_close()
        return file_name
       
'''
@csrf_exempt
def customer_status_reports(request):
    date_to = 0
    #return "welcome"
    date_from = request.POST['date_from']
    date_to = request.POST['date_to']
    if date_to:
         t = datetime.datetime.strptime(date_to, "%Y-%m-%d") + datetime.timedelta(days=1)
         date_to = t.strftime("%Y-%m-%d")
    shipments = Shipment.objects.using('local_ecomm').filter(shipper__code=request.user.employeemaster.lastname, added_on__range=(date_from, date_to))
    download_list = []
    for a in shipments:
         shipment = a
         rs = "In Transit"
         rem_status = 0
         upd_time = a.added_on
         monthdir = upd_time.strftime("%Y_%m")
         shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
         rto_status = shipment_history.objects.using('local_ecomm').filter(shipment=shipment, reason_code_id = 34)
         rem_status = shipment_history.objects.using('local_ecomm').filter(shipment=shipment, remarks = "Return to Origin")
         history = shipment_history.objects.using('local_ecomm').filter(shipment=a).latest('updated_on')
         if a.return_shipment == 0:
                                sc = a.service_centre
         else:
                                sc = a.original_dest
         if a.statusupdate_set.all():
                       su = shipment.statusupdate_set.all().order_by("-date","-time")[:1][0]
                       received_by = su.recieved_by
                       time  = su.time.strftime("%H:%m")
                       date  = su.date.strftime("%d-%m-%Y")
         else:
                       received_by = ""
                       date = ""
                       time = ""
         if not a.reason_code:
             rs = "In Transit"
         else:
             rs = a.reason_code
         try:
                      vendor = str(shipment.pickup.subcustomer_code) +" - "+str(shipment.pickup.subcustomer_code.id)
         except:
                      vendor = ""
         if shipment:
                              val = shipment.status
                              if str(val) == '0':
                                         val="Shipment Uploaded"
                              if str(val)== '1':
                                           val='Pickup Complete / Inscan'
                              if str(val)== '2':
                                        val='Inscan completion / Ready for Bagging'
                              if str(val)== '3':
                                   val='Bagging completed'
                              if str(val)== '4':
                                    val='Shipment at HUB'
                              if str(val)== '5':
                                       val='Bagging completed at Hub'
                              if str(val)== '6':
                                      val='Shipment at Delivery Centre'
                              if str(val)== '7':
                                     val='Outscan'
                              if str(val)== '8':
                                 val='Undelivered'
                              if str(val)==  '9':
                                  val='Delivered / Closed'
                              if str(val)== '11':
                                   val='Alternate Instruction given'
                              if str(val)== '13':
                                   val='Assigned to Run Code'
                              if str(val)==  '14':
                                      val='Airport Confirmation Sucessfull, connected to destination via Service Centre'
                              if str(val)== '15':
                                  val='Airport Confirmation Successfull, connected to destination via Hub'
                              if (shipment.reason_code_id == 5 or shipment.return_shipment==2 or rto_status or rem_status):
                                  val = "Returned"

         if shipment.ref_airwaybill_number and Shipment.objects.using('local_ecomm').filter(airwaybill_number = shipment.ref_airwaybill_number):
                       rts_shipment = Shipment.objects.using('local_ecomm').get(airwaybill_number = shipment.ref_airwaybill_number)
                       try:
                          rts_history = shipment_history.objects.using('local_ecomm').filter(shipment=rts_shipment).latest('updated_on')
                       except:
                          rts_history = ""
                       # rts_updated_on = rts_history
                       if rts_history:
                          rts_updated_on = rts_history.updated_on.strftime("%d-%m-%Y")
                       else:
                          rts_updated_on = ""
                       if rts_shipment:
                              rts_val = rts_shipment.status
                              if str(rts_val) == '0':
                                         rts_val="Shipment Uploaded"
                              if str(rts_val)== '1':
                                           rts_val='Pickup Complete / Inscan'
                              if str(rts_val)== '2':
                                        rts_val='Inscan completion / Ready for Bagging'
                              if str(rts_val)== '3':
                                   rts_val='Bagging completed'
                              if str(rts_val)== '4':
                                    rts_val='Shipment at HUB'
                              if str(rts_val)== '5':
                                       rts_val='Bagging completed at Hub'
                              if str(rts_val)== '6':
                                      rts_val='Shipment at Delivery Centre'
                              if str(rts_val)== '7':
                                    rts_val='Outscan'
                              if str(rts_val)== '8':
                                 rts_val='Undelivered'
                              if str(rts_val)==  '9':
                                  rts_val='Delivered / Closed'
                              if str(rts_val)== '13':
                                   rts_val='Assigned to Run Code'
                              if str(rts_val)==  '14':
                                      rts_val='Airport Confirmation Sucessfull, connected to destination via Service Centre'
                              if str(rts_val)== '15':
                                  rts_val='Airport Confirmation Successfull, connected to destination via Hub'
         else:
             shipment.ref_airwaybill_number=""
             rts_val = ""
             rts_updated_on = ""
         u = (a.airwaybill_number, a.order_number,a.collectable_value, a.pickup.service_centre.center_name, sc, a.added_on, a.shipper, vendor, a.consignee, rs, received_by, date, time, val, history.updated_on.date(), shipment.ref_airwaybill_number, rts_val, rts_updated_on, shipment.return_shipment)
         download_list.append(u)
    if download_list:
                sheet = book.add_sheet('Customer Report')
                distinct_list = download_list
                sheet.write(0, 2, "Customer Report", style=header_style)
                for a in range(23):
                    sheet.col(a).width = 6000
                sheet.col(8).width = 10000
                sheet.col(9).width = 6000
                sheet.write(3, 0, "Air Waybill No", style=header_style)
                sheet.write(3, 1, "Order No", style=header_style)
                sheet.write(3, 2, "COD Amount", style=header_style)
                sheet.write(3, 3, "Origin", style=header_style)
                sheet.write(3, 4, "Destination", style=header_style)
                sheet.write(3, 5, "P/U Date", style=header_style)
                sheet.write(3, 6, "Shipper", style=header_style)
                sheet.write(3, 7, "Vendor", style=header_style)
                sheet.write(3, 8, "Consignee", style=header_style)
                sheet.write(3, 9, "Reason", style=header_style)
                sheet.write(3, 10, "Received by", style=header_style)
                sheet.write(3, 11, "Del Date", style=header_style)
                sheet.write(3, 12, "Del Time", style=header_style)
                sheet.write(3, 13, "Status", style=header_style)
                sheet.write(3, 14, "Updated On", style=header_style)
                sheet.write(3, 15, "Ref Air Waybill (RTS)", style=header_style)
                sheet.write(3, 16, "Status", style=header_style)
                sheet.write(3, 17, "Updated on", style=header_style)
                style = datetime_style
                counter = 1

                for row, rowdata in enumerate(distinct_list, start=4):
                        if rowdata[18] == 3:
                            style = status_style
                        else:
                            style = datetime_style
                        for col, val in enumerate(rowdata, start=0):
                            if col <> 18:
                              try:
                                 sheet.write(row, col, str(val), style=style)
                              except:
                                   pass
                response = HttpResponse(mimetype='application/vnd.ms-excel')
                response['Content-Disposition'] = 'attachment; filename=customer_report.xls'
                book.save(response)
                return response

    response = excel_download(download_list, "Customer")
    response['Content-Disposition'] = 'attachment; filename=Customer_Report.xls'
    book.save(response)
    return response

def ndr(q):
    if request.POST:
        customer = request.POST['cust_id']
        date_from = request.POST['date_from']
        date_to = request.POST['date_to']
        sc=request.POST['sc']
        region_name = request.POST.get('region')
        state_name = request.POST.get('state')
       # shipments = query(customer, date_from, date_to, sc)

        report_type = request.POST['report_type']
        q = Q()
        if customer == "0":
            customer = None
        else:
            q = q & Q(shipper = int(customer))
        if not (date_from and date_to):
            pass
        else:
            t = datetime.datetime.strptime(date_to, "%Y-%m-%d") + datetime.timedelta(days=1)
            date_to = t.strftime("%Y-%m-%d")
            q = q & Q(added_on__range=(date_from,date_to))
        if sc == "0":
            sc = None
        else:
            q = q & Q(service_centre=int(sc))
        if region_name:
            if region_name != "0":
                region_id=Region.objects.filter(region_shortcode__in=region_name)
                q = q & Q(pickup__service_centre__city__region__region_name__in=region_id)
        if state_name:
            if state_name != "0":
                state_id=State.objects.filter(state_shortcode__in=state_name)
                q = q & Q(pickup__service_centre__city__state__state_name__in=state_id)
    
    shipments = Shipment.objects.filter(q,status__in=[7,8]).exclude(reason_code=5).exclude(reason_code__code__in=[216,208,202,311,200,111, 777, 999, 888, 333, 310,213]).exclude(reason_code__in=[52,4]).exclude(rts_status__gte=1)
    return HttpResponse(shipments)
    shipment_info={}
    download_list = []

    for a in shipments:
        if a.reason_code_id != 1:
           # if a.reason_code_id != 1 and a.reason_code_id !=34 and a.reason_code_id !=5 and a.ref_airwaybill_number !="" and a.return_shipment !=2:
                teleList = TeleCallingReport.objects.using('local_ecomm').filter(shipment__airwaybill_number=a.airwaybill_number)
                tele = ''
                if teleList:
                  tele = teleList.latest('id')
                comment =''
                if tele:
                    comment = tele.comments

                if not shipment_info.get(a):
                    upd_time = a.added_on
                    monthdir = upd_time.strftime("%Y_%m")
                    shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
                    history = shipment_history.objects.using('local_ecomm').filter(shipment=a)
                    upd_date = history.latest('updated_on').updated_on.date() if history.exists() else ''
                    supd = a.statusupdate_set.filter()
                    if supd:
                       su = supd.latest('added_on')
                       rs = su.reason_code.code
                       rsd = su.reason_code.code_description
                       remarks = su.remarks
                    else:
                       continue
                       rs = ""
                       rsd = ""
                       remarks = ""
                    sc = a.original_dest
                    if a.ref_airwaybill_number and Shipment.objects.using('local_ecomm').filter(airwaybill_number = a.ref_airwaybill_number):
                                    rts_shipment = Shipment.objects.using('local_ecomm').get(airwaybill_number = a.ref_airwaybill_number)
                                    try:
                                        rts_history = shipment_history.objects.using('local_ecomm').filter(shipment=rts_shipment).latest('updated_on')
                                    except:
                                        rts_history = ""
                       # rts_updated_on = rts_history
                                    if rts_history:
                                        rts_updated_on = rts_history.updated_on.strftime("%d-%m-%Y")
                                    else:
                                        rts_updated_on = ""
                                    u = (a.airwaybill_number, a.order_number, a.added_on.date(), a.pickup.service_centre.center_name, sc,
                                         a.pickup.service_centre.city.region.region_name, a.pickup.service_centre.city.state.state_name,
                                         a.shipper, a.consignee, a.collectable_value, upd_date, a.mobile, rs, rsd, remarks,
                                         a.deliveryoutscan_set.filter().only('id').count(),comment,a.current_sc, a.status)
                    else:
                        u = (a.airwaybill_number, a.order_number, a.added_on.date(), a.pickup.service_centre.center_name, sc,
                             a.pickup.service_centre.city.region.region_name, a.pickup.service_centre.city.state.state_name, 
                             a.shipper, a.consignee, a.collectable_value, upd_date, a.mobile, rs, rsd, remarks,
                             a.deliveryoutscan_set.filter().only('id').count(),comment,a.current_sc, a.status)

                    download_list.append(u)
                    shipment_info[a]=history
    report = ReportGenerator('NDR_report.xlsx')
    col_heads = ('Airwaybill no', 'Order no', 'Pickup Date', 'Origin SC', 'Destination SC', 'Origin Region', 'Origin State',
                 'Shipper', 'Consignee', 'Collectable Value', 'Mobile no', 'Reason Code', 'Reason Code Description', 
                 'Remarks', 'No. of attempts', 'Comment', 'Current SC','Status')
    report.write_header(col_heads)
    report.write_body(download_list)
    file_name = report.manual_sheet_close()
    return file_name

@csrf_exempt
def performance_analysis(request):
    if request.POST:
        customer = request.POST['cust_name']
        if request.POST['month']:
            year_month = request.POST['month']
            month = year_month.split("-")
            date_from =''
            date_to =''
	else:
            year_month = now.strftime("%Y-%m")

            month=year_month.split("-")
        if request.POST['date_from']:
            date_from = request.POST['date_from']
        if request.POST['date_to']:
            date_to = request.POST['date_to']
            month = ''
            year_month = ''
        sc = request.POST['sc']
        # shipments = Shipment.objects.filter(added_on__range=(month+"-01",month+"-31")
        dl_report = request.POST['dl_report']
        q = Q()
        if customer == "0":
            customer = None
        else:
            q = q & Q(shipper_id = int(customer))

        if not (month):
            t = datetime.datetime.strptime(date_to, "%Y-%m-%d") + datetime.timedelta(days=1)
            dated_to = t.strftime("%Y-%m-%d")
            q = q & Q(added_on__range=(date_from,dated_to))

        else:
            q = q & Q(added_on__year=month[0], added_on__month=month[1])

        if sc == "0":
            sc = None
        else:
            q = q & Q(original_dest_id=int(sc))
        p=1
        c=1
        ppd_shipment = Shipment.objects.using('local_ecomm').filter(q, product_type="ppd").exclude(return_shipment=3)
        ppd_shipment_count = ppd_shipment.only('id').count()
	shipment_ppd = Shipment.objects.using('local_ecomm').filter(q, product_type="ppd", status=9).exclude(return_shipment=3)
        delivered_ppd_count = shipment_ppd.only('id').count()

        if ppd_shipment_count == 0:
            p = 0
            ppd_shipment_count = 1
        ppd_delivered_perc = round((((float(delivered_ppd_count)/float(ppd_shipment_count)))*100.0),2)

        rto_ppd = Shipment.objects.using('local_ecomm').filter(q, product_type="ppd", return_shipment=2)
        rto_ppd_count = rto_ppd.only('id').count()
        ppd_rto_perc = round((((float(rto_ppd_count)/float(ppd_shipment_count)))*100.0),2)

        cod_shipment = Shipment.objects.using('local_ecomm').filter(q, product_type="cod").exclude(return_shipment=3)
        cod_shipment_count = cod_shipment.only('id').count()
	shipment_cod = Shipment.objects.using('local_ecomm').filter(q, product_type="cod", status=9).exclude(return_shipment=3)
        delivered_cod_count = shipment_cod.only('id').count()
        if cod_shipment_count == 0:
            c = 0
            cod_shipment_count = 1

       # delivered_cod = StatusUpdate.objects.filter(shipment__in=cod_shipment, status=2)
       # delivered_cod_count = delivered_cod.only('id').count()
        cod_delivered_perc = round((((float(delivered_cod_count)/float(cod_shipment_count)))*100.0),2)

        rto_cod = Shipment.objects.using('local_ecomm').filter(q, product_type="cod", return_shipment=2)
        rto_cod_count = rto_cod.only('id').count()
        cod_rto_perc = round((((float(rto_cod_count)/float(cod_shipment_count)))*100.0),2)

        total_delivered = delivered_ppd_count + delivered_cod_count
        total= ppd_shipment_count + cod_shipment_count
        g_del_perc = round((((float(total_delivered)/float(total)))*100.0),2)

        total_rto = rto_ppd_count + rto_cod_count
        g_rto_perc = round((((float(total_rto)/float(total)))*100.0),2)
        if p == 0:
            ppd_shipment_count = 0
        if c == 0:
            cod_shipment_count = 0
        if not (year_month):
            year_month = str(date_from)+' To '+str(date_to)


        if dl_report == "Download":
            sheet = book.add_sheet('Performance Analysis')
            sheet.write(0, 2, "Performance Analysis", style=header_style)

            for a in range(7):
                sheet.col(a).width = 3000

            sheet.write(3, 0, "Product", style=header_style)
            sheet.write(3, 1, "Month", style=header_style)
            sheet.write(3, 2, "Count", style=header_style)
            sheet.write(3, 3, "Delivered", style=header_style)
            sheet.write(3, 4, "%Age", style=header_style)
            sheet.write(3, 5, "RTO", style=header_style)
            sheet.write(3, 6, "%Age", style=header_style)

            sheet.write(4, 0, "Prepaid", style=header_style)
            sheet.write(5, 0, "COD", style=header_style)
            sheet.write(6, 0, "G Total", style=header_style)

            sheet.write(4, 1, year_month)
            sheet.write(5, 1, year_month)
            sheet.write(4, 2, str(ppd_shipment_count))
            sheet.write(5, 2, str(cod_shipment_count))
            sheet.write(6, 2, str(total))

            sheet.write(4, 3, str(delivered_ppd_count)+'/'+str(ppd_shipment_count))
            sheet.write(4, 4, str(ppd_delivered_perc)+'%')
            sheet.write(5, 3, str(delivered_cod_count)+'/'+str(cod_shipment_count))
            sheet.write(5, 4, str(cod_delivered_perc)+'%')
            sheet.write(6, 3, str(total_delivered)+'/'+str(total))
            sheet.write(6, 4, str(g_del_perc)+'%')

            sheet.write(4, 5, str(rto_ppd_count)+'/'+str(ppd_shipment_count))
            sheet.write(4, 6, str(ppd_rto_perc)+'%')
            sheet.write(5, 5, str(rto_cod_count)+'/'+str(cod_shipment_count))
            sheet.write(5, 6, str(cod_rto_perc)+'%')
            sheet.write(6, 5, str(total_rto)+'/'+str(total))
            sheet.write(6, 6, str(g_rto_perc)+'%')

            response = HttpResponse(mimetype='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename=Performance-Analysis.xls'
            book.save(response)
            return response
        else:
            return render_to_response('reports/reports-performanceanalysis.html',
                                  {'ppd_shipment':ppd_shipment_count,
                                   'cod_shipment':cod_shipment_count,
                                   'total':total,
                                   'month':year_month,
                                   'total':total,
                                   'delivered_ppd_count':delivered_ppd_count,
                                   'delivered_cod_count':delivered_cod_count,
                                   'rto_ppd_count':rto_ppd_count,
                                   'rto_cod_count':rto_cod_count,
                                   'total_delivered':total_delivered,
                                   'total_rto':total_rto,
                                   'ppd_delivered':ppd_delivered_perc,
                                   'cod_delivered':cod_delivered_perc,
                                   'cod_rto_perc':cod_rto_perc,
                                   'ppd_rto_perc':ppd_rto_perc,
                                    'g_del_perc':g_del_perc,
                                   'g_rto_perc':g_rto_perc,

                                   },
                                  context_instance=RequestContext(request))

    customer=Customer.objects.using('local_ecomm').all()
    sc = ServiceCenter.objects.using('local_ecomm').all()

    return render_to_response("reports/performanceanalysis.html",
                              {'customer':customer,
                               'sc':sc},
                               context_instance=RequestContext(request))

def get_strike_rate_from_shipments(shipments, strike_rate_dict):
    for shipment in shipments:
        # get the first outscan date for the given shipment
	    outscan_added_on = DeliveryOutscan.objects.using('local_ecomm').filter(shipments=shipment).order_by('added_on')
            if outscan_added_on:
                   outscan_added_on = outscan_added_on[0].added_on
                   expected_dod = shipment.expected_dod
                   d2 = datetime.datetime.date(outscan_added_on)
                   if not expected_dod:
                        d1= shipment.added_on.date() + datetime.timedelta(days=2)
                   else:
                        d1 = datetime.datetime.date(expected_dod)

                   days = int((d2-d1).days)
            else:
               days = 6
            if days < 0:
                strike_rate_dict[0] += 1
            elif days <= 3:
                strike_rate_dict[days] += 1
            else:
                strike_rate_dict[4] += 1

    return strike_rate_dict

def get_strike_rate_from_shipments_del(shipments, strike_rate_dict_del):
    for shipment in shipments:
        # get the first delivery date for the given shipment
            su_added_on = StatusUpdate.objects.using('local_ecomm').filter(shipment=shipment, status=2).order_by('added_on')
            if su_added_on:
                   su_added_on = su_added_on[0].added_on
                   expected_dod = shipment.expected_dod
                   d2 = datetime.datetime.date(su_added_on)
                   if not expected_dod:
                        d1= shipment.added_on.date() + datetime.timedelta(days=2)
                   else:
                        d1 = datetime.datetime.date(expected_dod)
                   days = int((d2-d1).days)
          #  else:
          #     days = 6
                   if days < 0:
                     strike_rate_dict_del[0] += 1
                   elif days <= 3:
                       strike_rate_dict_del[days] += 1
                   else:
                        strike_rate_dict_del[4] += 1

    return strike_rate_dict_del

@csrf_exempt
def strike_rate_analysis_location(request):
    if request.POST:
        date_from = request.POST.get('date_from','')
        date_to = request.POST.get('date_to','')
        cust_id = request.POST.get('cust_name')
        source_zone = request.POST.get('source_zone')
        dest_zone = request.POST.get('dest_zone')

        sc = request.POST['sc']
        dl_report = request.POST['dl_report']
        q = Q()
        s = Q()
        month = 0
        if not month:
            t = datetime.datetime.strptime(date_to, "%Y-%m-%d") + datetime.timedelta(days=1)
            dated_to = t.strftime("%Y-%m-%d")
            q = q & Q(added_on__range=(date_from,dated_to))
        else:
            q = q & Q(added_on__year=month[0], added_on__month=month[1])

        if int(cust_id) != 0:
            q = q & Q(shipper__id=cust_id)
        if int(source_zone) != 0:
            q = q & Q(pickup__service_centre__city__zone=source_zone)
        if int(dest_zone) != 0:
            q = q & Q(original_dest__city__zone=dest_zone)
            s = s & Q(city__zone=int(dest_zone))
            sc = 0

        if int(sc) == 0:
            sc = None
        else:
            q = q & Q(original_dest=int(sc))
            s = s & Q(id=int(sc))

        q = q & Q(rts_status__in = [0,2])
    else:
           sc=ServiceCenter.objects.using('local_ecomm').all()
           customers = Customer.objects.using('local_ecomm').all()
           zones = Zone.objects.using('local_ecomm').all()
           return render_to_response("reports/strikerateanalysis_location.html",
                              {'sc':sc, 'zones': zones, 'customers':customers},context_instance=RequestContext(request))
    excl_scs = ["ACB", "AHH", "BAA", "BIJ", "BLR", "BOA", "BOH", "BOP", "BUD", "CCP", "DAL", "DEH", "DEP", "DHQ", "DLR", "GGP", "GND", "GZB", "JAH", "JAI", "JMU", "LKH", "MTT", "NDA", "OKP"]
    scs = ServiceCenter.objects.using('local_ecomm').filter(s).exclude(center_shortcode__in=excl_scs).distinct().order_by("center_shortcode")
    file_name = "/strike_analysis_by_centre_%s.xlsx"%(datetime.datetime.now().strftime("%d%m%Y%H%M%S%s"))
    path_to_save = settings.FILE_UPLOAD_TEMP_DIR+file_name
    workbook = Workbook(path_to_save)
    sheet = workbook.add_worksheet()

    header = workbook.add_format()
    header.set_bg_color('green')
    header.set_bold()
    header.set_border()
    plain_format = workbook.add_format()
    #return HttpResponse(str(cust_id))
    if int(cust_id) != 0:
        cname = Customer.objects.using('local_ecomm').get(id=cust_id).name
        sheet.write(2, 0, 'Customer :'+str(cname))

    sheet.write(3, 0, "Centre", header)
    sheet.write(3, 1, "Month", header)
    sheet.write(3, 2, "Count", header)
    sheet.write(3, 3, "Total", header)
    sheet.write(3, 4, "On Time Delivery Attempt", header)
    sheet.write(3, 5, "%Age", header)
    sheet.write(3, 6, "Day 1 Delivery Attempt", header)
    sheet.write(3, 7, "%Age", header)
    sheet.write(3, 8, "Day 2 Delivery Attempt", header)
    sheet.write(3, 9, "%Age", header)
    sheet.write(3, 10, "Day 3 Delivery Attempt", header)
    sheet.write(3, 11, "%Age", header)
    sheet.write(3, 12, "Day>3 Delivery Attempt", header)
    sheet.write(3, 13, "%Age", header)
    sheet.write(3, 14, "On Time Delivered", header)
    sheet.write(3, 15, "%Age", header)
    sheet.write(3, 16, "Day 1 Delivered", header)
    sheet.write(3, 17, "%Age", header)
    sheet.write(3, 18, "Day 2 Delivered", header)
    sheet.write(3, 19, "%Age", header)
    sheet.write(3, 20, "Day 3 Delivered", header)
    sheet.write(3, 21, "%Age", header)
    sheet.write(3, 22, "Day>3 Delivered", header)
    sheet.write(3, 23, "%Age", header)


    row = 4

    for sc in scs:
        #q = Q()
        #year_month = 0
        #q = q & Q(original_dest=int(sc.id))
    #    nowd = now.date()-datetime.timedelta(days=1)
    #    yest = nowd-datetime.timedelta(days=4)
    #    q = q & Q(added_on__range = (yest,nowd))

        #yest = now.date()-datetime.timedelta(days=2)
       #q = q & Q(added_on__range = (yest,nowd))
        #q = q & Q(added_on__month=now.month, added_on__lt = yest)
        #q = q & Q(added_on__year=month[0], added_on__month=month[1])
   #     q = q & Q(added_on__range=('2013-09-25','2013-10-01')   )
        p = 1
        c = 1
      #  return HttpResponse(q)
        ppd_shipment = Shipment.objects.using('local_ecomm').filter(q, original_dest=sc, product_type="ppd").exclude(rts_status=1)
        ppd_shipment_count = ppd_shipment.only('id').count()
        if ppd_shipment_count == 0:
            p = 0
            ppd_shipment_count = 1

        strike_day_ppd_count = defaultdict(int)
        strike_day_ppd_count = get_strike_rate_from_shipments(ppd_shipment, strike_day_ppd_count)
        strike_day_ppd_count_del = defaultdict(int)
        strike_day_ppd_count_del = get_strike_rate_from_shipments_del(ppd_shipment, strike_day_ppd_count_del)
        on_time_ppd_perc= round(((float(strike_day_ppd_count[0])/float(ppd_shipment_count))*100.0),2)
        day1_ppd_perc = round(((float(strike_day_ppd_count[1])/float(ppd_shipment_count))*100.0),2)
        day2_ppd_perc = round(((float(strike_day_ppd_count[2])/float(ppd_shipment_count))*100.0),2)
        day3_ppd_perc = round(((float(strike_day_ppd_count[3])/float(ppd_shipment_count))*100.0),2)
        day4_ppd_perc = round(((float(strike_day_ppd_count[4])/float(ppd_shipment_count))*100.0),2)


        on_time_ppd_perc_del= round(((float(strike_day_ppd_count_del[0])/float(ppd_shipment_count))*100.0),2)
        day1_ppd_perc_del = round(((float(strike_day_ppd_count_del[1])/float(ppd_shipment_count))*100.0),2)
        day2_ppd_perc_del = round(((float(strike_day_ppd_count_del[2])/float(ppd_shipment_count))*100.0),2)
        day3_ppd_perc_del = round(((float(strike_day_ppd_count_del[3])/float(ppd_shipment_count))*100.0),2)
        day4_ppd_perc_del = round(((float(strike_day_ppd_count_del[4])/float(ppd_shipment_count))*100.0),2)

        cod_shipment = Shipment.objects.using('local_ecomm').filter(q, original_dest=sc, product_type="cod").exclude(rts_status=1)
        cod_shipment_count = cod_shipment.only('id').count()
        if cod_shipment_count == 0:
            c = 0
            cod_shipment_count = 1

        #delivered_cod = StatusUpdate.objects.filter(shipment__in=cod_shipment, status=2)
        #delivered_cods = DeliveryOutscan.objects.filter(shipments__in=cod_shipment)

        strike_day_cod_count = defaultdict(int)
        strike_day_cod_count = get_strike_rate_from_shipments(cod_shipment, strike_day_cod_count)

        strike_day_cod_count_del = defaultdict(int)

        strike_day_cod_count_del = get_strike_rate_from_shipments_del(cod_shipment, strike_day_cod_count_del)

        on_time_cod_perc= round(((float(strike_day_cod_count[0])/float(cod_shipment_count))*100.0),2)
        day1_cod_perc = round(((float(strike_day_cod_count[1])/float(cod_shipment_count))*100.0),2)
        day2_cod_perc = round(((float(strike_day_cod_count[2])/float(cod_shipment_count))*100.0),2)
        day3_cod_perc = round(((float(strike_day_cod_count[3])/float(cod_shipment_count))*100.0),2)
        day4_cod_perc = round(((float(strike_day_cod_count[4])/float(cod_shipment_count))*100.0),2)


        on_time_cod_perc_del= round(((float(strike_day_cod_count_del[0])/float(cod_shipment_count))*100.0),2)
        day1_cod_perc_del = round(((float(strike_day_cod_count_del[1])/float(cod_shipment_count))*100.0),2)
        day2_cod_perc_del = round(((float(strike_day_cod_count_del[2])/float(cod_shipment_count))*100.0),2)
        day3_cod_perc_del = round(((float(strike_day_cod_count_del[3])/float(cod_shipment_count))*100.0),2)
        day4_cod_perc_del = round(((float(strike_day_cod_count_del[4])/float(cod_shipment_count))*100.0),2)

        if p == 0:
            ppd_shipment_count = 0
        if c == 0:
            cod_shipment_count = 0
        if not 2==1:
           # year_month = str(yest)+' To '+str(nowd)
               year_month = ""

        total=ppd_shipment_count+cod_shipment_count

        sheet.write(0, 2, "Strike Rate Analysis - Centre")



        sheet.write(row, 0, sc.center_shortcode, plain_format)
        sheet.write(row+1, 0, sc.center_shortcode, plain_format)

        sheet.write(row, 1, year_month, plain_format)
        sheet.write(row+1, 1, year_month, plain_format)

        sheet.write(row, 2, "Prepaid", plain_format)
        sheet.write(row+1, 2, "COD", plain_format)

        sheet.write(row, 3, str(ppd_shipment_count), plain_format)
        sheet.write(row+1, 3, str(cod_shipment_count), plain_format)

        sheet.write(row, 4, str(strike_day_ppd_count[0]), plain_format)
        sheet.write(row+1, 4, str(strike_day_cod_count[0]), plain_format)
        sheet.write(row, 5, str(on_time_ppd_perc)+'%', plain_format)
        sheet.write(row+1, 5, str(on_time_cod_perc)+'%', plain_format)
        sheet.write(row, 6, str(strike_day_ppd_count[1]), plain_format)
        sheet.write(row+1, 6, str(strike_day_cod_count[1]), plain_format)
        sheet.write(row, 7, str(day1_ppd_perc)+'%', plain_format)
        sheet.write(row+1, 7, str(day1_cod_perc)+'%', plain_format)

        sheet.write(row, 8, str(strike_day_ppd_count[2]), plain_format)
        sheet.write(row+1, 8, str(strike_day_cod_count[2]), plain_format)
        sheet.write(row, 9, str(day2_ppd_perc)+'%', plain_format)
        sheet.write(row+1, 9, str(day2_cod_perc)+'%', plain_format)

        sheet.write(row, 10, str(strike_day_ppd_count[3]), plain_format)
        sheet.write(row+1, 10, str(strike_day_cod_count[3]), plain_format)
        sheet.write(row, 11, str(day3_ppd_perc)+'%', plain_format)
        sheet.write(row+1, 11, str(day3_cod_perc)+'%', plain_format)

        sheet.write(row, 12, str(strike_day_ppd_count[4]), plain_format)
        sheet.write(row+1, 12, str(strike_day_cod_count[4]), plain_format)
        sheet.write(row, 13, str(day4_ppd_perc)+'%', plain_format)
        sheet.write(row+1, 13, str(day4_cod_perc)+'%', plain_format)


        sheet.write(row, 14, str(strike_day_ppd_count_del[0]), plain_format)
        sheet.write(row+1, 14, str(strike_day_cod_count_del[0]), plain_format)
        sheet.write(row, 15, str(on_time_ppd_perc_del)+'%', plain_format)
        sheet.write(row+1, 15, str(on_time_cod_perc_del)+'%', plain_format)

        sheet.write(row, 16, str(strike_day_ppd_count_del[1]), plain_format)
        sheet.write(row+1, 16, str(strike_day_cod_count_del[1]), plain_format)
        sheet.write(row, 17, str(day1_ppd_perc_del)+'%', plain_format)
        sheet.write(row+1, 17, str(day1_cod_perc_del)+'%', plain_format)

        sheet.write(row, 18, str(strike_day_ppd_count_del[2]), plain_format)
        sheet.write(row+1, 18, str(strike_day_cod_count_del[2]), plain_format)
        sheet.write(row, 19, str(day2_ppd_perc_del)+'%', plain_format)
        sheet.write(row+1, 19, str(day2_cod_perc_del)+'%', plain_format)

        sheet.write(row, 20, str(strike_day_ppd_count_del[3]), plain_format)
        sheet.write(row+1, 20, str(strike_day_cod_count_del[3]), plain_format)
        sheet.write(row, 21, str(day3_ppd_perc_del)+'%', plain_format)
        sheet.write(row+1, 21, str(day3_cod_perc_del)+'%', plain_format)

        sheet.write(row, 22, str(strike_day_ppd_count_del[4]), plain_format)
        sheet.write(row+1, 22, str(strike_day_cod_count_del[4]), plain_format)
        sheet.write(row, 23, str(day4_ppd_perc_del)+'%', plain_format)
        sheet.write(row+1, 23, str(day4_cod_perc_del)+'%', plain_format)


        row += 3

    workbook.close()
    return HttpResponseRedirect("/static/uploads/%s"%(file_name))

@csrf_exempt
def strike_rate_analysis_customer(request):
    if request.POST:
        customer = request.POST['cust_name']

        date_from = request.POST.get('date_from','')
        date_to = request.POST.get('date_to','')

        dl_report = request.POST['dl_report']
        q = Q()
        s = Q()
        if customer == "0":
            customer = None
        else:
            q = q & Q(shipper = int(customer))
            s = s & Q(id=int(customer))
        month = 0
        if not month:
            t = datetime.datetime.strptime(date_to, "%Y-%m-%d") + datetime.timedelta(days=1)
            dated_to = t.strftime("%Y-%m-%d")
            q = q & Q(added_on__range=(date_from,dated_to))
        else:
            q = q & Q(added_on__year=month[0], added_on__month=month[1])
    else:
           customer=Customer.objects.using('local_ecomm').all()
           return render_to_response("reports/strikerateanalysis_customer.html",
                              {'customer':customer},context_instance=RequestContext(request))

    scs = Customer.objects.using('local_ecomm').filter(s).order_by("name")
    file_name = "/strike_analysis_by_client_%s.xlsx"%(datetime.datetime.now().strftime("%d%m%Y%H%M%S%s"))
    path_to_save = settings.FILE_UPLOAD_TEMP_DIR+file_name
    workbook = Workbook(path_to_save)
    sheet = workbook.add_worksheet()

    header = workbook.add_format()
    header.set_bg_color('green')
    header.set_bold()
    header.set_border()
    plain_format = workbook.add_format()

    sheet.write(3, 0, "Centre", header)
    sheet.write(3, 1, "Month", header)
    sheet.write(3, 2, "Count", header)
    sheet.write(3, 3, "Total", header)
    sheet.write(3, 4, "On Time Delivery Attempt", header)
    sheet.write(3, 5, "%Age", header)
    sheet.write(3, 6, "Day 1 Delivery Attempt", header)
    sheet.write(3, 7, "%Age", header)
    sheet.write(3, 8, "Day 2 Delivery Attempt", header)
    sheet.write(3, 9, "%Age", header)
    sheet.write(3, 10, "Day 3 Delivery Attempt", header)
    sheet.write(3, 11, "%Age", header)
    sheet.write(3, 12, "Day>3 Delivery Attempt", header)
    sheet.write(3, 13, "%Age", header)
    sheet.write(3, 14, "On Time Delivered", header)
    sheet.write(3, 15, "%Age", header)
    sheet.write(3, 16, "Day 1 Delivered", header)
    sheet.write(3, 17, "%Age", header)
    sheet.write(3, 18, "Day 2 Delivered", header)
    sheet.write(3, 19, "%Age", header)
    sheet.write(3, 20, "Day 3 Delivered", header)
    sheet.write(3, 21, "%Age", header)
    sheet.write(3, 22, "Day>3 Delivered", header)
    sheet.write(3, 23, "%Age", header)


    row = 4

    for sc in scs:

        #ym = request.POST.get('month',None)
       # year_month = now.strftime("%Y-%m")
       # month = year_month.split("-")
 #      date_from = now.strftime("%Y-%m")+"-01"
#       date_to = now.strftime("%Y-%m-%d")

        #q = Q()
        #year_month = 0
        #q = q & Q(shipper=int(sc.id))
     #   nowd = now.date()-datetime.timedelta(days=1)
     #   yest = nowd-datetime.timedelta(days=4)
     #   q = q & Q(added_on__range = (yest,nowd))

        #yest = now.date()-datetime.timedelta(days=2)
       #q = q & Q(added_on__range = (yest,nowd))
        #q = q & Q(added_on__month=now.month, added_on__lt = yest)
        #q = q & Q(added_on__year=month[0], added_on__month=month[1])
   #     q = q & Q(added_on__range=('2013-09-25','2013-10-01')   )
        p = 1
        c = 1
    #    return HttpResponse(q)
        ppd_shipment = Shipment.objects.using('local_ecomm').filter(q, shipper = sc, product_type="ppd").exclude(rts_status=1)
        ppd_shipment_count = ppd_shipment.only('id').count()
        if ppd_shipment_count == 0:
            p = 0
            ppd_shipment_count = 1

        strike_day_ppd_count = defaultdict(int)
        strike_day_ppd_count = get_strike_rate_from_shipments(ppd_shipment, strike_day_ppd_count)
        strike_day_ppd_count_del = defaultdict(int)
        strike_day_ppd_count_del = get_strike_rate_from_shipments_del(ppd_shipment, strike_day_ppd_count_del)
        on_time_ppd_perc= round(((float(strike_day_ppd_count[0])/float(ppd_shipment_count))*100.0),2)
        day1_ppd_perc = round(((float(strike_day_ppd_count[1])/float(ppd_shipment_count))*100.0),2)
        day2_ppd_perc = round(((float(strike_day_ppd_count[2])/float(ppd_shipment_count))*100.0),2)
        day3_ppd_perc = round(((float(strike_day_ppd_count[3])/float(ppd_shipment_count))*100.0),2)
        day4_ppd_perc = round(((float(strike_day_ppd_count[4])/float(ppd_shipment_count))*100.0),2)


        on_time_ppd_perc_del= round(((float(strike_day_ppd_count_del[0])/float(ppd_shipment_count))*100.0),2)
        day1_ppd_perc_del = round(((float(strike_day_ppd_count_del[1])/float(ppd_shipment_count))*100.0),2)
        day2_ppd_perc_del = round(((float(strike_day_ppd_count_del[2])/float(ppd_shipment_count))*100.0),2)
        day3_ppd_perc_del = round(((float(strike_day_ppd_count_del[3])/float(ppd_shipment_count))*100.0),2)
        day4_ppd_perc_del = round(((float(strike_day_ppd_count_del[4])/float(ppd_shipment_count))*100.0),2)

        cod_shipment = Shipment.objects.using('local_ecomm').filter(q, shipper = sc, product_type="cod").exclude(rts_status=1)
        cod_shipment_count = cod_shipment.only('id').count()
        if cod_shipment_count == 0:
            c = 0

            cod_shipment_count = 1

        #delivered_cod = StatusUpdate.objects.filter(shipment__in=cod_shipment, status=2)
        #delivered_cods = DeliveryOutscan.objects.using('local_ecomm').filter(shipments__in=cod_shipment)

        strike_day_cod_count = defaultdict(int)

        strike_day_cod_count = get_strike_rate_from_shipments(cod_shipment, strike_day_cod_count)

        strike_day_cod_count_del = defaultdict(int)

        strike_day_cod_count_del = get_strike_rate_from_shipments_del(cod_shipment, strike_day_cod_count_del)

        on_time_cod_perc= round(((float(strike_day_cod_count[0])/float(cod_shipment_count))*100.0),2)
        day1_cod_perc = round(((float(strike_day_cod_count[1])/float(cod_shipment_count))*100.0),2)
        day2_cod_perc = round(((float(strike_day_cod_count[2])/float(cod_shipment_count))*100.0),2)
        day3_cod_perc = round(((float(strike_day_cod_count[3])/float(cod_shipment_count))*100.0),2)
        day4_cod_perc = round(((float(strike_day_cod_count[4])/float(cod_shipment_count))*100.0),2)


        on_time_cod_perc_del= round(((float(strike_day_cod_count_del[0])/float(cod_shipment_count))*100.0),2)
        day1_cod_perc_del = round(((float(strike_day_cod_count_del[1])/float(cod_shipment_count))*100.0),2)
        day2_cod_perc_del = round(((float(strike_day_cod_count_del[2])/float(cod_shipment_count))*100.0),2)
        day3_cod_perc_del = round(((float(strike_day_cod_count_del[3])/float(cod_shipment_count))*100.0),2)
        day4_cod_perc_del = round(((float(strike_day_cod_count_del[4])/float(cod_shipment_count))*100.0),2)

        if p == 0:
            ppd_shipment_count = 0
        if c == 0:
            cod_shipment_count = 0
        if not 1==2:
            #year_month = str(yest)+' To '+str(nowd)
              year_month = ""

        total=ppd_shipment_count+cod_shipment_count

        sheet.write(0, 2, "Strike Rate Analysis - Client")



        sheet.write(row, 0, str(sc), plain_format)
        sheet.write(row+1, 0, str(sc), plain_format)

        sheet.write(row, 1, year_month, plain_format)
        sheet.write(row+1, 1, year_month, plain_format)

        sheet.write(row, 2, "Prepaid", plain_format)
        sheet.write(row+1, 2, "COD", plain_format)

        sheet.write(row, 3, str(ppd_shipment_count), plain_format)

        sheet.write(row+1, 3, str(cod_shipment_count), plain_format)

        sheet.write(row, 4, str(strike_day_ppd_count[0]), plain_format)
        sheet.write(row+1, 4, str(strike_day_cod_count[0]), plain_format)
        sheet.write(row, 5, str(on_time_ppd_perc)+'%', plain_format)
        sheet.write(row+1, 5, str(on_time_cod_perc)+'%', plain_format)

        sheet.write(row, 6, str(strike_day_ppd_count[1]), plain_format)
        sheet.write(row+1, 6, str(strike_day_cod_count[1]), plain_format)
        sheet.write(row, 7, str(day1_ppd_perc)+'%', plain_format)
        sheet.write(row+1, 7, str(day1_cod_perc)+'%', plain_format)

        sheet.write(row, 8, str(strike_day_ppd_count[2]), plain_format)
        sheet.write(row+1, 8, str(strike_day_cod_count[2]), plain_format)
        sheet.write(row, 9, str(day2_ppd_perc)+'%', plain_format)
        sheet.write(row+1, 9, str(day2_cod_perc)+'%', plain_format)

        sheet.write(row, 10, str(strike_day_ppd_count[3]), plain_format)
        sheet.write(row+1, 10, str(strike_day_cod_count[3]), plain_format)
        sheet.write(row, 11, str(day3_ppd_perc)+'%', plain_format)
        sheet.write(row+1, 11, str(day3_cod_perc)+'%', plain_format)

        sheet.write(row, 12, str(strike_day_ppd_count[4]), plain_format)
        sheet.write(row+1, 12, str(strike_day_cod_count[4]), plain_format)
        sheet.write(row, 13, str(day4_ppd_perc)+'%', plain_format)
        sheet.write(row+1, 13, str(day4_cod_perc)+'%', plain_format)


        sheet.write(row, 14, str(strike_day_ppd_count_del[0]), plain_format)
        sheet.write(row+1, 14, str(strike_day_cod_count_del[0]), plain_format)
        sheet.write(row, 15, str(on_time_ppd_perc_del)+'%', plain_format)
        sheet.write(row+1, 15, str(on_time_cod_perc_del)+'%', plain_format)

        sheet.write(row, 16, str(strike_day_ppd_count_del[1]), plain_format)
        sheet.write(row+1, 16, str(strike_day_cod_count_del[1]), plain_format)
        sheet.write(row, 17, str(day1_ppd_perc_del)+'%', plain_format)
        sheet.write(row+1, 17, str(day1_cod_perc_del)+'%', plain_format)

        sheet.write(row, 18, str(strike_day_ppd_count_del[2]), plain_format)
        sheet.write(row+1, 18, str(strike_day_cod_count_del[2]), plain_format)
        sheet.write(row, 19, str(day2_ppd_perc_del)+'%', plain_format)
        sheet.write(row+1, 19, str(day2_cod_perc_del)+'%', plain_format)

        sheet.write(row, 20, str(strike_day_ppd_count_del[3]), plain_format)
        sheet.write(row+1, 20, str(strike_day_cod_count_del[3]), plain_format)
        sheet.write(row, 21, str(day3_ppd_perc_del)+'%', plain_format)
        sheet.write(row+1, 21, str(day3_cod_perc_del)+'%', plain_format)

        sheet.write(row, 22, str(strike_day_ppd_count_del[4]), plain_format)
        sheet.write(row+1, 22, str(strike_day_cod_count_del[4]), plain_format)
        sheet.write(row, 23, str(day4_ppd_perc_del)+'%', plain_format)
        sheet.write(row+1, 23, str(day4_cod_perc_del)+'%', plain_format)


        row += 3

    workbook.close()
    return HttpResponseRedirect("/static/uploads/%s"%(file_name))




@csrf_exempt
def strike_rate_analysis(request):
    if request.POST:
        customer = request.POST['cust_name']

        ym = request.POST.get('month',None)
        year_month = ym if ym else now.strftime("%Y-%m")
        month = year_month.split("-")
 	date_from = request.POST.get('date_from','')
 	date_to = request.POST.get('date_to','')

        if date_to:
            month = ''
            year_month = ''

        sc = request.POST['sc']
        dl_report = request.POST['dl_report']
        q = Q()

        if customer == "0":
            customer = None
        else:
            q = q & Q(shipper = int(customer))

        if not month:
            t = datetime.datetime.strptime(date_to, "%Y-%m-%d") + datetime.timedelta(days=1)
            dated_to = t.strftime("%Y-%m-%d")
            q = q & Q(added_on__range=(date_from,dated_to))
        else:
            q = q & Q(added_on__year=month[0], added_on__month=month[1])

        if sc == "0":
            sc = None
        else:
            q = q & Q(service_centre=int(sc))

        p = 1
        c = 1
        ppd_shipment = Shipment.objects.using('local_ecomm').filter(q, product_type="ppd").exclude(return_shipment=3).exclude(rts_status=1)
        ppd_shipment_count = ppd_shipment.only('id').count()
        if ppd_shipment_count == 0:
            p = 0
            ppd_shipment_count = 1

        #delivered_ppd = StatusUpdate.objects.using('local_ecomm').filter(shipment__in=ppd_shipment, status=2)
        #strike_day_ppd_count = {0:0,1:0,2:0,3:0,4:0}
        strike_day_ppd_count = defaultdict(int)

        strike_day_ppd_count = get_strike_rate_from_shipments(ppd_shipment, strike_day_ppd_count)

        on_time_ppd_perc= round(((float(strike_day_ppd_count[0])/float(ppd_shipment_count))*100.0),2)
        day1_ppd_perc = round(((float(strike_day_ppd_count[1])/float(ppd_shipment_count))*100.0),2)
        day2_ppd_perc = round(((float(strike_day_ppd_count[2])/float(ppd_shipment_count))*100.0),2)
        day3_ppd_perc = round(((float(strike_day_ppd_count[3])/float(ppd_shipment_count))*100.0),2)
        day4_ppd_perc = round(((float(strike_day_ppd_count[4])/float(ppd_shipment_count))*100.0),2)

        cod_shipment = Shipment.objects.using('local_ecomm').filter(q, product_type="cod").exclude(return_shipment=3).exclude(rts_status=1)
        cod_shipment_count = cod_shipment.only('id').count()
        if cod_shipment_count == 0:
            c = 0
            cod_shipment_count = 1

        #delivered_cod = StatusUpdate.objects.using('local_ecomm').filter(shipment__in=cod_shipment, status=2)
        #delivered_cods = DeliveryOutscan.objects.using('local_ecomm').filter(shipments__in=cod_shipment)

        strike_day_cod_count = defaultdict(int)

        strike_day_cod_count = get_strike_rate_from_shipments(cod_shipment, strike_day_cod_count)

        on_time_cod_perc= round(((float(strike_day_cod_count[0])/float(cod_shipment_count))*100.0),2)
        day1_cod_perc = round(((float(strike_day_cod_count[1])/float(cod_shipment_count))*100.0),2)
        day2_cod_perc = round(((float(strike_day_cod_count[2])/float(cod_shipment_count))*100.0),2)
        day3_cod_perc = round(((float(strike_day_cod_count[3])/float(cod_shipment_count))*100.0),2)
        day4_cod_perc = round(((float(strike_day_cod_count[4])/float(cod_shipment_count))*100.0),2)
        if p == 0:
            ppd_shipment_count = 0
        if c == 0:
            cod_shipment_count = 0
        if not (year_month):
            year_month = str(date_from)+' To '+str(date_to)

        total=ppd_shipment_count+cod_shipment_count
        if dl_report == "Download":
            sheet = book.add_sheet('Strike Rate Analysis')
            sheet.write(0, 2, "Strike Rate Analysis", style=header_style)

            for a in range(13):
                sheet.col(a).width = 3000

            sheet.write(3, 0, "Month", style=header_style)
            sheet.write(3, 1, "Count", style=header_style)
            sheet.write(3, 2, "Total", style=header_style)
            sheet.write(3, 3, "On Time", style=header_style)
            sheet.write(3, 4, "%Age", style=header_style)
            sheet.write(3, 5, "Day 1", style=header_style)
            sheet.write(3, 6, "%Age", style=header_style)
            sheet.write(3, 7, "Day 2", style=header_style)
            sheet.write(3, 8, "%Age", style=header_style)
            sheet.write(3, 9, "Day 3", style=header_style)
            sheet.write(3, 10, "%Age", style=header_style)
            sheet.write(3, 11, "Day>3", style=header_style)
            sheet.write(3, 12, "%Age", style=header_style)

            sheet.write(4, 0, year_month)
            sheet.write(5, 0, year_month)

            sheet.write(4, 1, "Prepaid", style=header_style)
            sheet.write(5, 1, "COD", style=header_style)

            sheet.write(4, 2, str(ppd_shipment_count))
            sheet.write(5, 2, str(cod_shipment_count))

            sheet.write(4, 3, str(strike_day_ppd_count[0]))
            sheet.write(5, 3, str(strike_day_cod_count[0]))
            sheet.write(4, 4, str(on_time_ppd_perc)+'%')
            sheet.write(5, 4, str(on_time_cod_perc)+'%')

            sheet.write(4, 5, str(strike_day_ppd_count[1]))
            sheet.write(5, 5, str(strike_day_cod_count[1]))
            sheet.write(4, 6, str(day1_ppd_perc)+'%')
            sheet.write(5, 6, str(day1_cod_perc)+'%')

            sheet.write(4, 7, str(strike_day_ppd_count[2]))
            sheet.write(5, 7, str(strike_day_cod_count[2]))
            sheet.write(4, 8, str(day2_ppd_perc)+'%')
            sheet.write(5, 8, str(day2_cod_perc)+'%')

            sheet.write(4, 9, str(strike_day_ppd_count[3]))
            sheet.write(5, 9, str(strike_day_cod_count[3]))
            sheet.write(4, 10, str(day3_ppd_perc)+'%')
            sheet.write(5, 10, str(day3_cod_perc)+'%')

            sheet.write(4, 11, str(strike_day_ppd_count[4]))
            sheet.write(5, 11, str(strike_day_cod_count[4]))
            sheet.write(4, 12, str(day4_ppd_perc)+'%')
            sheet.write(5, 12, str(day4_cod_perc)+'%')

            response = HttpResponse(mimetype='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename=Strike-Rate-Analysis.xls'
            book.save(response)
            return response
        else:
            return render_to_response('reports/reports-strikerateanalysis.html',
                                  {
                                   'ppd_shipment':ppd_shipment_count,
                                   'cod_shipment':cod_shipment_count,
                                   'total':total,
                                   'month':year_month,
                                   'on_time_ppd':on_time_ppd_perc,
                                   'day1_ppd':day1_ppd_perc,
                                   'day2_ppd':day2_ppd_perc,
                                   'day3_ppd':day3_ppd_perc,
                                   'day4_ppd':day4_ppd_perc,
                                   'on_time_cod':on_time_cod_perc,
                                   'day1_cod':day1_cod_perc,
                                   'day2_cod':day2_cod_perc,
                                   'day3_cod':day3_cod_perc,
                                   'day4_cod':day4_cod_perc,
                                   'ppd_count_ontime':strike_day_ppd_count[0],
                                   'ppd_count_day1':strike_day_ppd_count[1],
                                   'ppd_count_day2':strike_day_ppd_count[2],
                                   'ppd_count_day3':strike_day_ppd_count[3],
                                   'ppd_count_day4':strike_day_ppd_count[4],
                                   'cod_count_ontime':strike_day_cod_count[0],
                                   'cod_count_day1':strike_day_cod_count[1],
                                   'cod_count_day2':strike_day_cod_count[2],
                                   'cod_count_day3':strike_day_cod_count[3],
                                   'cod_count_day4':strike_day_cod_count[4],
                                   },
                                  context_instance=RequestContext(request))

    customer=Customer.objects.using('local_ecomm').all()
    sc = ServiceCenter.objects.using('local_ecomm').all()

    return render_to_response("reports/strikerateanalysis.html",
                              {'customer':customer,
                               'sc':sc},
                               context_instance=RequestContext(request))

def strike_analysis_updated(request):
    file_name = "/strike_analysis_%s.xlsx"%(datetime.datetime.now().strftime("%d%m%Y%H%M%S%s"))
    path_to_save = settings.FILE_UPLOAD_TEMP_DIR+file_name
    workbook = Workbook(path_to_save)

    # define style formats for header and data
    header_format = workbook.add_format({
        'bold': 1,
        'align': 'center',
        'valign': 'vcenter',
        'fg_color': '#cccccc'})
    #header_format.set_bg_color('#cccccc')
    #header_format.set_bold()

    # Create a format to use in the merged range.
    merge_format = workbook.add_format({
        'bold': 1,
        'align': 'center',
        'valign': 'vcenter',
        'fg_color': 'yellow'})

    plain_format = workbook.add_format({
        'align': 'center',
        'valign': 'vcenter'})

    date_format = workbook.add_format({'num_format': 'mmmm d yyyy'})

    # add a worksheet and set excel sheet column headers
    sheet = workbook.add_worksheet()
    sheet.set_column(0, 14, 12) # set column width
    # write statement headers: statement name, customer name, and date
    sheet.write(2, 1, "Shipment Count", header_format)
    sheet.write(2, 2, "On Time", header_format)
    sheet.write(2, 3, "%Age", header_format)
    sheet.write(2, 4, "Day1", header_format)
    sheet.write(2, 5, "%Age", header_format)
    sheet.write(2, 6, "Day2", header_format)
    sheet.write(2, 7, "%Age", header_format)
    sheet.write(2, 8, "Day3", header_format)
    sheet.write(2, 9, "%Age", header_format)
    sheet.write(2, 10, ">Day3", header_format)
    sheet.write(2, 11, "%Age", header_format)

    now = datetime.datetime.now().date()
    now = now - datetime.timedelta(days=1)
    year = now.strftime("%Y")
    month = now.strftime("%m")
    strike_data = Shipment.objects.using('local_ecomm').filter(
        shipment_date__month=month,
        shipment_date__year=year).values("original_dest").\
        annotate(Count('id'),
            total_chargeable_weight=Sum('chargeable_weight'),
            collectable_value=Sum('collectable_value'),
            declared_value=Sum('declared_value'),
            op_freight=Sum('order_price__freight_charge'),
            op_sdl=Sum('order_price__sdl_charge'),
            op_fuel=Sum('order_price__fuel_surcharge'),
            op_rto_price=Sum('order_price__rto_charge'),
            op_sdd_charge=Sum('order_price__sdd_charge'),
            op_reverse_charge=Sum('order_price__reverse_charge'),
            op_valuable_cargo_handling_charge=Sum('order_price__valuable_cargo_handling_charge'),
            op_tab_charge=Sum('order_price__tab_charge'),
            op_to_pay=Sum('order_price__to_pay_charge')).exclude(shipment_date__gt=now).order_by('original_dest')

@csrf_exempt
def ageing_sop(request, type = 0):
    q = Q()
    if type == 1:
       yest = datetime.datetime.now().date() - datetime.timedelta(days=90)
       q = q & Q(added_on__range=(yest,now.date()))
    elif request.POST:
        customer = request.POST['cust_id']
        date_from = request.POST['date_from']
        date_to = request.POST['date_to']
        sc=request.POST['sc']
        report_type = request.POST['report_type']
        if customer == "0":
            customer = None
        else:
            q = q & Q(shipper_id = int(customer))
        if not (date_from and date_to):
            pass
        else:
            r = datetime.datetime.strptime(date_from, "%Y-%m-%d") - datetime.timedelta(days=6)
            t = datetime.datetime.strptime(date_to, "%Y-%m-%d") - datetime.timedelta(days=6)
            date_to = t.strftime("%Y-%m-%d")
            date_from = r.strftime("%Y-%m-%d")
            q = q & Q(added_on__range=(date_from,date_to))
        if sc == "0":
            sc = None
        else:
            q = q & Q(service_centre_id=int(sc))
    else:
        customer=Customer.objects.using('local_ecomm').all()
        sc = ServiceCenter.objects.using('local_ecomm').all()
        return render_to_response("reports/Ageing-Sop.html",
                              {'customer':customer,
                               'sc':sc},
                               context_instance=RequestContext(request))


    file_name = "Ageing_SOP_%s.xlsx"%(now.strftime('%Y-%m-%d'))
    report = ReportGenerator(file_name)
    #path_to_save = settings.FILE_UPLOAD_TEMP_DIR + file_name
    #workbook = Workbook(path_to_save)
    #header_format = workbook.add_format()
    #header_format.set_bg_color('green')
    #header_format.set_bold()
    #header_format.set_border()
    #plain_format = workbook.add_format()
    #sheet = workbook.add_worksheet()
    #sheet.set_column(0,15,30)

    col_head = ("Airwaybill Number", "Order Number", "Origin SC", "Destination SC", "Original Dest",
                "Pickup Date", "Shipper Code", "Consignee", "Mobile Number", "Collectable Value",
                 "Reason Code", "Status", "Status Updated On", "Remarks", "Days")
    report.write_header(col_head)
    #for col, val in enumerate(col_head):
             #sheet.write(3,col, val, header_format)
    row_count = 3

    shipments = Shipment.objects.using('local_ecomm').filter(
        q, status__gte=2).exclude(
        reason_code__id__in = [1,6,46, 4]
    ).exclude(rts_status=1).exclude(shipper__code = 32012)

    shipment_info={}

    for a in shipments.iterator():
        
        if not shipment_info.get(a):
            upd_time = a.added_on
            monthdir = upd_time.strftime("%Y_%m")
            shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
            try:
                history = shipment_history.objects.using('local_ecomm').filter(shipment=a).exclude(status__in=[11,16,9]).latest('updated_on')
            except:
                history = ""
            status = get_internal_shipment_status(a.status)
            if a.rts_status == 2 or a.reason_code_id == 5:
                 try:
                    rts_sh = Shipment.objects.get(airwaybill_number=a.ref_airwaybill_number)
                 except:
                    continue
                 if rts_sh.status == 9:
                      continue
                 status = "Returned"
            days = (now - a.added_on).days
            status_upd =  a.statusupdate_set.all().order_by('-added_on')
            if status_upd:
              remarks = status_upd[0].remarks
              if a.expected_dod:
                  if status_upd[0].date <= a.expected_dod.date():
                     continue
            else:
                remarks = ""
            if history:
               hist = history
               u = (a.airwaybill_number, a.order_number, a.pickup.service_centre, 
                    a.service_centre, a.original_dest, a.added_on,
                    a.shipper, a.consignee, a.mobile, a.collectable_value, a.reason_code, status,
                    hist.updated_on.date(), remarks, days)
               row_count += 1
               report.write_row(u)
               #for col, val in enumerate(u):
                   #try:
                     #sheet.write(row_count, col, str(val), plain_format)
                   #except UnicodeEncodeError:
                     #sheet.write(row_count, col, removeNonAscii(val), plain_format)
               shipment_info[a]=hist
    #workbook.close()
    if type:
       return (file_name)
    else:
       return HttpResponseRedirect("/static/uploads/reports/%s"%(file_name))

@csrf_exempt
def testmode_noinfo(request):
    if request.POST:
        customer_id = request.POST.get('cust_id',None)
        date_from = request.POST.get('date_from',None)
        date_to = request.POST.get('date_to',None)
        sc = request.POST.get('sc',None)

        q = Q()
        customer_id  = int(customer_id) if customer_id else None
        sc = int(sc) if sc else None

        if customer_id:
            q = q & Q(shipper_id = customer_id)

        if date_from and date_to:
            t = datetime.datetime.strptime(date_to, "%Y-%m-%d") + datetime.timedelta(days=1)
            date_to = t.strftime("%Y-%m-%d")
            q = q & Q(added_on__range=(date_from,date_to))

        if sc:
            q = q & Q(service_centre_id=sc)

        res_code = ShipmentStatusMaster.objects.using('local_ecomm').get(id=1)
	shipments = Shipment.objects.using('local_ecomm').filter(q, status=8).exclude(reason_code=res_code).exclude(status_type=5).exclude(rts_status=2)
        dl_report=request.POST['dl_report']
        shipment_info={}
        download_list = []

        for a in shipments:
            if not shipment_info.get(a):
                upd_time = a.added_on
                monthdir = upd_time.strftime("%Y_%m")
                shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
                status_upd =  a.statusupdate_set.all().order_by("-date")
		rto_status = 0
                rem_status = 0
                rts_status = 0
                rts_stat_val = 0
                shipment = a
                rto_status = shipment_history.objects.using('local_ecomm').filter(shipment=shipment, reason_code_id = 34)
                rem_status = shipment_history.objects.using('local_ecomm').filter(shipment=shipment, remarks = "Return to Origin")
                history1 = shipment_history.objects.using('local_ecomm').filter(shipment=shipment)
                history = history1.latest('updated_on')
                rtss = history1.order_by('id')
                if (rtss[0].reason_code_id==5):
                    rts_status = 1
                if (shipment.reason_code_id == 5 or shipment.return_shipment==3 or rts_status or shipment.return_shipment==2 or rto_status or rem_status):
                    rts_stat_val = 1
                sc = a.service_centre
		if history.updated_on:
                    upd_date = history.updated_on.strftime("%Y-%m-%d %H:%m")
                    last_date = (datetime.datetime.now() - datetime.timedelta(hours=48))
                    last_date = last_date.strftime("%Y-%m-%d %H:%m")
                    if upd_date >= last_date or rts_stat_val == 1:
                        b=0
                    else:
                        b =1
                else:
                    b = 1

                if b==1:
                        if history:
                                hist = history
                                if not a.original_dest:
                                    u = (a.pickup.service_centre.center_name,
                                         a.pickup.pickup_date,
                                         sc,
                                         a.airwaybill_number,
                                         a.shipper.name,
                                         a.consignee,
                                         a.reason_code,
                                         hist.updated_on.strftime("%d-%m-%Y %H:%m"))
                                else:
                                    u = (a.pickup.service_centre.center_name,
                                         a.pickup.pickup_date,
                                         sc,
                                         a.airwaybill_number,
                                         a.shipper.name,
                                         a.consignee,
                                         a.reason_code,
                                         hist.updated_on.strftime("%d-%m-%Y %H:%m"))
                                download_list.append(u)
                                shipment_info[a]=hist
                        else:
                                shipment_info[a]=None
        if dl_report == "Download":
	    sheet = book.add_sheet("No-Information")
            sheet.write(0, 2, "No-Information Report", style=header_style)
            for a in range(9):
                sheet.col(a).width = 6000
            sheet.write(3, 0, "Origin Service Centre", style=header_style)
            sheet.write(3, 1, "Pickup Date", style=header_style)
            sheet.write(3, 2, "Destination Service Centre", style=header_style)
            sheet.write(3, 3, "Air waybill Number", style=header_style)
            sheet.write(3, 4, "Shipper", style=header_style)
            sheet.write(3, 5, "Consignee", style=header_style)
            sheet.write(3, 6, "Reason Code", style=header_style)
            sheet.write(3, 7, "Status Updated On", style=header_style)

            for row, rowdata in enumerate(download_list, start=4):
                for col, val in enumerate(rowdata, start=0):
                    style = datetime_style
		    try:
                        sheet.write(row, col, str(val), style=style)
		    except:
			pass
            response = HttpResponse(mimetype='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename=No-Information-report.xls'
            book.save(response)
            return response
        else:
            return render_to_response('reports/reports-noinfo.html',
                                  {'shipments':download_list},
                                  context_instance=RequestContext(request))

    customer=Customer.objects.using('local_ecomm').all()
    sc = ServiceCenter.objects.using('local_ecomm').all()

    return render_to_response("reports/noinfo.html",
                              {'customer':customer,
                               'sc':sc},

                               context_instance=RequestContext(request))


@csrf_exempt
def noinfo(request):
    if request.POST:
        customer = request.POST['cust_id']
        date_from = request.POST['date_from']
        date_to = request.POST['date_to']
        sc=request.POST['sc']
        csc=request.POST['csc']
        q = Q()
        if customer == "0":
            customer = None
        else:
            q = q & Q(shipper_id = int(customer))
        if not (date_from and date_to):
            pass
        else:
            t = datetime.datetime.strptime(date_to, "%Y-%m-%d") + datetime.timedelta(days=1)
            date_to = t.strftime("%Y-%m-%d")
            q = q & Q(added_on__range=(date_from,date_to))
        if sc == "0":
            sc = None
        else:
            q = q & Q(service_centre_id=int(sc))
     #   if csc == "0":
     #      csc = None
     #   else:
     #      csc =
        q = q & Q(rts_status =0, rto_status=0)
        res_code = ShipmentStatusMaster.objects.using('local_ecomm').filter(id__in=[1,4,5,6,14,34,46,52,53])
	shipments = Shipment.objects.using('local_ecomm').filter(q).exclude(reason_code__in = res_code).exclude(shipper__code=32012).exclude(status_type=5)
        dl_report=request.POST['dl_report']
        shipment_info={}
        download_list = []

        for a in shipments:
            if not shipment_info.get(a):
                upd_time = a.added_on
                monthdir = upd_time.strftime("%Y_%m")
                shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
               # history = shipment_history.objects.filter(shipment=a).latest("updated_on")
                status_upd =  a.statusupdate_set.all().order_by("-date")
		rto_status = 0
                rem_status = 0
                rts_status = 0
                rts_stat_val = 0
                shipment=a
                rto_status = shipment_history.objects.using('local_ecomm').filter(shipment=shipment, reason_code_id = 34)
                rem_status = shipment_history.objects.using('local_ecomm').filter(shipment=shipment, remarks = "Return to Origin")
                history1 = shipment_history.objects.using('local_ecomm').filter(shipment=shipment).exclude(status__in=[11,12,16])
                history = history1.latest('updated_on')
                if history.reason_code_id in [1,6,46]:
                    continue
                if csc <> "0":
                   #return HttpResponse(history.current_sc_id)
                   if history.current_sc_id <> int(csc):
                      continue
                rtss = history1.order_by('id')
                if (rtss[0].reason_code_id==5):
                    rts_status = 1
                if (shipment.reason_code_id == 5 or shipment.return_shipment==3 or rts_status or shipment.return_shipment==2 or rto_status or rem_status):
                                  rts_stat_val = 1
		#if not a.original_dest:
                sc = a.service_centre
                #else:
                   # sc = a.original_dest
               # if status_upd and a.expected_dod:
                #    print status_upd[0].date, status_upd[0].id, a.expected_dod.date()
                 #   print "chk"
                  #  if status_upd[0].date <= a.expected_dod.date():
		if history.updated_on:
                    upd_date = history.updated_on.strftime("%Y-%m-%d")
                    #last_date = (datetime.datetime.now() - datetime.timedelta(hours=48))
                    last_date=datetime.datetime.today()-datetime.timedelta(days=2)
                    last_date = last_date.strftime("%Y-%m-%d")
                    if upd_date >= last_date or rts_stat_val == 1:
                        b=0
                    else:
                        b =1
                else:
                    b = 1

                if b==1:
                        if history:
                                hist = history
                                if not a.original_dest:
                                    u = (a.airwaybill_number,
                                         a.pickup.service_centre.center_name,
                                         a.added_on,
                                         hist.current_sc,
                                         sc,
                                         a.shipper.name,
                                         a.consignee,
                                         a.reason_code,
                                         hist.updated_on.date(),
                                         hist.updated_on.time(),
                                         get_internal_shipment_status(a.status),
                                         a.collectable_value,
                                         a.declared_value
                                         )
                                else:
                                    u = (a.airwaybill_number,
                                         a.pickup.service_centre.center_name,
                                         a.added_on,
                                         hist.current_sc,
                                         sc,
                                         a.shipper.name,
                                         a.consignee,
                                         a.reason_code,
                                         hist.updated_on.date(),
                                         hist.updated_on.time(),
                                         get_internal_shipment_status(a.status),
                                         a.collectable_value,
                                         a.declared_value

                                        )
                                download_list.append(u)
                                shipment_info[a]=hist
                        else:
                                shipment_info[a]=None
        if dl_report == "Download":
	    sheet = book.add_sheet("No-Information")
            sheet.write(0, 2, "No-Information Report", style=header_style)
            for a in range(9):
                sheet.col(a).width = 6000
            sheet.write(3, 0, "Air waybill Number", style=header_style)

            sheet.write(3, 1, "Origin Service Centre", style=header_style)
            sheet.write(3, 2, "Pickup Date", style=header_style)
            sheet.write(3, 3, "Current Service Centre", style=header_style)
            sheet.write(3, 4, "Destination Service Centre", style=header_style)
            sheet.write(3, 5, "Shipper", style=header_style)
            sheet.write(3, 6, "Consignee", style=header_style)
            sheet.write(3, 7, "Reason Code", style=header_style)
            sheet.write(3, 8, "Updated On Date", style=header_style)
            sheet.write(3, 9, "Updated On Time", style=header_style)

            sheet.write(3, 10, "Status", header_style)
            sheet.write(3, 11, "Collectable Value", header_style)
            sheet.write(3, 12, "Declared Value", header_style)



            for row, rowdata in enumerate(download_list, start=4):
                for col, val in enumerate(rowdata, start=0):
                             style = datetime_style
			     try:
                            	sheet.write(row, col, str(val), style=style)
			     except:
				pass
            response = HttpResponse(mimetype='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename=No-Information-report.xls'
            book.save(response)
            return response
        else:
            return render_to_response('reports/reports-noinfo.html',
                                  {'shipments':download_list},
                                  context_instance=RequestContext(request))

    customer=Customer.objects.using('local_ecomm').all()
    sc = ServiceCenter.objects.using('local_ecomm').all()

    return render_to_response("reports/noinfo.html",
                              {'customer':customer,
                               'sc':sc},

                               context_instance=RequestContext(request))


@csrf_exempt
def backdated(request):
    if request.POST:
        customer = request.POST['cust_id']
        date_from = request.POST['date_from']
        date_to = request.POST['date_to']
        sc=request.POST['sc']

        q = Q()
        if customer == "0":
            customer = None
        else:
            q = q & Q(shipper = int(customer))

        if not (date_from and date_to):
            pass
        else:
            q = q & Q(added_on__range=(date_from,date_to))

        if sc == "0":
            sc = None
        else:
            q = q & Q(service_centre=int(sc))
        shipments = Shipment.objects.using('local_ecomm').filter(q).exclude(status=9).exclude(reason_code__id__in=[1,6]).exclude(rts_status__gt=0).exclude(rto_status=1)
        report_type = request.POST['report_type']

        shipment_info={}
        download_list = []

        for a in shipments:
            if not shipment_info.get(a):
                upd_time = a.added_on
                monthdir = upd_time.strftime("%Y_%m")
                shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
                history = shipment_history.objects.using('local_ecomm').filter(shipment=a).exclude(status__in=[11,16,9]).latest("updated_on")
                if ((history.reason_code_id == 6) or (history.reason_code_id == 1)):
                   continue
                if a.statusupdate_set.all():
                       su = a.statusupdate_set.all().order_by("-date","-time")[:1][0]
                       rs=su.reason_code
                       remarks = su.remarks
                else:
                      rs = history.reason_code
                      remarks = ""
                updated_on = history.updated_on
                bck = a.added_on + datetime.timedelta(days=6)
                sc = a.original_dest
                if ((updated_on > bck)):
                                hist = history
                                u = (a.pickup.service_centre.center_name, a.added_on.strftime("%d-%m-%Y") , sc, a.airwaybill_number, a.shipper.name, a.consignee, rs, hist.updated_on.strftime("%d-%m-%Y %H:%m"), a.mobile, remarks)
                                download_list.append(u)
                                shipment_info[a]=hist
        if report_type == "dl":
            sheet = book.add_sheet("Backdated")
            sheet.write(0, 2, "Backdated Report", style=header_style)
            for a in range(9):
                sheet.col(a).width = 6000
            sheet.write(3, 0, "Origin Service Centre", style=header_style)
            sheet.write(3, 1, "Pickup Date", style=header_style)
            sheet.write(3, 2, "Destination Service Centre", style=header_style)
            sheet.write(3, 3, "Air waybill Number", style=header_style)
            sheet.write(3, 4, "Shipper", style=header_style)
            sheet.write(3, 5, "Consignee", style=header_style)
            sheet.write(3, 6, "Reason Code", style=header_style)
            sheet.write(3, 7, "Status Updated On", style=header_style)
            sheet.write(3, 8, "Mobile Number", style=header_style)
            sheet.write(3, 9, "Remarks", style=header_style)

            for row, rowdata in enumerate(download_list, start=4):
                for col, val in enumerate(rowdata, start=0):
                             style = datetime_style
			     try:
	                        sheet.write(row, col, str(val), style=style)
			     except:
				pass
            response = HttpResponse(mimetype='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename=Backdated-report.xls'
            book.save(response)
            return response
        else:
            return render_to_response('reports/reports-backdated.html',
                                  {'shipments':download_list},
                                  context_instance=RequestContext(request))
    customer=Customer.objects.using('local_ecomm').all()
    sc = ServiceCenter.objects.using('local_ecomm').all()

    return render_to_response("reports/backdated.html",
                              {'customer':customer,
                               'sc':sc},
                               context_instance=RequestContext(request))

def previousday(request):
    customer=Customer.objects.using('local_ecomm').all()
    sc = ServiceCenter.objects.using('local_ecomm').all()

    return render_to_response("reports/previousday.html",
                              {'customer':customer,
                               'sc':sc},

                               context_instance=RequestContext(request))
@csrf_exempt
def cod_collection_pod(request):
    if request.POST:
        customer = request.POST['cust_id']
        date_from = request.POST['date_from']
        date_to = request.POST['date_to']
        sc=request.POST['sc']
        report_type = request.POST['report_type']

        if report_type == 'dl':
            report = CodCollectionPodReport(date_from, date_to, customer, sc)
            file_name = report.generate_report()
            return HttpResponseRedirect('/static/uploads/reports/{0}'.format(file_name))
        else:
            report = CodCollectionPodReport(date_from, date_to, customer, sc)
            q = report.get_query()
            shipments = Shipment.objects.using('local_ecomm').filter(q).exclude(rts_status=1)
            return render_to_response("reports/reports_view.html",
                              {'shipment':shipments},
                              context_instance=RequestContext(request))
    else:
        customer=Customer.objects.using('local_ecomm').all()
        sc = ServiceCenter.objects.using('local_ecomm').all()
    return render_to_response("reports/cod_collection_exception.html",
                              {'customer':customer,
                               'sc':sc},
                               context_instance=RequestContext(request))

@csrf_exempt
def tally_input_xml(request):
    if request.POST:
        date_from = request.POST['date_from']
        date_to = request.POST['date_to']
        report_type = request.POST['report_type']

        report = CodCollectionPodReport(date_from, date_to)
        if report_type == 'dl':
            file_name = report.create_xml_report()
            return HttpResponseRedirect('/static/uploads/reports/{0}'.format(file_name))
        else:
            q = report.get_query()
            shipments = Shipment.objects.using('local_ecomm').filter(q).exclude(rts_status=1)
            return render_to_response("reports/reports_view.html",
                              {'shipment':shipments},
                              context_instance=RequestContext(request))
    else:
        customer=Customer.objects.using('local_ecomm').all()
        sc = ServiceCenter.objects.using('local_ecomm').all()
    return render_to_response("reports/tally_input_xml.html",
                              {'customer':customer,
                               'sc':sc},
                               context_instance=RequestContext(request))
@csrf_exempt
def cod_collection_pod_rev(request):
    if request.POST:
        customer = request.POST['cust_id']
        date_from = request.POST['date_from']
        date_to = request.POST['date_to']

        sc=request.POST['sc']
        q = Q()
        if customer == "0":
            customer = None
        else:
            q = q & Q(shipper_id = int(customer))
        if not (date_from and date_to):
            pass
        else:
            #t = datetime.datetime.strptime(date_to, "%Y-%m-%d") + datetime.timedelta(days=1)
            t = datetime.datetime.strptime(date_to, "%Y-%m-%d") + datetime.timedelta(days=1)
            date_to = t.strftime("%Y-%m-%d")
            q = q & Q(added_on__range=(date_from,date_to), status__in = [2,6], reason_code__in=[1,44])
            #q = q & Q(statusupdate__added_on__range=(date_from,date_to), statusupdate__status = 2, reason_code=1)
        if sc == "0":
            sc = None
        else:
            q = q & Q(service_centre_id=int(sc))
        shipments = StatusUpdate.objects.using('local_ecomm').filter(q, shipment__product_type = "cod").exclude(shipment__rts_status=1)
        #shipments = Shipment.objects.using('local_ecomm').filter(q, product_type = "cod").exclude(rts_status=1)

        #shipments = query_cod(customer, date_from, date_to, sc)

        report_type = request.POST['report_type']
        shipment_info={}
        download_list = []

        for b in shipments:
            a = b.shipment
            if 1==1:
                    if 1 == 1:
                        amount_collected_subtract=0
                        #awb = AirwaybillTally.objects.using('local_ecomm').get(shipment=a)
                        shipment_info[a]= a
                        upd_time = a.added_on
                        monthdir = upd_time.strftime("%Y_%m")
                        shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
                        if a.rts_status or a.rto_status:
                            amount_collected = "return"
                        else:
                            amount_collected = a.collectable_value

                       # if not awb.amount_collected:
                        #    amount_collected_subtract = 0

                        #if not awb.amount_collected:
                         #   amount_collected_subtract = 0

                      #  if not awb.delivery_emp_code:
                      #      emp_code = ""
                      #      emp_firstname  = ""
                      #  else:
                      #      emp_code = awb.delivery_emp_code.employee_code
                      #      emp_firstname  = awb.delivery_emp_code.firstname
                      #  if a.statusupdate_set.all():
                       #   status_upda =  a.statusupdate_set.filter(status=2).latest("added_on")
                        if 1==1:
                          status_upda = b
                          if b.status == 6:
                                amount_collected = 0 - a.collectable_value
                          status_upd=  status_upda.date.strftime("%d-%m-%Y")+" "+status_upda.time.strftime("%H:%m")
                          upd_date = status_upda.added_on.strftime("%Y-%m-%d %H:%m")
                          emp_code = status_upda.delivery_emp_code.employee_code
                          emp_firstname  = status_upda.delivery_emp_code.firstname
                        else:
                          emp_code = ""
                          emp_firstname  = ""
                          status_upd = ""
                          upd_date = ""
                        if a.codcharge_set.filter():
                           amt = a.codcharge_set.get().status
                           amt = "Yes" if amt else "No"
                        else:
                           amt = "No"
                        try:
                            history = shipment_history.objects.using('local_ecomm').filter(shipment=a).exclude(status__in=[11,12,16]).latest('updated_on')
                            u = (a.airwaybill_number, a.added_on, a.pickup.service_centre, a.shipper.code, a.consignee, amount_collected, amount_collected,a.collectable_value, emp_code, emp_firstname,a.service_centre, status_upda.reason_code, status_upda.added_on, str(status_upda.date)+" "+str(status_upda.time), amt)
                        except:
                            u = (a.airwaybill_number, a.added_on, a.pickup.service_centre, a.shipper.code, a.consignee, amount_collected, amount_collected,a.collectable_value, emp_code, emp_firstname,a.service_centre, "","", amt)
                        download_list.append(u)

                    else:
                        upd_time = a.added_on
                        monthdir = upd_time.strftime("%Y_%m")
                        shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
                        shipment_info[a]=None
                        try:
                            history = shipment_history.objects.using('local_ecomm').filter(shipment=a).latest('updated_on')
                            u = (a.airwaybill_number, a.added_on, a.pickup.service_centre, a.shipper.code, a.consignee, a.collectable_value, "","", "", "",a.service_centre, history.reason_code, upd_date, status_upd)
                        except:
                            u = (a.airwaybill_number, a.added_on, a.pickup.service_centre, a.shipper.code, a.consignee, a.collectable_value, "","", "", "",a.service_centre, "","")
                        download_list.append(u)

        if report_type == "dl":
            sheet = book.add_sheet('COD Collection')
            distinct_list = download_list
            sheet.write(0, 2, "COD Collection-POD Report", style=header_style)

            for a in range(14):
                sheet.col(a).width = 6000
            sheet.write(3, 0, "Serial Number", style=header_style)
            sheet.write(3, 1, "AWB Number", style=header_style)
            sheet.write(3, 2, "Pickup Date", style=header_style)
            sheet.write(3, 3, "Origin", style=header_style)
            sheet.write(3, 4, "Shipper", style=header_style)
            sheet.write(3, 5, "Consignee", style=header_style)
            sheet.write(3, 6, "COD Due", style=header_style)
            sheet.write(3, 7, "COD Collected", style=header_style)
            sheet.write(3, 8, "COD Balance", style=header_style)
            sheet.write(3, 9, "Delivery Employee Code", style=header_style)
            sheet.write(3, 10, "Delivery Employee Name", style=header_style)
            sheet.write(3, 11, "Dest Centre", style=header_style)
            sheet.write(3, 12, "Reason", style=header_style)
            sheet.write(3, 13, "Updated on", style=header_style)
            sheet.write(3, 14, "Delivery Date", style=header_style)
            sheet.write(3, 15, "Amount Deposited", style=header_style)
            style = datetime_style
            counter = 1
            for row, rowdata in enumerate(distinct_list, start=4):
                    sheet.write(row, 0, str(counter), style=style)
                    counter=counter+1

                    for col, val in enumerate(rowdata, start=1):
                       try:
                         sheet.write(row, col, str(val), style=style)
                       except:
                         pass
            response = HttpResponse(mimetype='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename=COD_Collection.xls'
            book.save(response)
            return response
        else:
            return render_to_response("reports/reports_view.html",
                              {'shipment':shipment_info},context_instance=RequestContext(request))

    else:
        customer=Customer.objects.using('local_ecomm').all()
        sc = ServiceCenter.objects.using('local_ecomm').all()
    return render_to_response("reports/cod_collection_exception.html",
                              {'customer':customer,
                               'sc':sc},
                               context_instance=RequestContext(request))



@csrf_exempt
def cod_collection(request):
    if request.POST:
        customer = request.POST['cust_id']
        date_from = request.POST['date_from']
        date_to = request.POST['date_to']

        sc=request.POST['sc']
        shipments = query_cod(customer, date_from, date_to, sc)
        shipments = shipments.exclude(rts_status=1)
        report_type = request.POST['report_type']
        shipment_info={}
        download_list = []

        for a in shipments:
            if a.product_type.lower()=="cod":
                if not shipment_info.get(a):
                    awbs =  AirwaybillTally.objects.using('local_ecomm').filter(shipment=a)
                    if len(awbs) == 1:
                        amount_collected_subtract=0
                        awb = AirwaybillTally.objects.using('local_ecomm').get(shipment=a)
                        shipment_info[a]= awb
                        upd_time = a.added_on
                        monthdir = upd_time.strftime("%Y_%m")
                        shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
                        if a.return_shipment == 3:
                            amount_collected = "rts"
                        else:
                            amount_collected = awb.amount_collected

                        if not awb.amount_collected:
                            amount_collected_subtract = 0

                        if not awb.amount_collected:
                            amount_collected_subtract = 0

                        if not awb.delivery_emp_code:
                            emp_code = ""
                            emp_firstname  = ""
                        else:
                            emp_code = awb.delivery_emp_code.employee_code
                            emp_firstname  = awb.delivery_emp_code.firstname

                        try:
                            history = shipment_history.objects.using('local_ecomm').filter(shipment=a).latest('updated_on')
                            u = (a.airwaybill_number, a.added_on, a.pickup.service_centre, a.shipper.code, a.consignee, a.collectable_value, amount_collected, (float(a.collectable_value) - float(amount_collected_subtract)), emp_code, emp_firstname,a.service_centre, history.reason_code, history.updated_on.strftime("%Y-%m-%d %H:%m"))
                        except:
                            u = (a.airwaybill_number, a.added_on, a.pickup.service_centre, a.shipper.code, a.consignee, a.collectable_value, amount_collected, (float(a.collectable_value) - float(amount_collected_subtract)), emp_code, emp_firstname,a.service_centre, "","")
                        download_list.append(u)

                    else:
                        upd_time = a.added_on
                        monthdir = upd_time.strftime("%Y_%m")
                        shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
                        shipment_info[a]=None
                        try:
                            history = shipment_history.objects.using('local_ecomm').filter(shipment=a).latest('updated_on')
                            u = (a.airwaybill_number, a.added_on, a.pickup.service_centre, a.shipper.code, a.consignee, a.collectable_value, "","", "", "",a.service_centre, history.reason_code, history.updated_on.strftime("%Y-%m-%d %H:%m"))
                        except:
                            u = (a.airwaybill_number, a.added_on, a.pickup.service_centre, a.shipper.code, a.consignee, a.collectable_value, "","", "", "",a.service_centre, "","")
                        download_list.append(u)

        if report_type == "dl":
            sheet = book.add_sheet('COD Collection')
            distinct_list = download_list
            sheet.write(0, 2, "COD Collection-Exception Report", style=header_style)

            for a in range(12):
                sheet.col(a).width = 6000
            sheet.write(3, 0, "Serial Number", style=header_style)
            sheet.write(3, 1, "AWB Number", style=header_style)
            sheet.write(3, 2, "Pickup Date", style=header_style)
            sheet.write(3, 3, "Origin", style=header_style)
            sheet.write(3, 4, "Shipper", style=header_style)
            sheet.write(3, 5, "Consignee", style=header_style)
            sheet.write(3, 6, "COD Due", style=header_style)
            sheet.write(3, 7, "COD Collected", style=header_style)
            sheet.write(3, 8, "COD Balance", style=header_style)
            sheet.write(3, 9, "Delivery Employee Code", style=header_style)
            sheet.write(3, 10, "Delivery Employee Name", style=header_style)
            sheet.write(3, 11, "Dest Centre", style=header_style)
            style = datetime_style
            counter = 1
            for row, rowdata in enumerate(distinct_list, start=4):
                    sheet.write(row, 0, str(counter), style=style)
                    counter=counter+1
                    for col, val in enumerate(rowdata, start=1):
                        try:
                            sheet.write(row, col, str(val), style=style)
                        except:
                           pass

            response = HttpResponse(mimetype='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename=COD_Collection.xls'
            book.save(response)
            return response
        else:
            return render_to_response("reports/reports_view.html",
                              {'shipment':shipment_info},context_instance=RequestContext(request))

    else:
        customer=Customer.objects.using('local_ecomm').all()
        sc = ServiceCenter.objects.using('local_ecomm').all()
    return render_to_response("reports/cod_collection_exception.html",
                              {'customer':customer,
                               'sc':sc},
                               context_instance=RequestContext(request))

@csrf_exempt
def cod_collection_daytally(request):
    if request.POST:
        customer = request.POST['cust_id']
        date_from = request.POST['date_from']
        date_to = request.POST['date_to']

        sc=request.POST['sc']
        emp=request.POST['emp']
        shipments = StatusUpdate.objects.using('local_ecomm').filter(delivery_emp_code_id=int(emp))
        shipment_info={}
        download_list = []

        for a in shipments:
                if not shipment_info.get(a):
                    try:
                        awb = AirwaybillTally.objects.using('local_ecomm').get(shipment=a.shipment)
                        shipment_info[a.shipment]= awb
                        #u = (a.airwaybill_number, a.pickup.pickup_date, a.pickup.service_centre, a.shipper.code, a.consignee, a.collectable_value, awb.amount_collected, (float(a.collectable_value) - float(awb.amount_collected)), awb.delivery_emp_code.employee_code, awb.delivery_emp_code.firstname,)
                        #download_list.append(u)

                    except:
                        #pass
                        shipment_info[a.shipment]=None
                        #u = (a.airwaybill_number, a.pickup.pickup_date, a.pickup.service_centre, a.shipper.code, a.consignee, a.collectable_value, "",a.collectable_value)
                        #download_list.append(u)
        return render_to_response("reports/reports_view.html",
                              {'shipment':shipment_info},context_instance=RequestContext(request))

        report_type = request.POST['report_type']
        shipment_info={}
        download_list = []
    else:
        customer=Customer.objects.using('local_ecomm').all()
        sc = ServiceCenter.objects.using('local_ecomm').all()
    return render_to_response("reports/cod_collection_daytally.html",
                              {'customer':customer,
                               'sc':sc},
                               context_instance=RequestContext(request))

@csrf_exempt
def sc_emp(request):

     emp_dict = {}
     emp = EmployeeMaster.objects.using('local_ecomm').filter(service_centre_id=int(request.POST['sc']))
     if emp:
         for a in emp:
             emp_dict[a.id]=str(a.employee_code)+"-"+str(a.firstname)
     return HttpResponse(json.dumps(emp_dict))

@csrf_exempt
def daily_sales_register(request):
#    shipment=Shipment.objects.using('local_ecomm').all()
    customer=Customer.objects.using('local_ecomm').all()
    sc = ServiceCenter.objects.using('local_ecomm').all()
    now=datetime.datetime.now()
    update_today=""
    dl_report=""
    if request.POST:
        if request.POST['date']:
            current_date=request.POST['date']
        else:
            current_date=""

        if request.POST['dl_report']:
            dl_report = request.POST['dl_report']

        else:
            dl_report=""

        shipment_info={}
        download_list = []
	if current_date<>'':
            update_today = StatusUpdate.objects.using('local_ecomm').filter(date=str(current_date))
            for a in update_today:
                order_price = Order_price.objects.using('local_ecomm').get(shipment=a.shipment)
                if a.shipment.product_type=="cod":
                    codcharge=CODCharge.objects.using('local_ecomm').filter(shipment=a.shipment)[0]
                    u = (a.shipment.shipper.code, a.shipment.shipper.name, a.shipment.airwaybill_number, a.shipment.collectable_value,order_price.freight_charge, codcharge.cod_charge,"",order_price.fuel_surcharge,"")
                else:
                    u = (a.shipment.shipper.code, a.shipment.shipper.name, a.shipment.airwaybill_number, a.shipment.collectable_value,order_price.freight_charge, "","",order_price.fuel_surcharge,"")
                download_list.append(u)
        else:
            current_date=now.strftime("%Y-%m-%d")
            update_today = StatusUpdate.objects.using('local_ecomm').filter(date=str(current_date))
            for a in update_today:
                order_price = Order_price.objects.using('local_ecomm').get(shipment=a.shipment)
                if a.shipment.product_type=="cod":
                    codcharge=CODCharge.objects.using('local_ecomm').filter(shipment=a.shpment)[0]
                    u = (a.shipment.shipper.code, a.shipment.shipper.name, a.shipment.airwaybill_number, a.shipment.collectable_value,order_price.freight_charge, codcharge.cod_charge,"",order_price.fuel_surcharge,"")
                else:
                    u = (a.shipment.shipper.code, a.shipment.shipper.name, a.shipment.airwaybill_number, a.shipment.collectable_value,order_price.freight_charge, "","",order_price.fuel_surcharge,"")
                download_list.append(u)
        if dl_report == "Download":
                sheet = book.add_sheet('Daily sales Register')
                distinct_list = download_list
                sheet.write(0, 2, "Daily sales Register", style=header_style)

                for a in range(10):
                    sheet.col(a).width = 6000
                sheet.write(3, 0, "Serial Number", style=header_style)
                sheet.write(3, 1, "CustCode", style=header_style)
                sheet.write(3, 2, "Customer", style=header_style)
                sheet.write(3, 3, "AWB No", style=header_style)
                sheet.write(3, 4, "Chargeable", style=header_style)
                sheet.write(3, 5, "Freight", style=header_style)
                sheet.write(3, 6, "COD", style=header_style)
                sheet.write(3, 7, "Other", style=header_style)
                sheet.write(3, 8, "Fuel", style=header_style)
                sheet.write(3, 9, "Total", style=header_style)

                style = datetime_style
                counter = 1
                for row, rowdata in enumerate(distinct_list, start=4):
                        sheet.write(row, 0, str(counter), style=style)
                        counter=counter+1
                        for col, val in enumerate(rowdata, start=1):
                            sheet.write(row, col, str(val), style=style)
                response = HttpResponse(mimetype='application/vnd.ms-excel')
                response['Content-Disposition'] = 'attachment; filename=daily_sales_register.xls'
                book.save(response)
                return response
        else:
            if update_today:
                return render_to_response("reports/reports-daily-sales.html",
                                  {'update_today':update_today,
                                   'sc':sc
                                   },

                                   context_instance=RequestContext(request))


    else:
        return render_to_response("reports/Daily-sales-Register.html",
                                      {'customer':customer,
                                       'sc':sc},

                                       context_instance=RequestContext(request))
@csrf_exempt
def customer_wise_day_wise_sales_summary(request):
    customer=Customer.objects.using('local_ecomm').all()
    sc = ServiceCenter.objects.using('local_ecomm').all()
    now=datetime.datetime.now()
    update_today=""
    dl_report=""
    if request.POST:
        if request.POST['date']:
            current_date=request.POST['date']
        else:
            current_date=""
        if request.POST['dl_report']:
            dl_report = request.POST['dl_report']

        else:
            dl_report=""
        shipment_info={}
        download_list = []
        if current_date<>'':
            update_today = StatusUpdate.objects.using('local_ecomm').filter(date=str('2013-04-09'))
            for a in update_today:
                shipment_info[a]= update_today
                u = (a.shipment.shipper.code, a.shipment.shipper.name, a.shipment.airwaybill_number, a.shipment.collectable_value,)
                download_list.append(u)
        else:
            current_date=now.strftime("%Y-%m-%d")
            update_today = StatusUpdate.objects.using('local_ecomm').filter(date=str(current_date))
            for a in update_today:
                shipment_info[a]= update_today
                u = (a.shipment.shipper.code, a.shipment.shipper.name, a.shipment.airwaybill_number, a.shipment.collectable_value,)
                download_list.append(u)
        if dl_report == "Download":
                sheet = book.add_sheet('Customer-wise Day-wise Sales')
                distinct_list = download_list
                sheet.write(0, 2, "Customer-wise Day-wise Sales", style=header_style)

                for a in range(10):
                    sheet.col(a).width = 6000
                sheet.write(3, 0, "Serial Number", style=header_style)
                sheet.write(3, 1, "CustCode", style=header_style)
                sheet.write(3, 2, "Customer", style=header_style)
                sheet.write(3, 3, "AWB No", style=header_style)
                sheet.write(3, 4, "Chargeable", style=header_style)
                sheet.write(3, 5, "Freight Charges", style=header_style)
                sheet.write(3, 6, "COD Charge", style=header_style)
                sheet.write(3, 7, "Other Charge", style=header_style)
                sheet.write(3, 8, "Fuel sc", style=header_style)
                sheet.write(3, 9, "Total", style=header_style)

                style = datetime_style
                counter = 1
                for row, rowdata in enumerate(distinct_list, start=4):
                        sheet.write(row, 0, str(counter), style=style)
                        counter=counter+1
                        for col, val in enumerate(rowdata, start=1):
                            sheet.write(row, col, str(val), style=style)
                response = HttpResponse(mimetype='application/vnd.ms-excel')
                response['Content-Disposition'] = 'attachment; filename=Customerwise_Daywise_Sales_Summary.xls'
                book.save(response)
                return response
        else:
            if update_today:
                return render_to_response("reports/report_customerwise_daywise.html",
                                  {'update_today':update_today,
                                   'sc':sc
                                   },

                                   context_instance=RequestContext(request))


    else:
        return render_to_response("reports/customer_wise_day_wise_sales_summary.html",
                              {'customer':customer,
                               'sc':sc},

                               context_instance=RequestContext(request))
@csrf_exempt
def customer_wise_bill_summary(request):
    if request.POST:
        customer = request.POST['cust_id']
        date_from = request.POST['date_from']

        date_to = request.POST['date_from']
        sc=0
        shipments = query_cod(customer, date_from, date_to, sc)
        report_type = request.POST['report_type']
        shipment_info={}
        download_list = []

        for a in shipments:
            if not shipment_info.get(a):
                    try:
                        awb = AirwaybillTally.objects.using('local_ecomm').get(shipment=a)
                        shipment_info[a]= awb
                        u = (a.airwaybill_number, a.added_on, a.pickup.service_centre, a.shipper.code, a.consignee, a.collectable_value, awb.amount_collected, (float(a.collectable_value) - float(awb.amount_collected)), awb.delivery_emp_code.employee_code, awb.delivery_emp_code.firstname,)
                        download_list.append(u)

                    except:
                        shipment_info[a]=None
                        u = (a.airwaybill_number, a.added_on, a.pickup.service_centre, a.shipper.code, a.consignee, a.collectable_value, "",a.collectable_value)
                        download_list.append(u)

        if report_type == "dl":
            sheet = book.add_sheet('COD Collection')
            distinct_list = download_list
            sheet.write(0, 2, "COD Collection-Exception Report", style=header_style)

            for a in range(12):
                sheet.col(a).width = 6000
            sheet.write(3, 0, "Serial Number", style=header_style)
            sheet.write(3, 1, "AWB Number", style=header_style)
            sheet.write(3, 2, "Pickup Date", style=header_style)
            sheet.write(3, 3, "Origin", style=header_style)
            sheet.write(3, 4, "Shipper", style=header_style)
            sheet.write(3, 5, "Consignee", style=header_style)
            sheet.write(3, 6, "COD Due", style=header_style)
            sheet.write(3, 7, "COD Collected", style=header_style)
            sheet.write(3, 8, "COD Balance", style=header_style)
            sheet.write(3, 9, "Delivery Employee Code", style=header_style)
            sheet.write(3, 10, "Delivery Employee Name", style=header_style)
            sheet.write(3, 11, "Delivery Employee Agent", style=header_style)
            style = datetime_style
            counter = 1
            for row, rowdata in enumerate(distinct_list, start=4):
                    sheet.write(row, 0, str(counter), style=style)
                    counter=counter+1
                    for col, val in enumerate(rowdata, start=1):
                        sheet.write(row, col, str(val), style=style)
            response = HttpResponse(mimetype='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename=COD_Collection.xls'
            book.save(response)
            return response
        else:
            return render_to_response("reports/report_customer_wise_bill_summary.html",
                              {'shipment':shipment_info},context_instance=RequestContext(request))

    else:
        customer=Customer.objects.using('local_ecomm').all()
        sc = ServiceCenter.objects.using('local_ecomm').all()
    return render_to_response("reports/customer_wise_bill_summary.html",
                              {'customer':customer,
                               'sc':sc},
                               context_instance=RequestContext(request))

def sub_customers(request):
    customer=Customer.objects.using('local_ecomm').all()
    sc = ServiceCenter.objects.using('local_ecomm').all()
    return render_to_response("reports/sub_customers_report.html",
                              {'customer':customer,
                               'sc':sc},
                               context_instance=RequestContext(request))

def sub_customers_report_view(request):
    if request.method == 'POST':
        return HttpResponseRedirect(reverse('excel_sub_customer_report', args=[request.POST.get('cust_id')]))

    cid = request.GET.get('cust_id')
    cid = int(cid)
    if cid:
        c = Customer.objects.using('local_ecomm').get(id=cid)
        sub_customers = Shipper.objects.using('local_ecomm').filter(customer=c)
    else:
        sub_customers = Shipper.objects.using('local_ecomm').all()

    return render_to_response("reports/sub_customer_report_data.html",
                               {'sub_customers':sub_customers},
                               context_instance=RequestContext(request))

def get_shipper_details(shipper):
    if shipper.address:
        return (shipper.id, shipper.alias_code, shipper.name, (str(shipper.address.city)+" - "+str(shipper.address.pincode)))
    else:
        return (shipper.id, shipper.name, '-')

@csrf_exempt
def sub_customer_report(request, cid):
    """ this view provides the excel file containing the subcustomers details"""
    cid = int(cid)
    if cid == 0:
        sub_customers = Shipper.objects.using('local_ecomm').all()
    else:
        c = Customer.objects.using('local_ecomm').get(id=cid)
        sub_customers = Shipper.objects.using('local_ecomm').filter(customer=c)

    distinct_list=(get_shipper_details(a) for a in sub_customers)

    sheet = book.add_sheet('Sub Customer')
    sheet.write(0, 2, "Sub Customer Details", style=header_style)

    for a in range(4):
        sheet.col(a).width = 9000

    sheet.write(3, 0, "Serial Number", style=header_style)
    sheet.write(3, 1, "Sub Customer Code", style=header_style)
    sheet.write(3, 2, "Alias Code", style=header_style)
    sheet.write(3, 3, "Sub Customer Name", style=header_style)
    sheet.write(3, 4, "Address", style=header_style)
    style = datetime_style
    counter = 1
    for row, rowdata in enumerate(distinct_list, start=4):
          sheet.write(row, 0, str(counter), style=style)
          counter=counter+1
          for col, val in enumerate(rowdata, start=1):
                  val = val.encode('utf8') if isinstance(val, unicode) else str(val)
                  sheet.write(row, col, val, style=style)
    response = HttpResponse(mimetype='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=Sub_Customer.xls'
    book.save(response)
    return response

@csrf_exempt
def backup_sub_customer_report(request, cid):
    c = Customer.objects.using('local_ecomm').get(id=cid)
    distinct_list=[]
    sub_customers = Shipper.objects.using('local_ecomm').filter(customer=c)
    for a in sub_customers:
         info = (a.id, a.name, (str(a.address.city)+" - "+str(a.address.pincode)))
         distinct_list.append(info)
    sheet = book.add_sheet('Sub Customer')
    #distinct_list = sub_customers
    sheet.write(0, 2, "Sub Customer Details", style=header_style)

    for a in range(4):
                sheet.col(a).width = 9000
    sheet.write(3, 0, "Serial Number", style=header_style)
    sheet.write(3, 1, "Sub Customer Code", style=header_style)
    sheet.write(3, 2, "Sub Customer Name", style=header_style)
    sheet.write(3, 3, "Address", style=header_style)
    style = datetime_style
    counter = 1
    for row, rowdata in enumerate(distinct_list, start=4):
          sheet.write(row, 0, str(counter), style=style)
          counter=counter+1
          for col, val in enumerate(rowdata, start=1):
                  sheet.write(row, col, str(val), style=style)
    response = HttpResponse(mimetype='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=Sub_Customer.xls'
    book.save(response)
    return response

@csrf_exempt
def delivery_dispatch(request):
    if request.POST:
        customer = request.POST['cust_id']
        date_from = request.POST['date_from']
        if request.POST['date_to']:
            date_to = request.POST['date_to']
        else:
            date_to = '2050-12-12'
        sc=request.POST['sc']
        q = Q()
        if customer == "0":
            customer = None
        else:
            q = q & Q(shipper_id = int(customer))
        if not (date_from and date_to):
            pass
        else:
            t = datetime.datetime.strptime(date_to, "%Y-%m-%d") + datetime.timedelta(days=1)
            date_to = t.strftime("%Y-%m-%d")
            q = q & Q(expected_dod__range=(date_from,date_to))
        if sc == "0":
            sc = None
        else:
            q = q & Q(service_centre_id=int(sc))
        shipments = Shipment.objects.using('local_ecomm').filter(q)
        #return HttpResponse(shipments)
        report_type = request.POST['report_type']

        shipment_info={}
        download_list = []
        for a in shipments:
                if not shipment_info.get(a):
                    try:
                        statusupdate = StatusUpdate.objects.using('local_ecomm').filter(shipment=a).latest('id')
                        shipment_info[a]= statusupdate
                        u = (a.airwaybill_number,a.order_number, a.added_on,a.shipper.name, a.consignee, a.consignee_address1,a.consignee_address2, a.destination_city, a.pincode, a.collectable_value,statusupdate.date,statusupdate.time, statusupdate.recieved_by)
                    except:
                        shipment_info[a]= None
                        u = (a.airwaybill_number,a.order_number, a.added_on,a.shipper.name, a.consignee, a.consignee_address1,a.consignee_address2, a.destination_city, a.pincode, a.collectable_value,"In Progress","","")
                    download_list.append(u)


        if report_type == "dl":
            sheet = book.add_sheet('Delivery and Dispatch')
            distinct_list = download_list
            sheet.write(0, 2, "Delivery and Dispatch Report", style=header_style)

            for a in range(6):
                sheet.col(a).width = 5000
            sheet.col(6).width = 7000
            sheet.col(7).width = 7000
            sheet.col(8).width = 4000
            sheet.col(9).width = 4000
            sheet.col(10).width = 4000
            sheet.col(11).width = 4000
            sheet.col(12).width = 4000
            sheet.col(13).width = 6000
            sheet.write(3, 0, "Serial Number", style=header_style)
            sheet.write(3, 1, "AWB Number", style=header_style)
            sheet.write(3, 2, "Order No", style=header_style)
            sheet.write(3, 3, "Pickup Date", style=header_style)
            sheet.write(3, 4, "Shipper Name", style=header_style)
            sheet.write(3, 5, "Consignee Name", style=header_style)
            sheet.write(3, 6, "Address1", style=header_style)
            sheet.write(3, 7, "Address2", style=header_style)
            sheet.write(3, 8, "City name", style=header_style)
            sheet.write(3, 9, "Pin Code", style=header_style)
            sheet.write(3, 10, "COD Amount", style=header_style)
            sheet.write(3, 11, "Date", style=header_style)
            sheet.write(3, 12, "Time", style=header_style)
            sheet.write(3, 13, "Recieved By", style=header_style)
            style = datetime_style
            counter = 1
            for row, rowdata in enumerate(distinct_list, start=4):
                    sheet.write(row, 0, str(counter), style=style)
                    counter=counter+1
                    for col, val in enumerate(rowdata, start=1):
                            if col==3:
                                d=datetime.datetime.strptime(str(val),'%Y-%m-%d')
                                sheet.write(row, col, d.strftime('%d-%m-%Y'), style=style)
                            if col==11:
                                if str(val)<>'In Progress':
                                    d=datetime.datetime.strptime(str(val),'%Y-%m-%d')
                                    sheet.write(row, col, d.strftime('%d-%m-%Y'), style=style)
                            if col <> 3 and col <> 11:
				try:
	                            sheet.write(row, col, str(val), style=style)
				except:
				    pass
#            response = excel_download(download_list, "delivery_dispatch")
            response = HttpResponse(mimetype='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename=Delivery-Dispatch.xls'
            book.save(response)
            return response
        else:
            return render_to_response('reports/reports-delivery-dispatch.html',
                                  {'shipments':shipment_info},
                                  context_instance=RequestContext(request))

    customer=Customer.objects.using('local_ecomm').all()
    sc = ServiceCenter.objects.using('local_ecomm').all()

    return render_to_response("reports/delivery-dispatch.html",
                              {'customer':customer,
                               'sc':sc},

                               context_instance=RequestContext(request))


@csrf_exempt
def day_wise_count(request):

    if request.POST:
        report_type = request.POST['report_type']
        customer = request.POST['cust_id']
        sc=request.POST['sc']

        date_from1 = now.strftime("%Y-%m-%d")
        t = datetime.datetime.strptime(date_from1, "%Y-%m-%d") - datetime.timedelta(days=1)
        date_from = t.strftime("%Y-%m-%d %H:%M:%S")
        t1 = datetime.datetime.strptime(date_from1, "%Y-%m-%d") - datetime.timedelta(seconds=1)
        date_to = t1.strftime("%Y-%m-%d %H:%M:%S")
        total_count=0
        ship_rec_count =0
        rto_count=0
        delivered_count=0
        undelivered_count=0
        download_list = []

        q = Q()
        if customer == "0":
            customer = None
        else:
            q = q & Q(shipper_id = int(customer))

        if sc == "0":
            sc = None
        else:
            q = q & Q(service_centre_id=int(sc))
        ship_rec_count=0
        total_shipment  = Shipment.objects.using('local_ecomm').filter(q,added_on__range=(date_from, date_to))
        total_count =  total_shipment.only('id').count()
        inscanned=Shipment.objects.using('local_ecomm').filter(q,inscan_date__range=(date_from, date_to))
        ship_rec = Shipment.objects.using('local_ecomm').filter(q, status = 6, added_on__range=(date_from, date_to))
        ship_red=Shipment.objects.using('local_ecomm').filter(q, rd_status = 1, added_on__range=(date_from, date_to))
        ship_redirc_count=ship_red.only('id').count()
        ship_rec_count =ship_rec.only('id').count()
        ship_outscan=Shipment.objects.using('local_ecomm').filter(q, status = 7, added_on__range=(date_from, date_to))
        rto_ship = Shipment.objects.using('local_ecomm').filter(q, return_shipment = 2, added_on__range=(date_from, date_to))
        rto_count = rto_ship.only('id').count()

        delivered_ship = Shipment.objects.using('local_ecomm').filter(q, status = 9, added_on__range=(date_from, date_to))
        delivered_count =delivered_ship.only('id').count()

        undelivered_ship = Shipment.objects.using('local_ecomm').filter(q, status = 8, added_on__range=(date_from, date_to))
        undelivered_count = undelivered_count + undelivered_ship.only('id').count()
        trnst =total_count - (delivered_count +undelivered_count)

        u = (str(t1.strftime('%d-%m-%Y')), ship_rec_count, rto_count, delivered_count, undelivered_count,ship_redirc_count,inscanned.only('id').count(),ship_outscan.only('id').count())
        download_list.append(u)

        if report_type == "dl":
            sheet = book.add_sheet('Day-Wise Count Reports')
            sheet.write(0, 2, "Day-Wise Count Reports", style=header_style)

            for a in range(7):
                sheet.col(a).width = 3000
            sheet.write(3, 0, "Date", style=header_style)

            sheet.write(3, 1, "RTO", style=header_style)
            sheet.write(3, 2, "Delivered", style=header_style)
            sheet.write(3, 3, "Undelivered", style=header_style)
            sheet.write(3, 4, "In Transit", style=header_style)
            sheet.write(3, 5, "Redirected", style=header_style)
            sheet.write(3, 6, "Shipments-Inscan", style=header_style)
            sheet.write(3, 7, "Shipments-Outscan", style=header_style)
            style = datetime_style
            for row, rowdata in enumerate(download_list, start=4):
                for col, val in enumerate(rowdata, start=0):
                     if col == 0:
                         sheet.write(row, col, str(val), style=header_style)
                     if col <> 0:
                         sheet.write(row, col, str(val), style=style)

            response = HttpResponse(mimetype='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename=Day-wise-count-rpt.xls'
            book.save(response)
            return response
        else:
            return render_to_response('reports/reports-daywise-count.html',
                                  {
                                   'shipments':download_list,

                                   },
                                  context_instance=RequestContext(request))

    customer=Customer.objects.using('local_ecomm').all()
    sc = ServiceCenter.objects.using('local_ecomm').all()

    return render_to_response("reports/day-wise-count.html",
                              {'customer':customer,
                               'sc':sc},

                               context_instance=RequestContext(request))
@csrf_exempt
def delivery_performance(request):
    if request.POST:
        report_type = request.POST['report_type']
        if request.POST['date_to']:
            date = request.POST['date_to']
        else:
            date = now.strftime("%Y-%m-%d")
        sc=request.POST['sc']
#        shipment_info={}
        download_list = []
 	if sc =='0':
            b=1
            service_center = ServiceCenter.objects.using('local_ecomm').filter()
            for a in service_center:
                shipments = StatusUpdate.objects.using('local_ecomm').filter(date=date,origin=a)
                total = shipments.only('id').count()
                delvr = StatusUpdate.objects.using('local_ecomm').filter(date=date,origin=a, status=2).only('id').count()
                undelvr = StatusUpdate.objects.using('local_ecomm').filter(date=date,origin=a, status__in=[1,3]).only('id').count()
                if total<>0:
                    perc_del = float((float(delvr)/float(total))*100)
                else:
                    perc_del=0
                u = (str(a.center_name),total, delvr, undelvr,perc_del)
                download_list.append(u)
        else:
            b=0
            emp = EmployeeMaster.objects.using('local_ecomm').filter(service_centre=int(sc))
            for a in emp:
                location = a.service_centre.center_name
                if StatusUpdate.objects.using('local_ecomm').filter(delivery_emp_code=a.id):
                    shipments = StatusUpdate.objects.using('local_ecomm').filter(date=date,origin=int(sc), delivery_emp_code=a.id, status__range=(1,2))
                    total = shipments.only('id').count()
                    delvr = StatusUpdate.objects.using('local_ecomm').filter(date=date,origin=int(sc), delivery_emp_code=a.id, status=2).only('id').count()
                    undelvr = StatusUpdate.objects.using('local_ecomm').filter(date=date,origin=int(sc), delivery_emp_code=a.id, status=1).only('id').count()
                    if total<>0:
                        perc_del = float((float(delvr)/float(total))*100)
                    else:
                        perc_del=0
                    u = (str(a.firstname)+" "+str(a.lastname)+" / "+str(a.employee_code),total, delvr, undelvr,perc_del)
                    download_list.append(u)
        if report_type == "dl":
            style = datetime_style
            sheet = book.add_sheet('Delivery Performance Report')
            distinct_list = download_list
            sheet.write(0, 2, "Delivery Performance Report", style=header_style)
	    sheet.write(2,0, 'location',style=header_style)
            if sc=="0":
                sheet.write(2,1, "All", style = style)
            else:
                sheet.write(2,1, location, style = style)
            sheet.write(2,4, 'Date',style=header_style)
            sheet.write(2,5, date, style = style)
            for a in range(1,6):
                sheet.col(a).width = 7000
            sheet.write(5, 0, "Sr No", style=header_style)
	    if sc=="0":
                sheet.write(5, 1, "Service Center", style=header_style)
            else:
                sheet.write(5, 1, "Employee Name / Code", style=header_style)
            sheet.write(5, 2, "Total Shipments", style=header_style)
            sheet.write(5, 3, "Total delivered shpts", style=header_style)
            sheet.write(5, 4, "total Undelivered shpts", style=header_style)
            sheet.write(5, 5, "% Delivered shipments", style=header_style)

            counter = 1
            for row, rowdata in enumerate(download_list, start=6):
                    sheet.write(row, 0, str(counter), style=style)
                    counter=counter+1
                    for col, val in enumerate(rowdata, start=1):
                        if col == 5:
                            sheet.write(row, col, str(val)+'%', style=style)
                        if col <> 5:
                            sheet.write(row, col, str(val), style=style)

            response = HttpResponse(mimetype='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename=Delivery-Performance_%s.xls'%date
            book.save(response)
            return response
        else:
            return render_to_response('reports/reports-delivery-performance.html',
                                  {'shipments':download_list,
					'b':b},
                                  context_instance=RequestContext(request))

    customer=Customer.objects.using('local_ecomm').all()
    sc = ServiceCenter.objects.using('local_ecomm').all()

    return render_to_response("reports/delivery-performance.html",
                              {'customer':customer,
                               'sc':sc},

                               context_instance=RequestContext(request))


@csrf_exempt
def not_outscan(request):
    if request.POST:
        report_type = request.POST['dl_report']
        date_from = request.POST['date_from']
        date_to = request.POST['date_to']
	if request.POST['time_from']:
            time_from = request.POST['time_from']
        else:
            time_from = '00:00:00'
        if request.POST['time_to']:
            time_to = request.POST['time_to']
        else:
            time_to = '00:00:00'
        if date_from:
            date_from = str(date_from)+" "+str(time_from)
        if date_to:
            date_to = str(date_to)+" "+str(time_to)
        sc=request.POST['sc']
        q = Q()

        if not (date_from and date_to):
            pass
        else:
            q = q & Q(added_on__range=(date_from,date_to))
	if sc == "0":
            sc = None
        else:
            destination = [int(x) for x in sc.split(",")]
            dest=[]
            for a in destination:
                destination=ServiceCenter.objects.using('local_ecomm').get(id=a)
                dest.append(destination)
            q = q & Q(service_centre__in=dest)
        shipments = Shipment.objects.using('local_ecomm').filter(q, status=6).exclude(status__range=(7,9)).exclude(status_type=5)
        shipment_info={}
        download_list = []

        for a in shipments:
                if not shipment_info.get(a):
                   # not_outscan = a.bags_set.all()
                   # d1 = datetime.datetime.strptime(str(date_from), "%Y-%m-%d").date()
                    monthdir = a.added_on.strftime("%Y_%m")
                    shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
                    try:
                       history = shipment_history.objects.using('local_ecomm').filter(shipment=a, status=6).latest('updated_on')
                    except:
                       continue
                    shipment_info[a]= history
                    if a.bags_set.all():
                        u = (a.service_centre, a.airwaybill_number, a.bags_set.all(), history.updated_on, history.updated_on)
                        download_list.append(u)
                    else:
                        u = (a.service_centre, a.airwaybill_number,"Debagged", history.updated_on, history.updated_on)
                        download_list.append(u)
        if report_type == "Download":
            style = datetime_style
            sheet = book.add_sheet('Not Out Scan Report')
            distinct_list = download_list
            sheet.write(0, 2, "Not Out Scan Report", style=header_style)

            for a in range(4):
                sheet.col(a).width = 4000
	    sheet.write(3, 0, "Sr No", style=header_style)
            sheet.write(3, 1, "Destination", style=header_style)
            sheet.write(3, 2, "Airwaybill Number", style=header_style)
            sheet.write(3, 3, "Bag Number", style=header_style)
            sheet.write(3, 4, "Inscan Date", style=header_style)
            sheet.write(3, 5, "Inscan Time", style=header_style)
            counter = 1
            for row, rowdata in enumerate(download_list, start=4):
                    sheet.write(row, 0, str(counter), style=style)
                    counter=counter+1
                    for col, val in enumerate(rowdata, start=1):
                        if col ==4:
			    try:
                            	sheet.write(row, col, val.strftime('%d-%m-%Y'), style=style)
			    except:
				pass
                        if col ==5:
			    try:
	                        sheet.write(row, col, val.strftime('%H:%M:%S'), style=style)
			    except:
				pass
                        if col<>4 and col<>5:
			    try:
	                        sheet.write(row, col, str(val), style=style)
			    except:
				pass
            response = HttpResponse(mimetype='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename=Not-OutScan.xls'
            book.save(response)
            return response
        else:
            return render_to_response("reports/reports-notoutscan.html",
                              {'shipments':shipment_info},context_instance=RequestContext(request))

        report_type = request.POST['report_type']
        shipment_info={}
        download_list = []
    else:
        customer=Customer.objects.using('local_ecomm').all()
        sc = ServiceCenter.objects.using('local_ecomm').all()
    return render_to_response("reports/not_outscan.html",
                              {'customer':customer,
                               'sc':sc},
                               context_instance=RequestContext(request))



@csrf_exempt
def bag_detail(request):
    if request.POST:
        report_type = request.POST['dl_report']
        bag_no = request.POST['bag_no']
        bags = Bags.objects.using('local_ecomm').filter(bag_number=bag_no)
        shipment_info={}
        download_list = []
        for bag in bags:
            if bag.ship_data.all():
                bag_detail = bag.ship_data.all()
                if not shipment_info.get(bag_detail):
                    for a in bag_detail:
                        #dated = a.added_on
                        #d1 = datetime.datetime.strptime(str(dated), "%Y-%m-%d %H:%M:%S").date()
                #        monthdir = a.added_on.strftime("%Y_%m")
                 #       shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
                       # history = shipment_history.objects.using('local_ecomm').filter(status__range=(14,15)).latest('updated_on')
                  #      history = shipment_history.objects.using('local_ecomm').filter().exclude(status__in=[11,12,16]).latest('updated_on')
                        shipment_info[a]=""
                        dt = a.updated_on
                        if not dt:
                           dt = ""
                        else:
                           dt = dt.strftime('%d-%m-%Y')
                        u = (a.added_on.strftime('%d-%m-%Y'), dt,a.airwaybill_number)
                        download_list.append(u)

        if report_type == "Download":
            style = datetime_style
            sheet = book.add_sheet('Bag Detail Report')
            distinct_list = download_list
            sheet.write(0, 2, "Bag Detail Report", style=header_style)

            for a in range(4):
                sheet.col(a).width = 4000
            sheet.write(3, 0, "Sr No", style=header_style)
            sheet.write(3, 1, "Date of Pickup", style=header_style)
            sheet.write(3, 2, "Last Updated", style=header_style)
            sheet.write(3, 3, "Airwaybill Number", style=header_style)


            counter = 1
            for row, rowdata in enumerate(download_list, start=4):
                    sheet.write(row, 0, str(counter), style=style)
                    counter=counter+1
                    for col, val in enumerate(rowdata, start=1):
                        if col == 1 or col == 2:
                            sheet.write(row, col, val, style=style)
       #                 if col ==2:
       #                     sheet.write(row, col, val.strftime('%d-%m-%Y'), style=style)
                        else:
                            sheet.write(row, col, str(val), style=style)

            response = HttpResponse(mimetype='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename=Bag-detail.xls'
            book.save(response)
            return response
        else:
            return render_to_response("reports/reports-bagdetail.html",
                              {'shipments':shipment_info},context_instance=RequestContext(request))

        report_type = request.POST['report_type']
        shipment_info={}
        download_list = []
    else:
        customer=Customer.objects.using('local_ecomm').all()
        sc = ServiceCenter.objects.using('local_ecomm').all()
    return render_to_response("reports/bag-detail.html",
                              {'customer':customer,
                               'sc':sc},
                               context_instance=RequestContext(request))

@csrf_exempt
def bag_exception_inbound(request):
    if request.POST:
        report_type = request.POST['dl_report']
        date_from = request.POST['date_from']
        date_to = request.POST['date_to']
        origin=request.POST['sc']

        file_name = bag_exception_inbound_report(origin, date_from, date_to)
        return HttpResponseRedirect('/static/uploads/reports/{0}'.format(file_name))
    else:
        customer=Customer.objects.using('local_ecomm').all()
        sc = ServiceCenter.objects.using('local_ecomm').all()
    return render_to_response("reports/bag-exception.html",
                              {'customer':customer,'exception_type': 'inbound', 'sc':sc},
                               context_instance=RequestContext(request))

@csrf_exempt
def bag_exception_outbound(request):
    if request.POST:
        report_type = request.POST['dl_report']
        date_from = request.POST['date_from']
        date_to = request.POST['date_to']
        origin=request.POST['sc']

        file_name = bag_exception_outbound_report(origin, date_from, date_to)
        return HttpResponseRedirect('/static/uploads/reports/{0}'.format(file_name))
    else:
        customer=Customer.objects.using('local_ecomm').all()
        sc = ServiceCenter.objects.using('local_ecomm').all()
    return render_to_response("reports/bag-exception.html",
                              {'customer':customer, 'sc':sc, 'exception_type': 'outbound'},
                               context_instance=RequestContext(request))

@csrf_exempt
def bag_exception_unconnected(request):
    if request.POST:
        report_type = request.POST['dl_report']
        date_from = request.POST['date_from']
        date_to = request.POST['date_to']
        origin=request.POST['sc']

        file_name = unconnected_bag_report(origin, date_from, date_to)
        return HttpResponseRedirect('/static/uploads/reports/{0}'.format(file_name))
    else:
        customer=Customer.objects.using('local_ecomm').all()
        sc = ServiceCenter.objects.using('local_ecomm').all()
    return render_to_response(
        "reports/bag-exception.html",
        {'customer':customer, 'sc':sc, 'exception_type': 'unconnected'},
        context_instance=RequestContext(request))

@csrf_exempt
def bag_inscan_unconnected(request):
    if request.POST:
        report_type = request.POST['dl_report']
        date_from = request.POST['date_from']
        date_to = request.POST['date_to']
        origin=request.POST['sc']

        file_name = bag_inscan_unconnected_report(origin, date_from, date_to)
        return HttpResponseRedirect('/static/uploads/reports/{0}'.format(file_name))
    else:
        customer=Customer.objects.using('local_ecomm').all()
        sc = ServiceCenter.objects.using('local_ecomm').all()
    return render_to_response(
        "reports/bag-exception.html",
        {'customer':customer, 'sc':sc, 'exception_type': 'inscan'},
        context_instance=RequestContext(request))

@csrf_exempt
def bag_hub_inscanned(request):
    if request.POST:
        report_type = request.POST['dl_report']
        date_from = request.POST['date_from']
        date_to = request.POST['date_to']
        origin=request.POST['sc']

        file_name = bag_hub_inscan_report(origin, date_from, date_to)
        return HttpResponseRedirect('/static/uploads/reports/{0}'.format(file_name))
    else:
        customer=Customer.objects.using('local_ecomm').all()
        sc = ServiceCenter.objects.using('local_ecomm').all()
    return render_to_response(
        "reports/bag-exception.html",
        {'customer':customer, 'sc':sc, 'exception_type': 'hub-inscan'},
        context_instance=RequestContext(request))

@csrf_exempt
def data_uploaded_status(request,stat):
    b=0

    if stat == "7":
        msg="Pending-Outscan"
        stat = [7]
    if stat =="0":
        msg = "Data-Uploaded"
        stat = [0]
    if stat == "1":
        msg = "Shipment-Pickuped"
        stat = [1]
    if stat == "2":
        msg = "Not-OutScan"
        b = 3
        stat = [0, 2, 4]
    if request.POST:
        report_type = request.POST['dl_report']
        date_from = request.POST['date_from']
        date_to = request.POST['date_to']
        sc=request.POST['sc']
	dest=request.POST['dest']
        q = Q()

        if not (date_from and date_to):
            pass
        else:
            q = q & Q(added_on__range=(date_from,date_to+" 23:59:59"))

	if dest == "0":
		dest=None
	else:
		 q = q & Q(service_centre=int(dest))
        #return HttpResponse(sc)
	if sc == "0":
           	sc = None
        else:
            	q = q & Q(pickup__service_centre=int(sc))

        date1 = now.strftime("%Y-%m-%d")
        date2 = datetime.datetime.strptime(date1, "%Y-%m-%d") - datetime.timedelta(days=1)
        date2 = date2.strftime("%Y-%m-%d")
        shipments = Shipment.objects.using('local_ecomm').filter(
            q, status__in=stat
        ).exclude(reason_code__code=310).exclude(rts_status=1).exclude(rto_status=1)
        if stat == "1":
               shipments = Shipment.objects.using('local_ecomm').filter(q, status__in=[0,1,2,3])
        shipment_info={}
        download_list = []

        for a in shipments:
	    if stat == "7":
                    del_outscan = a.deliveryoutscan_set.all()
		    tmp=len(del_outscan)
                    u=(del_outscan[tmp-1].added_on, del_outscan[tmp-1].id, del_outscan[tmp-1].employee_code, a.airwaybill_number, a.collectable_value)
                    download_list.append(u)
            else:
                upd_time = a.added_on
                monthdir = upd_time.strftime("%Y_%m")
                shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
	        if not a.original_dest:
                    sc = a.service_centre
                else:
                    sc = a.original_dest
                try:
                    history = shipment_history.objects.using('local_ecomm').filter(shipment=a).exclude(status__in=[11,12,16]).latest('updated_on')
                    updated_on = history.updated_on.strftime('%d-%m-%Y')
                    #return HttpResponse(a)
                    if b == 3 and request.POST['csc']:
            #           return HttpResponse(request.POST['csc'])
                       if history.current_sc_id <> int(request.POST['csc']):
                          continue
                except:
                    updated_on = ""
                    history=""
                status = get_internal_shipment_status(a.status)
                if stat == "1" and history:
                      if (history.status in [0,1,2,3] and history.reason_code is None):
                         u = (a.pickup.service_centre, a.added_on, sc, a.airwaybill_number, a.shipper.code, a.consignee, updated_on, status)
                         download_list.append(u)

                else:
                    u = (a.pickup.service_centre, a.added_on, sc, a.airwaybill_number, a.shipper.name, a.consignee, updated_on, status)
                    download_list.append(u)
          #  else:
           #     u = (a.pickup.service_centre, a.pickup.pickup_date, sc, a.airwaybill_number, a.shipper.code, a.consignee, '')
            #    download_list.append(u)

        if report_type == "Download":
            style = datetime_style
            sheet = book.add_sheet('%s status Report'%msg)
            distinct_list = download_list
            sheet.write(0, 2, str("%s status Report"%msg), style=header_style)

            for a in range(6):
                sheet.col(a).width = 4000
	    if stat=="7":
                sheet.write(3, 0, "Sr No", style=header_style)
                sheet.write(3, 1, "Outscan Date", style=header_style)
                sheet.write(3, 2, "Outscan Number", style=header_style)
                sheet.write(3, 3, "Employee ID", style=header_style)
                sheet.write(3, 4, "AirwayBill Number", style=header_style)
                sheet.write(3, 5, "Value", style=header_style)
                counter = 1
                for row, rowdata in enumerate(download_list, start=4):
                        sheet.write(row, 0, str(counter), style=style)
                        counter=counter+1
                        for col, val in enumerate(rowdata, start=1):
                            if col ==1:
                                sheet.write(row, col, val, style=style)
                            if col<>1:
                                sheet.write(row, col, str(val), style=style)
            else:
                sheet.col(8).width = 7000
                sheet.write(3, 0, "Sr No", style=header_style)
                sheet.write(3, 1, "Origin", style=header_style)
                sheet.write(3, 2, "Pickup Date", style=header_style)
                sheet.write(3, 3, "Destination", style=header_style)
                sheet.write(3, 4, "AirwayBill Number", style=header_style)
                sheet.write(3, 5, "Shipper", style=header_style)
                sheet.write(3, 6, "Consignee", style=header_style)
                sheet.write(3, 7, "Status update date", style=header_style)
                sheet.write(3, 8, "Current Status", style=header_style)
                counter = 1
                for row, rowdata in enumerate(download_list, start=4):
                        sheet.write(row, 0, str(counter), style=style)
                        counter=counter+1
                        for col, val in enumerate(rowdata, start=1):
                            if col ==2:
                                sheet.write(row, col, val, style=style)
                            if col ==7:
                                sheet.write(row, col, val, style=style)
                            if col<>2 and col <>7:
                                try:
                                  sheet.write(row, col, str(val), style=style)
                                except:
                                  pass

            response = HttpResponse(mimetype='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename=%s-status-Report.xls'%msg
            book.save(response)
            return response
        else:
            stat = stat[0]
            return render_to_response("reports/reports-datauploadedstatus.html",
                              {'shipments':download_list, 'stat':stat},context_instance=RequestContext(request))

        report_type = request.POST['report_type']
        shipment_info={}
        download_list = []
    else:
        customer=Customer.objects.using('local_ecomm').all()
        sc = ServiceCenter.objects.using('local_ecomm').all()
        stat = stat[0]
	if b == 3:
            stat =2
    return render_to_response("reports/data_uploaded_status.html",
                              {'customer':customer,
                               'sc':sc,
				'stat':stat,
                               'msg':msg},
                               context_instance=RequestContext(request))




@csrf_exempt
def shpt_pickuped_status(request):
    if request.POST:
        report_type = request.POST['dl_report']
        date_from = request.POST['date_from']
        date_to = request.POST['date_to']
        sc=request.POST['sc']
        q = Q()

        if not (date_from and date_to):
            pass
        else:
            q = q & Q(added_on__range=(date_from,date_to))
        if sc == "0":
            sc = None
        else:
            q = q & Q(pickup__service_centre=int(sc))


        date1 = now.strftime("%Y-%m-%d")
        date2 = datetime.datetime.strptime(date1, "%Y-%m-%d") - datetime.timedelta(days=1)
        date2 = date2.strftime("%Y-%m-%d")
        shipments = Shipment.objects.using('local_ecomm').filter(q, status__in=[1,2])
        shipment_info={}
        download_list = []

        for a in shipments:
            upd_time = a.added_on
            monthdir = upd_time.strftime("%Y_%m")
            shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
            try:
                history = shipment_history.objects.using('local_ecomm').filter(shipment=a).latest('updated_on')
            except:
                history = ""
            if history:
                u = (a.pickup.service_centre, a.added_on, a.service_centre, a.airwaybill_number, a.shipper.code, a.consignee, history.updated_on)
                download_list.append(u)
            else:
                u = (a.pickup.service_centre, a.added_on, "", a.airwaybill_number, a.shipper.code, a.consignee, '')
                download_list.append(u)

        if report_type == "Download":
            style = datetime_style
            sheet = book.add_sheet('Date Uploaded status Report')
            distinct_list = download_list
            sheet.write(0, 2, "Date Uploaded status Report", style=header_style)

            for a in range(4):
                sheet.col(a).width = 4000
            sheet.col(8).width = 7000
            sheet.write(3, 0, "Sr No", style=header_style)
            sheet.write(3, 1, "Origin", style=header_style)
            sheet.write(3, 2, "Pickup Date", style=header_style)
            sheet.write(3, 3, "Destination", style=header_style)
            sheet.write(3, 4, "AirwayBill Number", style=header_style)
            sheet.write(3, 5, "Shipper", style=header_style)
            sheet.write(3, 6, "Consignee", style=header_style)
            sheet.write(3, 7, "Status update date", style=header_style)
            counter = 1
            for row, rowdata in enumerate(download_list, start=4):
                    sheet.write(row, 0, str(counter), style=style)
                    counter=counter+1
                    for col, val in enumerate(rowdata, start=1):
                        if col ==2:
                            sheet.write(row, col, val.strftime('%d-%m-%Y'), style=style)
                        if col ==7:
                            sheet.write(row, col, val.strftime('%d-%m-%Y'), style=style)
                        if col<>2 and col <>7:
                            sheet.write(row, col, str(val), style=style)

            response = HttpResponse(mimetype='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename=shpt_pickuped_status-Report.xls'
            book.save(response)
            return response
        else:
            return render_to_response("reports/reports-shptpickupedstatus.html",
                              {'shipments':download_list},context_instance=RequestContext(request))

        report_type = request.POST['report_type']
        shipment_info={}
        download_list = []
    else:
        customer=Customer.objects.using('local_ecomm').all()
        sc = ServiceCenter.objects.using('local_ecomm').all()
    return render_to_response("reports/shpt_pickuped_status.html",
                              {'customer':customer,
                               'sc':sc},
                               context_instance=RequestContext(request))



@csrf_exempt
def hub_notoutscan(request):
    if request.POST:
        customer = request.POST['cust_id']
        report_type = request.POST['dl_report']
        date_from = request.POST['date_from']
        date_to = request.POST['date_to']
        sc=request.POST['sc']
        q = Q()
        if customer == "0":
            customer = None
        else:
            q = q & Q(shipper = int(customer))

        if not (date_from and date_to):
            pass
        else:
            q = q & Q(added_on__range=(date_from,date_to))
        if sc == "0":
            sc = None
        else:
            q = q & Q(pickup__service_centre=int(sc))

        shipments = Shipment.objects.using('local_ecomm').filter(q, status__in=[4,5]).exclude(status__range=(14,15))
        shipment_info={}
        download_list = []

        for a in shipments:
            upd_time = a.added_on
            monthdir = upd_time.strftime("%Y_%m")
            shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
            try:
                history = shipment_history.objects.using('local_ecomm').filter(shipment=a).exclude(status__range=(14,15)).latest('updated_on')
            except:
                history = ""
            if history:
                u = (a.pickup.service_centre, a.added_on, a.service_centre, a.airwaybill_number, a.shipper.name, a.consignee, history.updated_on)
                download_list.append(u)
            else:
                u = (a.pickup.service_centre, a.added_on, "", a.airwaybill_number, a.shipper.name, a.consignee, '')
                download_list.append(u)

        if report_type == "Download":
            style = datetime_style
            sheet = book.add_sheet('Hub-Notoutscan Report')
            distinct_list = download_list
            sheet.write(0, 2, "Hub-Notoutscan Report", style=header_style)

            for a in range(4):
                sheet.col(a).width = 4000
            sheet.col(8).width = 7000
            sheet.write(3, 0, "Sr No", style=header_style)
            sheet.write(3, 1, "Origin", style=header_style)
            sheet.write(3, 2, "Pickup Date", style=header_style)
            sheet.write(3, 3, "Destination", style=header_style)
            sheet.write(3, 4, "AirwayBill Number", style=header_style)
            sheet.write(3, 5, "Shipper", style=header_style)
            sheet.write(3, 6, "Consignee", style=header_style)
            sheet.write(3, 7, "Status update date", style=header_style)
            counter = 1
            for row, rowdata in enumerate(download_list, start=4):
                    sheet.write(row, 0, str(counter), style=style)
                    counter=counter+1
                    for col, val in enumerate(rowdata, start=1):
                        if col ==2:
                            sheet.write(row, col, val.strftime('%d-%m-%Y'), style=style)
                        if col ==7:
                            sheet.write(row, col, val.strftime('%d-%m-%Y'), style=style)
                        if col<>2 and col <>7:
                            sheet.write(row, col, str(val), style=style)

            response = HttpResponse(mimetype='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename=Hub-NotOutscann-Report.xls'
            book.save(response)
            return response
        else:
            return render_to_response("reports/reports-hubnotoutscan.html",
                              {'shipments':download_list},context_instance=RequestContext(request))

        report_type = request.POST['report_type']
        shipment_info={}
        download_list = []
    else:
        customer=Customer.objects.using('local_ecomm').all()
        sc = ServiceCenter.objects.using('local_ecomm').all()
    return render_to_response("reports/hub_notoutscan.html",
                              {'customer':customer,
                               'sc':sc},
                               context_instance=RequestContext(request))




@csrf_exempt
def bag_inbound(request, stat):
    if stat=='2':
        msg="Inbound"
    if stat=='7':
        msg='Outbound'
    if request.POST:
        report_type = request.POST['dl_report']
        date_from = request.POST['date_from']
        date_to = request.POST['date_to']
        sc=request.POST['sc']
        destsc=request.POST['destsc']
        p =Q()
	if stat =='7':
            p = p & Q(bag_status__in=[2,7])
        else:
            p= p &  Q(bag_status__in=[2,7])
        if not (date_from and date_to):
            pass
        else:
            p = p & Q(added_on__range=(date_from,date_to))
        if sc == "0":
            sc = None
        else:
            p = p & Q(origin=int(sc))

        if destsc == "0":
            destsc = None
        else:
            p = p & Q(destination=int(destsc))

        bags = Bags.objects.using('local_ecomm').filter(p)
        shipment_info={}
        download_list = []
        for a in bags:
            connection =  a.connection_set.all().latest('added_on')
            u = (a.origin,a.destination.center_name, a.updated_on,a.bag_number, connection.coloader)
            download_list.append(u)

        if report_type == "Download":
            style = datetime_style
            sheet = book.add_sheet('Bag %s Report'%msg)
            distinct_list = download_list
            sheet.write(0, 2, "Bag %s Report"%msg, style=header_style)

            for a in range(2):
                sheet.col(a).width = 4000
            sheet.col(2).width = 7000
            sheet.col(3).width = 4000
            sheet.write(3, 0, "Sr No", style=header_style)
            sheet.write(3, 1, "Origin", style=header_style)
            sheet.write(3, 2, "Destination", style=header_style)
            sheet.write(3, 3, "Connection Date", style=header_style)
            sheet.write(3, 4, "Bag Number", style=header_style)
            sheet.write(3, 5, "Coloader", style=header_style)

            counter = 1
            for row, rowdata in enumerate(download_list, start=4):
                    sheet.write(row, 0, str(counter), style=style)
                    counter=counter+1
                    for col, val in enumerate(rowdata, start=1):
                        if col ==3:
                            if val<>None:
                                sheet.write(row, col, val.strftime('%d-%m-%Y'), style=style)
                        if col<>3:
                            sheet.write(row, col, str(val), style=style)

            response = HttpResponse(mimetype='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename=Bag-%s-Report.xls'%msg
            book.save(response)
            return response
        else:
            return render_to_response("reports/reports-baginbound.html",
                              {'shipments':download_list},context_instance=RequestContext(request))

        report_type = request.POST['report_type']
        shipment_info={}
        download_list = []
    else:
        customer=Customer.objects.using('local_ecomm').all()
        sc = ServiceCenter.objects.using('local_ecomm').all()
    return render_to_response("reports/bag-inbound.html",
                              {'customer':customer,
                               'sc':sc,
                               'stat':stat,
                               'msg':msg},
                               context_instance=RequestContext(request))

def update_shipmentinfo_n_downloadlist(shipment):
    # get Shipmenthistory object for given shipment
    upd_time = shipment.added_on
    monthdir = upd_time.strftime("%Y_%m")
    shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
    history = shipment_history.objects.using('local_ecomm').filter(shipment=shipment, status=6)
    updated_on = history.order_by('updated_on')[0].updated_on if history else None
    status = get_internal_shipment_status(shipment.status)
    inscan_date = shipment.inscan_date

    # get DeliveryOutscan object for given shipment
    deliveryscan = DeliveryOutscan.objects.using('local_ecomm').filter(shipments=shipment)
    first_scan, second_scan, last_scan = None, None, None
    if deliveryscan:
        first_scan = deliveryscan.order_by('id')[0].added_on
        last_scan = deliveryscan.order_by('-id')[0].added_on
        try:
            second_scan = deliveryscan.order_by('id')[1].added_on
        except IndexError:
            pass

    # following are the list of values we required to generate this report
    # airway_bill_no, pickup date, shipment at delivery centre, origin,
    # destination, shipper, type, inscan_time, 1st outscan date, no of outscans,
    # last outscan date, last updation date, status
    u = (shipment.airwaybill_number, shipment.added_on, updated_on,
         shipment.pickup.service_centre, shipment.original_dest, shipment.shipper.name,
         shipment.product_type,inscan_date, first_scan,second_scan, len(deliveryscan),
         last_scan,shipment.updated_on, status)

    return u

@csrf_exempt
def outscan_for_shipment(request):
    if request.method == 'POST':
        customer_id = request.POST.get('cust_id')
        date_from = request.POST.get('date_from')
        date_to = request.POST.get('date_to','2050-12-12')
        sc = request.POST.get('sc')
        report_type = request.POST.get('report_type')
        q = Q()

        if not customer_id == "0":
            q = q & Q(shipper= int(customer_id))

        if date_from and date_to:
            t = datetime.datetime.strptime(date_to, "%Y-%m-%d") + datetime.timedelta(days=1)
            date_to = t.strftime("%Y-%m-%d")
            q = q & Q(added_on__range=(date_from,date_to))

        if not sc == "0":
            q = q & Q(service_centre=int(sc))

        shipments = Shipment.objects.using('local_ecomm').filter(q, status__gte=6).exclude(rts_status=2)

        display_data_list = (update_shipmentinfo_n_downloadlist(shipment) for shipment in shipments)

        cols_head = ( 'AWB No',
                     'Pickup Date',  #1
                     'Shipment DC',  #2
                     'Origin',       #3
                     'Destination',       #4
                     'Shipper',       #5
                     'Type',       #6
                     'Inscan Date',       #7
                     '1st outscan date',       #8
                     '2nd otscan date',       #9
                     'No of outscans',       #10
                     'Last outscan date',       #11
                     'Last updation date',       #12
                     'Status')       #13

        # if download button is clicked, downloadable file is getting created from here.
        if report_type == "dl":
            sheet = book.add_sheet('Outscan for Shipment')
            sheet.write(0, 2, "Outscan for Shipment Report", style=header_style)

            for a in range(12):
                sheet.col(a).width = 5000
            sheet.col(5).width = 10000
            sheet.col(11).width = 10000

            for ind,val in enumerate(cols_head):
                sheet.write(3, ind, val, style=header_style)

            style = datetime_style

            for row, rowdata in enumerate(display_data_list, start=4):
                for col, val in enumerate(rowdata):
                    if not val:
                        continue
                    if col in [1,2,7,8,9,11,12]:
                        sheet.write(row, col, val.strftime('%d-%m-%Y'), style=style)
                    else:
                        sheet.write(row, col, str(val), style=style)

            response = HttpResponse(mimetype='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename=Outscan-Shipment.xls'
            book.save(response)
            return response

        else:
            return render_to_response('reports/reports-outscan-shipment.html',
                                  {'shipments':display_data_list, 'cols_head': cols_head},
                                  context_instance=RequestContext(request))

    else:
        customer=Customer.objects.using('local_ecomm').all()
        sc = ServiceCenter.objects.using('local_ecomm').all()

        return render_to_response("reports/outscan_shipment.html",
                                  {'customer':customer, 'sc':sc},
                                   context_instance=RequestContext(request))
@csrf_exempt
def cust_reconcilation_report(request):

    shipment_total=[]
    download_list=[]
    if request.POST:
        download_list = []
        report_type = request.POST['dl_report']
        date_from = request.POST['date_from']
        date_to = request.POST['date_to']
        sc=request.POST['sc']
        customer=request.POST['cust_id']

        q = Q()

        if not (date_from and date_to):
            pass
        else:
            t = datetime.datetime.strptime(date_to, "%Y-%m-%d") + datetime.timedelta(days=1)
            date_to = t.strftime("%Y-%m-%d")
            q = q & Q(added_on__range=(date_from,date_to))
        if sc == "0":
            sc = None
        else:
            q = q & Q(pickup__service_centre=int(sc))

	if customer == "0":
            customer = None
        else:
            q = q & Q(shipper = int(customer))

        date1 = now.strftime("%Y-%m-%d")
        date2 = datetime.datetime.strptime(date1, "%Y-%m-%d") - datetime.timedelta(days=1)
        date2 = date2.strftime("%Y-%m-%d")
        shipment_total = Shipment.objects.using('local_ecomm').filter(q)#20307
        status=[]

        for tmp in shipment_total:
            status.append(tmp.reason_code_id)

        b = set(status)
        reason_code = ShipmentStatusMaster.objects.using('local_ecomm').filter(id__in=b)
        test = 0
        status_dict={}
        for a in reason_code:
            ppd_forcetaken=Shipment.objects.using('local_ecomm').filter(q,product_type="ppd",reason_code=a)
            cod_forcetaken=Shipment.objects.using('local_ecomm').filter(q,product_type="cod",reason_code=a)
            collected_cod=0.00
            for tmp in cod_forcetaken:
                collected_cod=collected_cod+tmp.collectable_value
            test = test+len(ppd_forcetaken)+len(cod_forcetaken)
            status_dict[a]=[len(ppd_forcetaken),len(cod_forcetaken),collected_cod]
            u = (a.code,a.code_description,len(ppd_forcetaken),len(cod_forcetaken),collected_cod)
            download_list.append(u)
        scaned=0

        #shipment = Shipment.objects.using('local_ecomm').all()
        total_ppd_scanned=0
        total_code_scanned=0
        total_col_value=0
        for tmp in reason_code:
            scaned=scaned+status_dict[tmp][0]+status_dict[tmp][1]
            total_ppd_scanned=total_ppd_scanned+status_dict[tmp][0]
            total_code_scanned=total_code_scanned+status_dict[tmp][1]
            total_col_value=+status_dict[tmp][2]

        shipments = Shipment.objects.using('local_ecomm').filter(q,product_type="ppd")
        shipments_cod_total=Shipment.objects.using('local_ecomm').filter(q,product_type="cod")

        cod_total_value=0.00

        for tmp in shipments_cod_total:
            cod_total_value=cod_total_value+tmp.collectable_value

        download_list_length=len(download_list)
        if report_type == "Download":

            style = datetime_style
            sheet = book.add_sheet('Customer Reconcilation  Report')
            distinct_list = download_list
            sheet.write(0, 2, "Customer Reconcilation  Report", style=header_style)

            for a in range(4):
                sheet.col(a).width = 4000
            sheet.col(8).width = 7000
            sheet.write(3, 0, "Sr. No", style=header_style)
            sheet.write(3, 1, "Status Code", style=header_style)
            sheet.write(3, 2, "Description", style=header_style)
            sheet.write(3, 3, "Prepaid Shipments", style=header_style)
            sheet.write(3, 4, "Shipments-COD", style=header_style)
            sheet.write(3, 5, "Value-COD", style=header_style)

            sheet.write(download_list_length+6, 2, "Total", style=header_style)
            sheet.write(download_list_length+6, 3, str(total_ppd_scanned), style=style)
            sheet.write(download_list_length+6, 4, str(total_code_scanned), style=style)
            sheet.write(download_list_length+6, 5, str(total_col_value), style=style)
            sheet.write(download_list_length+7, 2, "Difference", style=header_style)
            sheet.write(download_list_length+7, 3, str(len(shipments)-total_ppd_scanned), style=style)
            sheet.write(download_list_length+7, 4, str(len(shipments_cod_total)-total_code_scanned), style=style)
            sheet.write(download_list_length+7, 5, str(cod_total_value-total_col_value), style=style)

            counter = 1

            for row, rowdata in enumerate(download_list, start=4):
                    sheet.write(row, 0, str(counter), style=style)
                    counter=counter+1

                    for col, val in enumerate(rowdata, start=1):
                         val = val.encode('utf-8') if isinstance(val,unicode)  else val
                         sheet.write(row, col, str(val), style=style)


            response = HttpResponse(mimetype='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename=customer-reconciliation-Report.xls'
            book.save(response)
            return response
        else:
            return render_to_response("reports/reports-customer-reconciliation-report.html",
                              {
                               'total':len(shipment_total),
                               'scaned':status_dict,
                               'scaned_ppd':total_ppd_scanned,
                               'scaned_cod':total_code_scanned,
                               'col_value':total_col_value,
                               'ppd_diff':len(shipments)-total_ppd_scanned,
                               'cod_diff':len(shipments_cod_total)-total_code_scanned,
                               'cod_val_diff':cod_total_value-total_col_value
                               },

                              context_instance=RequestContext(request))


        report_type = request.POST['report_type']
        shipment_info={}
        download_list = []
    else:
        customer=Customer.objects.using('local_ecomm').all()
        sc = ServiceCenter.objects.using('local_ecomm').all()
    return render_to_response("reports/customer-reconciliation-report.html",
                              {'customer':customer,

                               'sc':sc},
                               context_instance=RequestContext(request))

@csrf_exempt
def cod_deposit_confirmation(request):
    shipment_total=[]
    download_list=[]
    if request.POST:
        download_list = []
        report_type = request.POST['dl_report']
        date_from = request.POST['date_from']
        date_to = request.POST['date_to']
        sc=request.POST['sc']

        q = Q()

        if not (date_from and date_to):
            pass
        else:
            t = datetime.datetime.strptime(date_to, "%Y-%m-%d") + datetime.timedelta(days=1)
            date_to = t.strftime("%Y-%m-%d")
            q = q & Q(added_on__range=(date_from,date_to))
            #q = q & Q(date__range=(date_from,date_to))
        if sc == "0":
            sc = None
        else:
            q = q & Q(origin=int(sc))


        date1 = now.strftime("%Y-%m-%d")
        date2 = datetime.datetime.strptime(date1, "%Y-%m-%d") - datetime.timedelta(days=1)
        date2 = date2.strftime("%Y-%m-%d")

        codots=CODDepositsOutscan.objects.using('local_ecomm').filter(q,status=1)
        cod_deposited=[]

        dict={}
        for codot in codots:
            dos=codot.deliveryoutscan
            ships=dos.shipments.all()
            amt=0.00
            awb_list=[]
            awb_amount_list=[]
            for ship in ships:
                amt=amt+ship.collectable_value
                awb_list.append(ship.airwaybill_number)
                awb_amount_list.append(str(ship.collectable_value))
            sheet_amount=codot.coddeposit.deliverydeposits_set.all()
            if not sheet_amount:
                sheet_amount=""
            cod_deposited.append(codot.coddeposit.collected_amount)
            dict[dos]=[dos.id,amt,ships,codot.coddeposit.collected_amount,sheet_amount]
            u = (dos.id,awb_list,awb_amount_list,amt,codot.coddeposit.collected_amount,sheet_amount)
            download_list.append(u)

        cod_deposited = sorted(set(cod_deposited))
        cod_deposited.sort()

        download_list_length=len(download_list)
        if report_type == "Download":

            style = datetime_style
            sheet = book.add_sheet('COD Deposit Confirmation Report')
            distinct_list = download_list
            sheet.write(0, 2, "COD Deposit Confirmation Report", style=header_style)

            for a in range(4):
                sheet.col(a).width = 4000
            sheet.col(8).width = 7000
            sheet.write(3, 0, "Sr. No", style=header_style)
            sheet.write(3, 1, "OutScan Number", style=header_style)
            sheet.write(3, 2, "Backend AWB", style=header_style)
            sheet.write(3, 3, "Backend Amount", style=header_style)
            sheet.write(3, 4, "Backend Subtotal", style=header_style)
            sheet.write(3, 5, "Cash Deposited", style=header_style)
            sheet.write(3, 6, "Value-COD", style=header_style)

            counter = 1
            row_count=1
            tmp=1
            for row, rowdata in enumerate(download_list, start=4):
                    sheet.write(row+row_count, 0, str(counter), style=style)
                    for col, val in enumerate(rowdata, start=1):

                         val = val.encode('utf-8') if isinstance(val,unicode)  else val

                         if col==1:
                             sheet.write(row+row_count, col, str(val), style=style)
                         elif col==2:
                             for a in val:
                                 sheet.write(row+row_count, col, str(a), style=style)
                                 row_count=row_count+1

                         elif col==3:

                             for a in val:
                                  sheet.write(row+tmp, col, str(a), style=style)
                                  tmp=tmp+1


                         else:
                             sheet.write(row+row_count-1, col, str(val), style=style)

                    counter=counter+1
                    row_count=row_count+1
                    tmp=tmp+1

            response = HttpResponse(mimetype='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename=cod-deposit-confirmation-Report.xls'
            book.save(response)
            return response
        else:
            return render_to_response("reports/reports-cod-deposit-confirmation.html",
                              {
                               'total':len(shipment_total),
                               'dict':dict,
                               'cod_list':cod_deposited
                               },

                              context_instance=RequestContext(request))


        report_type = request.POST['report_type']
        shipment_info={}

    else:
        customer=Customer.objects.using('local_ecomm').all()
        sc = ServiceCenter.objects.using('local_ecomm').all()
    return render_to_response("reports/cod-deposit-confirmation.html",
                              {'customer':customer,

                               'sc':sc},
                               context_instance=RequestContext(request))

def get_inscan_report(request):
    customer=Customer.objects.using('local_ecomm').all()
    sc = ServiceCenter.objects.using('local_ecomm').all()
    return render_to_response("reports/inscan_report.html",
                              {'customer':customer,
                               'sc':sc},
                               context_instance=RequestContext(request))

def get_excel_for_inscan_report(field_names, data_list):
    # add filename and set save file path
    file_name = "/inscan_report_%s.xlsx"%(now.strftime("%d%m%Y%H%M%S%s"))
    path_to_save = settings.FILE_UPLOAD_TEMP_DIR+file_name
    workbook = Workbook(path_to_save)

    # define style formats for header and data
    header_format = workbook.add_format()
    header_format.set_bg_color('yellow')
    header_format.set_bold()
    header_format.set_border()
    plain_format = workbook.add_format()

    # add a worksheet and set excel sheet column headers
    sheet = workbook.add_worksheet()
    sheet.set_column(0, 11, 12) # set column width
    sheet.write(0, 2, "Inscan Report")
    for col,name in enumerate(field_names):
        sheet.write(2,col,name, header_format)

    # write data to excel sheet
    for row,data_list in enumerate(data_list, start=3):
        for col,val in enumerate(data_list):
            sheet.write_string(row,col,str(val))

    workbook.close()
    return file_name

def get_inscan_display_info(shipment):
    return (
        shipment.airwaybill_number,
        shipment.order_number,
        shipment.actual_weight,
        shipment.volumetric_weight,
        shipment.collectable_value,
        shipment.declared_value,
        shipment.pickup.service_centre.center_name,
        shipment.destination_city,
        shipment.added_on.date(),
        shipment.added_on.time(),
        shipment.inscan_date.date(),
        shipment.inscan_date.time(),
    )

def get_inscan_shipments(date_from, date_to, sc):

    q = Q()

    if date_from and date_to:
        t = datetime.datetime.strptime(date_to, "%Y-%m-%d") + datetime.timedelta(days=1)
        date_to = t.strftime("%Y-%m-%d")
        q = q & Q(inscan_date__gte=date_from,inscan_date__lte=date_to)
    elif date_from:
        q = q & Q(inscan_date__gte=date_from)
    elif date_to:
        q = q & Q(inscan_date__lte=date_to)

    if int(sc):
        q = q & Q(service_centre_id=sc)

    q = q & Q(rts_status=2)

    return Shipment.objects.using('local_ecomm').filter(q)


@csrf_exempt
def inscan_report(request):
    """ this view will provide the inscan report
        info: http://projects.prtouch.com/issues/550
    """
    # required fields for inscan reports
    inscan_report_fields = (
        'AWB No',
        'Order No',
        'Weight',
        'Vol Weight',
        'COD Amount',
        'Declared Value',
        'Origin',
        'Destination',
        'Pickup Date',
        'Pickup Time',
        'Inscan Date',
        'Inscan Time'
    )

    # if request is ajax and it is get then show the report through html
    if request.is_ajax() and request.method == 'GET':
        # get the data from request
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        sc = request.GET.get('sc')

        # make appropriate request query and get all shipments
        shipments = get_inscan_shipments(date_from, date_to, sc)

        # get display data from shipments
        display_info = (get_inscan_display_info(shipment) for shipment in shipments)

        # get the html string to display on the report page
        html = render_to_string('reports/inscan_report_data.html',
                   {'display_list':display_info, 'inscan_report_fields':inscan_report_fields},
               )

        data = {'html':html}
        json = simplejson.dumps(data)
        return HttpResponse(json, mimetype='application/json')

    # else if it is a post request then give the excel file for dowload
    elif request.POST:
        # get the data from request
        date_from = request.POST.get('date_from')
        date_to = request.POST.get('date_to')
        sc = request.POST.get('sc')

        # make appropriate request query and get all shipments
        shipments = get_inscan_shipments(date_from, date_to, sc)

        # get display data from shipments
        download_info = (get_inscan_display_info(shipment) for shipment in shipments)

        # make downloadable excel file
        file_name = get_excel_for_inscan_report(inscan_report_fields, download_info)
        return HttpResponseRedirect("/static/uploads/%s"%(file_name))

    return HttpResponse("This is inscan report ")


def get_prev_day_load_report(request):
    customers = Customer.objects.using('local_ecomm').all()
    return render_to_response("reports/prev_day_load_report.html",
                              {'customers':customers},
                               context_instance=RequestContext(request))

def get_load_report_display_info(customer, pick_date):

    shipments = Shipment.objects.using('local_ecomm').filter(shipper=customer,
                                        added_on__year=pick_date.year,
                                        added_on__month=pick_date.month,
                                        added_on__day=pick_date.day).exclude(return_shipment=3)
    total_pickups = len(shipments)
    tat_24 = 0
    day1_attempt = 0
    late_delivery = 0
    delivered = 0
    undelivered = 0
    out_for_delivery = 0
    tat_48 = 0

    for shipment in shipments:
        added_on = shipment.added_on
        expected_dod = shipment.expected_dod
        status = shipment.status

        # check if shipment delivered, undelivered or out for delivery
        # using shipment status
        if status == 9:
            delivered += 1
        elif status == 8:
            undelivered += 1
        else:
            out_for_delivery += 1

        if expected_dod and added_on and (expected_dod - added_on) == datetime.timedelta(1):
            tat_24 += 1
            first_outscan = DeliveryOutscan.objects.using('local_ecomm').filter(
                                 shipments=shipment).order_by('added_on')
            # compare first outscan date and expected_dod to check
            # for first day attempt
            if first_outscan and first_outscan[0].added_on.date() - expected_dod.date() == datetime.timedelta(0):
                day1_attempt += 1  # increment day 1 attempt count
            else:
                late_delivery += 1 # increment late delivery count
        else:
            tat_48 += 1

    return (
        customer.name,
        total_pickups,
        tat_24,
        day1_attempt,
        late_delivery,
        delivered,
        undelivered,
        out_for_delivery,
        tat_48
    )

def get_excel_for_load_report(field_names, data_list, date):
    # add filename and set save file path
    file_name = "/load_report_%s.xlsx"%(now.strftime("%d%m%Y%H%M%S%s"))
    path_to_save = settings.FILE_UPLOAD_TEMP_DIR+file_name
    workbook = Workbook(path_to_save)

    # define style formats for header and data
    header_format = workbook.add_format()
    header_format.set_bg_color('yellow')
    header_format.set_bold()
    #header_format.set_border()
    plain_format = workbook.add_format()
    plain_format.set_bold()

    # add a worksheet and set excel sheet column headers
    sheet = workbook.add_worksheet()
    sheet.set_column(0, 9, 12) # set column width
    sheet.set_column(0, 1, 15) # set column width
    sheet.write(0, 2, "Previous Day Load Report(%s)" % date)
    for col,name in enumerate(field_names):
        sheet.write(2,col,name, header_format)

    total = [0] * 9
    total[0] = 'Grand Total'
    count = 3

    # write data to excel sheet
    for row,data_list in enumerate(data_list, start=3):
        count += 1
        for col,val in enumerate(data_list):
            if col != 0:
                total[col] = total[col] + int(val)
            sheet.write_string(row,col,str(val))

    for col,val in enumerate(total):
        sheet.write(count,col,str(val),plain_format)
        #sheet.write_string(count,col,str(val))

    workbook.close()
    return file_name



@csrf_exempt
def prev_day_load_report(request):
    """ this view will provide the Previous day load report
        info: http://projects.prtouch.com/issues/554
    """
    # required fields for inscan reports
    load_report_fields = (
        'Customer Name',
        'Total Pickup', # len(PickupRegistration.objects.using('local_ecomm').filter(customer_code=c,pickup_date=pick_date))
        'TAT 24 hours', # shipment.added_on and expected_dod
        '1st Day Attempt',
        'Late Delivery',
        'Delivered', # shipment history , status 9
        'Undelivered', # shipment history , status 8
        'Out for Delivery',
        'TAT 48 hours'
    )

    # if request is ajax and it is get then show the report through html
    if request.is_ajax() and request.method == 'GET':
        # get the data from request
        date_on = request.GET.get('date_on')
        if date_on:
            date_on = datetime.datetime.strptime(date_on, "%Y-%m-%d") - datetime.timedelta(days=1)
        else:
            date_on = datetime.datetime.today() - datetime.timedelta(days=1)

        cust_id = request.GET.get('cust_id')
        display_info = []

        if int(cust_id):
            customer = Customer.objects.using('local_ecomm').get(pk=int(cust_id))
            display_info.append(get_load_report_display_info(customer,date_on))
        else:
            # get all customers
            customers = Customer.objects.using('local_ecomm').all()

            # get display data  for each customer
            display_info = (get_load_report_display_info(c, date_on) for c in customers)

        # get the html string to display on the report page
        html = render_to_string('reports/prev_day_load_report_data.html',
                   {'display_list':display_info, 'load_report_fields':load_report_fields},
               )

        data = {'html':html}
        json = simplejson.dumps(data)
        return HttpResponse(json, mimetype='application/json')

    # else if it is a post request then give the excel file for dowload
    elif request.POST:
        # get the data from request
        date_on = request.POST.get('date_on')
        if date_on:
            date_on = datetime.datetime.strptime(date_on, "%Y-%m-%d") - datetime.timedelta(days=1)
        else:
            date_on = datetime.datetime.today() - datetime.timedelta(days=1)
        cust_id = request.POST.get('cust_id')
        download_info = []

        if int(cust_id):
            customer = Customer.objects.using('local_ecomm').get(pk=int(cust_id))
            download_info.append(get_load_report_display_info(customer,date_on))
        else:
            # get all customers
            customers = Customer.objects.using('local_ecomm').all()

            # get display data  for each customer
            download_info = (get_load_report_display_info(c, date_on) for c in customers)

        # make downloadable excel file
        date = str(date_on.day) + 'th ' + str(date_on.strftime('%B'))
        file_name = get_excel_for_load_report(load_report_fields, download_info,date)
        return HttpResponseRedirect("/static/uploads/%s"%(file_name))

    return HttpResponse("This is laod report")


@csrf_exempt
def strike_rate_analysis_operations(request):

    if request.POST:
        customer = request.POST['cust_name']

        ym = request.POST.get('month',None)
        year_month = ym if ym else now.strftime("%Y-%m")
        month = year_month.split("-")
        date_from = request.POST.get('date_from','')
        date_to = request.POST.get('date_to','')

        if date_to:
            month = ''
            year_month = ''

        sc = request.POST['sc']
        dl_report = request.POST['dl_report']
        q = Q()

        if customer == "0":
            customer = None
        else:
            q = q & Q(shipper = int(customer))

        if not month:
            t = datetime.datetime.strptime(date_to, "%Y-%m-%d") + datetime.timedelta(days=1)
            dated_to = t.strftime("%Y-%m-%d")
            q = q & Q(added_on__range=(date_from,dated_to))
        else:
            q = q & Q(added_on__year=month[0], added_on__month=month[1])

        if sc == "0":
            sc = None
        else:
            q = q & Q(service_centre=int(sc))

        p = 1
        c = 1
        ppd_shipment = Shipment.objects.using('local_ecomm').filter(q, product_type="ppd",status=9).exclude(return_shipment=3).exclude(rts_status=1)
        ppd_shipment_count = ppd_shipment.only('id').count()
        if ppd_shipment_count == 0:
            p = 0
            ppd_shipment_count = 1

        #delivered_ppd = StatusUpdate.objects.using('local_ecomm').filter(shipment__in=ppd_shipment, status=2)
        #strike_day_ppd_count = {0:0,1:0,2:0,3:0,4:0}
        strike_day_ppd_count = defaultdict(int)

        strike_day_ppd_count = get_strike_rate_from_shipments(ppd_shipment, strike_day_ppd_count)

        on_time_ppd_perc= round(((float(strike_day_ppd_count[0])/float(ppd_shipment_count))*100.0),2)
        day1_ppd_perc = round(((float(strike_day_ppd_count[1])/float(ppd_shipment_count))*100.0),2)
        day2_ppd_perc = round(((float(strike_day_ppd_count[2])/float(ppd_shipment_count))*100.0),2)
        day3_ppd_perc = round(((float(strike_day_ppd_count[3])/float(ppd_shipment_count))*100.0),2)
        day4_ppd_perc = round(((float(strike_day_ppd_count[4])/float(ppd_shipment_count))*100.0),2)

        cod_shipment = Shipment.objects.using('local_ecomm').filter(q, product_type="cod",status=9).exclude(return_shipment=3).exclude(rts_status=1)
        cod_shipment_count = cod_shipment.only('id').count()
        if cod_shipment_count == 0:
            c = 0
            cod_shipment_count = 1

        #delivered_cod = StatusUpdate.objects.using('local_ecomm').filter(shipment__in=cod_shipment, status=2)
        #delivered_cods = DeliveryOutscan.objects.using('local_ecomm').filter(shipments__in=cod_shipment)

        strike_day_cod_count = defaultdict(int)

        strike_day_cod_count = get_strike_rate_from_shipments(cod_shipment, strike_day_cod_count)

        on_time_cod_perc= round(((float(strike_day_cod_count[0])/float(cod_shipment_count))*100.0),2)
        day1_cod_perc = round(((float(strike_day_cod_count[1])/float(cod_shipment_count))*100.0),2)
        day2_cod_perc = round(((float(strike_day_cod_count[2])/float(cod_shipment_count))*100.0),2)
        day3_cod_perc = round(((float(strike_day_cod_count[3])/float(cod_shipment_count))*100.0),2)
        day4_cod_perc = round(((float(strike_day_cod_count[4])/float(cod_shipment_count))*100.0),2)
        if p == 0:
            ppd_shipment_count = 0
        if c == 0:
            cod_shipment_count = 0
        if not (year_month):
            year_month = str(date_from)+' To '+str(date_to)

        total=ppd_shipment_count+cod_shipment_count
        if dl_report == "Download":
            sheet = book.add_sheet('Strike Rate Analysis-Operations')
            sheet.write(0, 2, "Strike Rate Analysis-Operations", style=header_style)

            for a in range(13):
                sheet.col(a).width = 3000

            sheet.write(3, 0, "Month", style=header_style)
            sheet.write(3, 1, "Count", style=header_style)
            sheet.write(3, 2, "Total", style=header_style)
            sheet.write(3, 3, "On Time", style=header_style)
            sheet.write(3, 4, "%Age", style=header_style)
            sheet.write(3, 5, "Day 1", style=header_style)
            sheet.write(3, 6, "%Age", style=header_style)
            sheet.write(3, 7, "Day 2", style=header_style)
            sheet.write(3, 8, "%Age", style=header_style)
            sheet.write(3, 9, "Day 3", style=header_style)
            sheet.write(3, 10, "%Age", style=header_style)
            sheet.write(3, 11, "Day>3", style=header_style)
            sheet.write(3, 12, "%Age", style=header_style)

            sheet.write(4, 0, year_month)
            sheet.write(5, 0, year_month)

            sheet.write(4, 1, "Prepaid", style=header_style)
            sheet.write(5, 1, "COD", style=header_style)

            sheet.write(4, 2, str(ppd_shipment_count))
            sheet.write(5, 2, str(cod_shipment_count))

            sheet.write(4, 3, str(strike_day_ppd_count[0]))
            sheet.write(5, 3, str(strike_day_cod_count[0]))
            sheet.write(4, 4, str(on_time_ppd_perc)+'%')
            sheet.write(5, 4, str(on_time_cod_perc)+'%')

            sheet.write(4, 5, str(strike_day_ppd_count[1]))
            sheet.write(5, 5, str(strike_day_cod_count[1]))
            sheet.write(4, 6, str(day1_ppd_perc)+'%')
            sheet.write(5, 6, str(day1_cod_perc)+'%')

            sheet.write(4, 7, str(strike_day_ppd_count[2]))
            sheet.write(5, 7, str(strike_day_cod_count[2]))
            sheet.write(4, 8, str(day2_ppd_perc)+'%')
            sheet.write(5, 8, str(day2_cod_perc)+'%')

            sheet.write(4, 9, str(strike_day_ppd_count[3]))
            sheet.write(5, 9, str(strike_day_cod_count[3]))
            sheet.write(4, 10, str(day3_ppd_perc)+'%')
            sheet.write(5, 10, str(day3_cod_perc)+'%')

            sheet.write(4, 11, str(strike_day_ppd_count[4]))
            sheet.write(5, 11, str(strike_day_cod_count[4]))
            sheet.write(4, 12, str(day4_ppd_perc)+'%')
            sheet.write(5, 12, str(day4_cod_perc)+'%')

            response = HttpResponse(mimetype='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename=Strike-Rate-Analysis-Operations.xls'
            book.save(response)
            return response
        else:
            return render_to_response('reports/reports-strikerateanalysis.html',
                                  {
                                   'ppd_shipment':ppd_shipment_count,
                                   'cod_shipment':cod_shipment_count,
                                   'total':total,
                                   'month':year_month,
                                   'on_time_ppd':on_time_ppd_perc,
                                   'day1_ppd':day1_ppd_perc,
                                   'day2_ppd':day2_ppd_perc,
                                   'day3_ppd':day3_ppd_perc,
                                   'day4_ppd':day4_ppd_perc,
                                   'on_time_cod':on_time_cod_perc,
                                   'day1_cod':day1_cod_perc,
                                   'day2_cod':day2_cod_perc,
                                   'day3_cod':day3_cod_perc,
                                   'day4_cod':day4_cod_perc,
                                   'ppd_count_ontime':strike_day_ppd_count[0],
                                   'ppd_count_day1':strike_day_ppd_count[1],
                                   'ppd_count_day2':strike_day_ppd_count[2],
                                   'ppd_count_day3':strike_day_ppd_count[3],
                                   'ppd_count_day4':strike_day_ppd_count[4],
                                   'cod_count_ontime':strike_day_cod_count[0],
                                   'cod_count_day1':strike_day_cod_count[1],
                                   'cod_count_day2':strike_day_cod_count[2],
                                   'cod_count_day3':strike_day_cod_count[3],
                                   'cod_count_day4':strike_day_cod_count[4],
                                   },
                                  context_instance=RequestContext(request))

    customer=Customer.objects.using('local_ecomm').all()
    sc = ServiceCenter.objects.using('local_ecomm').all()

    return render_to_response("reports/strikerateanalysis-operations.html",
                              {'customer':customer,
                               'sc':sc},
                               context_instance=RequestContext(request))


@csrf_exempt
def performance_analysis_location(request, type=0, rtype=0):
    q = Q()
    r = Q()
    s = Q()
    if type == 1:
       #nowd = now.date()-datetime.timedelta(days=1)
       yest = now.date()-datetime.timedelta(days=2)
       #q = q & Q(added_on__range = (yest,nowd))
       if now.date().day < 10:
           today = datetime.date.today()   
           first = datetime.date(day=1, month=today.month, year=today.year)
           lastMonth = first - datetime.timedelta(days=1)
           q = q & Q(added_on__month=lastMonth.month) | Q(added_on__month = today.month, added_on__year = today.year, added_on__lt = now.date())
       else:    
           q = q & Q(added_on__month=now.month, added_on__year = now.year, added_on__lt = yest)
    elif request.POST:
        report_type = request.POST['report_type']
        date_from = request.POST['date_from']
        date_to = request.POST['date_to']
        sc=request.POST['sc']
        report_type = request.POST['report_type']
        if not (date_from and date_to):
            pass
        else:
            t = datetime.datetime.strptime(date_to, "%Y-%m-%d") + datetime.timedelta(days=1)
            date_to = t.strftime("%Y-%m-%d")
            q = q & Q(added_on__range=(date_from,date_to))
        if sc == "0":
            sc = None
        else:
            q = q & Q(service_centre_id=int(sc))
            s = s & Q(id=int(sc))
    else:
      if rtype:
           customer=Customer.objects.using('local_ecomm').all()
           return render_to_response("reports/performance-analysis-customer.html",
                              {'customer':customer},context_instance=RequestContext(request))

      sc = ServiceCenter.objects.using('local_ecomm').all()
      return render_to_response("reports/performance-analysis-location.html",
                              {'sc':sc},context_instance=RequestContext(request))
#    q = Q(added_on__range=("2014-05-01","2014-06-01"))
    c = "Customer" if rtype else "Location"
    file_name = '/Performance_Analysis_%s%s.xlsx'%(c,now.strftime('%d%m%Y%H%M%S%s'))
    path_to_save = settings.FILE_UPLOAD_TEMP_DIR+file_name
    workbook = Workbook(path_to_save)

    header = workbook.add_format()
    header.set_bg_color('green')
    header.set_bold()
    header.set_border()
    plain_format = workbook.add_format()
    sheet = workbook.add_worksheet()
    sheet.set_column(0,15,30)
    col_head = (c, 'Total Shipments','Total Delivered Shipments','% Delivered Shipments',
                'Returned Shipments','%Returned Shipments','Shipments in Outscan','Total Undelivered Shipments',
                '%Undelivered Shipments','Shipments in Transit','RTO in Transit')
    for col, val in enumerate(col_head):
        sheet.write(3,col,val,header)
    q = q & Q(rts_status__in = [0,2])
    #return HttpResponse(str(q))
    row_count = 3
  #  tot_ships = Shipment.objects.using('local_ecomm').filter(q).values('service_centre').annotate(Count('id')).order_by('service_centre')
  #  del_ships = Shipment.objects.using('local_ecomm').filter(q, status = 9).values('service_centre').annotate(Count('id')).order_by('service_centre')
  #  ret_ships = Shipment.objects.using('local_ecomm').filter(q).filter(Q(rto_status=1) | Q(rts_status=2)).\
 #   ret_ships = Shipment.objects.using('local_ecomm').filter(q, rts_status=2).\
 #            values('service_centre').annotate(Count('id')).order_by('service_centre')
 #   ofd_ships = Shipment.objects.using('local_ecomm').filter(q, status = 7).values('service_centre').annotate(Count('id')).order_by('service_centre')
 #   undel_ships = Shipment.objects.using('local_ecomm').filter(q, status = 8).values('service_centre').annotate(Count('id')).order_by('service_centre')
 #   transit_ships = Shipment.objects.using('local_ecomm').filter(q, status__in__range = [0,6]).exclude(rto_status=0).\
 #                   values('service_centre').annotate(Count('id')).order_by('service_centre')
 #   rto_transit_ships = Shipment.objects.using('local_ecomm').filter(q, status__in__range=[0,6], rto_status=1).\
 #                        values('service_centre').annotate(Count('id')).order_by('service_centre')
    #return HttpResponse(q)
    filter_by = Customer.objects.using('local_ecomm').all() if rtype else ServiceCenter.objects.using('local_ecomm').filter(s)
    for a in filter_by:
          r = Q(shipper = a) if rtype else Q(service_centre = a)
          tot_ships = Shipment.objects.using('local_ecomm').filter(q).filter(r).only('id').count()
     #     return HttpResponse(str(tot_ships.query))
    #      return HttpResponse(tot_ships)
          del_ships = Shipment.objects.using('local_ecomm').filter(q, status = 9).filter(r).only('id').count()
          ret_ships = Shipment.objects.using('local_ecomm').filter(q, rts_status=2).filter(r).only('id').count()
          ofd_ships = Shipment.objects.using('local_ecomm').filter(q, status = 7).filter(r).only('id').count()
          undel_ships = Shipment.objects.using('local_ecomm').filter(q, status = 8).exclude(rts_status=2).filter(r).only('id').count()
          transit_ships = Shipment.objects.using('local_ecomm').filter(q, status__in = [0,1,2,3,4,5,6]).filter(r).exclude(rto_status=1).only('id').count()
          rto_transit_ships = Shipment.objects.using('local_ecomm').filter(q, status__in=[0,1,2,3,4,5,6], rto_status=1).filter(r).only('id').count()

          del_perc = float(del_ships)/float(tot_ships)*100.0 if tot_ships else 0
          ret_perc = float(ret_ships)/float(tot_ships)*100.0 if tot_ships else 0
          undel_perc = float(undel_ships)/float(tot_ships)*100.0 if tot_ships else 0

          u = (a, tot_ships, del_ships, round(del_perc,2), ret_ships, round(ret_perc,2), ofd_ships, undel_ships, round(undel_perc,2), transit_ships, rto_transit_ships)
          row_count += 1
     #     return HttpResponse(u)
          for col, val in enumerate(u):
              sheet.write(row_count, col, str(val), plain_format)
    workbook.close()
    if type:
       return (file_name)
    else:
       return HttpResponseRedirect("/static/uploads/%s"%(file_name))


@csrf_exempt
def performance_analysis_location_bk(request):

 #return render_to_response('reports/reports-strikerateanalysis.html',
  if request.POST:
        report_type = request.POST['report_type']
        if request.POST['date_to']:
            todate = request.POST['date_to']
            t = datetime.datetime.strptime(todate, "%Y-%m-%d") + datetime.timedelta(days=1)
            todate = t.strftime("%Y-%m-%d")
        else:
            todate = now.strftime("%Y-%m-%d")
        fromdate=request.POST['date_from']

        sc=request.POST['sc']
#        shipment_info={}
        download_list = []
        if sc =='0':
            b=1
            service_center = ServiceCenter.objects.using('local_ecomm').filter()
            for a in service_center:
                #print "this si the date",date
                shipments = Shipment.objects.using('local_ecomm').filter(added_on__gte=fromdate, added_on__lte = todate,original_dest=a).exclude(rts_status=1)
                total = shipments.only('id').count()
                #print "total",total, a
                delvr = Shipment.objects.using('local_ecomm').filter(added_on__gte=fromdate, added_on__lte = todate,original_dest=a, status=9).exclude(rts_status=1).only('id').count()
                undelvr = Shipment.objects.using('local_ecomm').filter(added_on__gte=fromdate, added_on__lte = todate,original_dest=a, status=8).exclude(rts_status=1).exclude(rts_status=2).only('id').count()
                #returned=0
                returned=Shipment.objects.using('local_ecomm').filter(added_on__gte=fromdate, added_on__lte = todate,original_dest=a).filter(rto_status=1).filter(rts_status=2).exclude(rts_status=1).only('id').count()

                #print returned[0].airwaybill_number
                #returned=returned.only('id').count()
                outscan=Shipment.objects.using('local_ecomm').filter(added_on__gte=fromdate, added_on__lte = todate,original_dest=a, status=7).exclude(rts_status=1).only('id').count()
                #print "outscan is",outscan,a,
                transit=Shipment.objects.using('local_ecomm').filter(added_on__gte=fromdate, added_on__lte = todate,original_dest=a, status__in=[0,1,2,3,4,5,6]).exclude(rts_status=1).only('id').count()
                if total<>0:
                    perc_del = float((float(delvr)/float(total))*100)
                    perc_returned = float((float(returned)/float(total))*100)
                    perc_undel = float((float(undelvr)/float(total))*100)
                else:
                    perc_del=0
                    perc_returned=0
                    perc_undel=0
                u = (str(a.center_name),total, delvr,perc_del,returned,perc_returned,outscan,undelvr,perc_undel,transit)
                download_list.append(u)
        else:
            b=0
            emp = EmployeeMaster.objects.using('local_ecomm').filter(service_centre=int(sc))
            total=0
            shipments=""
	    #location =sc.center_name
            if Shipment.objects.using('local_ecomm').filter(original_dest=sc):
		    shipments = Shipment.objects.using('local_ecomm').filter(added_on__gte=fromdate, added_on__lte = todate,original_dest=sc).exclude(rts_status=1)
                    total = shipments.only('id').count()
            #print "total",total, a
            delvr = shipments.filter(added_on__gte=fromdate, added_on__lte = todate,original_dest=sc, status=9).exclude(rts_status=1).only('id').count()
            undelvr =shipments.filter(added_on__gte=fromdate, added_on__lte = todate,original_dest=sc, status=8).exclude(rts_status=1).exclude(rts_status=2).only('id').count()
                #returned=0
            returned=shipments.filter(added_on__gte=fromdate, added_on__lte = todate,original_dest=sc).filter(rto_status=1).filter(rts_status=2).exclude(rts_status=1).only('id').count()
            #for a in returned:

                #print returned[0].airwaybill_number
                #returned=returned.only('id').count()
            outscan=shipments.filter(added_on__gte=fromdate, added_on__lte = todate,original_dest=sc, status=7).exclude(rts_status=1).only('id').count()
                #print "outscan is",outscan,a,
            transit=shipments.filter(added_on__gte=fromdate, added_on__lte = todate,original_dest=sc, status__in=[0,1,2,3,4,5,6]).exclude(rts_status=1).only('id').count()
            if total<>0:
                        perc_del = float((float(delvr)/float(total))*100)
                        perc_returned = float((float(returned)/float(total))*100)
                        perc_undel = float((float(undelvr)/float(total))*100)
            else:
                        perc_del=0
                        perc_returned=0
                        perc_undel=0
            service_center = ServiceCenter.objects.using('local_ecomm').get(id=sc)
            u = (str(service_center.center_name),total,  delvr,perc_del,returned,perc_returned,outscan,undelvr,perc_undel,transit)
            download_list.append(u)
        if report_type == "dl":
            style = datetime_style
            sheet = book.add_sheet('Performance Analysis Loc Report')
            distinct_list = download_list
            sheet.write(0, 2, "Performance Analysis Location Report", style=header_style)
            sheet.write(2,0, 'location',style=header_style)
            if sc=="0":
                sheet.write(2,1, "All", style = style)
            else:
                sheet.write(2,1, service_center.center_name, style = style)
            sheet.write(2,4, 'Date',style=header_style)
            sheet.write(2,5, fromdate, style = style)
            sheet.write(2,6,"to",style=header_style)
	    sheet.write(2,7,todate,style=style)
            for a in range(1,6):
                sheet.col(a).width = 7000
            sheet.write(5, 0, "Sr No", style=header_style)
            sheet.write(5, 1, "Service Center", style=header_style)
            sheet.write(5, 2, "Total Shipments", style=header_style)
            sheet.write(5, 3, "Total delivered shpts", style=header_style)
            sheet.write(5, 4, "% Delivered shipments", style=header_style)
            sheet.write(5, 5, "Returned shipments", style=header_style)
            sheet.write(5, 6, "% Returned shipments", style=header_style)
            sheet.write(5, 7, "Shipments in outscan", style=header_style)
            sheet.write(5, 8, "Total delivered shpts", style=header_style)
            sheet.write(5, 9, "% Delivered shipments", style=header_style)
            sheet.write(5, 10, "Shipments in Transit", style=header_style)


            counter = 1
            for row, rowdata in enumerate(download_list, start=6):
                    sheet.write(row, 0, str(counter), style=style)
                    counter=counter+1
                    for col, val in enumerate(rowdata, start=1):
                        if col == 4 or col == 6 or col == 9:
                            sheet.write(row, col, str(val)+'%', style=style)
                        else:
                            sheet.write(row, col, str(val), style=style)

            response = HttpResponse(mimetype='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename=Performance-Analysis-Location_%s.xls'%fromdate
            book.save(response)
            return response
        else:
            return render_to_response('reports/reports-performance-analysis-location.html',
                                  {'shipments':download_list,
                    'b':b},
                                  context_instance=RequestContext(request))
  else:

    sc = ServiceCenter.objects.using('local_ecomm').all()

    return render_to_response("reports/performance-analysis-location.html",
                              {
                               'sc':sc},

                               context_instance=RequestContext(request))

@csrf_exempt
def performance_analysis_customer(request):
  if request.POST:
        if request.POST['report_type']:
            report_type = request.POST['report_type']
        if request.POST['date_to']:
            todate = request.POST['date_to']
            #t = datetime.datetime.strptime(fromdate, "%Y-%m-%d") + datetime.timedelta(days=1)
            #todate = t.strftime("%Y-%m-%d")
        else:
            todate = now.strftime("%Y-%m-%d")
            #t = datetime.datetime.strptime(fromdate, "%Y-%m-%d") + datetime.timedelta(days=1)
            #todate = t.strftime("%Y-%m-%d")
	fromdate=request.POST['date_from']
        customer=request.POST['sc']

#        shipment_info={}
        download_list = []
        if customer =='0':
            b=1
            customer = Customer.objects.using('local_ecomm').filter()
            for a in customer:
                 #print "this si the date",date
                shipments = Shipment.objects.using('local_ecomm').filter(added_on__gte=fromdate, added_on__lte = todate,shipper=a).exclude(rts_status=1)
                total = shipments.only('id').count()
                #print "total",total, a
                #delvr = shipments.filter(added_on__gte=fromdate, added_on__lte = todate,shipper=a, status=9).exclude(rts_status=1).only('id').count()
                delvr = shipments.filter(added_on__gte=fromdate, added_on__lte = todate,shipper=a, status=9).exclude(rts_status=1).only('id').count()
                undelvr = shipments.filter(added_on__gte=fromdate, added_on__lte = todate,shipper=a, status=8).exclude(rts_status=1).exclude(rts_status=2).only('id').count()
                #returned=0
                returned=shipments.filter(added_on__gte=fromdate, added_on__lte = todate,shipper=a).filter(rto_status=1).filter(rts_status=2).exclude(rts_status=1).only('id').count()

                #print returned[0].airwaybill_number
                #returned=returned.only('id').count()
                outscan=shipments.filter(added_on__gte=fromdate, added_on__lte = todate,shipper=a, status=7).exclude(rts_status=1).only('id').count()
                #print "outscan is",outscan,a,
                transit=shipments.filter(added_on__gte=fromdate, added_on__lte = todate,shipper=a, status__in=[0,1,2,3,4,5,6]).exclude(rts_status__gte=1).exclude(rto_status=1).only('id').count()
                rtotransit = shipments.filter(added_on__gte=fromdate, added_on__lte = todate,shipper=a, status__in=[0,1,2,3,4,5,6], rto_status=1).exclude(rts_status__gt=1).only('id').count()

                if total<>0:
                    perc_del = float((float(delvr)/float(total))*100)
                    perc_returned = float((float(returned)/float(total))*100)
                    perc_undel = float((float(undelvr)/float(total))*100)
                else:
                    perc_del=0
                    perc_returned=0
                    perc_undel=0
                u = (str(a.name),total, delvr,round(perc_del,2),returned,round(perc_returned,2),outscan,undelvr,round(perc_undel,2),transit, rtotransit)
                download_list.append(u)
        else:
                b=0
            #emp = EmployeeMaster.objects.using('local_ecomm').filter(service_centre=int(sc))
            #for a in emp:
                #location = a.service_centre.center_name
		total=0
                if Shipment.objects.using('local_ecomm').filter(shipper=customer):
                    shipments = Shipment.objects.using('local_ecomm').filter(added_on__gte=fromdate, added_on__lte = todate,shipper=customer).exclude(rts_status=1)
                    total = shipments.only('id').count()
                #print "total",total, a
                delvr = Shipment.objects.using('local_ecomm').filter(added_on__gte=fromdate, added_on__lte = todate,shipper=customer, status=9).exclude(rts_status=1).only('id').count()
                undelvr = Shipment.objects.using('local_ecomm').filter(added_on__gte=fromdate, added_on__lte = todate,shipper=customer, status=8).exclude(rts_status=1).exclude(rts_status=2).only('id').count()
                #returned=0
                returned=Shipment.objects.using('local_ecomm').filter(added_on__gte=fromdate, added_on__lte = todate,shipper=customer).filter(rto_status=1).filter(rts_status=2).exclude(rts_status=1).only('id').count()

                #print returned[0].airwaybill_number
                #returned=returned.only('id').count()
                outscan=Shipment.objects.using('local_ecomm').filter(added_on__gte=fromdate, added_on__lte = todate,shipper=customer, status=7).exclude(rts_status=1).only('id').count()
                #print "outscan is",outscan,a,
                transit=Shipment.objects.using('local_ecomm').filter(added_on__gte=fromdate, added_on__lte = todate,shipper=customer, status__in=[0,1,2,3,4,5,6]).exclude(rts_status__gte=1).exclude(rto_status=1).only('id').count()
                rtotransit = shipments.filter(added_on__gte=fromdate, added_on__lte = todate,shipper=customer, status__in=[0,1,2,3,4,5,6], rto_status=1).exclude(rts_status__gt=1).only('id').count()

                if total<>0:
                        perc_del = float((float(delvr)/float(total))*100)
                        perc_returned = float((float(returned)/float(total))*100)
                        perc_undel = float((float(undelvr)/float(total))*100)
                else:
                        perc_del=0
                        perc_returned=0
                        perc_undel=0
                customer=Customer.objects.using('local_ecomm').get(id=customer)
	 	customer_name=customer.name
                u = (str(customer_name),total, delvr, round(perc_del,2),returned,round(perc_returned,2),outscan,undelvr,round(perc_undel,2),transit, rtotransit)
                download_list.append(u)
        if report_type == "dl":
            style = datetime_style
            sheet = book.add_sheet('Performance Analysis CustReport')
            distinct_list = download_list
            sheet.write(0, 2, "Performance Analysis Customer Report", style=header_style)
            sheet.write(2,0, 'Customer',style=header_style)
            if customer=="0":
                sheet.write(2,1, "All", style = style)
            else:
                pass
                #sheet.write(2,1, location, style = style)
            sheet.write(2,4, 'Date',style=header_style)
            sheet.write(2,5, fromdate, style = style)
	    sheet.write(2,6,'to',style=header_style)
	    sheet.write(2,7,todate,style=style)
            for a in range(1,6):
                sheet.col(a).width = 7000
            sheet.write(5, 0, "Sr No", style=header_style)
            sheet.write(5, 1, "Customer Name", style=header_style)
            #if sc=="0":
             #   sheet.write(5, 1, "Customer Name", style=header_style)
            #else:
             #   sheet.write(5, 1, "Employee Name / Code", style=header_style)
            sheet.write(5, 2, "Total Shipments", style=header_style)
            sheet.write(5, 3, "Total delivered shpts", style=header_style)
            sheet.write(5, 4, "% Delivered shipments", style=header_style)
            sheet.write(5, 5, "Returned shipments", style=header_style)
            sheet.write(5, 6, "% Returned shipments", style=header_style)
            sheet.write(5, 7, "Shipments in outscan", style=header_style)
            sheet.write(5, 8, "Total delivered shpts", style=header_style)
            sheet.write(5, 9, "% Delivered shipments", style=header_style)
            sheet.write(5, 10, "Shipments in Transit", style=header_style)
            sheet.write(5, 11, "RTO Shipments in Transit", style=header_style)

            counter = 1
            default_style = xlwt.Style.default_style
            style_percent = xlwt.easyxf(num_format_str='0.00%')
            for row, rowdata in enumerate(download_list, start=6):
                    sheet.write(row, 0, counter, style=default_style)
                    counter=counter+1
                    for col, val in enumerate(rowdata, start=1):
                        if col == 4 or col == 6 or col == 9:
                            sheet.write(row, col, (val/100), style=style_percent)
                        else:
                            sheet.write(row, col, val, style=default_style)

            response = HttpResponse(mimetype='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename=Performance-Analysis-Location_%s.xls'%fromdate
            book.save(response)
            return response
        else:
            return render_to_response('reports/reports-performance-analysis-customer.html',
                                  {'shipments':download_list,
                    'b':b},
                                  context_instance=RequestContext(request))
  else:

    customer=Customer.objects.using('local_ecomm').all()

    return render_to_response("reports/performance-analysis-customer.html",
                              {
                               'customer':customer},

                               context_instance=RequestContext(request))


@csrf_exempt
def weekly_report(request):

  if request.POST:
        top_ten=[]
        top_ten_low=[]
        last_week=[]
        reason_code_list=[]

        if request.POST['report_type']:
            report_type = request.POST['report_type']
        if request.POST['date_to']:
            todate = request.POST['date_to']
        else:
            todate = now.strftime("%Y-%m-%d")
        t = datetime.datetime.strptime(todate, "%Y-%m-%d") - datetime.timedelta(days=6)
        fromdate = t.strftime("%Y-%m-%d")
        customer=request.POST['sc']
        service_center=ServiceCenter.objects.using('local_ecomm').all()
        download_list = []
        week_report=[]
        total=0
        delvr=0
        undelvr=0
        returned=0
        perc_del=0.00
        perc_returned=0.00
        perc_undel=0.00
        shipments=""
        returned_ships=[]
        returned_reasons=[]
        sc_percentage=[]

        all_undelv_reason_code=[]
        for b in service_center:


                if Shipment.objects.using('local_ecomm').filter(shipper=customer,original_dest=b):
                    shipments = Shipment.objects.using('local_ecomm').filter(added_on__gte=fromdate, added_on__lte = todate,shipper=customer,original_dest=b).exclude(rts_status=1).exclude(rts_status=2)
                    sc_total = shipments.only('id').count()
                    sc_delvr =  shipments.filter(status=9)
                    sc_undelvr =  shipments.filter(status=8)
                    sc_returned=shipments.filter().exclude(status__in=[8,9])  #in noy_in ~
                    for ship in sc_undelvr:
                        returned_ships.append(ship)

                    sc_delvr=sc_delvr.only('id').count()
                    sc_undelvr=sc_undelvr.only('id').count()
                    if sc_total <> 0:
                        del_per = float((float(sc_delvr)/float(sc_total))*100)
                        u=(b,del_per)
                        sc_percentage.append(u)
                    else:
                        del_per=0.00

                    total=total+sc_total
                    delvr=delvr+sc_delvr
                    undelvr=undelvr+sc_undelvr
                    returned=returned+sc_returned.only('id').count()
        for abc in returned_ships:
            returned_reasons.append(abc.reason_code)

        new_lis = sorted(sc_percentage, key = lambda x : x[1], reverse = True)[:10]
        for item in new_lis:
            top_ten.append(item[0])

        new_lis = sorted(sc_percentage, key = lambda x : x[1], reverse =False)[:10]
        for item in new_lis:
            top_ten_low.append(item[0])

        if total<>0:
                        perc_del = float((float(delvr)/float(total))*100)
                        perc_returned = float((float(returned)/float(total))*100)
                        perc_undel = float((float(undelvr)/float(total))*100)
        else:
                        perc_del=0
                        perc_returned=0
                        perc_undel=0

        perc_del = Decimal(str(perc_del)).quantize(Decimal('0.01'))
        perc_returned = Decimal(str(perc_returned)).quantize(Decimal('0.01'))
        perc_undel = Decimal(str(perc_undel)).quantize(Decimal('0.01'))
        u=(total,delvr,perc_del,undelvr,perc_undel,returned,perc_returned)
        week_report.append(u)

        download_list=[]
        for top1 in top_ten:
                ts_total=Shipment.objects.using('local_ecomm').filter(added_on__gte=fromdate, added_on__lte = todate,shipper=customer,original_dest=top1).exclude(rts_status=1).exclude(rts_status=2)
                tmp_delvr = ts_total.filter(status=9).exclude(rts_status=1).only('id').count()
                returned_shipmnts=ts_total.filter(rts_status=1,rto_status=1).only('id').count()
                undelv_shipments=ts_total.filter(status=8).exclude(rts_status=1).only('id').count()
                ts_total=ts_total.only('id').count()

                if ts_total<>0:
                                tmp_perc_del = float((float(tmp_delvr))/float((ts_total))*100)
                                ret_perc=float(((float(returned_shipmnts))/float((ts_total)))*100)
                                undel_perc=float((float((undelv_shipments))/float((ts_total)))*100)
                else:
                                tmp_perc_del=0
                                ret_perc=0
                                undel_perc=0
                tmp_perc_del = Decimal(str(tmp_perc_del)).quantize(Decimal('0.01'))
                ret_perc = Decimal(str(ret_perc)).quantize(Decimal('0.01'))
                undel_perc = Decimal(str(undel_perc)).quantize(Decimal('0.01'))
                u = (str(top1),ts_total, tmp_delvr, tmp_perc_del,returned_shipmnts,ret_perc,undelv_shipments,undel_perc)
                download_list.append(u)
        low_shipment_sc=[]
        low_shipment=[]
        for low in top_ten_low:
            low_sc_shipments=Shipment.objects.using('local_ecomm').filter(added_on__gte=fromdate, added_on__lte = todate,shipper=customer,original_dest=low,status=8).exclude(rts_status=1).exclude(rts_status=2)
            u=(str(low),low_sc_shipments.only('id').count())
            low_shipment_sc.append(u)

            for low_ship in low_sc_shipments:
                u=(low_ship)
                low_shipment.append(u)

        status=[]
        for ab in low_shipment:
             status.append(ab.reason_code)
        status = list(set(status))
        returned_reasons=list(set(returned_reasons))
        for tmp1 in status:
                rc_count=0
                for a in low_shipment:
                    if tmp1==a.reason_code:
                        rc_count=rc_count+1

                if len(low_shipment)<>0:
                	rc_perc = float(((rc_count)/(float(len(low_shipment))))*100)
                else:
                	rc_perc	=0
                rc_perc = Decimal(str(rc_perc)).quantize(Decimal('0.01'))
                u=(tmp1,rc_count,rc_perc)
                reason_code_list.append(u)

        for beta in returned_reasons:
            count=0
            for beta1 in returned_ships:
                if beta==beta1.reason_code:
                        count=count+1

                if len(returned_ships)<>0:
                    rc_perc = float(((count)/(float(len(returned_ships))))*100)
                else:
                    rc_perc    =0
                rc_perc = Decimal(str(rc_perc)).quantize(Decimal('0.01'))
                u=(beta,count,rc_perc)
            all_undelv_reason_code.append(u)

        other=Shipment.objects.using('local_ecomm').filter(added_on__gte=fromdate, added_on__lte = todate,shipper=customer).exclude(rts_status=1)

        for a in range(7):
            tmp_t = datetime.datetime.strptime(todate, "%Y-%m-%d") - datetime.timedelta(days=a)
            tmp_fromdate = tmp_t.strftime("%Y,%m,%d")
            dated=tmp_t.strftime("%d-%m-%Y")
            day=tmp_t.strftime("%A")
            yy=tmp_t.strftime("%Y")
            mm=tmp_t.strftime("%m")
            dd=tmp_t.strftime("%d")
            yy=int(yy)
            mm=int(mm)
            dd=int(dd)
            tmp_count=other.filter(added_on__startswith = datetime.date(yy,mm,dd)).only('id').count()
            u=(str(dated),tmp_count,day)
            last_week.append(u)

        if report_type == "dl":
            customer=Customer.objects.using('local_ecomm').get(id=customer)
            style = datetime_style
            sheet = book.add_sheet('Weekly Report')
            sheet.write(0,1, "Weekly Report", style=header_style)
            sheet.write(1,0, 'Customer',style=header_style)
            sheet.write(1,1, customer.name, style = style)
            sheet.write(1,2, 'Date',style=header_style)
            sheet.write(1,3, fromdate, style = style)
            sheet.write(1,4,'to',style=header_style)
            sheet.write(1,5,todate,style=style)
            sheet.write(3, 3, "WEEKLY ANALYSIS", style=header_style)
            sheet.write(4,1, 'Total',style=header_style)
            sheet.write(4,2, 'Delivered', style = header_style)
            sheet.write(4,3,'%ge Delivered',style=header_style)
            sheet.write(4,6,'Returned',style=header_style)
            sheet.write(4,7,'% Returned',style=header_style)
            sheet.write(4,4,'Undelv',style=header_style)
            sheet.write(4,5,'% Undlev',style=header_style)
            for a in range(1,6):
                sheet.col(a).width = 7000
            sheet.write(8, 0, "Sr No", style=header_style)
            sheet.write(8, 1, "Service Center", style=header_style)
            sheet.write(8, 2, "Total Shipments", style=header_style)
            sheet.write(8, 3, "Total delivered shpts", style=header_style)
            sheet.write(8, 4, "% Delivered shipments", style=header_style)
            sheet.write(8, 5, "Returned ", style=header_style)
            sheet.write(8, 6, "% Returned shipments", style=header_style)
            sheet.write(8, 7, "Undelivered shipments", style=header_style)
            sheet.write(8, 8, "% Undelivered shipments", style=header_style)
            sheet.write(7, 3, " TOP TEN Delivery Centers", style=header_style)

            tmplen=25
            sheet.write(tmplen-3,1,"Low Performance Delivery Centers",style=header_style)
            sheet.write(tmplen-2,0,"Sr. No",style=header_style)
            sheet.write(tmplen-2,1,"Service Center",style=header_style)
            sheet.write(tmplen-2,2,"No of Shipments",style=header_style)

            newtmplen=40
            sheet.write(newtmplen-3,1,"Reasons for undelivered shipments",style=header_style)
            sheet.write(newtmplen-3,2,"Low Performing DC",style=header_style)
            sheet.write(newtmplen-2,0,"Sr. No",style=header_style)
            sheet.write(newtmplen-2,1,"Reason",style=header_style)
            sheet.write(newtmplen-2,2,"No of Shipments",style=header_style)
            sheet.write(newtmplen-2,3,"% Shipments",style=header_style)
            tmp2len=newtmplen+7+len(reason_code_list)
            tmp1len=tmp2len+5+len(all_undelv_reason_code)
            sheet.write(tmp1len-3,2,"Weekly Performance",style=header_style)
            sheet.write(tmp1len-2,2,"No of Shipments",style=header_style)
            sheet.write(tmp1len-2,1,"Date",style=header_style)
            sheet.write(tmp1len-2,3,"Day",style=header_style)
            sheet.write(tmp1len-2,0,"Sr. No",style=header_style)


            sheet.write(tmp2len-3,1,"Reasons for undelivered shipments",style=header_style)
            sheet.write(tmp2len-2,0,"Sr. No",style=header_style)
            sheet.write(tmp2len-2,1,"Reason",style=header_style)
            sheet.write(tmp2len-2,2,"No of  Undev. Shipments",style=header_style)
            sheet.write(tmp2len-2,3,"% Shipments",style=header_style)


            counter = 1
            for row, rowdata in enumerate(download_list, start=9):
                    sheet.write(row, 0, str(counter), style=style)
                    counter=counter+1
                    for col, val in enumerate(rowdata, start=1):
                        if col == 4 or col==6 or col==8:
                            sheet.write(row, col, str(val)+'%', style=style)
                        else:
                            sheet.write(row, col, str(val), style=style)
            for row_wk, rowdata in enumerate(week_report, start=5):
                  for col_wk, val_wk in enumerate(rowdata, start=1):
                        if col_wk == 3 or col_wk== 5 or col_wk==7 :
                            sheet.write(row_wk, col_wk, str(val_wk)+'%', style=style)
                        else:
                            sheet.write(row_wk, col_wk, str(val_wk), style=style)

            tmp_counter=1
            for row1,rowdata1 in enumerate(reason_code_list, start=newtmplen):
                    sheet.write(row1, 0, str(tmp_counter), style=style)
                    tmp_counter=tmp_counter+1
                    for col1, val1 in enumerate(rowdata1, start=1):
                        if col1 == 3 :
                            sheet.write(row1, col1, str(val1)+'%', style=style)
                        else:
                            sheet.write(row1, col1, str(val1), style=style)

            tmp_counter1=1
            if len(low_shipment_sc) <> 0:
                for row2,rowdata2 in enumerate(low_shipment_sc, start=tmplen):
                    sheet.write(row2, 0, str(tmp_counter1), style=style)
                    tmp_counter1=tmp_counter1+1
                    for col2, val2 in enumerate(rowdata2, start=1):
                          sheet.write(row2, col2, str(val2), style=style)

            tmp_counter3=1
            for row3,rowdata3 in enumerate(last_week, start=tmp1len):
                    sheet.write(row3, 0, str(tmp_counter3), style=style)
                    tmp_counter3=tmp_counter3+1
                    for col3, val3 in enumerate(rowdata3, start=1):
                          if val3 <> "Sunday":
                              sheet.write(row3, col3, str(val3), style=style)
                          else:
                              sheet.write(row3, col3, str(val3), style=header_style)

            tmp_counter2=1
            if len(all_undelv_reason_code) <> 0:
                for row3,rowdata3 in enumerate(all_undelv_reason_code, start=tmp2len):
                    sheet.write(row3, 0, str(tmp_counter2), style=style)
                    tmp_counter2=tmp_counter2+1
                    for col3, val3 in enumerate(rowdata3, start=1):
                        if col3 == 3 :
                            sheet.write(row3, col3, str(val3)+'%', style=style)
                        else:
                            sheet.write(row3, col3, str(val3), style=style)
            response = HttpResponse(mimetype='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename=Weekly-Analysis_%s.xls'%fromdate
            book.save(response)
            return response
        else:
            return render_to_response('reports/reports-weekly-report.html',
                                  {'shipments':download_list,
                    'b':b},
                                  context_instance=RequestContext(request))
  else:

    customer=Customer.objects.using('local_ecomm').all()
    return render_to_response("reports/weekly-report.html",
                              {
                               'customer':customer},

                               context_instance=RequestContext(request))





def high_value_shipments(request):
    list_100=[]
    list_200=[]
    shipments=Shipment.objects.using('local_ecomm').filter(status__in = [6,7,8],return_shipment=0).exclude(rts_status=2).exclude(rts_status=1).exclude(rto_status=1).exclude(reason_code_id=1)
    for a in shipments:
        try:
            if a.codcharge_set.get().cod_charge > 100 :
                u=(a.airwaybill_number,a.shipper,a.added_on,a.original_dest,a.reason_code,a.current_sc,a.codcharge_set.get().cod_charge)
                list_100.append(u)
                if a.codcharge_set.get().cod_charge > 200 :
                    list_200.append(u)
        except:
             pass
    todate = now.strftime("%Y-%m-%d")
    style = datetime_style
    sheet = book.add_sheet('High Value Shipments')
    sheet.write(1, 2, "High Value Shipments", style=header_style)
    sheet.write(3,1, 'Date',style=header_style)
    sheet.write(3,2, todate, style = style)
    sheet.write(5,2," COD Charge > 100",style=header_style)
    for a in range(1,6):
        sheet.col(a).width = 7000
    sheet.write(6, 0, "Sr No", style=header_style)
    sheet.write(6, 1, "Airway Bill Number", style=header_style)
    sheet.write(6, 2, "Shipper", style=header_style)
    sheet.write(6, 3, "Added On", style=header_style)
    sheet.write(6, 4, "Original Destination", style=header_style)
    sheet.write(6, 5, "Reason Code", style=header_style)
    sheet.write(6, 6, " Current SC ", style=header_style)
    sheet.write(6, 7, "COD Charge", style=header_style)
    counter = 1
    for row, rowdata in enumerate(list_100, start=7):
                    sheet.write(row, 0, str(counter), style=style)
                    counter=counter+1
                    for col, val in enumerate(rowdata, start=1):
                        sheet.write(row, col, str(val), style=style)

    counter1=1
    newlen=len(list_100)+12
    sheet.write(newlen-3,2," COD Charge > 200",style=header_style)
    sheet.write(newlen-1, 0, "Sr No", style=header_style)
    sheet.write(newlen-1, 1, "Airway Bill Number", style=header_style)
    sheet.write(newlen-1, 2, "Shipper", style=header_style)
    sheet.write(newlen-1, 3, "Added On", style=header_style)
    sheet.write(newlen-1, 4, "Original Destination", style=header_style)
    sheet.write(newlen-1, 5, "Reason Code", style=header_style)
    sheet.write(newlen-1, 6, " Current SC ", style=header_style)
    sheet.write(newlen-1, 7, "COD Charge", style=header_style)
    for row1, rowdata1 in enumerate(list_200, start=newlen):
                    sheet.write(row1, 0, str(counter1), style=style)
                    counter1=counter1+1
                    for col1, val1 in enumerate(rowdata1, start=1):
                        sheet.write(row1, col1, str(val1), style=style)

    file_name = "/high_value_shipments_%s.xls"%(now.strftime("%H%M%S%s"))
    path_to_save = settings.FILE_UPLOAD_TEMP_DIR+file_name
    book.save(path_to_save)
    return "/home/web/ecomm.prtouch.com/ecomexpress/static/uploads%s"%(file_name)
  #  response = HttpResponse(mimetype='application/vnd.ms-excel')
  #  response['Content-Disposition'] = 'attachment; filename=High Value Shipments_%s.xls'%todate
  #  book.save(response)
  #  return response

def get_daily_report(request):
    customers = Customer.objects.using('local_ecomm').all()
    return render_to_response("reports/daily_report.html",
                              {'customers':customers},
                               context_instance=RequestContext(request))


def get_excel_for_daily_report(field_names, data_list, date):
    # add filename and set save file path
    file_name = "/daily_report_%s.xlsx"%(now.strftime("%d%m%Y%H%M%S%s"))
    path_to_save = settings.FILE_UPLOAD_TEMP_DIR+file_name
    workbook = Workbook(path_to_save)

    # define style formats for header and data
    header_format = workbook.add_format()
    header_format.set_bold()
    header_format.set_align('center')

    plain_format = workbook.add_format()
    plain_format.set_align('center')

    # add a worksheet and set excel sheet column headers
    sheet = workbook.add_worksheet()
    sheet.set_column(0, 12, 15) # set column width
    sheet.write(0, 4, "Daily Report(%s)" % date)
    row_num = 3

    # write data to excel sheet
    def write_to_excel(row_data, row_num):
        # write customer name
        sheet.write(row_num, 4, str(row_data[0]), header_format)
        # write col heads
        for c, field in enumerate(field_names):
            sheet.write(row_num+1, c, str(field), header_format)
        # write values
        for c, data in enumerate(row_data):
            sheet.write(row_num+2, c, str(data), plain_format)
        return row_num

    for row_data in data_list:
        row_num = write_to_excel(row_data, row_num)
        row_num += 4

    workbook.close()
    return file_name


def get_shipments_in_range(customer, dt):
    q = Q()
    q = q & Q(shipper_id = int(customer.id))
    df = dt - datetime.timedelta(days=dt.day-1)
    date_to = dt.strftime("%Y-%m-%d")
    date_from = df.strftime("%Y-%m-%d")
    q = q & Q(added_on__range=(date_from, date_to))
    shipments = Shipment.objects.using('local_ecomm').filter(q)
    return shipments

def get_daily_report_display_info(customer, date_on):
    shipments = Shipment.objects.using('local_ecomm').filter(shipper=customer,
                                        added_on__year=date_on.year,
                                        added_on__month=date_on.month,
                                        added_on__day=date_on.day)

    shipments_in_range = get_shipments_in_range(customer, date_on)

    total_pickups = shipments.only('id').count()
    month_pickups = shipments_in_range.only('id').count()
    delivered_ships = shipments_in_range.filter(status=9).only('id').count()
    delivered_ships_per = round( (float(delivered_ships) / month_pickups ) * 100, 2) if month_pickups else 0
    undelivered_ships = shipments_in_range.filter(status=8).only('id').count()
    undelivered_ships_per = round( (float(undelivered_ships) / month_pickups ) * 100, 2) if month_pickups else 0
    rto_ships = shipments_in_range.filter(rto_status=8).only('id').count()
    rto_ships_per = ( rto_ships / month_pickups ) * 100 if month_pickups else 0
    out_for_delivery = shipments_in_range.filter(status=7).only('id').count()
    out_for_delivery_per = round( (float(out_for_delivery) / month_pickups ) * 100, 2) if month_pickups else 0
    res_code = ShipmentStatusMaster.objects.using('local_ecomm').filter(id__in=[1,6,46])
    total_no_info = shipments_in_range.filter(status=8).\
            exclude(reason_code__in = res_code).\
            exclude(status_type=5).\
            exclude(reason_code_id=6).only('id').count()

    return (
        customer.name,
        total_pickups,
        month_pickups,
        delivered_ships,
        delivered_ships_per,
        undelivered_ships,
        undelivered_ships_per,
        rto_ships,
        rto_ships_per,
        out_for_delivery,
        out_for_delivery_per,
        total_no_info,
    )


@csrf_exempt
def daily_report(request):
    """ this view will provide the daily report
        info: http://projects.prtouch.com/issues/553
    """
    # required fields for inscan reports
    report_fields = (
        'Customer Name',
        'Total Pickup On Previous Day',
        'Total Pickup For the Month', # shipment.added_on and expected_dod
        'Delivered Count',
        'Delivered %',
        'Undelivered', # shipment history , status 9 delivered
        'Undelivered %', # shipment history , status 8 undelivered
        'RTO',
        'RTO %',
        'Out for Delivery',
        'Out for Delivery %',
        'Total No Info',
        #'Action Taken',
        #'Reason'
    )

    # if request is ajax and it is get then show the report through html
    if request.is_ajax() and request.method == 'GET':
        # get the data from request
        date_on = request.GET.get('date_on')
        cust_id = request.GET.get('cust_id')
        if date_on:
            date_on = datetime.datetime.strptime(date_on, "%Y-%m-%d") - datetime.timedelta(days=1)
        else:
            date_on = datetime.datetime.today() - datetime.timedelta(days=1)

        display_info = []

        if int(cust_id):
            customer = Customer.objects.using('local_ecomm').get(pk=int(cust_id))
            display_info.append(get_daily_report_display_info(customer, date_on))
        else:
            # get all customers
            customers = Customer.objects.using('local_ecomm').all()
            # get display data  for each customer
            display_info = (get_daily_report_display_info(c, date_on) for c in customers)

        # get the html string to display on the report page
        html = render_to_string('reports/daily_report_data.html',
                   {'display_list':display_info, 'report_fields':report_fields},
               )

        data = {'html':html}
        json = simplejson.dumps(data)
        return HttpResponse(json, mimetype='application/json')

    # else if it is a post request then give the excel file for dowload
    elif request.POST:
        # get the data from request
        date_on = request.POST.get('date_on')
        if date_on:
            date_on = datetime.datetime.strptime(date_on, "%Y-%m-%d") - datetime.timedelta(days=1)
        else:
            date_on = datetime.datetime.today() - datetime.timedelta(days=1)
        cust_id = request.POST.get('cust_id')
        download_info = []

        if int(cust_id):
            customer = Customer.objects.using('local_ecomm').get(pk=int(cust_id))
            download_info.append(get_daily_report_display_info(customer,date_on))
        else:
            # get all customers
            customers = Customer.objects.using('local_ecomm').all()
            # get display data  for each customer
            download_info = (get_daily_report_display_info(c, date_on) for c in customers)

        # make downloadable excel file
        date = str(date_on.day) + 'th ' + str(date_on.strftime('%B'))
        file_name = get_excel_for_daily_report(report_fields, download_info, date)
        return HttpResponseRedirect("/static/uploads/%s"%(file_name))

    return HttpResponse("This is laod report")


def get_missed_pickup(request):
    sc = ServiceCenter.objects.using('local_ecomm').all()
    report_url = reverse('missed-pickup')
    return render_to_response("reports/df_dt_dest.html",
                              {'sc':sc,
                               'report_url':report_url,
                               'report_name':'Missed Pickup Report'},
                               context_instance=RequestContext(request))


def get_missed_pickup_objs(df_str, dt_str, dest):
    q = Q()
    if int(dest):
        q = q & Q(service_centre__id=dest)
    if not df_str:
        df_str = get_last_date_str()

    if not dt_str:
        dt_str = get_today_str()

    q = q & Q(pickup_date__range=(df_str, dt_str))
    pickups = PickupSchedulerRegistration.objects.using('local_ecomm').filter(q).\
                  values('added_on',
                         'subcustomer_code__name',
                         'subcustomer_code__customer__name',
                         'service_centre__center_name',
                         'reason_code__code')
    return pickups


def get_missed_pickup_report_display_info(date_from, date_to, dest):
    display_data = get_missed_pickup_objs(date_from, date_to, dest)
    return display_data

def get_excel_for_missed_pickup_report(field_names, data_list):
    # add filename and set save file path
    file_name = "/missed_pickup_report_%s.xlsx"%(now.strftime("%d%m%Y%H%M%S%s"))
    path_to_save = settings.FILE_UPLOAD_TEMP_DIR+file_name
    workbook = Workbook(path_to_save)

    # define style formats for header and data
    header_format = workbook.add_format()
    header_format.set_bold()
    header_format.set_align('center')

    plain_format = workbook.add_format()
    plain_format.set_align('center')

    # add a worksheet and set excel sheet column headers
    sheet = workbook.add_worksheet()
    sheet.set_column(0, 4, 20) # set column width
    sheet.write(0, 2, "Missed Pickup Report")
    sheet.write(0, 3, "DATE: " + str(datetime.date.today()))

    # write col heads
    row_num = 3
    for col, field in enumerate(field_names):
        sheet.write(row_num, col, str(field), header_format)

    # write values
    for row, data in enumerate(data_list, start=4):
        sheet.write(row, 0,  str(data['added_on']), plain_format)
        vendor = data['subcustomer_code__name']
        vendor = vendor.encode('utf-8') if isinstance(vendor, unicode) else vendor
        sheet.write(row, 1,  str(vendor), plain_format)
        customer = data['subcustomer_code__customer__name']
        customer = customer.encode('utf-8') if isinstance(customer, unicode) else customer
        sheet.write(row, 2,  str(customer), plain_format)
        dest = data['service_centre__center_name']
        dest = dest.encode('utf-8') if isinstance(dest, unicode) else dest
        sheet.write(row, 3,  str(dest), plain_format)
        desc = data['reason_code__code']
        desc = desc.encode('utf-8') if isinstance(desc, unicode) else desc
        sheet.write(row, 4,  str(desc), plain_format)

    workbook.close()
    return file_name



@csrf_exempt
def missed_pickup(request):
    """ this view will provide the missed pickup report
        info: http://projects.prtouch.com/issues/
    """
    # required fields for inscan reports
    report_fields = (
        'Registration Date',
        'Vendor Name',
        'Customer',
        'Location',
        'Reason',
    )

    # if request is ajax and it is get then show the report through html
    if request.is_ajax() and request.method == 'GET':
        # get the data from request
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        dest = request.GET.get('sc')

        # get display data
        # [{'subcustomer_code__name': u'Bata - Sector 14',
        # 'subcustomer_code__customer__name': u'XERION RETAIL PRIVATE LIMITED',
        # 'service_centre__center_name': u'GURGAON-GGC',
        # 'added_on': datetime.datetime(2013, 7, 10, 13, 46, 50), 'reason_code__code_description': None}]
        display_info = get_missed_pickup_report_display_info(date_from, date_to, dest)

        # get the html string to display on the report page
        html = render_to_string('reports/missed_pickup_report_data.html',
                   {'display_list':display_info, 'report_fields':report_fields},
               )

        data = {'html':html}
        json = simplejson.dumps(data)
        return HttpResponse(json, mimetype='application/json')

    # else if it is a post request then give the excel file for dowload
    elif request.POST:
        # get the data from request
        date_from = request.POST.get('date_from')
        date_to = request.POST.get('date_to')
        dest = request.POST.get('sc')

        # get display data
        # [{'subcustomer_code__name': u'Bata - Sector 14',
        # 'subcustomer_code__customer__name': u'XERION RETAIL PRIVATE LIMITED',
        # 'service_centre__center_name': u'GURGAON-GGC',
        # 'added_on': datetime.datetime(2013, 7, 10, 13, 46, 50), 'reason_code__code_description': None}]
        display_info = get_missed_pickup_report_display_info(date_from, date_to, dest)

        # make downloadable excel file
        #date = str(date_on.day) + 'th ' + str(date_on.strftime('%B'))
        file_name = get_excel_for_missed_pickup_report(report_fields, display_info)
        return HttpResponseRedirect("/static/uploads/%s"%(file_name))

    return HttpResponse("This is missed pickup report")

@csrf_exempt
def rto_status_report(request):
    if request.POST:
        file_name = "/RTOStatusReport.xlsx"
        path_to_save = settings.FILE_UPLOAD_TEMP_DIR+file_name
        workbook = Workbook(path_to_save)
        header_format = workbook.add_format()
        header_format.set_bg_color('yellow')
        header_format.set_bold()
        header_format.set_border()

        plain_format = workbook.add_format()
        sheet = workbook.add_worksheet()
        sheet.set_column(0,12,30)
        #sheet.write(0,2,"RTO Report",header_format)
        sheet.write(0,0,"Airwaybill Number",header_format)
        sheet.write(0,1,"Added On",header_format)
        sheet.write(0,2,"Origin",header_format)
        sheet.write(0,3,"Current SC",header_format)
        sheet.write(0,4,"Destination",header_format)
        sheet.write(0,5,"Original Destination",header_format)
        sheet.write(0,6,"Status",header_format)
        sheet.write(0,7,"Reason Code",header_format)
        sheet.write(0,8,"Updated On",header_format)
        sheet.write(0,9,"New AWB",header_format)
        sheet.write(0,10,"Status",header_format)
        sheet.write(0,11,"Updated On",header_format)
        sheet.write(0,12,"Shipper",header_format)
        sheet.write(0,13,"Current SC shortcode",header_format)

        q = Q()
        row = 0
        date_from = request.POST['date_from']
        date_to = request.POST['date_to']
        customer = request.POST['cust_id']
        if date_to:
          date_to = datetime.datetime.strptime(date_to, "%Y-%m-%d")+datetime.timedelta(days=1)
          date_to = date_to.strftime("%Y-%m-%d")
        if customer == "0":
            customer = None
        else:
            q = q & Q(shipper_id = int(customer))

        ship = Shipment.objects.using('local_ecomm').filter(rto_status=1, added_on__range=(date_from,date_to)).filter(q).exclude(status=9).exclude(rts_status=1)
        for a in ship.iterator():
            monthdir = a.added_on.strftime("%Y_%m")
            shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
            hist = shipment_history.objects.using('local_ecomm').filter(shipment=a).exclude(status__in=[11,12,16]).latest('updated_on')
            status=get_internal_shipment_status(a.status)

            if a.ref_airwaybill_number:
               ref_sh = Shipment.objects.using('local_ecomm').filter(airwaybill_number=a.ref_airwaybill_number)
               if not ref_sh:
                  continue
               else:
                 ref_sh = ref_sh[0]
               if ref_sh.status == 9:
                  continue
               rts_awb = a.ref_airwaybill_number
               rts_status = get_internal_shipment_status(ref_sh.status)
               rts_updated_on = ref_sh.updated_on
            else:
              rts_awb = ""
              rts_status = ""
              rts_updated_on = ""
            center_shortcode = hist.current_sc.center_shortcode if hist.current_sc else ''
            u = (a.airwaybill_number, a.added_on, a.pickup.service_centre, hist.current_sc, a.service_centre, a.original_dest,
                status, a.reason_code, hist.updated_on, rts_awb, rts_status, rts_updated_on, a.shipper, center_shortcode)
            row = row+1
            for col, val in enumerate(u, start=0):
         #       try:
                   sheet.write(row, col, str(val),plain_format )
        #        except:
        #           pass
        workbook.close()
        return HttpResponseRedirect("/static/uploads/%s"%(file_name))
    else:
        customer = Customer.objects.using('local_ecomm').all()
        return render_to_response("reports/rto_status_report.html",
                                  {'customer':customer},
                               context_instance=RequestContext(request))

def outscan_performance_report(request, type=0, ebs = 0):
      q = Q()
      ebsq = Q()
      ebsq1 = Q()
      if ebs:
         ebsq = (Q(shipments__airwaybill_number__startswith = 3) | Q(shipments__airwaybill_number__startswith = 4))
         ebsq1 = (Q(shipment__airwaybill_number__startswith = 3) | Q(shipment__airwaybill_number__startswith = 4))
      if type == 1:
         end_date = datetime.datetime.now().date()
         start_date = now.date() - datetime.timedelta(days=1)
    #     print start_date, end_date
      elif request.POST:

         date_from = request.POST['date_from']
         date_to = request.POST['date_to']
         start_date = datetime.datetime.strptime(date_from, '%Y-%m-%d').date()
         end_date = datetime.datetime.strptime(date_to, '%Y-%m-%d').date()
         sc = request.POST['sc']
         if sc <> '0':
            q = q & Q(service_centre=sc)
      else:
         sc = ServiceCenter.objects.using('local_ecomm').all()
         return render_to_response("reports/outscan_performance_report.html",
                                  {'sc':sc},
                               context_instance=RequestContext(request))
      file_name = "outscan_del_%s.xlsx"%(datetime.datetime.now().strftime("%d%m%Y%H%M%S%s"))
      path_to_save = settings.FILE_UPLOAD_TEMP_DIR+"/"+file_name
      workbook = Workbook(path_to_save)

    # define style formats for header and data
      header_format = workbook.add_format({
        'bold': 1,
        'align': 'center',
        'valign': 'vcenter',
        'fg_color': '#cccccc'})
    #header_format.set_bg_color('#cccccc')
    #header_format.set_bold()

    # Create a format to use in the merged range.
      merge_format = workbook.add_format({
        'bold': 1,
        'align': 'center',
        'valign': 'vcenter',
        'fg_color': 'yellow'})

      plain_format = workbook.add_format({
        'align': 'center',
        'valign': 'vcenter'})

      date_format = workbook.add_format({'num_format': 'mmmm d yyyy'})

    # add a worksheet and set excel sheet column headers
      sheet = workbook.add_worksheet()

      sheet.set_column(0, 14, 12) # set column width
    # write statement headers: statement name, customer name, and date
      u = ("Date", "Employee Code", "Employee Name", "Service Centre", "OFD", "Delivered", "%", "MTD OFD", "MTD Delivered", "%")
      for col, val in enumerate(u):
          sheet.write(2, col, val, header_format)
      em_list = []
      #print q, ebs
      row_count = 3
      day_count = (end_date - start_date).days + 1
      delta = datetime.timedelta(days = 1)
      while start_date <= end_date:
            em = EmployeeMaster.objects.using('local_ecomm').filter(user_type = "Staff").exclude(staff_status=2).filter(q).order_by('service_centre')
            for emp in em:
                total_dcount = DeliveryOutscan.objects.using('local_ecomm').filter(ebsq, added_on__gte=start_date, added_on__lt=(start_date + datetime.timedelta(days = 1)),
                              employee_code=emp,shipments__rts_status__in = [0], shipments__reverse_pickup__in=[0]).values('employee_code__employee_code').annotate(Count('shipments'))
                totd = total_dcount[0]['shipments__count'] if total_dcount else 0
                os_tot = DeliveryOutscan.objects.using('local_ecomm').filter(added_on__gte=start_date, added_on__lt=(start_date + datetime.timedelta(days = 1)),
                              employee_code=emp)

                total_mcount = DeliveryOutscan.objects.using('local_ecomm').filter(ebsq, added_on__month=start_date.month, added_on__lt=(start_date + datetime.timedelta(days = 1)),
                              employee_code=emp,shipments__rts_status__in = [0], shipments__reverse_pickup__in=[0]).values('employee_code__employee_code').annotate(Count('shipments'))
                totm = total_mcount[0]['shipments__count'] if total_mcount else 0
                if totm == 0:
                   continue
                os_mom = DeliveryOutscan.objects.using('local_ecomm').filter(added_on__month=start_date.month, added_on__lt=(start_date + datetime.timedelta(days = 1)),
                              employee_code=emp)

                deld_dcount = DOShipment.objects.using('local_ecomm').filter(ebsq1, added_on__gte=start_date, added_on__lt=(start_date + datetime.timedelta(days = 1)),status=1, deliveryoutscan__employee_code=emp, shipment__rts_status__in = [0], shipment__reverse_pickup__in=[0], deliveryoutscan__in=os_tot).values('deliveryoutscan__employee_code__employee_code').annotate(Count('id'))
#                deld_dcount = DeliveryOutscan.objects.using('local_ecomm').filter(added_on__gte=start_date, added_on__lt=(start_date + datetime.timedelta(days = 1)),
 #                             doshipment__status__exact=1, employee_code=emp, shipments__rts_status__in = [0], shipments__reverse_pickup__in=[0]).values('employee_code__employee_code').annotate(Count('shipments'))
                deldd = deld_dcount[0]['id__count'] if deld_dcount else 0
                deld_mcount = DOShipment.objects.using('local_ecomm').filter(ebsq1, added_on__month=start_date.month, added_on__lt=(start_date + datetime.timedelta(days = 1)),status=1, deliveryoutscan__employee_code=emp, shipment__rts_status__in = [0], shipment__reverse_pickup__in=[0], deliveryoutscan__in=os_mom).values('deliveryoutscan__employee_code__employee_code').annotate(Count('id'))

         #       deld_mcount = DeliveryOutscan.objects.using('local_ecomm').filter(added_on__month=start_date.month, added_on__lt=(start_date + datetime.timedelta(days = 1)),
         #                     shipments__status__exact=9, employee_code=emp, shipments__rts_status__in = [0], shipments__reverse_pickup__in=[0]).values('employee_code__employee_code').annotate(Count('shipments'))
                deldm = deld_mcount[0]['id__count'] if deld_mcount else 0


               # if emp not in del_dict:
               #    del_dict[emp]=[totd,deldd]
               # else:
               #    del_dict[emp][0] += totd
               #    del_dict[emp][1] += deldd

                perc = round(float((deldd * 100)/totd),2) if totd else 0
                mtd_perc = round(float((deldm * 100)/totm),2) if totm else 0
              #  mtd_perc = del_dict[emp][1]*100/del_dict[emp][0] if del_dict[emp][0] else 0
                if not emp.service_centre:
                    continue
                u = (str(start_date), str(emp.employee_code), str(emp.firstname), str(emp.service_centre.center_shortcode), totd, deldd,
                    perc, totm, deldm, mtd_perc)
                for col, val in enumerate(u):
                    sheet.write(row_count, col, val)
                row_count += 1
            start_date += delta
      if type:
         return (file_name)
      return HttpResponseRedirect('/static/uploads/%s'%(file_name))

    #  outscan_perf_report(date_from, date_to, 1)

#def strike_rate_analysis_location(request):
    ## expect date string in the following format: yyyy-mm-dd
    ## Daily Report
    #file_name = get_location_strike_rate_report(date_str)
#
    #response = HttpResponse(mimetype='application/vnd.ms-excel')
    #response['Content-Disposition'] = 'attachment; filename=%s_report_%s.xls' % (file_name ,report_date_str)
#
    #return HttpResponseRedirect("/static/uploads/%s"%(file_name))

def get_correction_report(request):
    if request.method == 'GET':
        sc = ServiceCenter.objects.using('local_ecomm').all()
        return render_to_response("reports/correction_report.html",
                                  {'sc':sc},
                               context_instance=RequestContext(request))
    elif request.method == 'POST':
        date_from = request.POST['date_from']
        date_to = request.POST['date_to']
        file_name = generate_correction_report(date_from, date_to)
        return HttpResponseRedirect("/static/uploads/reports/%s"%(file_name))

def telecalling_report(request):
  if request.method != 'POST':
        sc = ServiceCenter.objects.using('local_ecomm').all()
        customer=Customer.objects.using('local_ecomm').all()
        return render_to_response("reports/telecalling_report.html",
                                  {'sc':sc,'customer':customer},
                               context_instance=RequestContext(request))
  else:
     date_from = request.POST['date_from']
     date_to = request.POST['date_to']
     cust_id = request.POST['cust_id']
     destination = request.POST['sc']
     file_name = generate_tellecalling_report(date_from, date_to, cust_id , destination)
     return HttpResponseRedirect("/static/uploads/reports/%s"%(file_name))

def pickup_mis_report(request):
  if request.method != 'POST':
        sc = ServiceCenter.objects.using('local_ecomm').all()
        customer=Customer.objects.using('local_ecomm').all()
        return render_to_response("reports/pickup_report.html",
                                  {'sc':sc,'customer':customer},
                               context_instance=RequestContext(request))
  else:
     date_uploading_from = request.POST['date_uploading_from']
     date_uploading_to = request.POST['date_uploading_to']
     cust_id = request.POST['cust_id']
     origin = request.POST['sc']

     file_name = pickup_report(date_uploading_from, date_uploading_to, cust_id, origin)
   #  file_name = pickup_report(None, None, None, None)
     return HttpResponseRedirect("/static/uploads/reports/%s"%(file_name))



def overage_reports(request):
  if request.method != 'POST':
        sc = ServiceCenter.objects.all()
        return render_to_response("reports/overage_report.html",
                                  {'sc':sc},
                               context_instance=RequestContext(request))
  else:
     date_uploading_from = request.POST['date_uploading_from']
     date_uploading_to = request.POST['date_uploading_to']
     current_sc = request.POST['sc']
     e = EmployeeMaster.objects.get(user = request.user)
     file_name = generate_overage_report(date_uploading_from, date_uploading_to,current_sc)
     return HttpResponseRedirect("/static/uploads/reports/%s"%(file_name))

def shortage_reports(request):
  if request.method != 'POST':
        sc = ServiceCenter.objects.all()
        return render_to_response("reports/shortage_report.html",
                                  {'sc':sc},
                               context_instance=RequestContext(request))
  else:
     date_uploading_from = request.POST['date_uploading_from']
     date_uploading_to = request.POST['date_uploading_to']
     current_sc = request.POST['sc']
     #return HttpResponse(destination)
     #e = EmployeeMaster.objects.get(user = request.user)
     file_name = generate_shortage_report(date_uploading_from, date_uploading_to,current_sc)
     #return HttpResponse("/static/uploads/reports/%s"%(file_name))
     return HttpResponseRedirect("/static/uploads/reports/%s"%(file_name))

def trf_invice_report(request):
    if request.method != 'POST':
        return render_to_response("reports/trf_invoice_report.html",
                               context_instance=RequestContext(request))
    else:
        year= request.POST['Year']
        month = request.POST['Month']
        report_list = generate_invoicetrfreport(year, month)
        data = {'report_list':report_list}
        return render_to_response(
            "reports/trf_invoice_report.html",
            data,
            context_instance=RequestContext(request)
        )

@csrf_exempt
def checked(request):
    if request.method == 'POST': 
        r_id = request.POST.getlist('r_id[]')
        
        bill = Billing.objects.get(id=r_id[0])
        invoice = InvoiceXmlReport(bill.billing_date.year,bill.billing_date.month)
        path = invoice.create_invoice_xml_for_customers(r_id)
        data = {'path':path}
        json = simplejson.dumps(data)
        return HttpResponse(json, mimetype='applicatioan/json')

def daily_cash_tally_report(request):
    if request.method == 'GET':
        sc_list = ServiceCenter.objects.all()
        return render_to_response(
            "reports/daily_cash_tally_report.html",
            {'sc_list': sc_list},
            context_instance=RequestContext(request)
        )
    else:
        date_from = request.POST.get('date_from')
        date_to = request.POST.get('date_to')
        sc = request.POST.get('sc')
        #file_name = scwise_daily_cash_tally_report(date_from, date_to, sc)
        report = CodCollectionPodReport(date_from, date_to)
        file_name = report.daily_cash_tally_report(date_from, date_to, sc)
        return HttpResponseRedirect("/static/uploads/reports/{0}".format(file_name))


@csrf_exempt
def west_bengal_report(request):
  if request.method == 'POST':
    date_from = request.POST.get('date_from')
    if request.POST.get('date_to'):
       date_to=request.POST.get('date_to')
    else:
       date_to=now.strftime("%Y-%m-%d")
    customer=request.POST['sc']
    tmp=date_from + date_to + customer
    reports= generate_wbtax_report(date_from,date_to,customer)
    return HttpResponseRedirect("/static/uploads/reports/{0}".format(reports))
    
  else:
     customer=Customer.objects.using('local_ecomm').all() 
     return render_to_response("reports/west-bengal.html",
                               {'customer':customer},
                           context_instance=RequestContext(request))



#@csrf_exempt
def status_report(date_from,date_to,customer):
   #return "hi"
   from delivery.models import *
   if 1==1:
   #if request.method == 'POST' :
      #date_from = request.POST['date_from']
      #date_to = request.POST['date_to']
      #customer = request.POST['customer']
      if customer == "0" or customer == 0:
         shipper = None
      else:
         shipper = Customer.objects.get(id=customer)
      if shipper:
         ships = Shipment.objects.filter(added_on__range=(date_from,date_to),shipper=shipper)
      else:
         ships = Shipment.objects.filter(added_on__range=(date_from,date_to))
      data=[]
      for s in ships:
          awb=s.airwaybill_number
          upd_time = s.added_on
          monthdir = upd_time.strftime("%Y_%m")
          shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
          hist=shipment_history.objects.filter(shipment=s)
          if hist:
             origin = hist[0].current_sc
             uptime = hist[0].updated_on.strftime("%d-%m-%Y %H:%M") 
          else:
             origin = ""
             uptime = ""
          dest = s.original_dest
          redirect_dest = s.service_centre
          bg_data = s.shipment_data.filter()
          for b in bg_data:
             added_on = b.added_on.strftime("%Y_%m")
             bag_history = models.get_model('delivery', 'BaggingHistory_%s'%(added_on)) 
             if bag_history:
                bh =bag_history.objects.filter(bag=b,status =2 )
                if bh:
                   cl_time = bh[0].updated_on.strftime("%d-%m-%Y %H:%M")
                   break
                else:
                   cl_time = ""
             else:
                   cl_time = "" 
          for b in bg_data:   
              added_on = b.added_on.strftime("%Y_%m")
              bag_history = models.get_model('delivery', 'BaggingHistory_%s'%(added_on)) 
              if bag_history:
                 bh =bag_history.objects.filter(bag=b,status =2 ) 
                 if bh:
                    cn_sc = bh[0].updated_on.strftime("%d-%m-%Y %H:%M")
                    break
                 else:
                     cn_sc = ""
              else:
                   cn_sc=''
          for b in bg_data:
              added_on = b.added_on.strftime("%Y_%m")
              bag_history = models.get_model('delivery', 'BaggingHistory_%s'%(added_on)) 
              if bag_history:
                 bh =bag_history.objects.filter(bag=b,status =3 ) 
                 if bh:
                    in_hub=bh[0].updated_on.strftime("%d-%m-%Y %H:%M")
                    break
                 else:
                    hist=shipment_history.objects.filter(shipment=s,status=6)
                    if hist:
                      in_hub=hist[0].updated_on.strftime("%d-%m-%Y %H:%M")
                    else:
                      in_hub="" 
              else:
                    in_hub=""
          for b in reversed(bg_data) :
              added_on = b.added_on.strftime("%Y_%m")
              bag_history = models.get_model('delivery', 'BaggingHistory_%s'%(added_on))
              if bag_history:
                 bh =bag_history.objects.filter(bag=b,status =7 )
                 if bh:
                    lt_sc= bh[0].bag_sc
                    lt_time=bh[0].updated_on.strftime("%d-%m-%Y %H:%M")
                    break
                 else:
                   lt_sc=''
                   lt_time = '' 
              else:
                  lt_sc=''
                  lt_time=''
          for b in bg_data:
              added_on = b.added_on.strftime("%Y_%m")
              bag_history = models.get_model('delivery', 'BaggingHistory_%s'%(added_on))
              if bag_history:
                 bh =bag_history.objects.filter(bag=b,status =6)
                 if bh:
                    lt1_sc = bh[0].bag_sc
                    lt1_time = bh[0].updated_on.strftime("%d-%m-%Y %H:%M")
                    break
                 else:
                    lt1_sc=''
                    lt1_time  = ''
              else:
                    lt1_sc=''
                    lt1_time  = ''
          for b in reversed(bg_data) :
              added_on = b.added_on.strftime("%Y_%m") 
              bag_history = models.get_model('delivery', 'BaggingHistory_%s'%(added_on))
              if bag_history:
                  bh =bag_history.objects.filter(bag=b,status = 10)
                  if bh:
                     bl_sc=bh[0].bag_sc
                     bl_time=bh[0].updated_on.strftime("%d-%m-%Y %H:%M")
                     break
                  else:
                     bl_sc=''
                     bl_time = ''
              else:
                  bl_sc=''
                  bl_time = ''
          hist=shipment_history.objects.filter(shipment=s,status=7)
          if hist:
            ofd=hist[0].updated_on.strftime("%d-%m-%Y %H:%M")
          else:
            ofd=''
          hist=shipment_history.objects.filter(shipment=s,status=9)
          if hist:
             deli=hist[0].updated_on.strftime("%d-%m-%Y %H:%M")
          else:
             deli='' 
          u=(awb,origin,uptime,dest,redirect_dest,s.rts_status,s.shipper,cl_time,cn_sc,in_hub,lt_sc,lt_time,lt1_sc,lt1_time,bl_sc,bl_time,ofd,deli)
  
          data.append(u)
      now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
      report = ReportGenerator('status_report_{0}.xlsx'.format(now))
      header=("AWB","origin","added on","original dest","redirect dest","rts status","shipper","bag 1st close time","1st time connected at sc","1st inscan at hub","1st conn at hub","last hub inscan","last hub inscan loc","last hub conn","last hub conn","last inscan at dc","first outscan","delivered")
      report.write_header(header)
      path = report.write_body(data)
      url="http://billing.ecomexpress.in/static/uploads/reports/{0}".format(path)
      return HttpResponse(url)
   else:
      customer=Customer.objects.using('local_ecomm').filter(activation_status=True)
      return render_to_response("reports/status_update.html",
                                {'customer':customer},
                                context_instance=RequestContext(request))

def daywise_report(request):
    if request.POST:
         report_type = request.POST['dl_report']
         report_no =int(request.POST['report_id'])
         month_no = int(request.POST['month_id'])
 
         filename = get_daywise_charge_report(month_no,report_no)
         return HttpResponseRedirect('/static/uploads/reports/{0}'.format(filename))
    return render_to_response("reports/daywise-reports.html",
                              context_instance=RequestContext(request))
'''
