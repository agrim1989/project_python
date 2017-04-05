# Create your views here.
import traceback
import json
from utils import history_update
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.db.models import *
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from jsonview.decorators import json_view

from service_centre.models import *
from collections import defaultdict
from xlsxwriter.workbook import Workbook
from delivery.models import update_bag_history, remove_shipment_from_bag
from hub.models import Bag_shipment_table
from octroi.models import  *

now = datetime.datetime.now()
monthdir = now.strftime("%Y_%m")
before = now - datetime.timedelta(days=10)
beforem = now - datetime.timedelta(days=30)


def dash_board_bag(request, pid=0):
  runcode = RunCode.objects.get(id=pid)
  bags = runcode.connection.all()[0].bags.all()
  return render_to_response("hub/hub_bag.html",{'bags':bags},
                               context_instance=RequestContext(request))

def dash_board(request):
  enddate = datetime.datetime.today()
  startdate = enddate + datetime.timedelta(days=-30)
  runcode = RunCode.objects.filter(added_on__range=[startdate, enddate]).order_by('-added_on')
  runcode = RunCode.objects.all().order_by('-added_on')[:1000]
  runcode = RunCode.objects.all()[:1000]
  bag_count ={}
  airport ={}
  for run  in runcode:
    air = AirportConfirmation.objects.filter(run_code__id=run.id)
    if air:
      airport[run.id] = run.airportconfirmation_set.all().latest('date').date
    else:
      airport[run.id] =''
    if run.connection:
        conn = run.connection.all()
        if conn:
            bag_count[run.id] = conn[0].bags.all().count()
  return render_to_response("hub/hub_dashboard.html",{"runcode":runcode,"bag_count":bag_count,'airport':airport},
                               context_instance=RequestContext(request))


@csrf_exempt
def inscan_bag(request):
    beforeb = now - datetime.timedelta(days=4)
    if request.POST:
        bag_number=request.POST['bag_id']
        bag_count = mismatch_count = 0
        try:
            bag=Bags.objects.get(bag_number=bag_number, bag_status__in=[1, 2, 3, 6, 7, 8])
        except Bags.DoesNotExist:
            return HttpResponse("Does Not Exists")
        if (bag.destination != request.user.employeemaster.service_centre) and \
                (bag.hub != request.user.employeemaster.service_centre):
            status_type=3
        else:
            status_type=1

       #conn = bag.connection_set.all()
       #connection = Connection.objects.get(id=conn[0].id)
        connection = bag.connection_set.all()
        if connection: connection = connection[0]
        else: connection = None

        Bags.objects.filter(bag_number=bag_number).update(
            bag_status=3, status_type=status_type, updated_on=now,
            current_sc=request.user.employeemaster.service_centre)
        bag=Bags.objects.get(bag_number=bag_number)
        update_bag_history(
            bag, employee=request.user.employeemaster, action="scanned at Hub",
            content_object=bag, sc=request.user.employeemaster.service_centre,
            status=15)

        ships = bag.shipments.exclude(status__in=[7,8,9]).exclude(
      	    reason_code__code__in=[333, 888, 999]).exclude(rts_status=2)

        for ship in ships:
            history_update(ship, 50, request, "Bag ({0}) scanned at Hub".format(bag_number))
        return render_to_response(
            "hub/inscan_bag_data.html",
            {"bag":bag, "connection":connection, 'sucess_bags':"", 'mismatch_bags':""})
    else:
        if request.user.employeemaster.user_type == "Staff" or "Supervisor" or "Sr Supervisor":
              sucess_bags = Bags.objects.using('local_ecomm').filter(
                  bag_status=3, status_type=2, bag_type="mixed",
                  origin=request.user.employeemaster.service_centre)
              mismatch_bags = Bags.objects.using('local_ecomm').filter(
                  bag_status=3, status_type=1,
                  origin=request.user.employeemaster.service_centre)
        else:
              sucess_bags = Bags.objects.using('local_ecomm').filter(bag_status=3, status_type=2, bag_type="mixed")
              mismatch_bags = Bags.objects.using('local_ecomm').filter(bag_status=3, status_type=1)

        # bags to show in bag report area
        scanned_bags = Bags.objects.using('local_ecomm').filter(
            hub=request.user.employeemaster.service_centre,
            added_on__gte=beforeb, bag_status=3).annotate(
            num_shipments=Count('shipments')).filter(num_shipments__gt=0).order_by('-id')[:1000]

        # connections to show in connection area
        conn = Connection.objects.using('local_ecomm').filter(
            destination_id=request.user.employeemaster.service_centre, added_on__gte=before,
            connection_status__in=[1,4]
        ).annotate(num_bags=Count('bags')).filter(num_bags__gt=0)
        pending_bags = {}
        conn_bags = {}
        totalweight = {}
#        elapsed_days ={} 
        for cid in conn:
            c = Connection.objects.using('local_ecomm').filter(id=cid.id).annotate(
                ship_count=Count('bags__shipments'),total_weight=Sum('bags__actual_weight')).filter(ship_count__gt=0)
            pb = Connection.objects.using('local_ecomm').filter(id=cid.id,bags__bag_status__gte=8).annotate(
                pending=Count('bags')).filter(pending__gt=0)
            
#	    elapsed_days = (curr_date - cid.added_on.date()).days
	    if c:
              conn_bags[c[0]]=c[0].ship_count
              totalweight[c[0]]=c[0].total_weight
            if pb:
              pending_bags[pb[0]]=pb[0].pending

        return render_to_response(
            "hub/inscan_bag.html",
            {"bags":scanned_bags, "connection":conn, "conn_bags":conn_bags,"totalweight":totalweight,"pending_bags":pending_bags},
            context_instance=RequestContext(request))

def bag_tallied(request):
    bags = Bags.objects.filter(
        (Q(hub = request.user.employeemaster.service_centre) |
         Q(destination = request.user.employeemaster.service_centre)) &
         Q(bag_status=3)).filter(added_on__range=(beforem,now)).exclude(status_type=3)
    for a in bags:
        if a.status_type==1:
            if a.shipments.count():
                a.bag_status=3
                a.status_type=2
            else:
               a.bag_status=9
        else:
              a.bag_status=3
              a.status_type=2
        a.save()
    bagsf = Bags.objects.annotate(num_shipments=Count('shipments'))\
        .filter(hub=request.user.employeemaster.service_centre,
                added_on__range=(before,now), bag_status=3,
                num_shipments__gt=0).order_by('-id')
    return render_to_response(
        "hub/bag_tallied.html", {"bags":bagsf},
        context_instance=RequestContext(request))

