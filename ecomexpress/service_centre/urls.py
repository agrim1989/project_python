'''
Created on Oct 19, 2012

@author: Sirius
'''
from django.conf.urls.defaults import *

urlpatterns = patterns('service_centre.views',
                       url(r'^$','inscan_shipment'),
                       url(r'^connection/$','connection'),
                       url(r'^close_connection/$','close_connection'),
                       url(r'^redirection/$','redirection'),
                       url(r'^get_connection_bags/$','get_connection_bags'),
                       url(r'^include_bags/(?P<cid>\w+)/$','include_bags'),
                       url(r'^include_bags_connection/$','include_bags_connection'),
                       url(r'^delink_bags/(?P<cid>\w+)/$','delink_bags'),
                       url(r'^include_connection/(?P<rid>\w+)/$','include_connection'),
                       url(r'^delink_connection/(?P<rid>\w+)/$','delink_connection'),
                       url(r'^generate_challan/(?P<cid>\w+)/$','generate_challan'),
                       url(r'^bagging/$','bagging'),
                       url(r'^airport_confirmation/$','airport_confirmation'),
                       url(r'^awb_add/$','awb_add'),
                       url(r'^field_pickup_operation/(?P<pid>\w+)/$', 'field_pickup_operation'),
#                       url(r'^field_pickup_operation/(?P<pid>\w+)/mobile/$', 'field_pickup_operation_mobile'),
                       url(r'^generate_exception/(?P<pid>\w+)/$', 'generate_exception'),
                       url(r'^download_prn/$', 'download_prn'),
                       url(r'^download_xcl/(?P<dtype>\w+)/$', 'download_xcl'),
                       url(r'^field_pickup_operation/$', 'field_pickup_operation'),
                       url(r'^upload_file/(?P<pid>\w+)/$','upload_file'),
                       url(r'^auto_upload_file/$','auto_upload_file'),
                       url(r'^upload_rev_file/$','upload_rev_file'),
                       url(r'^shipment_orders/$','shipment_orders'),
                       url(r'^awb_add/pup_num/$','pup_data'),
                       url(r'^awb_add/awb_num/$','awb_data'),
                       url(r'^order_pricing/$','order_pricing'),
                       url(r'^add-bagging/$','add_bagging'),
                       url(r'^include_shipment/(?P<bid>\w+)/$','include_shipment'),
                       url(r'^delink_shipment/(?P<bid>\w+)/$','delink_shipment'),
                       url(r'^generate_manifest/(?P<bid>\w+)/$','generate_manifest'),
                       url(r'^close-bagging/$','close_bagging'),
                       url(r'^close_runcode/$','close_runcode'),
                       url(r'^reason_code/$','reason_code'),
                       url(r'^run_code_bags/$','run_code_bags'),
                       url(r'^delete_bags/$','delete_bags'),
                       url(r'^awb_query/$','awb_query'),
                       url(r'^run_code/$','run_code'),
                       url(r'^rts_report/$','rts_report'),
                       url(r'^awb_edit/$','awb_edit'),
                       url(r'^shipment_update/$','shipment_update'),
                       url(r'^shipment_lbh_update/$','shipment_lbh_update'),
		      #url(r'^upload-csv/$','upload-csv'),
		       url(r'get_csv_file/$','get_csv_file'),
		       url(r'get_csv/$','get_csv'),
                       url(r'auto_upload_file_updated/$','auto_upload_file_updated'),
                       url(r'^cbags/',include('operations.urls')),
                       url(r'^check_bagging/$','check_bagging'),
			)
