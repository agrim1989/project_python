# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2010 - 2016 ScrumDo LLC
#
# This software is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy (See file COPYING) of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA


from django.contrib import admin
from apps.organizations.models import *


class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization')
    search_fields = ('name',)

admin.site.register(Team , TeamAdmin)
admin.site.register(TeamInvite)