def connection_tallied(request):
    connections = Connection.objects.filter(
        destination=request.user.employeemaster.service_centre,
        added_on__gte=before, connection_status__in=[1,4]).only('id')
    conn_bags = {}
    for conn in connections:
        bags = conn.bags.filter(bag_status=8).exclude(status_type=3)
        # update shortage bag's status type
        bags.annotate(num_shipments=Count('shipments'))\
            .filter(num_shipments__gt=0).update(status_type=2)
        # close bags if all shipments debagged
        bags.annotate(num_shipments=Count('shipments'))\
            .filter(status_type=1, num_shipments=0).update(bag_status=10)
        unscaned_bags = conn.bags.filter(bag_status__in=[2,3,7])\
            .exclude(status_type=3).values_list('bag_number', flat=True)
        if unscaned_bags:
            conn_bags[conn.id] = ', '.join(unscaned_bags)
    return render_to_response(
        "hub/connection_tallied.html", {"conn_bags":conn_bags},
        context_instance=RequestContext(request))

@csrf_exempt
def inscan_shipment(request):
    if request.POST:
       bag_num=request.POST['bag_num']

       awb_num=request.POST['awb_num']
       try:
           bags = Bags.objects.get(bag_number=bag_num)
       except Bags.DoesNotExist:
          return HttpResponse("Invalid Bag")

      # shipment = Shipment.objects.get(airwaybill_number=int(awb_num), status=3)
      # shipment.status=4
     #  if bags.shipments.count() == 0:
     #      bags.bag_status=9
     #      bags.save()
       try:
          shipment = Shipment.objects.get(airwaybill_number=int(awb_num))
       except Shipment.DoesNotExist:
          return HttpResponse("Invalid Shipment")
       if shipment.rts_status == 2:
               return HttpResponse("Shipment RTS'd")
       if (shipment.status in [7,9]):
                return HttpResponse("Shipment at Outscan/Delivered, cannot be inscanned!!")
       if shipment.reason_code:
            if shipment.reason_code.code in [333, 888, 999,777,111]:
                return HttpResponse("Shipment Closed")
       #original_bag_number = shipment.bags_set.filter().latest('added_on') if shipment.bags_set.filter() else None
       original_bag_number = shipment.shipment_data.filter().latest('added_on') if shipment.shipment_data.filter() else None
       bag_ships = Bag_shipment_table.objects.filter(airwaybill_number=awb_num)
       if bag_ships:
           bag_ship = bag_ships[0]
           bag_ship.scanned_bag_number=bag_num
           bag_ship.original_bag_number = original_bag_number
           #bag_ship.current_sc = shipment.pickup.service_centre
           bag_ship.current_sc = request.user.employeemaster.service_centre
           bag_ship.save()
       else:
           Bag_shipment_table.objects.create(airwaybill_number=awb_num,scanned_bag_number=bag_num,
                       original_bag_number = original_bag_number, current_sc = request.user.employeemaster.service_centre)
       bags = shipment.bags_set.all()
       bag_num = ""
       if bags:
           bags = bags[0]
           bag_num = bags.bag_number if bags.bag_number else bags.id
       service_center=request.user.employeemaster.service_centre
       shipment.current_sc = service_center
       history_update(shipment, 4, request, remarks="Debag Shipment at Hub from Bag Number %s"%(bag_num))
       status_type = 0
       if not (shipment.status_type == 1 and shipment.status == 4):
         shipment.status_type=0
         if shipment.airwaybill_number=="" or shipment.order_number=="" or shipment.shipper=="" \
             or shipment.destination_city=="" or shipment.pincode=="" or shipment.collectable_value =="" or shipment.actual_weight =="":
             status_type= 4
         elif shipment.status <> 3:
             status_type=5
         else:
             status_type= 1
         if not bags:
            if shipment.status <> 4:
                  status_type = 5
         shipment.status=4
         shipment.updated_on=now
         shipment.status_type=status_type
       shipment.save()

       if status_type == 1 and bags.bag_status in [2,7]:
            Bags.objects.filter(pk=bags.id).update(bag_status=3)

       if not ((shipment.status_type == 5)):
         if (shipment.status_type == 1 and shipment.status == 4):
            if bags:
               bags.shipments.remove(shipment)
               if bags.shipments.count() == 0:
                  bags.bag_status=9
                  bags.save()
                  update_bag_history(bags, employee=request.user.employeemaster, action="debagged at hub",
                    content_object=bags, sc=request.user.employeemaster.service_centre, status=18)

       total_records = bags.ship_data.using('local_ecomm').count()
       mismatch_count = bags.shipments.using('local_ecomm').count()
       success_count = total_records - mismatch_count
       return render_to_response("service_centre/shipment_data.html",
                                  {'a':shipment,
                                   'status':"2",
                                   'total_records':total_records,
                                   'sucess_count':success_count,
                                   'mismatch_count':mismatch_count
              })
       return HttpResponse("Sucess")
    else:
      if request.user.employeemaster.user_type == "Staff" or "Supervisor" or "Sr Supervisor":
          shipment=Shipment.objects.using('local_ecomm').filter(status=4, current_sc=request.user.employeemaster.service_centre).exclude(status_type=0)
          total_records = Shipment.objects.using('local_ecomm').filter(status=4, current_sc=request.user.employeemaster.service_centre).count()
          success_count = Shipment.objects.using('local_ecomm').filter(status_type=1, current_sc=request.user.employeemaster.service_centre, status=4).count()
          mismatch_count = Shipment.objects.using('local_ecomm').filter(status=4, current_sc=request.user.employeemaster.service_centre, status_type= 4).count()
      else:
          shipment=Shipment.objects.using('local_ecomm').filter(status=4).exclude(status_type=0)
          total_records = Shipment.objects.using('local_ecomm').filter(status=4).count()
          success_count = Shipment.objects.using('local_ecomm').filter(status_type=1, status=4).count()
          mismatch_count = Shipment.objects.using('local_ecomm').filter(status=4, status_type= 4).count()

      return render_to_response("hub/inscan_shipment.html",
                                {'shipment':"",
                                 'total_records':total_records,
                                 'success_count':success_count,
                                 'mismatch_count':mismatch_count},
                               context_instance=RequestContext(request))


