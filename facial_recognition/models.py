from django.db import models
from accounts.models import BaseModel , UserAccount , Project, Location

class CheckInAndOut(BaseModel):

    CHECK_CHOICES = [
        ('checkin', 'CheckIn'),
        ('checkout', 'CheckOut'),       
    ]

    type = models.CharField(max_length=100, choices=CHECK_CHOICES , blank = True , null = True)
    user = models.ForeignKey(UserAccount , related_name='checks' , on_delete=models.CASCADE)
    image = models.URLField(null=True, blank=True)
    project = models.ForeignKey(Project , related_name = 'check_ins_and_check_outs' , on_delete = models.SET_NULL , blank = True , null = True)
    location =models.ForeignKey(Location, related_name = 'check_ins_and_check_outs', on_delete = models.SET_NULL, blank = True, null = True)


class BreakInAndOut(BaseModel):

    BREAK_CHOICES = [
        ('breakin', 'BreakIn'),
        ('breakout', 'BreakOut'),       
    ]

    type = models.CharField(max_length=100, choices=BREAK_CHOICES , blank = True , null = True)
    user = models.ForeignKey(UserAccount , related_name='breaks' , on_delete=models.CASCADE)
    image = models.URLField(null=True, blank=True)
    project = models.ForeignKey(Project , related_name = 'break_ins_and_break_outs' , on_delete = models.SET_NULL , blank = True , null = True)
    location =models.ForeignKey(Location, related_name = 'break_ins_and_break_outs', on_delete = models.SET_NULL, blank = True, null = True)

class TimeSheet(BaseModel):

    user = models.ForeignKey(UserAccount , related_name='timesheets' , on_delete=models.CASCADE)
    date = models.DateField(blank = True , null = True)
    working_time = models.DurationField( blank = True , null = True)
    break_time = models.DurationField(blank = True , null = True)





