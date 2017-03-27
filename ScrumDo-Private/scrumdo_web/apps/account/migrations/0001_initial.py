# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings



class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timezone', models.CharField(default=b'US/Eastern', max_length=100, verbose_name='timezone', choices=[(b'Pacific/Midway', b'(GMT-1100) Pacific/Midway'), (b'Pacific/Niue', b'(GMT-1100) Pacific/Niue'), (b'Pacific/Pago_Pago', b'(GMT-1100) Pacific/Pago_Pago'), (b'America/Adak', b'(GMT-1000) America/Adak'), (b'Pacific/Honolulu', b'(GMT-1000) Pacific/Honolulu'), (b'Pacific/Johnston', b'(GMT-1000) Pacific/Johnston'), (b'Pacific/Rarotonga', b'(GMT-1000) Pacific/Rarotonga'), (b'Pacific/Tahiti', b'(GMT-1000) Pacific/Tahiti'), (b'US/Hawaii', b'(GMT-1000) US/Hawaii'), (b'Pacific/Marquesas', b'(GMT-0930) Pacific/Marquesas'), (b'America/Anchorage', b'(GMT-0900) America/Anchorage'), (b'America/Juneau', b'(GMT-0900) America/Juneau'), (b'America/Nome', b'(GMT-0900) America/Nome'), (b'America/Sitka', b'(GMT-0900) America/Sitka'), (b'America/Yakutat', b'(GMT-0900) America/Yakutat'), (b'Pacific/Gambier', b'(GMT-0900) Pacific/Gambier'), (b'US/Alaska', b'(GMT-0900) US/Alaska'), (b'America/Dawson', b'(GMT-0800) America/Dawson'), (b'America/Los_Angeles', b'(GMT-0800) America/Los_Angeles'), (b'America/Metlakatla', b'(GMT-0800) America/Metlakatla'), (b'America/Santa_Isabel', b'(GMT-0800) America/Santa_Isabel'), (b'America/Tijuana', b'(GMT-0800) America/Tijuana'), (b'America/Vancouver', b'(GMT-0800) America/Vancouver'), (b'America/Whitehorse', b'(GMT-0800) America/Whitehorse'), (b'Canada/Pacific', b'(GMT-0800) Canada/Pacific'), (b'Pacific/Pitcairn', b'(GMT-0800) Pacific/Pitcairn'), (b'US/Pacific', b'(GMT-0800) US/Pacific'), (b'America/Boise', b'(GMT-0700) America/Boise'), (b'America/Cambridge_Bay', b'(GMT-0700) America/Cambridge_Bay'), (b'America/Chihuahua', b'(GMT-0700) America/Chihuahua'), (b'America/Creston', b'(GMT-0700) America/Creston'), (b'America/Dawson_Creek', b'(GMT-0700) America/Dawson_Creek'), (b'America/Denver', b'(GMT-0700) America/Denver'), (b'America/Edmonton', b'(GMT-0700) America/Edmonton'), (b'America/Hermosillo', b'(GMT-0700) America/Hermosillo'), (b'America/Inuvik', b'(GMT-0700) America/Inuvik'), (b'America/Mazatlan', b'(GMT-0700) America/Mazatlan'), (b'America/Ojinaga', b'(GMT-0700) America/Ojinaga'), (b'America/Phoenix', b'(GMT-0700) America/Phoenix'), (b'America/Yellowknife', b'(GMT-0700) America/Yellowknife'), (b'Canada/Mountain', b'(GMT-0700) Canada/Mountain'), (b'US/Arizona', b'(GMT-0700) US/Arizona'), (b'US/Mountain', b'(GMT-0700) US/Mountain'), (b'America/Bahia_Banderas', b'(GMT-0600) America/Bahia_Banderas'), (b'America/Belize', b'(GMT-0600) America/Belize'), (b'America/Cancun', b'(GMT-0600) America/Cancun'), (b'America/Chicago', b'(GMT-0600) America/Chicago'), (b'America/Costa_Rica', b'(GMT-0600) America/Costa_Rica'), (b'America/El_Salvador', b'(GMT-0600) America/El_Salvador'), (b'America/Guatemala', b'(GMT-0600) America/Guatemala'), (b'America/Indiana/Knox', b'(GMT-0600) America/Indiana/Knox'), (b'America/Indiana/Tell_City', b'(GMT-0600) America/Indiana/Tell_City'), (b'America/Managua', b'(GMT-0600) America/Managua'), (b'America/Matamoros', b'(GMT-0600) America/Matamoros'), (b'America/Menominee', b'(GMT-0600) America/Menominee'), (b'America/Merida', b'(GMT-0600) America/Merida'), (b'America/Mexico_City', b'(GMT-0600) America/Mexico_City'), (b'America/Monterrey', b'(GMT-0600) America/Monterrey'), (b'America/North_Dakota/Beulah', b'(GMT-0600) America/North_Dakota/Beulah'), (b'America/North_Dakota/Center', b'(GMT-0600) America/North_Dakota/Center'), (b'America/North_Dakota/New_Salem', b'(GMT-0600) America/North_Dakota/New_Salem'), (b'America/Rainy_River', b'(GMT-0600) America/Rainy_River'), (b'America/Rankin_Inlet', b'(GMT-0600) America/Rankin_Inlet'), (b'America/Regina', b'(GMT-0600) America/Regina'), (b'America/Resolute', b'(GMT-0600) America/Resolute'), (b'America/Swift_Current', b'(GMT-0600) America/Swift_Current'), (b'America/Tegucigalpa', b'(GMT-0600) America/Tegucigalpa'), (b'America/Winnipeg', b'(GMT-0600) America/Winnipeg'), (b'Canada/Central', b'(GMT-0600) Canada/Central'), (b'Pacific/Galapagos', b'(GMT-0600) Pacific/Galapagos'), (b'US/Central', b'(GMT-0600) US/Central'), (b'America/Atikokan', b'(GMT-0500) America/Atikokan'), (b'America/Bogota', b'(GMT-0500) America/Bogota'), (b'America/Cayman', b'(GMT-0500) America/Cayman'), (b'America/Detroit', b'(GMT-0500) America/Detroit'), (b'America/Eirunepe', b'(GMT-0500) America/Eirunepe'), (b'America/Guayaquil', b'(GMT-0500) America/Guayaquil'), (b'America/Havana', b'(GMT-0500) America/Havana'), (b'America/Indiana/Indianapolis', b'(GMT-0500) America/Indiana/Indianapolis'), (b'America/Indiana/Marengo', b'(GMT-0500) America/Indiana/Marengo'), (b'America/Indiana/Petersburg', b'(GMT-0500) America/Indiana/Petersburg'), (b'America/Indiana/Vevay', b'(GMT-0500) America/Indiana/Vevay'), (b'America/Indiana/Vincennes', b'(GMT-0500) America/Indiana/Vincennes'), (b'America/Indiana/Winamac', b'(GMT-0500) America/Indiana/Winamac'), (b'America/Iqaluit', b'(GMT-0500) America/Iqaluit'), (b'America/Jamaica', b'(GMT-0500) America/Jamaica'), (b'America/Kentucky/Louisville', b'(GMT-0500) America/Kentucky/Louisville'), (b'America/Kentucky/Monticello', b'(GMT-0500) America/Kentucky/Monticello'), (b'America/Lima', b'(GMT-0500) America/Lima'), (b'America/Montreal', b'(GMT-0500) America/Montreal'), (b'America/Nassau', b'(GMT-0500) America/Nassau'), (b'America/New_York', b'(GMT-0500) America/New_York'), (b'America/Nipigon', b'(GMT-0500) America/Nipigon'), (b'America/Panama', b'(GMT-0500) America/Panama'), (b'America/Pangnirtung', b'(GMT-0500) America/Pangnirtung'), (b'America/Port-au-Prince', b'(GMT-0500) America/Port-au-Prince'), (b'America/Rio_Branco', b'(GMT-0500) America/Rio_Branco'), (b'America/Thunder_Bay', b'(GMT-0500) America/Thunder_Bay'), (b'America/Toronto', b'(GMT-0500) America/Toronto'), (b'Canada/Eastern', b'(GMT-0500) Canada/Eastern'), (b'Pacific/Easter', b'(GMT-0500) Pacific/Easter'), (b'US/Eastern', b'(GMT-0500) US/Eastern'), (b'America/Caracas', b'(GMT-0430) America/Caracas'), (b'America/Anguilla', b'(GMT-0400) America/Anguilla'), (b'America/Antigua', b'(GMT-0400) America/Antigua'), (b'America/Aruba', b'(GMT-0400) America/Aruba'), (b'America/Barbados', b'(GMT-0400) America/Barbados'), (b'America/Blanc-Sablon', b'(GMT-0400) America/Blanc-Sablon'), (b'America/Boa_Vista', b'(GMT-0400) America/Boa_Vista'), (b'America/Curacao', b'(GMT-0400) America/Curacao'), (b'America/Dominica', b'(GMT-0400) America/Dominica'), (b'America/Glace_Bay', b'(GMT-0400) America/Glace_Bay'), (b'America/Goose_Bay', b'(GMT-0400) America/Goose_Bay'), (b'America/Grand_Turk', b'(GMT-0400) America/Grand_Turk'), (b'America/Grenada', b'(GMT-0400) America/Grenada'), (b'America/Guadeloupe', b'(GMT-0400) America/Guadeloupe'), (b'America/Guyana', b'(GMT-0400) America/Guyana'), (b'America/Halifax', b'(GMT-0400) America/Halifax'), (b'America/Kralendijk', b'(GMT-0400) America/Kralendijk'), (b'America/La_Paz', b'(GMT-0400) America/La_Paz'), (b'America/Lower_Princes', b'(GMT-0400) America/Lower_Princes'), (b'America/Manaus', b'(GMT-0400) America/Manaus'), (b'America/Marigot', b'(GMT-0400) America/Marigot'), (b'America/Martinique', b'(GMT-0400) America/Martinique'), (b'America/Moncton', b'(GMT-0400) America/Moncton'), (b'America/Montserrat', b'(GMT-0400) America/Montserrat'), (b'America/Port_of_Spain', b'(GMT-0400) America/Port_of_Spain'), (b'America/Porto_Velho', b'(GMT-0400) America/Porto_Velho'), (b'America/Puerto_Rico', b'(GMT-0400) America/Puerto_Rico'), (b'America/Santo_Domingo', b'(GMT-0400) America/Santo_Domingo'), (b'America/St_Barthelemy', b'(GMT-0400) America/St_Barthelemy'), (b'America/St_Kitts', b'(GMT-0400) America/St_Kitts'), (b'America/St_Lucia', b'(GMT-0400) America/St_Lucia'), (b'America/St_Thomas', b'(GMT-0400) America/St_Thomas'), (b'America/St_Vincent', b'(GMT-0400) America/St_Vincent'), (b'America/Thule', b'(GMT-0400) America/Thule'), (b'America/Tortola', b'(GMT-0400) America/Tortola'), (b'Atlantic/Bermuda', b'(GMT-0400) Atlantic/Bermuda'), (b'Canada/Atlantic', b'(GMT-0400) Canada/Atlantic'), (b'America/St_Johns', b'(GMT-0330) America/St_Johns'), (b'Canada/Newfoundland', b'(GMT-0330) Canada/Newfoundland'), (b'America/Araguaina', b'(GMT-0300) America/Araguaina'), (b'America/Argentina/Buenos_Aires', b'(GMT-0300) America/Argentina/Buenos_Aires'), (b'America/Argentina/Catamarca', b'(GMT-0300) America/Argentina/Catamarca'), (b'America/Argentina/Cordoba', b'(GMT-0300) America/Argentina/Cordoba'), (b'America/Argentina/Jujuy', b'(GMT-0300) America/Argentina/Jujuy'), (b'America/Argentina/La_Rioja', b'(GMT-0300) America/Argentina/La_Rioja'), (b'America/Argentina/Mendoza', b'(GMT-0300) America/Argentina/Mendoza'), (b'America/Argentina/Rio_Gallegos', b'(GMT-0300) America/Argentina/Rio_Gallegos'), (b'America/Argentina/Salta', b'(GMT-0300) America/Argentina/Salta'), (b'America/Argentina/San_Juan', b'(GMT-0300) America/Argentina/San_Juan'), (b'America/Argentina/San_Luis', b'(GMT-0300) America/Argentina/San_Luis'), (b'America/Argentina/Tucuman', b'(GMT-0300) America/Argentina/Tucuman'), (b'America/Argentina/Ushuaia', b'(GMT-0300) America/Argentina/Ushuaia'), (b'America/Asuncion', b'(GMT-0300) America/Asuncion'), (b'America/Bahia', b'(GMT-0300) America/Bahia'), (b'America/Belem', b'(GMT-0300) America/Belem'), (b'America/Campo_Grande', b'(GMT-0300) America/Campo_Grande'), (b'America/Cayenne', b'(GMT-0300) America/Cayenne'), (b'America/Cuiaba', b'(GMT-0300) America/Cuiaba'), (b'America/Fortaleza', b'(GMT-0300) America/Fortaleza'), (b'America/Godthab', b'(GMT-0300) America/Godthab'), (b'America/Maceio', b'(GMT-0300) America/Maceio'), (b'America/Miquelon', b'(GMT-0300) America/Miquelon'), (b'America/Paramaribo', b'(GMT-0300) America/Paramaribo'), (b'America/Recife', b'(GMT-0300) America/Recife'), (b'America/Santarem', b'(GMT-0300) America/Santarem'), (b'America/Santiago', b'(GMT-0300) America/Santiago'), (b'Antarctica/Palmer', b'(GMT-0300) Antarctica/Palmer'), (b'Antarctica/Rothera', b'(GMT-0300) Antarctica/Rothera'), (b'Atlantic/Stanley', b'(GMT-0300) Atlantic/Stanley'), (b'America/Montevideo', b'(GMT-0200) America/Montevideo'), (b'America/Noronha', b'(GMT-0200) America/Noronha'), (b'America/Sao_Paulo', b'(GMT-0200) America/Sao_Paulo'), (b'Atlantic/South_Georgia', b'(GMT-0200) Atlantic/South_Georgia'), (b'America/Scoresbysund', b'(GMT-0100) America/Scoresbysund'), (b'Atlantic/Azores', b'(GMT-0100) Atlantic/Azores'), (b'Atlantic/Cape_Verde', b'(GMT-0100) Atlantic/Cape_Verde'), (b'Africa/Abidjan', b'(GMT+0000) Africa/Abidjan'), (b'Africa/Accra', b'(GMT+0000) Africa/Accra'), (b'Africa/Bamako', b'(GMT+0000) Africa/Bamako'), (b'Africa/Banjul', b'(GMT+0000) Africa/Banjul'), (b'Africa/Bissau', b'(GMT+0000) Africa/Bissau'), (b'Africa/Casablanca', b'(GMT+0000) Africa/Casablanca'), (b'Africa/Conakry', b'(GMT+0000) Africa/Conakry'), (b'Africa/Dakar', b'(GMT+0000) Africa/Dakar'), (b'Africa/El_Aaiun', b'(GMT+0000) Africa/El_Aaiun'), (b'Africa/Freetown', b'(GMT+0000) Africa/Freetown'), (b'Africa/Lome', b'(GMT+0000) Africa/Lome'), (b'Africa/Monrovia', b'(GMT+0000) Africa/Monrovia'), (b'Africa/Nouakchott', b'(GMT+0000) Africa/Nouakchott'), (b'Africa/Ouagadougou', b'(GMT+0000) Africa/Ouagadougou'), (b'Africa/Sao_Tome', b'(GMT+0000) Africa/Sao_Tome'), (b'America/Danmarkshavn', b'(GMT+0000) America/Danmarkshavn'), (b'Antarctica/Troll', b'(GMT+0000) Antarctica/Troll'), (b'Atlantic/Canary', b'(GMT+0000) Atlantic/Canary'), (b'Atlantic/Faroe', b'(GMT+0000) Atlantic/Faroe'), (b'Atlantic/Madeira', b'(GMT+0000) Atlantic/Madeira'), (b'Atlantic/Reykjavik', b'(GMT+0000) Atlantic/Reykjavik'), (b'Atlantic/St_Helena', b'(GMT+0000) Atlantic/St_Helena'), (b'Europe/Dublin', b'(GMT+0000) Europe/Dublin'), (b'Europe/Guernsey', b'(GMT+0000) Europe/Guernsey'), (b'Europe/Isle_of_Man', b'(GMT+0000) Europe/Isle_of_Man'), (b'Europe/Jersey', b'(GMT+0000) Europe/Jersey'), (b'Europe/Lisbon', b'(GMT+0000) Europe/Lisbon'), (b'Europe/London', b'(GMT+0000) Europe/London'), (b'GMT', b'(GMT+0000) GMT'), (b'UTC', b'(GMT+0000) UTC'), (b'Africa/Algiers', b'(GMT+0100) Africa/Algiers'), (b'Africa/Bangui', b'(GMT+0100) Africa/Bangui'), (b'Africa/Brazzaville', b'(GMT+0100) Africa/Brazzaville'), (b'Africa/Ceuta', b'(GMT+0100) Africa/Ceuta'), (b'Africa/Douala', b'(GMT+0100) Africa/Douala'), (b'Africa/Kinshasa', b'(GMT+0100) Africa/Kinshasa'), (b'Africa/Lagos', b'(GMT+0100) Africa/Lagos'), (b'Africa/Libreville', b'(GMT+0100) Africa/Libreville'), (b'Africa/Luanda', b'(GMT+0100) Africa/Luanda'), (b'Africa/Malabo', b'(GMT+0100) Africa/Malabo'), (b'Africa/Ndjamena', b'(GMT+0100) Africa/Ndjamena'), (b'Africa/Niamey', b'(GMT+0100) Africa/Niamey'), (b'Africa/Porto-Novo', b'(GMT+0100) Africa/Porto-Novo'), (b'Africa/Tunis', b'(GMT+0100) Africa/Tunis'), (b'Arctic/Longyearbyen', b'(GMT+0100) Arctic/Longyearbyen'), (b'Europe/Amsterdam', b'(GMT+0100) Europe/Amsterdam'), (b'Europe/Andorra', b'(GMT+0100) Europe/Andorra'), (b'Europe/Belgrade', b'(GMT+0100) Europe/Belgrade'), (b'Europe/Berlin', b'(GMT+0100) Europe/Berlin'), (b'Europe/Bratislava', b'(GMT+0100) Europe/Bratislava'), (b'Europe/Brussels', b'(GMT+0100) Europe/Brussels'), (b'Europe/Budapest', b'(GMT+0100) Europe/Budapest'), (b'Europe/Busingen', b'(GMT+0100) Europe/Busingen'), (b'Europe/Copenhagen', b'(GMT+0100) Europe/Copenhagen'), (b'Europe/Gibraltar', b'(GMT+0100) Europe/Gibraltar'), (b'Europe/Ljubljana', b'(GMT+0100) Europe/Ljubljana'), (b'Europe/Luxembourg', b'(GMT+0100) Europe/Luxembourg'), (b'Europe/Madrid', b'(GMT+0100) Europe/Madrid'), (b'Europe/Malta', b'(GMT+0100) Europe/Malta'), (b'Europe/Monaco', b'(GMT+0100) Europe/Monaco'), (b'Europe/Oslo', b'(GMT+0100) Europe/Oslo'), (b'Europe/Paris', b'(GMT+0100) Europe/Paris'), (b'Europe/Podgorica', b'(GMT+0100) Europe/Podgorica'), (b'Europe/Prague', b'(GMT+0100) Europe/Prague'), (b'Europe/Rome', b'(GMT+0100) Europe/Rome'), (b'Europe/San_Marino', b'(GMT+0100) Europe/San_Marino'), (b'Europe/Sarajevo', b'(GMT+0100) Europe/Sarajevo'), (b'Europe/Skopje', b'(GMT+0100) Europe/Skopje'), (b'Europe/Stockholm', b'(GMT+0100) Europe/Stockholm'), (b'Europe/Tirane', b'(GMT+0100) Europe/Tirane'), (b'Europe/Vaduz', b'(GMT+0100) Europe/Vaduz'), (b'Europe/Vatican', b'(GMT+0100) Europe/Vatican'), (b'Europe/Vienna', b'(GMT+0100) Europe/Vienna'), (b'Europe/Warsaw', b'(GMT+0100) Europe/Warsaw'), (b'Europe/Zagreb', b'(GMT+0100) Europe/Zagreb'), (b'Europe/Zurich', b'(GMT+0100) Europe/Zurich'), (b'Africa/Blantyre', b'(GMT+0200) Africa/Blantyre'), (b'Africa/Bujumbura', b'(GMT+0200) Africa/Bujumbura'), (b'Africa/Cairo', b'(GMT+0200) Africa/Cairo'), (b'Africa/Gaborone', b'(GMT+0200) Africa/Gaborone'), (b'Africa/Harare', b'(GMT+0200) Africa/Harare'), (b'Africa/Johannesburg', b'(GMT+0200) Africa/Johannesburg'), (b'Africa/Kigali', b'(GMT+0200) Africa/Kigali'), (b'Africa/Lubumbashi', b'(GMT+0200) Africa/Lubumbashi'), (b'Africa/Lusaka', b'(GMT+0200) Africa/Lusaka'), (b'Africa/Maputo', b'(GMT+0200) Africa/Maputo'), (b'Africa/Maseru', b'(GMT+0200) Africa/Maseru'), (b'Africa/Mbabane', b'(GMT+0200) Africa/Mbabane'), (b'Africa/Tripoli', b'(GMT+0200) Africa/Tripoli'), (b'Africa/Windhoek', b'(GMT+0200) Africa/Windhoek'), (b'Asia/Amman', b'(GMT+0200) Asia/Amman'), (b'Asia/Beirut', b'(GMT+0200) Asia/Beirut'), (b'Asia/Damascus', b'(GMT+0200) Asia/Damascus'), (b'Asia/Gaza', b'(GMT+0200) Asia/Gaza'), (b'Asia/Hebron', b'(GMT+0200) Asia/Hebron'), (b'Asia/Jerusalem', b'(GMT+0200) Asia/Jerusalem'), (b'Asia/Nicosia', b'(GMT+0200) Asia/Nicosia'), (b'Europe/Athens', b'(GMT+0200) Europe/Athens'), (b'Europe/Bucharest', b'(GMT+0200) Europe/Bucharest'), (b'Europe/Chisinau', b'(GMT+0200) Europe/Chisinau'), (b'Europe/Helsinki', b'(GMT+0200) Europe/Helsinki'), (b'Europe/Istanbul', b'(GMT+0200) Europe/Istanbul'), (b'Europe/Kaliningrad', b'(GMT+0200) Europe/Kaliningrad'), (b'Europe/Kiev', b'(GMT+0200) Europe/Kiev'), (b'Europe/Mariehamn', b'(GMT+0200) Europe/Mariehamn'), (b'Europe/Riga', b'(GMT+0200) Europe/Riga'), (b'Europe/Sofia', b'(GMT+0200) Europe/Sofia'), (b'Europe/Tallinn', b'(GMT+0200) Europe/Tallinn'), (b'Europe/Uzhgorod', b'(GMT+0200) Europe/Uzhgorod'), (b'Europe/Vilnius', b'(GMT+0200) Europe/Vilnius'), (b'Europe/Zaporozhye', b'(GMT+0200) Europe/Zaporozhye'), (b'Africa/Addis_Ababa', b'(GMT+0300) Africa/Addis_Ababa'), (b'Africa/Asmara', b'(GMT+0300) Africa/Asmara'), (b'Africa/Dar_es_Salaam', b'(GMT+0300) Africa/Dar_es_Salaam'), (b'Africa/Djibouti', b'(GMT+0300) Africa/Djibouti'), (b'Africa/Juba', b'(GMT+0300) Africa/Juba'), (b'Africa/Kampala', b'(GMT+0300) Africa/Kampala'), (b'Africa/Khartoum', b'(GMT+0300) Africa/Khartoum'), (b'Africa/Mogadishu', b'(GMT+0300) Africa/Mogadishu'), (b'Africa/Nairobi', b'(GMT+0300) Africa/Nairobi'), (b'Antarctica/Syowa', b'(GMT+0300) Antarctica/Syowa'), (b'Asia/Aden', b'(GMT+0300) Asia/Aden'), (b'Asia/Baghdad', b'(GMT+0300) Asia/Baghdad'), (b'Asia/Bahrain', b'(GMT+0300) Asia/Bahrain'), (b'Asia/Kuwait', b'(GMT+0300) Asia/Kuwait'), (b'Asia/Qatar', b'(GMT+0300) Asia/Qatar'), (b'Asia/Riyadh', b'(GMT+0300) Asia/Riyadh'), (b'Europe/Minsk', b'(GMT+0300) Europe/Minsk'), (b'Europe/Moscow', b'(GMT+0300) Europe/Moscow'), (b'Europe/Simferopol', b'(GMT+0300) Europe/Simferopol'), (b'Europe/Volgograd', b'(GMT+0300) Europe/Volgograd'), (b'Indian/Antananarivo', b'(GMT+0300) Indian/Antananarivo'), (b'Indian/Comoro', b'(GMT+0300) Indian/Comoro'), (b'Indian/Mayotte', b'(GMT+0300) Indian/Mayotte'), (b'Asia/Tehran', b'(GMT+0330) Asia/Tehran'), (b'Asia/Baku', b'(GMT+0400) Asia/Baku'), (b'Asia/Dubai', b'(GMT+0400) Asia/Dubai'), (b'Asia/Muscat', b'(GMT+0400) Asia/Muscat'), (b'Asia/Tbilisi', b'(GMT+0400) Asia/Tbilisi'), (b'Asia/Yerevan', b'(GMT+0400) Asia/Yerevan'), (b'Europe/Samara', b'(GMT+0400) Europe/Samara'), (b'Indian/Mahe', b'(GMT+0400) Indian/Mahe'), (b'Indian/Mauritius', b'(GMT+0400) Indian/Mauritius'), (b'Indian/Reunion', b'(GMT+0400) Indian/Reunion'), (b'Asia/Kabul', b'(GMT+0430) Asia/Kabul'), (b'Antarctica/Mawson', b'(GMT+0500) Antarctica/Mawson'), (b'Asia/Aqtau', b'(GMT+0500) Asia/Aqtau'), (b'Asia/Aqtobe', b'(GMT+0500) Asia/Aqtobe'), (b'Asia/Ashgabat', b'(GMT+0500) Asia/Ashgabat'), (b'Asia/Dushanbe', b'(GMT+0500) Asia/Dushanbe'), (b'Asia/Karachi', b'(GMT+0500) Asia/Karachi'), (b'Asia/Oral', b'(GMT+0500) Asia/Oral'), (b'Asia/Samarkand', b'(GMT+0500) Asia/Samarkand'), (b'Asia/Tashkent', b'(GMT+0500) Asia/Tashkent'), (b'Asia/Yekaterinburg', b'(GMT+0500) Asia/Yekaterinburg'), (b'Indian/Kerguelen', b'(GMT+0500) Indian/Kerguelen'), (b'Indian/Maldives', b'(GMT+0500) Indian/Maldives'), (b'Asia/Colombo', b'(GMT+0530) Asia/Colombo'), (b'Asia/Kolkata', b'(GMT+0530) Asia/Kolkata'), (b'Asia/Kathmandu', b'(GMT+0545) Asia/Kathmandu'), (b'Antarctica/Vostok', b'(GMT+0600) Antarctica/Vostok'), (b'Asia/Almaty', b'(GMT+0600) Asia/Almaty'), (b'Asia/Bishkek', b'(GMT+0600) Asia/Bishkek'), (b'Asia/Dhaka', b'(GMT+0600) Asia/Dhaka'), (b'Asia/Novosibirsk', b'(GMT+0600) Asia/Novosibirsk'), (b'Asia/Omsk', b'(GMT+0600) Asia/Omsk'), (b'Asia/Qyzylorda', b'(GMT+0600) Asia/Qyzylorda'), (b'Asia/Thimphu', b'(GMT+0600) Asia/Thimphu'), (b'Asia/Urumqi', b'(GMT+0600) Asia/Urumqi'), (b'Indian/Chagos', b'(GMT+0600) Indian/Chagos'), (b'Asia/Rangoon', b'(GMT+0630) Asia/Rangoon'), (b'Indian/Cocos', b'(GMT+0630) Indian/Cocos'), (b'Antarctica/Davis', b'(GMT+0700) Antarctica/Davis'), (b'Asia/Bangkok', b'(GMT+0700) Asia/Bangkok'), (b'Asia/Ho_Chi_Minh', b'(GMT+0700) Asia/Ho_Chi_Minh'), (b'Asia/Hovd', b'(GMT+0700) Asia/Hovd'), (b'Asia/Jakarta', b'(GMT+0700) Asia/Jakarta'), (b'Asia/Krasnoyarsk', b'(GMT+0700) Asia/Krasnoyarsk'), (b'Asia/Novokuznetsk', b'(GMT+0700) Asia/Novokuznetsk'), (b'Asia/Phnom_Penh', b'(GMT+0700) Asia/Phnom_Penh'), (b'Asia/Pontianak', b'(GMT+0700) Asia/Pontianak'), (b'Asia/Vientiane', b'(GMT+0700) Asia/Vientiane'), (b'Indian/Christmas', b'(GMT+0700) Indian/Christmas'), (b'Antarctica/Casey', b'(GMT+0800) Antarctica/Casey'), (b'Asia/Brunei', b'(GMT+0800) Asia/Brunei'), (b'Asia/Chita', b'(GMT+0800) Asia/Chita'), (b'Asia/Choibalsan', b'(GMT+0800) Asia/Choibalsan'), (b'Asia/Hong_Kong', b'(GMT+0800) Asia/Hong_Kong'), (b'Asia/Irkutsk', b'(GMT+0800) Asia/Irkutsk'), (b'Asia/Kuala_Lumpur', b'(GMT+0800) Asia/Kuala_Lumpur'), (b'Asia/Kuching', b'(GMT+0800) Asia/Kuching'), (b'Asia/Macau', b'(GMT+0800) Asia/Macau'), (b'Asia/Makassar', b'(GMT+0800) Asia/Makassar'), (b'Asia/Manila', b'(GMT+0800) Asia/Manila'), (b'Asia/Shanghai', b'(GMT+0800) Asia/Shanghai'), (b'Asia/Singapore', b'(GMT+0800) Asia/Singapore'), (b'Asia/Taipei', b'(GMT+0800) Asia/Taipei'), (b'Asia/Ulaanbaatar', b'(GMT+0800) Asia/Ulaanbaatar'), (b'Australia/Perth', b'(GMT+0800) Australia/Perth'), (b'Australia/Eucla', b'(GMT+0845) Australia/Eucla'), (b'Asia/Dili', b'(GMT+0900) Asia/Dili'), (b'Asia/Jayapura', b'(GMT+0900) Asia/Jayapura'), (b'Asia/Khandyga', b'(GMT+0900) Asia/Khandyga'), (b'Asia/Pyongyang', b'(GMT+0900) Asia/Pyongyang'), (b'Asia/Seoul', b'(GMT+0900) Asia/Seoul'), (b'Asia/Tokyo', b'(GMT+0900) Asia/Tokyo'), (b'Asia/Yakutsk', b'(GMT+0900) Asia/Yakutsk'), (b'Pacific/Palau', b'(GMT+0900) Pacific/Palau'), (b'Australia/Darwin', b'(GMT+0930) Australia/Darwin'), (b'Antarctica/DumontDUrville', b'(GMT+1000) Antarctica/DumontDUrville'), (b'Asia/Magadan', b'(GMT+1000) Asia/Magadan'), (b'Asia/Sakhalin', b'(GMT+1000) Asia/Sakhalin'), (b'Asia/Ust-Nera', b'(GMT+1000) Asia/Ust-Nera'), (b'Asia/Vladivostok', b'(GMT+1000) Asia/Vladivostok'), (b'Australia/Brisbane', b'(GMT+1000) Australia/Brisbane'), (b'Australia/Lindeman', b'(GMT+1000) Australia/Lindeman'), (b'Pacific/Chuuk', b'(GMT+1000) Pacific/Chuuk'), (b'Pacific/Guam', b'(GMT+1000) Pacific/Guam'), (b'Pacific/Port_Moresby', b'(GMT+1000) Pacific/Port_Moresby'), (b'Pacific/Saipan', b'(GMT+1000) Pacific/Saipan'), (b'Australia/Adelaide', b'(GMT+1030) Australia/Adelaide'), (b'Australia/Broken_Hill', b'(GMT+1030) Australia/Broken_Hill'), (b'Antarctica/Macquarie', b'(GMT+1100) Antarctica/Macquarie'), (b'Asia/Srednekolymsk', b'(GMT+1100) Asia/Srednekolymsk'), (b'Australia/Currie', b'(GMT+1100) Australia/Currie'), (b'Australia/Hobart', b'(GMT+1100) Australia/Hobart'), (b'Australia/Lord_Howe', b'(GMT+1100) Australia/Lord_Howe'), (b'Australia/Melbourne', b'(GMT+1100) Australia/Melbourne'), (b'Australia/Sydney', b'(GMT+1100) Australia/Sydney'), (b'Pacific/Bougainville', b'(GMT+1100) Pacific/Bougainville'), (b'Pacific/Efate', b'(GMT+1100) Pacific/Efate'), (b'Pacific/Guadalcanal', b'(GMT+1100) Pacific/Guadalcanal'), (b'Pacific/Kosrae', b'(GMT+1100) Pacific/Kosrae'), (b'Pacific/Noumea', b'(GMT+1100) Pacific/Noumea'), (b'Pacific/Pohnpei', b'(GMT+1100) Pacific/Pohnpei'), (b'Pacific/Norfolk', b'(GMT+1130) Pacific/Norfolk'), (b'Asia/Anadyr', b'(GMT+1200) Asia/Anadyr'), (b'Asia/Kamchatka', b'(GMT+1200) Asia/Kamchatka'), (b'Pacific/Funafuti', b'(GMT+1200) Pacific/Funafuti'), (b'Pacific/Kwajalein', b'(GMT+1200) Pacific/Kwajalein'), (b'Pacific/Majuro', b'(GMT+1200) Pacific/Majuro'), (b'Pacific/Nauru', b'(GMT+1200) Pacific/Nauru'), (b'Pacific/Tarawa', b'(GMT+1200) Pacific/Tarawa'), (b'Pacific/Wake', b'(GMT+1200) Pacific/Wake'), (b'Pacific/Wallis', b'(GMT+1200) Pacific/Wallis'), (b'Antarctica/McMurdo', b'(GMT+1300) Antarctica/McMurdo'), (b'Pacific/Auckland', b'(GMT+1300) Pacific/Auckland'), (b'Pacific/Enderbury', b'(GMT+1300) Pacific/Enderbury'), (b'Pacific/Fakaofo', b'(GMT+1300) Pacific/Fakaofo'), (b'Pacific/Fiji', b'(GMT+1300) Pacific/Fiji'), (b'Pacific/Tongatapu', b'(GMT+1300) Pacific/Tongatapu'), (b'Pacific/Chatham', b'(GMT+1345) Pacific/Chatham'), (b'Pacific/Apia', b'(GMT+1400) Pacific/Apia'), (b'Pacific/Kiritimati', b'(GMT+1400) Pacific/Kiritimati')])),
                ('language', models.CharField(default=b'en', max_length=10, verbose_name='language', choices=[(b'af', b'Afrikaans'), (b'ar', b'Arabic'), (b'ast', b'Asturian'), (b'az', b'Azerbaijani'), (b'bg', b'Bulgarian'), (b'be', b'Belarusian'), (b'bn', b'Bengali'), (b'br', b'Breton'), (b'bs', b'Bosnian'), (b'ca', b'Catalan'), (b'cs', b'Czech'), (b'cy', b'Welsh'), (b'da', b'Danish'), (b'de', b'German'), (b'el', b'Greek'), (b'en', b'English'), (b'en-au', b'Australian English'), (b'en-gb', b'British English'), (b'eo', b'Esperanto'), (b'es', b'Spanish'), (b'es-ar', b'Argentinian Spanish'), (b'es-mx', b'Mexican Spanish'), (b'es-ni', b'Nicaraguan Spanish'), (b'es-ve', b'Venezuelan Spanish'), (b'et', b'Estonian'), (b'eu', b'Basque'), (b'fa', b'Persian'), (b'fi', b'Finnish'), (b'fr', b'French'), (b'fy', b'Frisian'), (b'ga', b'Irish'), (b'gl', b'Galician'), (b'he', b'Hebrew'), (b'hi', b'Hindi'), (b'hr', b'Croatian'), (b'hu', b'Hungarian'), (b'ia', b'Interlingua'), (b'id', b'Indonesian'), (b'io', b'Ido'), (b'is', b'Icelandic'), (b'it', b'Italian'), (b'ja', b'Japanese'), (b'ka', b'Georgian'), (b'kk', b'Kazakh'), (b'km', b'Khmer'), (b'kn', b'Kannada'), (b'ko', b'Korean'), (b'lb', b'Luxembourgish'), (b'lt', b'Lithuanian'), (b'lv', b'Latvian'), (b'mk', b'Macedonian'), (b'ml', b'Malayalam'), (b'mn', b'Mongolian'), (b'mr', b'Marathi'), (b'my', b'Burmese'), (b'nb', b'Norwegian Bokmal'), (b'ne', b'Nepali'), (b'nl', b'Dutch'), (b'nn', b'Norwegian Nynorsk'), (b'os', b'Ossetic'), (b'pa', b'Punjabi'), (b'pl', b'Polish'), (b'pt', b'Portuguese'), (b'pt-br', b'Brazilian Portuguese'), (b'ro', b'Romanian'), (b'ru', b'Russian'), (b'sk', b'Slovak'), (b'sl', b'Slovenian'), (b'sq', b'Albanian'), (b'sr', b'Serbian'), (b'sr-latn', b'Serbian Latin'), (b'sv', b'Swedish'), (b'sw', b'Swahili'), (b'ta', b'Tamil'), (b'te', b'Telugu'), (b'th', b'Thai'), (b'tr', b'Turkish'), (b'tt', b'Tatar'), (b'udm', b'Udmurt'), (b'uk', b'Ukrainian'), (b'ur', b'Urdu'), (b'vi', b'Vietnamese'), (b'zh-cn', b'Simplified Chinese'), (b'zh-hans', b'Simplified Chinese'), (b'zh-hant', b'Traditional Chinese'), (b'zh-tw', b'Traditional Chinese')])),
                ('approved', models.BooleanField(default=True)),
                ('classic_mode', models.SmallIntegerField(default=0)),
                ('user', models.ForeignKey(related_name='account', verbose_name='user', to=settings.AUTH_USER_MODEL, unique=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OtherServiceInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(max_length=50, verbose_name='Other Service Info Key')),
                ('value', models.TextField(verbose_name='Other Service Info Value')),
                ('user', models.ForeignKey(verbose_name='user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PasswordReset',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('temp_key', models.CharField(max_length=100, verbose_name='temp_key')),
                ('timestamp', models.DateTimeField(default=datetime.datetime.now, verbose_name='timestamp')),
                ('reset', models.BooleanField(default=False, verbose_name='reset yet?')),
                ('user', models.ForeignKey(verbose_name='user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='otherserviceinfo',
            unique_together=set([('user', 'key')]),
        ),
    ]