@csrf_exempt
def inscan_shipment_bkup(request):
    if request.POST:
    #   bag_num=request.POST['bag_num']
       awb_num=request.POST['awb_num']

     #  bags = Bags.objects.get(bag_number=bag_num)
     #  if bags.shipments.count() == 0:
     #      bags.bag_status=9
     #      bags.save()
       shipment = Shipment.objects.get(airwaybill_number=int(awb_num))
       if shipment.rts_status == 2:
               return HttpResponse("Shipment RTS'd")
       if (shipment.status in [7,9]):
                return HttpResponse("Shipment at Outscan/Delivered, cannot be inscanned!!")
       if shipment.reason_code:
            if shipment.reason_code.code in [333, 888, 999]:
                return HttpResponse("Shipment Closed")
    #   shipment = bags.shipments.get(id=ship.id)

       bags = shipment.bags_set.all()
       bag_num = ""
       if bags:
           bags = bags[0]
           bag_num = bags.bag_number if bags.bag_number else bags.id
       service_center=request.user.employeemaster.service_centre
       shipment.current_sc = service_center
       history_update(shipment, 4, request, remarks="Debag Shipment at Hub from Bag Number %s"%(bag_num))
      # try:
       #        upd_time = shipment.added_on
       #        monthdir = upd_time.strftime("%Y_%m")
        #       shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
        #       shipment_history.objects.create(shipment=shipment, status=4, employee_code = request.user.employeemaster, current_sc = request.user.employeemaster.service_centre, expected_dod=shipment.expected_dod, remarks="Debag Shipment at Hub from Bag Number %s"%(bag_num))
      # except:
       # pass
       if not (shipment.status_type == 1 and shipment.status == 4):
         shipment.status_type=0
         if shipment.airwaybill_number=="" or shipment.order_number=="" or shipment.shipper=="" or shipment.destination_city=="" or shipment.pincode=="" or shipment.collectable_value =="" or shipment.actual_weight =="":
          shipment.status_type= 4
         elif shipment.status <> 3:
          shipment.status_type=5
         else:
          shipment.status_type= 1
         if not bags:
            if shipment.status <> 4:
                  shipment.status_type = 5
         shipment.status=4
         shipment.updated_on=now
       shipment.save()
       if not ((shipment.status_type == 5)):
         if (shipment.status_type == 1 and shipment.status == 4):
            if bags:
               bags.shipments.remove(shipment)
               if bags.shipments.count() == 0:
                  bags.bag_status=9
                  bags.save()
                  update_bag_history(bags, employee=request.user.employeemaster, action="debagged at hub",
                    content_object=bags, sc=request.user.employeemaster.service_centre, status=17)

  #     bags.shipments.remove(shipment)

     #  total_records = Shipment.objects.filter(status__in=[3,4], current_sc=request.user.employeemaster.service_centre).count()
     #  success_count = Shipment.objects.filter(status=4, current_sc=request.user.employeemaster.service_centre, status_type=1).count()

     #  mismatch_count = Shipment.objects.filter(status=4, current_sc=request.user.employeemaster.service_centre, status_type__in=[2,3,4,5]).count()
       total_records = ""
       success_count = ""
       mismatch_count = ""
       return render_to_response("service_centre/shipment_data.html",
                                  {'a':shipment,
                                   'status':"2",
                                   'total_records':total_records,
                                   'sucess_count':success_count,
                                   'mismatch_count':mismatch_count
              })
       return HttpResponse("Sucess")
    else:
      if request.user.employeemaster.user_type == "Staff" or "Supervisor" or "Sr Supervisor":
          shipment=Shipment.objects.using('local_ecomm').filter(status=4, current_sc=request.user.employeemaster.service_centre).exclude(status_type=0)
          total_records = Shipment.objects.using('local_ecomm').filter(status=4, current_sc=request.user.employeemaster.service_centre).count()
          success_count = Shipment.objects.using('local_ecomm').filter(status_type=1, current_sc=request.user.employeemaster.service_centre, status=4).count()
          mismatch_count = Shipment.objects.using('local_ecomm').filter(status=4, current_sc=request.user.employeemaster.service_centre, status_type= 4).count()
      else:
          shipment=Shipment.objects.using('local_ecomm').filter(status=4).exclude(status_type=0)
          total_records = Shipment.objects.using('local_ecomm').filter(status=4).count()
          success_count = Shipment.objects.using('local_ecomm').filter(status_type=1, status=4).count()
          mismatch_count = Shipment.objects.using('local_ecomm').filter(status=4, status_type= 4).count()

      return render_to_response("hub/inscan_shipment.html",
                                {'shipment':"",
                                 'total_records':total_records,
                                 'success_count':success_count,
                                 'mismatch_count':mismatch_count},
                               context_instance=RequestContext(request))

def bagging(request):
    if request.user.employeemaster.user_type == "Staff" or "Supervisor" or "Sr Supervisor":
        bags = Bags.objects.filter(
            added_on__gte=beforem, bag_status__in=[5,6],
            origin=request.user.employeemaster.service_centre
        ).order_by("-id")
    else:
        bags = Bags.objects.filter(added_on__gte=beforem, bag_status__in=[5,6]).order_by("-id")

    service_centre = ServiceCenter.objects.all()
    return render_to_response(
        "hub/bagging.html",
        {'bags':bags, 'service_centre':service_centre,
            'origin_sc':request.user.employeemaster.service_centre},
        context_instance=RequestContext(request))


@json_view
@csrf_exempt
def add_bagging(request):
    bag_type = request.POST['bag_type']
    bag_size = request.POST['bag_size']
    bag_number = request.POST['bag_num']
    hub = request.POST['hub']
    destination = request.POST['dest']

    if Bags.objects.filter(bag_number=bag_number).exists():
        return {'success': False, 'message': 'Bag number already exists'}

    origin = request.user.employeemaster.service_centre

    if int(hub):
        hub = ServiceCenter.objects.get(id=int(hub))
    else:
        hub = None

    if int(destination):
        destination = ServiceCenter.objects.get(id=int(destination))
    else:
        destination = None

    bag = Bags.objects.create(
        bag_number=bag_number, bag_type=bag_type, bag_size=bag_size,
        bag_status=5, origin=origin, hub=hub, destination=destination,
        current_sc=origin)

    update_bag_history(
        bag, employee=request.user.employeemaster, action="created",
        content_object=bag, sc=request.user.employeemaster.service_centre,
        status=1)

    html = render_to_string(
        "hub/bag_data.html", {'a':bag},
        context_instance=RequestContext(request))

    return {'success': True, 'html': html}


def ship_updation(request, reason_code, remark, status, ship, q=0):
  for shipment in ship:
    if shipment.status == 9:
       return "Shipment Already Delivered"
    #if shipment.status == 7:
       #if shipment.deliveryoutscan_set.all():
           #os = shipment.deliveryoutscan_set.latest('added_on')
           #os.shipments.remove(shipment)
           #shipment.doshipment_set.filter(deliveryoutscan=os).update(status=2)
    if reason_code.code in [304, 305, 306, 307, 308, 309]:
       ShipmentExtension.objects.filter(shipment=shipment).update(delay_code=reason_code)
    shipment.reason_code=reason_code
    if reason_code.code in [201,213,222,215,216,226,228,229,311]:
        shipment.status = 6
        shipment.status_type=0
        shipment.return_shipment = 0
        shipment.current_sc = request.user.employeemaster.service_centre
    if reason_code.code == 305:
        shipment.status = 4
        shipment.status_type = 1

    shipment.save()
    if not remark:
        remark = "Mass Updated"
    history_update(shipment, 40, request, remark, reason_code)
  return True

