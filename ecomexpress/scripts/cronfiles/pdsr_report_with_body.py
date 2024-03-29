import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = "ecomexpress.settings"
sys.path.append('/home/web/ecomm.prtouch.com/ecomexpress/')

from decimal import Decimal
from billing.pdsr_report import write_pdsr_to_excel
import settings

import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders
from django.core.mail import EmailMultiAlternatives
from service_centre.models import *
from datetime import date,timedelta,datetime
TW = Decimal(10) ** -2
import calendar
import datetime

def main():
        now = datetime.datetime.now()
        before = now - datetime.timedelta(days=1)
        today_str = before.strftime('%Y-%m-%d')
        month_begn = before.strftime('%Y-%m-01')
        (file_name,total) = write_pdsr_to_excel(today_str)

        #add more
        total_rts = Shipment.objects.filter(shipment_date=today_str,rts_status=1).only('id').count()
        cod_rts_count = Shipment.objects.filter(shipment_date=today_str,rts_status=1,product_type='cod').only('id').count()
        ppd_rts_count = Shipment.objects.filter(shipment_date=today_str,rts_status=1,product_type='ppd').only('id').count()

        fre_total = Shipment.objects.filter(shipment_date=today_str).only('id').count()
        cod_total = Shipment.objects.filter(shipment_date=today_str,product_type='cod').only('id').count()
        ppd_total = Shipment.objects.filter(shipment_date=today_str,product_type='ppd').only('id').count()
        cod_fresh = cod_total-cod_rts_count
        ppd_fresh = ppd_total-ppd_rts_count
        total_fresh = fre_total - total_rts
        ebs_ppd = Shipment.objects.filter(shipment_date=today_str,airwaybill_number__istartswith=3).only('id').count()
        ebs_cod =Shipment.objects.filter(shipment_date=today_str,airwaybill_number__istartswith=4).only('id').count()
        rvb_totlal = Shipment.objects.filter(shipment_date=today_str,reverse_pickup=1).only('id').count()
        rvb_cod = Shipment.objects.filter(shipment_date=today_str,reverse_pickup=1,product_type='cod').only('id').count()
        rvb_ppd = Shipment.objects.filter(shipment_date=today_str,reverse_pickup=1,product_type='ppd').only('id').count()

        month_start = int(now.day -1)
        start_date = now - datetime.timedelta(days=month_start)
        daygenerator = (start_date.date() + timedelta(x + 1) for x in xrange((now.date() - start_date.date()).days))
        current_day_count = sum(1 for day in daygenerator if day.weekday() < 6)

        sunday_count = len([1 for i in calendar.monthcalendar(datetime.datetime.now().year,datetime.datetime.now().month) if i[6] != 0])
        total_work_day =calendar.monthrange(now.year, now.month)[1]-sunday_count
        #total_work_day =25
        #current_day_count =25


        m_total_rts = Shipment.objects.filter(shipment_date__lte=today_str,shipment_date__gte=month_begn,rts_status=1).only('id').count()
        m_cod_rts_count = Shipment.objects.filter(shipment_date__lte=today_str,shipment_date__gte=month_begn,rts_status=1,product_type='cod').only('id').count()
        m_ppd_rts_count = Shipment.objects.filter(shipment_date__lte=today_str,shipment_date__gte=month_begn,rts_status=1,product_type='ppd').only('id').count()
        m_fre_total = Shipment.objects.filter(shipment_date__lte=today_str,shipment_date__gte=month_begn).only('id').count()
        m_cod_total = Shipment.objects.filter(shipment_date__lte=today_str,shipment_date__gte=month_begn, product_type='cod').only('id').count()
        m_ppd_total = Shipment.objects.filter(shipment_date__lte=today_str,shipment_date__gte=month_begn, product_type='ppd').only('id').count()
        m_cod_fresh = m_cod_total-m_cod_rts_count
        m_ppd_fresh = m_ppd_total-m_ppd_rts_count
        m_total_fresh = m_fre_total - m_total_rts
        m_ebs_ppd = Shipment.objects.filter(shipment_date__lte=today_str,shipment_date__gte=month_begn,airwaybill_number__istartswith=3).only('id').count()
        m_ebs_cod =Shipment.objects.filter(shipment_date__lte=today_str,shipment_date__gte=month_begn,airwaybill_number__istartswith=4).only('id').count()
        m_rvb_totlal = Shipment.objects.filter(shipment_date__lte=today_str,shipment_date__gte=month_begn,reverse_pickup=1).only('id').count()
        m_rvb_cod = Shipment.objects.filter(shipment_date__lte=today_str,shipment_date__gte=month_begn,reverse_pickup=1,product_type='cod').only('id').count()
        m_rvb_ppd = Shipment.objects.filter(shipment_date__lte=today_str,shipment_date__gte=month_begn,reverse_pickup=1,product_type='ppd').only('id').count()

        cod_projection =  (m_cod_rts_count * total_work_day)/current_day_count
        ppd_projection =  (m_ppd_rts_count * total_work_day)/current_day_count
        total_projection =  (m_total_rts * total_work_day)/current_day_count
        fresh_cod_projection =  (m_cod_fresh * total_work_day)/current_day_count
        fresh_ppd_projection =  (m_ppd_fresh * total_work_day)/current_day_count
        fresh_total_projection =  (m_total_fresh * total_work_day)/current_day_count
        ebs_cod_projection =  (m_ebs_cod * total_work_day)/current_day_count
        ebs_ppd_projection =  (m_ebs_ppd * total_work_day)/current_day_count
        reverse_cod_projection =  (m_rvb_cod * total_work_day)/current_day_count
        reverse_ppd_projection =  (m_rvb_ppd * total_work_day)/current_day_count
        reverse_total_projection =  (m_rvb_totlal * total_work_day)/current_day_count

        #return "hello" 
        #add end
        f = open(file_name,"r")
        pdsr_content = f.read()
        f.close()

        filename = file_name.split('uploads/')
        attach = MIMEApplication(pdsr_content, 'xlsx')
        attach.add_header('Content-Disposition', 'attachment', filename = filename[1])
        msg = MIMEMultipart()
        msg['From'] = "Reports <support@ecomexpress.in>"
        s1 = smtplib.SMTP('i.prtouch.com', 26)
        smtp_to_mail_ids = ["onkar@prtouch.com","theonkar10@gmail.com"]
        #smtp_to_mail_ids = ["krishnanta@ecomexpress.in","prashanta@ecomexpress.in" , "satyak@ecomexpress.in", "sanjeevs@ecomexpress.in", "anila@ecomexpress.in", "manjud@ecomexpress.in", "jitendrad@ecomexpress.in", "jaideeps@ecomexpress.in", "neha@prtouch.com", "nareshb@ecomexpress.in","onkar.tonge@gmail.com", "onkar@prtouch.com", "jinesh@prtouch.com", "sravan@ecomexpress.in","jignesh@prtouch.com"]
        content = '<html><body><p>Dear Team,</p><p>Please find  attached Previous Day Sales Report.</p><p>Summary of report follows</p><table  border="1" cellpadding="10"  cellspacing="0"><tr><th></th><th>PPD</th><th>COD</th><th>Total</th></tr>'
        count = 0
        row1, row2, row3, row4 = total
        row1 = list(row1[5:])
        row1 = [str(value) for value in row1]

        row2 = [str(int(value)) if ind == 0 or ind ==10 or ind ==20 else str(Decimal(value).quantize(TW)) for ind, value in enumerate(row2)]
        row3 = [str(int(value)) if ind == 0 or ind ==10 or ind ==20 else str(Decimal(value).quantize(TW)) for ind, value in enumerate(row3)]
        row4 = [str(int(value)) if ind == 0 or ind ==10 or ind ==20 else str(Decimal(value).quantize(TW)) for ind, value in enumerate(row4)]
        ziped_total = zip(row1, row2, row3, row4)

        row_count =0
        for i in ziped_total:
            row_count = row_count+1
            content = content+'<tr><td bgcolor="Yellow"> '+i[0]+' </td><td> '+i[1]+' </td><td> '+i[2]+'</td><td>'+i[3]+'</td></tr>'

        content = content+'</table><h2>Daily</h2><table  border="1" cellpadding="10"  cellspacing="0"><tr><th></th><th>PPD</th><th>COD</th><th>Total</th></tr>'
        content = content+'<tr><td bgcolor="Yellow">Total Rts</td><td> '+str(ppd_rts_count)+' </td><td> '+str(cod_rts_count)+'</td><td>'+str(total_rts)+'</td></tr>'
        content = content+'<tr><td bgcolor="Yellow">Total Fresh</td><td> '+str(ppd_fresh)+' </td><td> '+str(cod_fresh)+'</td><td>'+str(total_fresh)+'</td></tr>'
        content = content+'<tr><td bgcolor="Yellow">EBS Total</td><td> '+str(ebs_ppd)+' </td><td> '+str(ebs_cod)+'</td><td>'+str(ebs_ppd+ebs_cod)+'</td></tr>'

        content = content+'<tr><td bgcolor="Yellow">Reverse Pickup Total</td><td> '+str(rvb_ppd)+' </td><td> '+str(rvb_cod)+'</td><td>'+str(rvb_totlal)+'</td></tr>'

        content = content+'</table><h2>Monthly</h2><table  border="1" cellpadding="10"  cellspacing="0"><tr><th></th><th>PPD</th><th>COD</th><th>Total</th></tr>'
        content = content+'<tr><td bgcolor="Yellow">Total Rts</td><td> '+str(m_ppd_rts_count)+' </td><td> '+str(m_cod_rts_count)+'</td><td>'+str(m_total_rts)+'</td></tr>'

        content = content+'<tr><td bgcolor="Yellow">Total Fresh</td><td> '+str(m_ppd_fresh)+' </td><td> '+str(m_cod_fresh)+'</td><td>'+str(m_total_fresh)+'</td></tr>'
        content = content+'<tr><td bgcolor="Yellow">EBS Total</td><td> '+str(m_ebs_ppd)+' </td><td> '+str(m_ebs_cod)+'</td><td>'+str(m_ebs_ppd+m_ebs_cod)+'</td></tr>'
        content = content+'<tr><td bgcolor="Yellow">Reverse Pickup Total</td><td> '+str(m_rvb_ppd)+' </td><td> '+str(m_rvb_cod)+'</td><td>'+str(m_rvb_totlal)+'</td></tr>'

        content = content+'</table><p>Regards</p><p>Support Team</p></body></html>'
        text =("Dear Team, \nPlease find  attached Previous Day Sales Report. \n\nRegards\n\nSupport Team\n total=%s"%(content))
        html =content
        html =MIMEText(html, 'html')
        msg['Subject'] = 'Daily Sales Report'
        msg.attach(html)
        msg.attach(attach)

        for a in smtp_to_mail_ids:
            s1.sendmail(msg['From'] , a, msg.as_string())
        s1.quit()


main()

