from django.db import models
from accounts.models import BaseModel , UserAccount

class CheckInAndOut(BaseModel):

    CHECK_CHOICES = [
        ('checkin', 'CheckIn'),
        ('checkout', 'CheckOut'),       
    ]

    type = models.CharField(max_length=100, choices=CHECK_CHOICES , blank = True , null = True)
    user = models.ForeignKey(UserAccount , related_name='checks' , on_delete=models.CASCADE)
    image = models.FileField(upload_to='attendance_images/', null=True, blank=True)


class BreakInAndOut(BaseModel):

    BREAK_CHOICES = [
        ('breakin', 'BreakIn'),
        ('breakout', 'BreakOut'),       
    ]

    type = models.CharField(max_length=100, choices=BREAK_CHOICES , blank = True , null = True)
    user = models.ForeignKey(UserAccount , related_name='breaks' , on_delete=models.CASCADE)
    image = models.FileField(upload_to='attendance_images/', null=True, blank=True)

class TimeSheet(BaseModel):

    user = models.ForeignKey(UserAccount , related_name='timesheets' , on_delete=models.CASCADE)
    date = models.DateField(blank = True , null = True)
    working_time = models.DurationField( blank = True , null = True)
    break_time = models.DurationField(blank = True , null = True)