def mass_updation(request, rtype=0):
    q = Q()
    t = None
    emp_code = ['26388','12048','12404','12830','13072','13111','13543','13978    ','14019','13730','13977','14668','14669','15610','14968','15376','16416','14770']
    if rtype == "1":
       rsp = "delivery/mass_updation.html"
#       emp = EmployeeMaster.objects.filter(email__in  ['balappamk@ecomexpress.in','prabuck@ecomexpress.in','premananda@ecomexpress.in','santhoshk@ecomexpress.in','lokeshb@ecomexpress.in','sridhar@ecomexpress.in','manikandan@ecomexpress.in','ponnurangam@ecomexpress.in','gopicr@ecomexpress.in','sathishb@ecomexpress.in','fredrick@ecomexpress.in','thirumavalavan@ecomexpress.in','shankaramoorthy@ecomexpress.in','shaik.rafeeq@ecomexpress.in','vikraml@ecomexpress.in','ramakrishna@ecomexpress.in','syed.karim@ecomexpress.in','freeman@prtouch.com'])
 #      if emp == '':
       q = q & Q(code__in=[201,213,222,215,216,226,228,229,305,310])
          # status = 5
  #     else:
   #        q = q & Q(code__in=[201,213,222,215,216,226,228,229,305,310,332])
          # status = 5
       status = 5 
    else:
       rsp = "hub/mass_updation.html"
       status = 4
    if request.POST:
      remark = request.POST['remark']
      reason_code = request.POST['reason_code']
      reason_code = ShipmentStatusMaster.objects.get(id=int(reason_code))
      rc=request.POST['rc']
      rc_split = rc.split('\r\n')
      bag=request.POST['bag']
      b = bag.split('\r\n')
      awb=request.POST['awb']
      awbs = awb.split('\r\n')
      airwaybills = [int(a) for a in awbs if a]
      error_dict = defaultdict(list)

      if airwaybills:
          for awb in airwaybills:
              shipment = Shipment.objects.filter(airwaybill_number=awb)\
                  .exclude(status=9)\
                  .exclude(reason_code__code__in=[333, 888, 999,777,111])\
                  .exclude(rts_status=2)
              if not shipment:
                  error_dict[awb].append("Shipment already closed")
                  continue
              if shipment.filter(status = 7):
                  error_dict[awb].append("Shipment at outscan stage cannot be updated")
                  continue
              if status == 5 and not shipment.filter(status = 6):
                  error_dict[awb].append("Shipment not at DC cannot be updated")
                  continue
              if status == 5 and shipment[0].current_sc != request.user.employeemaster.service_centre:
                  error_dict[awb].append("Shipment not at DC cannot be updated")
                  continue
              if reason_code.code == 305:
                  remove_shipment_from_bag(awb)
              ship_updation(request, reason_code, remark, status, shipment, 1)
      if b:
          for bag in b:
            if bag:
              bag = Bags.objects.get(bag_number=bag)
              ship_updation(
                  request, reason_code, remark, status,
                  bag.shipments.all().exclude(
                      status=9).exclude(
                      reason_code__code__in=[333, 888, 999, 111]).exclude(
                      rts_status=2), 
                  0
              )
              update_bag_history(
                  bag, employee=request.user.employeemaster,
                  action="mass updated", content_object = bag,
                  sc=request.user.employeemaster.service_centre, 
                  reason_code=reason_code, status=16)

      # this is to be removed since we are no longer using runcode
      if rc:
        runcode = RunCode.objects.filter(id__in = rc_split).values_list('connection')
        conn_rc = Connection.objects.filter(id__in = runcode)
        for conn in conn_rc:
           if conn:
              connection = Connection.objects.get(id=conn.id)
              for bag in connection.bags.all():
                  if bag:
                     bag = Bags.objects.get(id=bag.id)
                     ship_updation(request, reason_code, remark, status, bag.shipments.filter().exclude(status=9).exclude(reason_code__code__in = [333, 888, 999,777,111]).exclude(rts_status = 2),0)
                     update_bag_history(bag, employee=request.user.employeemaster,
                        action="mass updated",content_object = bag,
                        sc=request.user.employeemaster.service_centre, reason_code = reason_code)

      reason_code = ShipmentStatusMaster.objects.filter(q)
      return render_to_response(
            rsp, {'reason_code':reason_code, 'msg':None, 'errors': error_dict,'emp_code':emp_code},
            context_instance=RequestContext(request))
    else:
        reason_code = ShipmentStatusMaster.objects.filter(q).exclude(code__in=[999,777])
        return render_to_response(
            rsp, {'reason_code':reason_code,'emp_code':emp_code},
            context_instance=RequestContext(request))

@csrf_exempt
def connection(request):
#    total_weight = ''
#    pending_bags = ''
    before1 = now - datetime.timedelta(days=3)
    if request.POST:
        destination=request.POST['dest']
        destination=ServiceCenter.objects.get(id=int(destination))
        vehicle_num=request.POST['vehicle']
        coloader=request.POST['coloader']
        coloader=Coloader.objects.get(id=int(coloader))
        origin_sc = request.POST['origin_sc']
        origin=ServiceCenter.objects.get(id=int(origin_sc))
        connection = Connection.objects.create(
            coloader=coloader, destination=destination,
            vehicle_number=vehicle_num, connection_status=3, origin=origin)
        return render_to_response(
            "service_centre/connection_data.html",
            {"a":connection}, context_instance=RequestContext(request))
    else:
        if request.user.employeemaster.user_type in ["Staff", "Supervisor", "Sr Supervisor"]:
            connection = Connection.objects.filter(
                connection_status__in=[2,3,4], added_on__range=(before1, now),
                origin=request.user.employeemaster.service_centre
            ).values_list('id','destination').aggregate(ch_wt=Sum('bags__actual_weight')).order_by("-id")
#            for co in connection:
 #               total_weight = co.bags.aggregate(Sum('actual_weight'))
  #              pending_bags = co.bags.filter(bag_status__gt=8).count()
        else:
            connection = Connection.objects.filter(
                connection_status__in=[2,3,4], added_on__range=(before1, now)
            ).order_by("-id")

        conn_bags ={}
        totalweight = {}
        pending_bags = {}
	curr_date = datetime.datetime.today().date()
