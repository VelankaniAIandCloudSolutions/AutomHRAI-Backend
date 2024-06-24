from django.utils import timezone
from django.db import models

# Create your models here.


class Module(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Customer(models.Model):
    name = models.CharField(max_length=255)
    api_key = models.CharField(max_length=255)
    modules = models.ManyToManyField(Module, related_name='customers')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Company(models.Model):
    name = models.CharField(max_length=255)
    ref_id = models.IntegerField(null=True, blank=True)
    customer = models.ForeignKey(
        Customer, related_name='companies', on_delete=models.CASCADE)
    cut_off_time = models.TimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

# class Entity(models.Model):
#     name = models.CharField(max_length=200)
#     ref_id = models.IntegerField(null=True, blank=True)
#     company = models.ForeignKey(Company, related_name='entities', on_delete=models.SET_NULL, null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return self.name
