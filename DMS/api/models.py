from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
import os

# Create your models here.

#File Model
class File(models.Model):
    file = models.FileField(upload_to='uploads/', blank=True, null=True)
    file_name = models.CharField(max_length=100, null=True, blank=True)
    client = models.ForeignKey('Client', related_name='files', on_delete=models.CASCADE)

    # def __str__(self):
    #     if self.file:
    #         return self.file_name  # Return the file name in the admin panel
    #     return 'No file'


# Client Model
class Client(models.Model):
    entites = [
       ('proprietorship','Proprietorship'),
       ('partnership', 'Partnership'),
       ('llp', 'LLP'),
       ('opc', 'OPC'),
       ('huf', 'HUF'),
       ('private ltd', 'Private Ltd'),
       ('Public Limited', 'public limited'),
       ('trust', 'Trust')
    ]

    client_name = models.CharField(max_length=100, null=True, blank=True)
    entity_type = models.CharField(max_length=100, choices=entites, null=True, blank=True)
    # default_share = models.IntegerField(default=100, null=True, blank=True)
    date_of_incorporation = models.DateField(null=True, blank=True)
    contact_person = models.CharField(max_length=100, null=True, blank=True)
    designation = models.CharField(max_length=100, null=True, blank=True)
    contact_no_1 = models.IntegerField(null=True, blank=True)
    contact_no_2 = models.IntegerField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    business_detail = models.TextField(null=True, blank=True)
    # mom = models.ManyToManyField(File, related_name='mom_files', blank=True)
    # pf = models.ManyToManyField(File, related_name='pf_files', blank=True)
    # file_name = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=40, null=True, blank=True)
    # file_names = models.ManyToManyField(File, related_name='file_names', blank=True)
    # files = models.ManyToManyField(File, related_name='files', blank=True)
    

    def __str__(self):
        return self.client_name  if self.client_name else 'No name provided'

# Bank Model
class Bank(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True)
    bank_name = models.CharField(max_length=100, null=True, blank=True)
    account_no = models.IntegerField(null=True, blank=True)
    ifsc = models.CharField(max_length=50, null=True, blank=True)
    account_type = models.CharField(max_length=50, null=True, blank=True)
    branch = models.CharField(max_length=100, null=True, blank=True)
    attachment = models.FileField(null=True, blank=True)

    def __str__(self):
        return self.bank_name

#Owner Model
class Owner(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True)
    owner_name = models.CharField(max_length=100, null=True, blank=True)
    share = models.IntegerField()
    pan = models.CharField(max_length=10, null=True, blank=True)
    aadhar = models.CharField(max_length=12, null=True, blank=True)
    mobile = models.IntegerField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    it_password = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.owner_name

#User Model
class CustomUser(AbstractUser):

    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',  # Unique related_name for groups
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_permissions_set',  # Unique related_name for permissions
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )
    # first_name = models.CharField(max_length=100, null=True, blank=True)
    # last_name = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    ca_admin = models.BooleanField(default=False, null=True, blank=True)
    ca_user = models.BooleanField(null=True, blank=True)
    cus_admin = models.BooleanField(default=False, null=True, blank=True)
    cus_user = models.BooleanField(null=True, blank=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True)

# CompanyDocument Model
class CompanyDocument(models.Model):

    document_type = [
        ('pan', 'PAN'),
        ('tan', 'TAN'),
        ('msme','MSME'),
        ('udym', 'UDYM'),
        ('mca', 'MCA'),
        ('pf', 'PF'),
        ('esic', 'ESIC'),
        ('other', 'OTHER'),
    ]
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True)
    document_type = models.CharField(max_length=100, choices=document_type, null=True, blank=True)
    login = models.CharField(max_length=100, null=True, blank=True)
    password = models.CharField(max_length=100, null=True, blank=True)
    remark = models.TextField(null=True, blank=True)
    file = models.FileField(null=True, blank=True)


#Branch Model
class Branch(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True)
    branch_name = models.CharField(max_length=100, null=True, blank=True)
    contact = models.IntegerField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    gst_no = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.branch_name

#OfficeLocation Model
class OfficeLocation(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    contact = models.IntegerField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.location

# Branch Document Model
class BranchDocument(models.Model):
    document_type = [
        ('ptec', 'PTEC'),
        ('ptrc', 'PTRC'),
        ('gst', 'GST'),
        ('eway', 'EWAY'),
        ('other', 'OTHER'),
    ]
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True, blank=True)
    document_type = models.CharField(max_length=100, choices=document_type, null=True, blank=True)
    login = models.CharField(max_length=100, null=True, blank=True)
    password = models.CharField(max_length=100, null=True, blank=True)
    remark = models.TextField(null=True, blank=True)
    file = models.FileField(null=True, blank=True)

#Customer or Vendor Model
class Customer(models.Model):
   name = models.CharField(max_length=100, null=True, blank=True)
   gst_no = models.CharField(max_length=100, null=True, blank=True)
   pan = models.CharField(max_length=100, null=True, blank=True)
   address = models.TextField(null=True, blank=True)