#        elaspsed_days = {}
        for cid in connection:
            c = Connection.objects.using('local_ecomm').filter(id=cid.id).annotate(
                ship_count=Count('bags__shipments'),total_weight=Sum('bags__actual_weight')).filter(ship_count__gt=0)
            pb = Connection.objects.using('local_ecomm').filter(id=cid.id,bags__bag_status__gte=8).annotate(
                pending=Count('bags')).filter(pending__gt=0)
#            ed = Connection.objects.using('local_ecomm').filter(id=cid.id).values_list('added_on')
#	    elapsed_days = (curr_date - cid.added_on.date()).days
	    if c:
              conn_bags[c[0]]=c[0].ship_count
              totalweight[c[0]]=c[0].total_weight
            if pb:
              pending_bags[pb[0]]=pb[0].pending
#	    if ed:
#              elaspsed_days[ed[0]] = pb[0]


        coloader = Coloader.objects.all()
        service_centre = ServiceCenter.objects.all()
        
        return render_to_response(
            "hub/connection.html",
            {"connection":connection, 'coloader':coloader,
                'service_centre':service_centre,'origin_sc':request.user.employeemaster.service_centre,"conn_bags":conn_bags,"totalweight":totalweight,'pending_bags':pending_bags},
            context_instance=RequestContext(request))

@csrf_exempt
def octroi(request):
    if request.is_ajax() and request.method == 'POST':
        date = request.POST.get('oct_date')
        date = datetime.date.today() if not date else date
        oct_conns = OctroiConnection.objects.filter(status=0)
        for oc in oct_conns:
            if OctroiShipments.objects.filter(shipment=oc.shipment):
                OctroiConnection.objects.filter(id=oc.id).update(status=1)
        oct_conns = OctroiConnection.objects.filter(status=0)
        if not oct_conns:
            return HttpResponse("No shipments for Octroi")
        octroi = Octroi.objects.create(date=date, origin=request.user.employeemaster.service_centre)
        for oct_conn in oct_conns:
            OctroiShipments.objects.create(
                octroi=octroi, shipment=oct_conn.shipment,
                shipper=oct_conn.shipment.shipper, origin=oct_conn.origin)
            OctroiConnection.objects.filter(id=oct_conn.id).update(status=1, updated_on=now)
        return render_to_response("hub/octroi_data.html", {"a":octroi})
    else:
        if request.user.employeemaster.employee_code in ['10500','10612','11662']:
            octroi = Octroi.objects.filter().order_by('-id')
        else:
            octroi = Octroi.objects.filter(origin=request.user.employeemaster.service_centre).order_by('-id')
        shipper = Customer.objects.all()

    return render_to_response(
        "hub/octroi.html",
        {"octroi":octroi, 'shipper':shipper},
        context_instance=RequestContext(request)
    )

def octroi_summary(request, oid):
    octroi=Octroi.objects.get(id=oid)
    shipments = OctroiShipments.objects.filter(octroi=octroi)
    weight = shipments.aggregate(Sum('shipment__chargeable_weight'))
    weight = weight['shipment__chargeable_weight__sum']
    dec_value = shipments.aggregate(Sum('shipment__declared_value'))
    dec_value = dec_value['shipment__declared_value__sum']
   # bags = shipments.aggregate(Count('shipment__bags'))
   # bags = bags['shipment__bags__count']
    ls = []
    for a in shipments:
        if a.shipment.bags_set.filter(origin__center_shortcode__in=['bmr','boc','bok','bog','bow','bot','bov','bod']):
            ls.append(a.shipment.bags_set.filter()[0])
    bags = len(set(ls))
    text = render_to_string("hub/manifest_txt.html",
                                  {'bags':bags,
                                   'dec_value':dec_value,
                                   'weight':weight,
                                   'shipments':shipments},
                                   context_instance=RequestContext(request))
    response =  HttpResponse("%s"%text, content_type="text/plain", mimetype='text/plain')
    #response['Content-Disposition'] = 'attachment; filename=octroi_manifest.txt'
    return response

@csrf_exempt
def flat_update_octroi(request):
    if request.POST:
       shipment_list=[]
       oid=request.POST['oct_id']
       flat_rate=request.POST['flat_rate']
       octroi=Octroi.objects.get(id=oid)
       shipments = OctroiShipments.objects.filter(status=0,shipment__billing=None,octroi=octroi).order_by("status")[:100]
       for ship in shipments:
	  rate=CustomerOctroiCharges.objects.filter(customer=ship.shipper)
          if rate:
              oct_charge=rate[0].octroi_charge
          else:
              oct_charge=5
          octroi=float((ship.shipment.declared_value)*(float(flat_rate)))/100
          charge=float((octroi)*(float(oct_charge)))/100
          shipment_list.append([ship,flat_rate,oct_charge, octroi,charge,ship.status])
          #OctroiShipments.objects.filter(shipment__airwaybill_number=ship.shipment.airwaybill_number).update(status=1,octroi_charge=charge,octroi_ecom_charge=ecomm_charge)
       return render_to_response("hub/manisfest_txt_rates2.html",
                                {       'oct_id':oid,
                                        'shipments':shipment_list
                                },context_instance=RequestContext(request))
       #return HttpResponse("updated ")
    else :
        return HttpResponse("Unabel to process the request ")

@csrf_exempt
def octroi_reciept_edit(request,oid):
        octroi=Octroi.objects.get(id=oid)
        cust_list=[]
        shipments = OctroiShipments.objects.filter(octroi=octroi,shipment__original_dest__center_shortcode__in=['bmr','boc','bok','bog','bow','bot','bov','bod']).\
                     values('shipper__name','shipper__id').annotate(ship_count=Count('shipment'),
                     decl_sum=Sum('octroi_charge'),declared_value=Sum('shipment__declared_value'))
        #shipments=OctroiShipments.objects.filter(octroi=octroi,shipment__original_dest__center_shortcode__in=['bmr','boc','bok','bog','bow','bot','bov','bod'])
        #return HttpResponse(str(shipments.count()))
        return render_to_response("hub/reciept_details.html",


                                {       'shipments':shipments,
                                         'oct_id':oid,
                                },context_instance=RequestContext(request))



def octroi_summary_edit(request,oid):
    octroi=Octroi.objects.get(id=oid)
    shipments = OctroiShipments.objects.filter(octroi_billing=None,octroi=octroi,status=0).order_by("status")[:100]
    shipment_list = []
    for ship in shipments:
	rate=CustomerOctroiCharges.objects.filter(customer=ship.shipper)
	if rate:
	   oct_rate=rate[0].octroi_rate
           oct_charge=rate[0].octroi_charge
           octroi=float((ship.shipment.declared_value)*(rate[0].octroi_rate))/100
	   charge=float((octroi)*(rate[0].octroi_charge))/100
        else:
           oct_rate=5.5
           oct_charge=5
           octroi=float((ship.shipment.declared_value)*(oct_rate))/100
           charge=float((octroi)*(oct_charge))/100
        shipment_list.append([ship,oct_rate,oct_charge, octroi,charge,ship.status])
    return render_to_response("hub/manisfest_txt_rates.html",
				{	'oct_id':oid,
					'shipments':shipment_list
				},context_instance=RequestContext(request))

