from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from app_settings.models import *
from django.db.models import Max


class BaseModel(models.Model):
    updated_by = models.ForeignKey(
        'accounts.UserAccount',
        related_name='%(class)s_updates',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    created_by = models.ForeignKey(
        'accounts.UserAccount',
        related_name='%(class)s_creators',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    company = models.ForeignKey(
        Company, related_name='%(class)s', on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class UserAccountManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)

        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class Agency(BaseModel):

    name = models.CharField(max_length=255)
    agency_id = models.CharField(max_length=10)
    agency_owner = models.CharField(max_length=255, blank=True, null=True)
    gst = models.CharField(max_length=255, blank=True, null=True)
    labour_license = models.FileField(
        upload_to='agency_documents/', null=True, blank=True)
    pan = models.FileField(upload_to='agency_documents/',
                           null=True, blank=True)
    wcp = models.FileField(upload_to='agency_documents/',
                           null=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        try:
            if not self.pk:
                super().save(*args, **kwargs)  # Save the object to assign the primary key
                # Assign agency_id based on the auto-generated primary key
                self.agency_id = f"A-{self.pk:06}"
                self.save()  # Save again to update agency_id
            else:
                super().save(*args, **kwargs)
        except Exception as e:
            # Handle the exception here
            print(f"Error occurred while saving: {e}")


class Category(BaseModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class SubCategory(BaseModel):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(
        Category, related_name='sub_categories', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name


class Location(BaseModel):
    name = models.CharField(max_length=255)
    company = models.ForeignKey(
        Company, related_name='locations', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name


class Project(BaseModel):
    name = models.CharField(max_length=255)
    location = models.ForeignKey(
        Location, related_name='projects', on_delete=models.CASCADE, null=True)
    category = models.ForeignKey(
        Category, related_name='projects',  on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name


class UserAccount(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(max_length=255, unique=True)
    emp_id = models.CharField(
        max_length=255, unique=True, null=True, blank=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=13, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        'self',
        related_name='created_users',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        to_field='id'
    )
    company = models.ForeignKey(
        Company, related_name='user_accounts', on_delete=models.CASCADE, null=True, blank=True)
    user_image = models.FileField(
        upload_to='user_images/', null=True, blank=True)
    is_contract_worker = models.BooleanField(default=False)
    is_supervisor = models.BooleanField(default=False)
    is_supervisor_admin = models.BooleanField(default=False)
    agency = models.ForeignKey(
        Agency, related_name='user_accounts', on_delete=models.CASCADE, null=True, blank=True)
    dob = models.DateField(blank=True, null=True)
    age = models.IntegerField(null=True, blank=True)
    aadhaar_card = models.FileField(
        upload_to='user_files/', null=True, blank=True)
    pan = models.FileField(upload_to='user_files/', null=True, blank=True)
    mobile = models.CharField(max_length=255, blank=True, null=True)
    location = models.ForeignKey(
        Location, related_name='user_accounts', on_delete=models.SET_NULL, null=True, blank=True)
    sub_category = models.ForeignKey(
        SubCategory, related_name='user_accounts', on_delete=models.SET_NULL, null=True, blank=True)
    objects = UserAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def get_full_name(self):
        if self.last_name and self.first_name:
            return "{fname} {lname}".format(fname=self.first_name, lname=self.last_name)
        elif not self.last_name:
            return "{fname}".format(fname=self.first_name)
        else:
            return ""

    def __str__(self):
        return self.email

    # def save(self, *args, **kwargs):
    #     try:
    #         if not self.pk:
    #             super().save(*args, **kwargs)  # Save the object to assign the primary key
    #             # Assign emp_id based on the auto-generated primary key

    #             if self.is_contract_worker:
    #                 self.emp_id = f"CW-{self.pk:06}"
    #                 self.save()  # Save again to update agency_id
    #         else:
    #             super().save(*args, **kwargs)
    #     except Exception as e:
    #         # Handle the exception here
    #         print(f"Error occurred while saving: {e}")

    def save(self, *args, **kwargs):
        try:
            if not self.emp_id:
                # If emp_id is not provided, generate it based on the auto-generated primary key
                if not self.pk:
                    super().save(*args, **kwargs)  # Save the object to assign the primary key
                    # Assign emp_id based on the auto-generated primary key
                    if self.is_contract_worker:
                        self.emp_id = f"CW-{self.pk:06}"
                        super().save(*args, **kwargs)  # Save again to update emp_id
                else:
                    # Primary key is already generated
                    if self.is_contract_worker:
                        self.emp_id = f"CW-{self.pk:06}"
                        super().save(*args, **kwargs)  # Save again to update emp_id
            else:
                # If emp_id is provided (through Excel or otherwise), use the provided one
                super().save(*args, **kwargs)
        except Exception as e:
            # Handle the exception here
            print(f"Error occurred while saving: {e}")


class UserDocument(BaseModel):
    user = models.ForeignKey(
        UserAccount, related_name='user_documents', on_delete=models.CASCADE)
    document = models.FileField(upload_to='user_documents/')

    def __str__(self):
        return self.user.email