#    type = models.CharField(max_length=100, choices=type_choices, null=True, blank=True)
   client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True)
   customer = models.BooleanField(null=True, blank=True)
   vendor = models.BooleanField(null=True, blank=True)

   def __str__(self):
        return self.name

#HSN Code Model
class HSNCode(models.Model):
    hsn_code = models.IntegerField(null=True, blank=True)
    gst_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

#Sales Invoice Model
class SalesInvoice(models.Model):

    invoice_type = [
        ('b2b', 'B2B'),
        ('b2c-l', 'B2C-L'),
        ('bsc-o', 'BSC-O'),
        ('nil rated', 'Nil Rated'),
        ('advance received', 'Advance Received'),
        ('export', 'Export'),
        ('unregistered local', 'Unregistered Local'),
    ]

    entry_type = [
        ('sales_invoice', 'Sales_Invoice'),
        ('debit_note', 'Debit Note'),
        ('income', 'Income'),
    ]
    client_Location = models.ForeignKey(OfficeLocation, on_delete=models.CASCADE, null=True, blank=True)
    attach_invoice = models.FileField(null=True, blank=True)
    attach_e_way_bill = models.FileField(null=True, blank=True)
    month = models.DateField(null=True, blank=True)
    cutomer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    invoice_no = models.CharField(max_length=100, null=True, blank=True)
    invoice_date = models.DateField(null=True, blank=True)
    invoice_type = models.CharField(max_length=100, choices=invoice_type, null=True, blank=True)
    entry_type = models.CharField(max_length=100, choices=entry_type, null=True, blank=True)
    hsn = models.ForeignKey(HSNCode, on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    unit_of_measure = models.CharField(max_length=100, null=True, blank=True)
    unit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    taxable_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cgst = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sgst = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    igst = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_invoice_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tds_tcs_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tds_tcs_section = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tcs = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tds = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    amount_receivable = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

#Purchase Invoice Model
class PurchaseInvoice(models.Model):
   entry_type = [
        ('purchase_invoice', 'Purchase_Invoice'),
        ('credit_note', 'Credit Note'),
        ('expenses', 'Expenses'),
    ]
   client_Location = models.ForeignKey(OfficeLocation, on_delete=models.CASCADE, null=True, blank=True)
   attach_invoice = models.FileField(null=True, blank=True)
   attach_e_way_bill = models.FileField(null=True, blank=True)
   utilise_credit = models.BooleanField(null=True, blank=True)
   month = models.DateField(null=True, blank=True)
   vendor = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
   invoice_no = models.CharField(max_length=100, null=True, blank=True)
   invoice_date = models.DateField(null=True, blank=True)
   entry_type = models.CharField(max_length=100, choices=entry_type, null=True, blank=True)
   hsn = models.ForeignKey(HSNCode, on_delete=models.CASCADE, null=True, blank=True)
   description = models.TextField(null=True, blank=True)
   unit_of_measure = models.CharField(max_length=100, null=True, blank=True)
   unit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
   rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
   taxable_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
   cgst = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
   sgst = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
   igst = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
   total_invoice_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
   tds_tcs_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
   tds_tcs_section = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
   tcs = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
   tds = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
   amount_receivable = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)


# Income Tax Document
class IncomeTaxDocument(models.Model):
    frequency_choices = [
        ('26as', '26AS'),
        ('form_16', 'FORM 16'),
        ('bank_statement', 'BANK_STATEMENT')
    ]
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank= True)
    document_type = models.CharField(max_length=100, choices=frequency_choices, null=True, blank=True)
    financial_year = models.IntegerField(null=True, blank=True)
    month = models.DateField(null=True, blank=True)
    attachment = models.FileField(null=True, blank=True)

#PF
class PF(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True,  related_name='pf_files')
    employee_code = models.CharField(max_length=100, null=True, blank=True)
    employee_name = models.CharField(max_length=100, null=True, blank=True)
    uan = models.CharField(max_length=100, null=True, blank=True)
    pf_number = models.CharField(max_length=100, null=True, blank=True)
    pf_deducted = models.BooleanField(null=True, blank=True)
    date_of_joining = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=100, null=True, blank=True)
    month = models.DateField(null=True, blank=True)
    gross_ctc = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    basic_pay = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    hra = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    statutory_bouns =models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    special_allowance = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    pf = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    gratutiy = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    total_gross_salary = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=False)
    number_of_days_in_month = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=False)
    present_days = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=False)
    lwp = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=False)
    leave_adjustment = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=False)
    gender = models.CharField(max_length=100, null=True, blank=True)
    basic_pay_monthly = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=False)
    hra_monthly = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=False)
    statutory_bonus_monthly = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=False)
    special_allowance_monthly = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=False)
    total_gross_salary_monthly = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=False)
    provident_fund = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=False)
    professional_tax = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=False)
    advance = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=False)
    esic_employee = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=False)
    tds = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=False)
    total_deduction = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=False)
    net_pay = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=False)
    advance_esic_employer_cont =models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=False)