@csrf_exempt
def update_reciepts(request,oid):
    if request.POST:
        name={}
        #oct_id=request.POST['oct_id']
        if request.POST.getlist("shipper"):
           shipper_list=request.POST.getlist("shipper")
        else:
           shipper_list=[]
        for key,value in request.POST.iteritems():
            if "reciept" in key and value:
               cid=key.split('-')

               octroi_shipments = OctroiShipments.objects.filter(shipment__original_dest__center_shortcode__in=['bmr','boc','bok','bog','bow','bot','bov','bod'], octroi__id=oid,shipper__id=cid[1])
               for oct_s in octroi_shipments:
                   rate=CustomerOctroiCharges.objects.filter(customer=oct_s.shipper)
                   if rate:
                      oct_rate=rate[0].octroi_rate
                      oct_charge=rate[0].octroi_charge
                      octroi=round(float((oct_s.shipment.declared_value)*(rate[0].octroi_rate))/100,2)
                      charge=round(float((octroi)*(rate[0].octroi_charge))/100,2)
                   else:
                      oct_rate=5.5
                      oct_charge=5
                      octroi=round(float((oct_s.shipment.declared_value)*(oct_rate))/100,2)
                      charge=round(float((octroi)*(oct_charge))/100,2)

                   upd = OctroiShipments.objects.filter(id=oct_s.id).update(octroi_charge=octroi, octroi_ecom_charge=charge,status=1,receipt_number = value)


               shipments = OctroiShipments.objects.filter(shipment__original_dest__center_shortcode__in=['bmr','boc','bok','bog','bow','bot','bov','bod'],octroi__id=oid,shipper__id=cid[1]).\
                     values('shipper__name','shipper__id').annotate(ship_count=Count('shipment'),
                     decl_sum=Sum('octroi_charge'))
               total_value=float(shipments[0]['decl_sum'])
               number_ofshipments=int(shipments[0]['ship_count'])

               #return HttpResponse(int(cid[1]))
               oct_customer = OctroiCustomer.objects.filter(octroi__id = oid, customer__id = int(cid[1]))
               if not oct_customer:
                   tmp_octroi=Octroi.objects.get(id=oid)
                   tmp_customer=Customer.objects.get(id=cid[1])
                   oct_customer = OctroiCustomer.objects.create(octroi = tmp_octroi, customer = tmp_customer, reciept_number = value,number_ofshipments=number_ofshipments,octroi_paid=total_value )
               else:
                   oct_customer.update(reciept_number=value,number_ofshipments=number_ofshipments,octroi_paid=total_value)
               #shipments = OctroiShipments.objects.filter( octroi__id=oid,shipper__id=cid[1]).update(receipt_number = value)
        return HttpResponse("success")

@csrf_exempt
def update_octroi(request):
    if request.POST:
        awb = {}
        if request.POST.getlist("oct_update"): oct_update = request.POST.getlist("oct_update")
        else: oct_update = []
	for key, value in request.POST.iteritems():
	    if "rate" in key or "charge" in key:
		awb_name=key.split('-')
                if awb_name[1] not in oct_update:
                    if "update" in key:
		    	if not awb.get(int(awb_name[1])): awb[int(awb_name[1])] = {}
		    	awb[int(awb_name[1])]["update"] = float(value)
            	    if "rate" in key:
		    	if not awb.get(int(awb_name[1])): awb[int(awb_name[1])] = {}
		    	awb[int(awb_name[1])]["rate"] = float(value)
            	    if "charge" in key:
		    	if not awb.get(int(awb_name[1])): awb[int(awb_name[1])] = {}
		    	awb[int(awb_name[1])]["charge"] = float(value)
	for octroi_id, values in awb.iteritems():
           	OctroiShipments.objects.filter(id=octroi_id).update(status=1,octroi_charge=values['rate'],octroi_ecom_charge=values['charge'])

        return HttpResponse('Updated')

@csrf_exempt
def delink_shipment_oct(request, oid):
    octroi = Octroi.objects.get(id=oid)
    shipments = OctroiShipments.objects.filter(octroi=octroi)
    if request.POST:
       awb_number = request.POST['awb']
       try:
            OctroiShipments.objects.delete(shipment__airwaybill_number=awb_number, octroi=octroi)
            OctroiConnection.objects.filter(shipment__airwaybill_number=awb_number).update(status=0, updated_on=now)
       except:
            return HttpResponse("Incorrect Shipment Number")

       return render_to_response("hub/shipment_octroi_data.html",
                                  {'shipment':shipment,
                                   },
                                   context_instance=RequestContext(request))
    else:
        return render_to_response("hub/delink_shipment_oct.html",
                                  { 'oid':oid,
                                   'shipment':shipments},
                                   context_instance=RequestContext(request))

def octroi_summary(request, oid):
    octroi=Octroi.objects.get(id=oid)
    shipments = OctroiShipments.objects.filter(octroi=octroi)
    weight = shipments.aggregate(Sum('shipment__chargeable_weight'))
    weight = weight['shipment__chargeable_weight__sum']
    dec_value = shipments.aggregate(Sum('shipment__declared_value'))
    dec_value = dec_value['shipment__declared_value__sum']
   # bags = shipments.aggregate(Count('shipment__bags'))
   # bags = bags['shipment__bags__count']
    ls = []
    for a in shipments:
        if a.shipment.bags_set.filter():
            ls.append(a.shipment.bags_set.filter()[0])
    bags = len(set(ls))
    text = render_to_string("hub/manifest_txt.html",
                                  {'bags':bags,
                                   'dec_value':dec_value,
                                   'weight':weight,
                                   'shipments':shipments},
                                   context_instance=RequestContext(request))
    response =  HttpResponse("%s"%text, content_type="text/plain", mimetype='text/plain')
    response['Content-Disposition'] = 'attachment; filename=octroi_manifest.txt'
    return response



