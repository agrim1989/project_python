'''
Created on Oct 19, 2012

@author: Sirius
'''
from django.conf.urls.defaults import *
from sorter_api  import views
from privateviews.decorators import login_not_required
urlpatterns = patterns('',
                       #url(r'^$','index'),
                       url(r'^update_weight/$',login_not_required(views.add_to_history)),
                       url(r'^api/$','add_to_history'),
)
