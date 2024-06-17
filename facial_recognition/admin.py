from django.contrib import admin

from .models import *

admin.site.register(CheckInAndOut)
admin.site.register(BreakInAndOut)
admin.site.register(TimeSheet)
admin.site.register(AttendanceBilling)