def octroi_manifest(request, oid, stat):
      #octroi=Octroi.objects.get(id=oid)
      if stat == '1':
         octroi=Octroi.objects.get(id=oid)
         shipments = OctroiShipments.objects.filter(octroi=octroi,shipment__original_dest__center_shortcode__in=['bmr','boc','bok','bog','bow','bot','bov','bod']).order_by('shipper','origin')
      elif stat == '2':
         nf=NForm.objects.get(id=oid)
         shipments = NFormShipments.objects.filter(nhform=nf).order_by('shipper','origin')
      #shipments = OctroiShipments.objects.filter(octroi=octroi).order_by('shipper','origin').values('shipment','shipper')
      ship = defaultdict(list)
      for a in shipments:
          ship[(a.shipper, a.origin)].append(a.shipment)
     	#   ship[a['shipper']].append(a['shipment'])

    # for k, v in ship.items():
      file_name = "/manifest_%s.xlsx"%(oid)
      path_to_save = settings.FILE_UPLOAD_TEMP_DIR+file_name
      workbook = Workbook(path_to_save)
      c = 0
      for k in ship:
          c = c +1
          sheet = workbook.add_worksheet()
          sheet.set_column('A:H', 16)
          sheet.set_row(0, 30)
          sheet.set_row(1, 20)
          sheet.set_row(2, 20)
          #sheet.set_row(6, 30)
          #worksheet.set_row(7, 30)
          #sheet.set_column(0, 3, 12)

          sheet.set_column(4, 5, 45)
         # sheet.set_column(5, 9, 12)
          nformat = workbook.add_format()
          nformat.set_border(style=2)
          bformat = workbook.add_format({
              'bold': 1,
                    })
          bformat.set_border(style=2)
          merge_format = workbook.add_format({
              #'bold': 1,
              'align': 'center',
              'valign': 'vcenter',
              'border':'border',
                         })
          merge_format.set_border(style=2)
          sheet.merge_range('A1:D1', 'From Ecom Express Pvt Ltd %s'%(k[1].address), merge_format)
#(0, 0, "From Ecom Express Pvt Ltd %s"k[1].address)
          sheet.merge_range('E1:G1', "To Ecom Express Pvt Ltd Gr, Flr., Plot No. 111/3, Marol Co-op Indl Estate,Marol, Andheri (E), Mumbai 400 059", merge_format)
          sheet.merge_range('A2:B2', "Manifest Number", bformat)
          sheet.merge_range('A3:B3', "Manifest Date", bformat)
          sheet.write(1, 2, str(oid)+str(c), nformat)
          sheet.write(2, 2, str(now.date()), nformat)
          sheet.write(1, 3, "Shipper Name", bformat)
          sheet.write(2, 3, "Origin Hub", bformat)
          sheet.write(1, 4, str(k[0].name), nformat)
          sheet.write(2, 4, str(k[1].center_name), nformat)
          sheet.write(1, 5, "Slip No.", bformat)
          #sheet.write(1, 6, "Amount", bformat)
          sheet.merge_range('F3:G3', "Date", bformat)
          sheet.write(3, 0, "Sr No.", bformat)
          sheet.write(3, 1, "Air Waybill No.", bformat)
          sheet.write(3, 2, "Order No.", bformat)
          sheet.write(3, 3, "Consignee Name", bformat)
          #sheet.write(3, 4, "Consignee Address", bformat)
          sheet.write(3, 4, "Product Description", bformat)
          sheet.write(3, 5, "Value", bformat)
          sheet.write(3, 6, "Bag Number", bformat)
          counter =1
          coll_val = 0
          for b in ship[k]:
                 coll_val = coll_val + b.declared_value
             # for b in v:
                 sheet.write(counter+3, 0, counter, nformat)
                 sheet.write(counter+3, 1, b.airwaybill_number, nformat)
                 sheet.write(counter+3, 2, b.order_number, nformat)
                 sheet.write(counter+3, 3, b.consignee, nformat)
#                 sheet.write(counter+3, 4, u'%s, %s, %s'%(b.consignee_address1, b.consignee_address2, b.consignee_address3), nformat)
                 sheet.write(counter+3, 4, b.item_description[0:10], nformat)
                 sheet.write(counter+3, 5, b.declared_value, nformat)
                 if b.shipment_data.all():
                     sheet.write(counter+3, 6, b.shipment_data.all()[0].bag_number, nformat)
                 counter = counter+1
          sheet.write(1, 6, "Amount: %s"%(coll_val), bformat)
     # sheet.write(0, 1, spid[0].pickedup_by.employee_code)
      workbook.close()
      return HttpResponseRedirect("/static/uploads/%s"%(file_name))





     # text =  render_to_string("hub/oct_manifest_txt.html",
     #                             {'octroi':octroi,
     #                              'shipments':shipments,
     #                              },
     #                              context_instance=RequestContext(request))
  #   response =  HttpResponse("%s"%text, content_type="text/plain", mimetype='text/plain')
  #   response['Content-Disposition'] = 'attachment; filename=manifest.txt'
  #   return response


@csrf_exempt
def close_octroi(request):
    octroi_id=request.POST['octroi_id']
    octroi = Octroi.objects.filter(id=octroi_id).update(status=1)
    return HttpResponse("Sucess")

@csrf_exempt
def nform(request):
   if request.is_ajax():
      #total_ship = request.POST['total_ship']
      #nhform_slip_no = request.POST['nhform_slip_no']
      date = request.POST['nform_date']
      nf = NForm.objects.create(date = date, origin=request.user.employeemaster.service_centre)
      ship = NFormAirportConfirmation.objects.filter(status=0)
      for a in ship:
                NFormShipments.objects.create(nhform=nf, shipment=a.shipment, shipper=a.shipment.shipper, origin=a.origin)
                NFormAirportConfirmation.objects.filter(id=a.id).update(status=1, updated_on=now)

      return render_to_response("hub/nform_data.html",
                        {"a":nf},)
    #  return HttpResponse("Success")
   else:

      nform = NForm.objects.filter(origin=request.user.employeemaster.service_centre).order_by('-id')
      shipper = Customer.objects.all()

   return render_to_response("hub/nform.html",
                                  {"nform":nform,
                                   'shipper':shipper},
                                  # 'origin_sc':request.user.employeemaster.service_centre},
                                  context_instance=RequestContext(request))



@csrf_exempt
def delink_shipment_nform(request, oid):
    nform = NForm.objects.get(id=oid)
    shipments = NFormShipments.objects.filter(nform=nform)
    if request.POST:
       awb_number = request.POST['awb']
       try:
            NFormShipments.objects.delete(shipment__airwaybill_number=awb_number, nform=nform)
       #     shipment = Shipment.objects.get(airwaybill_number=awb_number, shipper=octroi.shipper)
       except:
            return HttpResponse("Incorrect Shipment Number")

       #octroi.shipments.remove(shipment)
       return render_to_response("hub/shipment_nform_data.html",
                                  {'shipment':shipments,
                                   },
                                   context_instance=RequestContext(request))


    else:
        #shipments = octroi.shipments.all()
        return render_to_response("hub/delink_shipment_nform.html",
                                  { 'oid':oid,
                                   'shipment':shipments},
                                   context_instance=RequestContext(request))


