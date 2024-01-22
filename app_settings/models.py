from django.db import models

# Create your models here.

class Module(models.Model):
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name
    
class Customer(models.Model):
    name = models.CharField(max_length=255)
    api_key = models.CharField(max_length=255)
    modules = models.ManyToManyField(Module,related_name='customers')

    def __str__(self):
        return self.name

class Company(models.Model):
    name = models.CharField(max_length=255)
    customer = models.ForeignKey(Customer,related_name='companies', on_delete=models.CASCADE)
    def __str__(self):
        return self.name