def nform_manifest(request, oid):
     nform=NForm.objects.get(id=oid)
     ship = NFormShipments.objects.filter(nhform=nform).order_by('shipment__shipper')
    # user=request.user.employeemaster
     text =  render_to_string("hub/nform_manifest_txt.html",
                                  {'nhform':nform,
                                   'shipments':ship,
     #                              'user':user
                                   },
                                   context_instance=RequestContext(request))
     response =  HttpResponse("%s"%text, content_type="text/plain", mimetype='text/plain')
     response['Content-Disposition'] = 'attachment; filename=manifest.txt'
     return response


@csrf_exempt
def close_nform(request):
    nform_id=request.POST['nform_id']
    nform = NForm.objects.filter(id=nform_id).update(status=1)
    return HttpResponse("Sucess")



@csrf_exempt
def close_connection(request):
    connection_id=request.POST['connection_id']
    connection = Connection.objects.get(id=connection_id)
    # following function to be updated async
    octroi_update_for_connection(connection)
    connection.connection_status = 4
    connection.save()
    ConnectionQueue.objects.create(connection=connection, employee=request.user.employeemaster)
    return HttpResponse("Sucess")


@csrf_exempt
def run_code(request):
    if request.POST:
     #destination=request.POST['dest']
     #destination=ServiceCenter.objects.get(id=int(destination))
     vehicle_num=request.POST['vehicle']
     coloader=request.POST['coloader']
     coloader=Coloader.objects.get(id=int(coloader))
     origin_sc = request.user.employeemaster.service_centre
     runcode = RunCode.objects.create(coloader=coloader, vehicle_number=vehicle_num, origin=origin_sc)
     destination=request.POST['dest']
     destination = [int(x) for x in destination.split(",")]
     for a in destination:
         destination=ServiceCenter.objects.get(id=a)
         runcode.destination.add(destination)

     return render_to_response("service_centre/runcode_data.html",
                               {"a":runcode},
                               context_instance=RequestContext(request))

    else:
        coloader = Coloader.objects.all()
        service_centre = ServiceCenter.objects.all()
        run_code = RunCode.objects.filter(runcode_status__in=[0,1], origin=request.user.employeemaster.service_centre).order_by("-id")
        return render_to_response("hub/run_code.html",
                                  {'coloader':coloader,
                                   'service_centre':service_centre,
                                   'run_code':run_code
                                    },
                                  context_instance=RequestContext(request))

@csrf_exempt
def airport_confirmation(request):
    if request.POST:
      date=request.POST['date']
      run_code=request.POST['run_code']
      run_code = RunCode.objects.get(id=int(run_code))
      flight_num=request.POST['flight_num']
      std=request.POST['std']
      atd=request.POST['atd']
      num_bags=request.POST['num_bags']
      #coloader=request.POST['coloader']
      #coloader=Coloader.objects.get(id=int(coloader))
      cnote=request.POST['connection']
      #connection = Connection.objects.get(id=int(connection))
      status_code=request.POST['status_code']
      airport_confirm = AirportConfirmation(date=date, run_code=run_code, flight_num=flight_num, std=std, atd=atd, num_of_bags=num_bags, cnote=cnote, status_code=status_code, origin=request.user.employeemaster.service_centre)

      airport_confirm.save()

      mum_sc = ServiceCenter.objects.filter(city__city_shortcode="MUM").exclude(id__in=[180, 178, 179, 192, 205, 206, 211])
      outer_mum_sc = ServiceCenter.objects.filter(id__in=[180, 178, 179, 192, 205, 206, 211])
      try:
       status = ShipmentStatusMaster.objects.get(id=status_code)
       for connection in run_code.connection.all():
        conn = Connection.objects.get(id=connection.id)
        for bags in conn.bags.all():
            bag = Bags.objects.get(id=bags.id)
            bag.updated_on = now
            bag.bag_status = 7
            bag.save()
            update_bag_history(bag, employee=request.user.employeemaster,
                        #action="runcode airport confirmation completed", content_object=airport_confirm,
                        action="intransit (Airport confirmation: %s, Run Code: %s)"%(airport_confirm.id, run_code.id), content_object=airport_confirm,
                        sc=request.user.employeemaster.service_centre, reason_code = status)

            for shipment in bag.shipments.filter().exclude(status=9).exclude(reason_code__code__in = [333, 888, 999]).exclude(rts_status = 2):
                if (shipment.pickup.service_centre not in mum_sc) and (shipment.service_centre in mum_sc):
                      OctroiAirportConfirmation.objects.create(airportconfirmation=airport_confirm, shipment=shipment, origin=request.user.employeemaster.service_centre)
                history_update(shipment, 15, request, "", status)
             #   upd_time = shipment.added_on
             #   monthdir = upd_time.strftime("%Y_%m")
             #   shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
             #   shipment_history.objects.create(shipment=shipment, status=15, employee_code = request.user.employeemaster, current_sc = request.user.employeemaster.service_centre, expected_dod=shipment.expected_dod)
      except:
        pass
      return render_to_response("service_centre/airportconfir_data.html",
                                {'a':airport_confirm},
                               context_instance=RequestContext(request))

    else:
      coloader=Coloader.objects.all()
      reason_code = ShipmentStatusMaster.objects.all()
      airport_confirm = AirportConfirmation.objects.filter(origin=request.user.employeemaster.service_centre).order_by("-id")
      return render_to_response("hub/airportconfir.html",
                                {'coloader':coloader,
                                 'reason_code':reason_code,
                                  'airport_confirm':airport_confirm},
                               context_instance=RequestContext(request))



def connection_bags(request, cid):
    conn = Connection.objects.get(id=int(cid))
    bags = conn.bags.all()
    return render_to_response("hub/conn_bags.html",
                              {'cid':cid,
                               'bags':bags})

def redirection(request):
    if request.method == 'GET':
        reason_code = ShipmentStatusMaster.objects.filter(code__in=[207, 230])
        service_centre = ServiceCenter.objects.all()
        return render_to_response('hub/redirection.html',
            {'reason_code':reason_code, 'service_centre':service_centre},
            context_instance = RequestContext(request))

def bag_count(request, bid):
    bags = Bags.objects.using('local_ecomm').filter(bag_number=bid)
    if not bags:
      return HttpResponse("Bag does not exists")
    total_records = bags[0].ship_data.using('local_ecomm').count()
    mismatch_count = bags[0].shipments.using('local_ecomm').count()
    success_count = total_records - mismatch_count
    data = {'total':total_records, 'mismatch':mismatch_count, 'success':success_count}
    json_data = simplejson.dumps(data)
    return HttpResponse(json_data, mimetype='application/json')
