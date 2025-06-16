from rest_framework import serializers
from rest_framework.parsers import MultiPartParser, FormParser
from api.models import *
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime
import json
from decimal import Decimal, InvalidOperation
from django.contrib.auth.hashers import make_password
from django.template.loader import render_to_string # used returns the resulting content as a string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode #  used to safely encode and decode data in a URL-friendly format
from .utils import TokenGenerator, generate_token
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError #  helps in managing string and byte conversions
from django.core.mail import EmailMessage # used to construct and send email messages
from django.conf import settings

# File Serializer
class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ['id', 'files', 'fileinfo']

class FileInfoSerializer(serializers.ModelSerializer):
    files = FileSerializer(many=True, required=False)

    class Meta:
        model = FileInfo
        fields = ['id', 'document_type', 'login', 'password', 'remark', 'files']

    def create(self, validated_data):
        files_data = validated_data.pop('files', [])
        file_info = FileInfo.objects.create(**validated_data)
        for file_data in files_data:
            File.objects.create(fileinfo=file_info, **file_data)
        return file_info

    def update(self, instance, validated_data):
        files_data = validated_data.pop('files', [])
        instance.document_type = validated_data.get('document_type', instance.document_type)
        instance.login = validated_data.get('login', instance.login)
        instance.password = validated_data.get('password', instance.password)
        instance.remark = validated_data.get('remark', instance.remark)
        instance.save()

        # Clear existing files and add new ones
        # instance.files.all().delete()
        for file_data in files_data:
            File.objects.create(fileinfo=instance, **file_data)
        return instance


class ClientSerializer(serializers.ModelSerializer):
    fileinfos = FileInfoSerializer(many=True, required=False)
    date_of_incorporation =  serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)
    # invoice_date = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)


    class Meta:
        model = Client
        fields = ['id', 'client_name', 'entity_type', 'date_of_incorporation',
                  'contact_person', 'designation', 'contact_no_1',
                  'contact_no_2', 'email', 'business_detail',
                  'status', 'fileinfos']

    def create(self, validated_data):
        fileinfos_data = validated_data.pop('fileinfos', [])
        client = Client.objects.create(**validated_data)

        for fileinfo_data in fileinfos_data:
            # Only create FileInfo if required fields are present
            if any(fileinfo_data.values()):
                files_data = fileinfo_data.pop('files', [])
                file_info = FileInfo.objects.create(client=client, **fileinfo_data)
                for file_data in files_data:
                    File.objects.create(fileinfo=file_info, **file_data)

        return client

    def update(self, instance, validated_data):
        fileinfos_data = validated_data.pop('fileinfos', [])
        instance.client_name = validated_data.get('client_name', instance.client_name)
        instance.entity_type = validated_data.get('entity_type', instance.entity_type)
        instance.date_of_incorporation = validated_data.get('date_of_incorporation', instance.date_of_incorporation)
        instance.contact_person = validated_data.get('contact_person', instance.contact_person)
        instance.designation = validated_data.get('designation', instance.designation)
        instance.contact_no_1 = validated_data.get('contact_no_1', instance.contact_no_1)
        instance.contact_no_2 = validated_data.get('contact_no_2', instance.contact_no_2)
        instance.email = validated_data.get('email', instance.email)
        instance.business_detail = validated_data.get('business_detail', instance.business_detail)
        instance.status = validated_data.get('status', instance.status)
        instance.save()

        for fileinfo_data in fileinfos_data:
            # Only create FileInfo if required fields are present
            if any(fileinfo_data.values()):
                files_data = fileinfo_data.pop('files', [])
                file_info = FileInfo.objects.create(client=instance, **fileinfo_data)
                for file_data in files_data:
                    File.objects.create(fileinfo=file_info, **file_data)

        return instance

class FileInfoCreateSerializer(serializers.ModelSerializer):
    files = FileSerializer(many=True, required=False)

    class Meta:
        model = FileInfo
        fields = ['id', 'document_type', 'login', 'password', 'remark', 'files']

    def create(self, validated_data):
        files_data = validated_data.pop('files', [])
        client = validated_data.pop('client')  # Get client instance from validated data
        file_info = FileInfo.objects.create(client=client, **validated_data)
        for file_data in files_data:
            File.objects.create(fileinfo=file_info, **file_data)
        return file_info


# Bank
class BankSerializer(serializers.ModelSerializer):
    files = serializers.SerializerMethodField()

    class Meta:
        model = Bank
        fields = ['id','client','bank_name','account_no','ifsc','account_type','branch','files']

    def get_files(self, obj):
        files = Files.objects.filter(bank=obj)
        return FilesSerializer(files, many=True).data

# Acknowledgement

# class AcknowledgementSerializer(serializers.ModelSerializer):
#     return_file = serializers.SerializerMethodField()
#     computation_file = serializers.SerializerMethodField()

#     class Meta:
#         model = Acknowledgement
#         fields = ['id','client','return_type','frequency','return_period','from_date','to_date','client_review','month','remarks','status','return_file','computation_file']

    
#     def get_return_file(self, obj):
#         return_file = Files.objects.filter(ack=obj)
#         return FilesSerializer(return_file, many=True).data

#     def get_computation_file(self, obj):
#         computation_file = Files.objects.filter(ack=obj)
#         return FilesSerializer(computation_file, many=True).data
        
        
#         def validate(self, data):
#         # Ensure 'remarks' is required when 'client_review' is 'remark'
#             if data.get('client_review') == 'remark' and not data.get('remarks'):
#                 raise serializers.ValidationError({"remarks": "This field is required when client_review is 'Remark'."})
#             return data

class AcknowledgementSerializer(serializers.ModelSerializer):
    return_file = serializers.SerializerMethodField()
    computation_file = serializers.SerializerMethodField()
    from_date = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"])
    to_date = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"])

    class Meta:
        model = Acknowledgement
        fields = ['id', 'client', 'return_type', 'frequency', 'return_period', 
                  'from_date', 'to_date', 'client_review', 'month', 'remarks', 
                  'status', 'return_file', 'computation_file']

    def get_return_file(self, obj):
        return_files = Files.objects.filter(ack=obj).exclude(return_file="")  # Fetch only non-empty return files
        return FilesSerializer(return_files, many=True).data

    def get_computation_file(self, obj):
        computation_file = Files.objects.filter(ack=obj).exclude(computation_file="")  # Fetch only non-empty computation files
        return FilesSerializer(computation_file, many=True).data

    def validate(self, data):
        if data.get('client_review') == 'remark' and not data.get('remarks'):
            raise serializers.ValidationError({"remarks": "This field is required when client_review is 'remark'."})
        return data





# Owner Serializer
class OwnerSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Owner
        fields = '__all__'

    # def validate(self, data):
    #     email = data.get('email')
    #     if email and CustomUser.objects.filter(email=email).exists():
    #         raise serializers.ValidationError({'email': 'A user with this email already exists.'})
    #     return data
    def validate(self, data):
        email = data.get('email')

        # When updating, exclude the current user's email from the check
        instance = self.instance
        if email:
            if instance and instance.user:
                if CustomUser.objects.exclude(pk=instance.user.pk).filter(email=email).exists():
                    raise serializers.ValidationError({'email': 'A user with this email already exists.'})
            else:
                if CustomUser.objects.filter(email=email).exists():
                    raise serializers.ValidationError({'email': 'A user with this email already exists.'})
        return data



    
class CustomerVendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

class UserSerializerWithToken(serializers.ModelSerializer):
    # name = serializers.SerializerMethodField(read_only= True)
    token = serializers.SerializerMethodField(read_only = True)
    ca_admin = serializers.SerializerMethodField()
    cus_admin = serializers.SerializerMethodField()
    is_active = serializers.BooleanField(default=False)
    previous_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    # customer = CustomerVendorSerializer(many=False, read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id','username','email','name','password','ca_admin', 'cus_admin','is_active', 'token','client', 'previous_password','new_password','confirm_password']

    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Name cannot be blank.")
        return value
        # mmfm mmmfm mmfmm mmmmf rytyh

    def get_ca_admin(self,obj):
        return obj.is_staff

    def get_cus_admin(self, obj):
        return obj.is_staff

    def get_token(self, obj):
        token = RefreshToken.for_user(obj)
        return str(token.access_token)

# class CompanyFilesSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Files
#         field = '__all__'


# Company Document
class CompanyDocSerailizer(serializers.ModelSerializer):
    files = serializers.SerializerMethodField()

    class Meta:
        model = CompanyDocument
        fields = ['id', 'client', 'document_type', 'login', 'password', 'remark', 'files' ]

    def get_files(self, obj):
        files = Files.objects.filter(company_doc=obj)
        return FilesSerializer(files, many=True).data

# Branch
class BranchSerailizer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = '__all__'

# Office Location
class OfficeLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfficeLocation
        fields = '__all__'

class FilesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Files
        fields = '__all__'


# Branch Document
class BranchDocSerailizer(serializers.ModelSerializer):
    files = serializers.SerializerMethodField()

    class Meta:
        model = BranchDocument
        fields = ['id','branch','document_type','login','password','remark','files']

    def get_files(self, obj):
        files = Files.objects.filter(branch_doc=obj)
        return FilesSerializer(files, many=True).data

# Customer Or Vendor
# class CustomerVendorSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Customer
#         fields = '__all__'

# Incometax Document
class IncomeTaxDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncomeTaxDocument
        fields = '__all__'

# PF
class DateFromDateTimeField(serializers.DateField):
    def to_representation(self, value):
        if isinstance(value, datetime):
            return value.date()  # Convert datetime to date
        return super().to_representation(value)

class PfSerializer(serializers.ModelSerializer):
    date_of_joining = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"])
    class Meta:
        model = PF
        fields = [
            'id','employee_code', 'employee_name', 'uan', 'pf_number', 'pf_deducted',
            'date_of_joining', 'status', 'gender', 'month', 'gross_ctc', 'basic_pay',
            'hra', 'statutory_bonus', 'special_allowance', 'pf', 'gratuity',
            'total_gross_salary', 'number_of_days_in_month', 'present_days',
            'lwp', 'leave_adjustment', 'basic_pay_monthly', 'hra_monthly',
            'statutory_bonus_monthly', 'special_allowance_monthly',
            'total_gross_salary_monthly', 'provident_fund', 'professional_tax',
            'advance', 'esic_employee', 'tds','total_deduction', 'net_pay', 'advance_esic_employer_cont'
            ]

# TDS Payment
class TDSPaymentSerializer(serializers.ModelSerializer):
    date = DateFromDateTimeField()
    date = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"])
    tds_payment_date = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"])
    class Meta:
        model = TDSPayment
        fields = [
            'id','client_name', 'date', 'PAN', 'amount', 
            'cgst', 'sgst', 'igst', 'total_amt', 
            'tds_rate', 'tds_section', 'tds_amount', 
            'net_amount', 'tds_payment_date', 'tds_challan_no',
        ]

# TDS Section
class TDSSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TDSSection
        fields = ['id', 'name']

# Tax Audit
class TaxAuditSerializer(serializers.ModelSerializer):
    files = serializers.SerializerMethodField()

    class Meta:
        model = TaxAudit
        fields = ['id','client','financial_year','month','files']

    def get_files(self, obj):
        files = Files.objects.filter(tax_audit=obj)
        return FilesSerializer(files, many=True).data


# AIR
class AIRSerializer(serializers.ModelSerializer):
    files = serializers.SerializerMethodField()

    class Meta:
        model = AIR
        fields = ['id','client','financial_year','month','files']

    def get_files(self, obj):
        files = Files.objects.filter(air=obj)
        return FilesSerializer(files, many=True).data

# SFT
class SFTSerializer(serializers.ModelSerializer):
    files = serializers.SerializerMethodField()

    class Meta:
        model = SFT
        fields = ['id','client','financial_year','month','files']

    def get_files(self, obj):
        files = Files.objects.filter(sft=obj)
        return FilesSerializer(files, many=True).data

# Others
class OthersSerializer(serializers.ModelSerializer):
    files = serializers.SerializerMethodField()

    class Meta:
        model = Others
        fields = ['id','client','financial_year','month','text','files']

    def get_files(self, obj):
        files = Files.objects.filter(others=obj)
        return FilesSerializer(files, many=True).data

# TDS Return
class TDSReturnSerializer(serializers.ModelSerializer):
    files = serializers.SerializerMethodField()
    challan_date = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"])
    last_filed_return_ack_date = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"])


    class Meta:
        model = TDSReturn
        fields = ['id','client','challan_date','challan_no','challan_type','tds_section','amount','last_filed_return_ack_no','last_filed_return_ack_date','files']

    def get_files(self, obj):
        files = Files.objects.filter(tds=obj)
        return FilesSerializer(files, many=True).data

# # TDS Section
# class TDSSectionSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TDSSection
#         fields = '__all__'

####################################################### Sales Invoice
class SalesSerializer(serializers.ModelSerializer):
    invoice_date = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)
    po_date = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)

    class Meta:
        model = SalesInvoice
        fields = '__all__'

class SalesSerializer3(serializers.ModelSerializer):
    invoice_date = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)
    po_date = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)

    class Meta:
        model = SalesInvoice
        exclude = ['client','client_Location','customer','product_summaries']

class ProductSummarySerializerList(serializers.ModelSerializer):
    hsn_code = serializers.CharField(source="hsn.hsn_code", read_only=True)
    gst_rate = serializers.DecimalField(source="hsn.gst_rate", max_digits=10, decimal_places=2, read_only=True)
    product_name = serializers.CharField(source="product.product_name", read_only=True)
    product_amount = serializers.CharField(source="prod_description.product_amount", read_only=True)
    description_text = serializers.CharField(source="prod_description.description", read_only=True)
    unit = serializers.DecimalField(source="prod_description.unit", max_digits=10, decimal_places=2, read_only=True)
    rate = serializers.DecimalField(source="prod_description.rate", max_digits=10, decimal_places=2, read_only=True)
    cgst = serializers.DecimalField(source="prod_description.cgst", max_digits=10, decimal_places=2, read_only=True)
    sgst = serializers.DecimalField(source="prod_description.sgst", max_digits=10, decimal_places=2, read_only=True)
    igst = serializers.DecimalField(source="prod_description.igst", max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = ProductSummary
        fields = [
            "id",
            "hsn_code",
            "gst_rate",
            "product_name",
            "description_text",
            "unit",
            "rate",
            'cgst',
            'sgst',
            'igst',
            'product_amount'
        ]
# class ProductSummaryPurchaseSerializerList(serializers.ModelSerializer):
#     hsn_code = serializers.CharField(source="hsn.hsn_code", read_only=True)
#     gst_rate = serializers.DecimalField(source="hsn.gst_rate", max_digits=10, decimal_places=2, read_only=True)
#     product_name = serializers.CharField(source="product.product_name", read_only=True)
#     product_amount = serializers.CharField(source="prod_description.product_amount", read_only=True)
#     description_text = serializers.CharField(source="prod_description.description", read_only=True)
#     unit = serializers.DecimalField(source="prod_description.unit", max_digits=10, decimal_places=2, read_only=True)
#     rate = serializers.DecimalField(source="prod_description.rate", max_digits=10, decimal_places=2, read_only=True)
#     cgst = serializers.DecimalField(source="prod_description.cgst", max_digits=10, decimal_places=2, read_only=True)
#     sgst = serializers.DecimalField(source="prod_description.sgst", max_digits=10, decimal_places=2, read_only=True)
#     igst = serializers.DecimalField(source="prod_description.igst", max_digits=10, decimal_places=2, read_only=True)

#     class Meta:
#         model = ProductSummaryPurchase
#         fields = [
#             "id",
#             "hsn_code",
#             "gst_rate",
#             "product_name",
#             "description_text",
#             "unit",
#             "rate",
#             'cgst',
#             'sgst',
#             'igst',
#             'product_amount'
#         ]
# def validate_decimal(value):
#     try:
#         return Decimal(value) if value is not None else Decimal('0.00')
#     except (ValueError, InvalidOperation):
#         raise serializers.ValidationError("Invalid decimal value")

class SalesSerializerList(serializers.ModelSerializer):
    invoice_date = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)
    po_date = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)


    client_name = serializers.CharField(source="client.client_name", read_only=True)
    customer_name = serializers.CharField(source="customer.name", read_only=True)
    customer_gst_no = serializers.CharField(source="customer.gst_no", read_only=True)
    customer_pan = serializers.CharField(source="customer.pan", read_only=True)
    customer_address = serializers.CharField(source="customer.address", read_only=True)
    customer_customer = serializers.CharField(source="customer.customer", read_only=True)
    customer_vendor = serializers.CharField(source="customer.vendor", read_only=True)
    customer_email = serializers.CharField(source="customer.email", read_only=True) #nnnnn
    customer_contact = serializers.CharField(source="customer.contact", read_only=True) #nnnnn
    client_location_name = serializers.CharField(source="client_Location.location", read_only=True)
    contact = serializers.CharField(source="client_Location.contact", read_only=True)
    address = serializers.CharField(source="client_Location.address", read_only=True)
    city = serializers.CharField(source="client_Location.city", read_only=True)
    state = serializers.CharField(source="client_Location.state", read_only=True)
    country = serializers.CharField(source="client_Location.country", read_only=True)
    product_summaries = ProductSummarySerializerList(many=True, read_only=True)

#lllllllllllll
    taxable_amount = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False, allow_null=True, default=None)
    totalall_gst = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False, allow_null=True, default=None)
    total_invoice_value = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False, allow_null=True, default=None)
    amount_receivable = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False, allow_null=True, default=None)
    tcs = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False, allow_null=True, default=None)
    tds = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False, allow_null=True, default=None)
    tds_tcs_rate = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False, allow_null=True, default=None)

    class Meta:
        model = SalesInvoice
        fields = [
            'id',
            "invoice_no",
            "invoice_date",
            "po_no",
            "po_date",
            "invoice_type",
            "entry_type",
            'attach_e_way_bill',
            'attach_invoice',
            "client_name",
            "customer_name",
            "customer_gst_no",
            "customer_pan",
            "customer_address",
            "customer_customer",
            "customer_vendor",
            "customer_email",  #nnnnn
            "customer_contact",  #nnnnn
            "client_location_name",
            "contact",
            "address",
            "city",
            "state",
            "country",
            "taxable_amount",
            "totalall_gst",
            "total_invoice_value",
            "amount_receivable",
            'tcs',
            'tds',
            'tds_tcs_rate',
            'product_summaries'
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Validate Decimal fields
        decimal_fields = ['taxable_amount', 'totalall_gst', 'total_invoice_value', 'amount_receivable', 'tcs', 'tds', 'tds_tcs_rate']
        for field in decimal_fields:
            try:
                if data[field] is not None:
                    data[field] = Decimal(data[field])
            except (InvalidOperation, ValueError, TypeError):
                data[field] = 'Invalid Value'
        return data

class SalesSerializer2(serializers.ModelSerializer):
    class Meta:
        model = SalesInvoice
        fields = ['attach_invoice','client']

class SalesSerializer2(serializers.ModelSerializer):
    attach_invoice = serializers.FileField()

    class Meta:
        model = SalesInvoice  # Your model where the file should be saved
        fields = ['attach_invoice', 'client']

# class SalesSer


class HSNSerializer(serializers.ModelSerializer):
    class Meta:
        model = HSNCode
        fields = ['id','hsn_code', 'gst_rate']

class ProductSerializer(serializers.ModelSerializer):
    hsn_code = serializers.CharField(source='hsn.hsn_code', read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'product_name', 'hsn_code', 'hsn', 'unit_of_measure']
        extra_kwargs = {
            'product_name': {'validators': []},  # Disable default unique validator
        }

    def validate(self, data):
        product_name = data.get('product_name')
        hsn = data.get('hsn')

        if Product.objects.filter(product_name=product_name, hsn=hsn).exists():
            raise serializers.ValidationError({"error_message":"A product with this name and HSN code already exists."})
        return data

class ProductDescriptionSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.product_name', read_only=True)

    class Meta:
        model = ProductDescription
        fields = ['id', 'description', 'unit', 'rate','product_name','product','product_amount','cgst','sgst','igst']

    # def validate(self, data):
    #     product_name = data.get('product_name')

    #     if ProductDescription.filter(product_name=product_name).exists():
    #         raise serializer.ValidationError({"error_message":"Product name already exists"})

# class ProductSummarySerializer(serializers.ModelSerializer):
#     gst_rate = serializers.CharField(source='hsn.gst_rate', read_only=True)
#     hsn_code = serializers.CharField(source='hsn.hsn_code', read_only=True)
#     product_name = serializers.CharField(source='product.product_name', read_only=True)
#     description = serializers.CharField(source='prod_description.description', read_only=True)
#     unit = serializers.CharField(source='prod_description.unit', read_only=True)
#     rate = serializers.CharField(source='prod_description.rate', read_only=True)

#     class Meta:
#         model = ProductSummary
#         fields = ['id','hsn','product','prod_description','hsn_code','gst_rate','product_name','unit','rate','description']

class ProductSummarySerializer(serializers.ModelSerializer):
    gst_rate = serializers.CharField(source='hsn.gst_rate', read_only=True)
    hsn_code = serializers.CharField(source='hsn.hsn_code', read_only=True)
    product_name = serializers.CharField(source='product.product_name', read_only=True)
    product_amount = serializers.CharField(source='prod_description.product_amount', read_only=True)
    description = serializers.CharField(source='prod_description.description', read_only=True)
    unit = serializers.CharField(source='prod_description.unit', read_only=True)
    rate = serializers.CharField(source='prod_description.rate', read_only=True)

    class Meta:
        model = ProductSummary
        fields = ['id', 'hsn', 'product', 'prod_description', 'hsn_code', 'gst_rate', 'product_name', 'product_amount','description', 'unit', 'rate']

#******************************************************Purchase

class PurchaseSerializer(serializers.ModelSerializer):
    # invoice_date = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"])
    invoice_date = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)
    month = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)
    utilise_month = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)
    # invoice_date = serializers.DateField(format="%d/%m/%Y", required=False)

    class Meta:
        model = PurchaseInvoice
        fields = [
            'id', 'client', 'client_Location', 'attach_invoice', 'attach_e_way_bill', 'month',
            'vendor', 'invoice_no', 'invoice_date', 'invoice_type', 'entry_type',
            'product_summaries', 'taxable_amount', 'totalall_gst', 'total_invoice_value',
            'tds_tcs_rate', 'tcs', 'tds', 'amount_receivable', 'utilise_edit', 'utilise_month'
        ]



    # class Meta:
    #     model = PurchaseInvoice
    #     fields = '__all__'

class PurchaseSerializer3(serializers.ModelSerializer):
    invoice_date = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)
    month = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)
    utilise_month = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)
    class Meta:
        model = PurchaseInvoice
        exclude = ['client','client_Location','vendor','product_summaries']

class ProductSummaryPurchaseSerializerList(serializers.ModelSerializer):
    # invoice_date = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)
    # month = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)

    hsn_code = serializers.CharField(source="hsn.hsn_code", read_only=True, allow_null=True)
    gst_rate = serializers.DecimalField(source="hsn.gst_rate", max_digits=10, decimal_places=2, read_only=True)
    product_name = serializers.CharField(source="product.product_name", read_only=True)
    product_amount = serializers.CharField(source="prod_description.product_amount", read_only=True)
    description_text = serializers.CharField(source="prod_description.description", read_only=True)
    unit = serializers.DecimalField(source="prod_description.unit", max_digits=10, decimal_places=2, read_only=True)
    rate = serializers.DecimalField(source="prod_description.rate", max_digits=10, decimal_places=2, read_only=True)
    cgst = serializers.DecimalField(source="prod_description.cgst", max_digits=10, decimal_places=2, read_only=True)
    sgst = serializers.DecimalField(source="prod_description.sgst", max_digits=10, decimal_places=2, read_only=True)
    igst = serializers.DecimalField(source="prod_description.igst", max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = ProductSummaryPurchase
        fields = [
            "id",
            "hsn_code",
            "gst_rate",
            "product_name",
            "description_text",
            "unit",
            "rate",
            'cgst',
            'sgst',
            'igst',
            'product_amount'
        ]

class PurchaseSerializerList(serializers.ModelSerializer):
    invoice_date = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)
    month = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)
    utilise_month = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)

    client_name = serializers.CharField(source="client.client_name", read_only=True)
    customer_name = serializers.CharField(source="vendor.name", read_only=True)
    customer_gst_no = serializers.CharField(source="vendor.gst_no", read_only=True)
    customer_pan = serializers.CharField(source="vendor.pan", read_only=True)
    customer_address = serializers.CharField(source="vendor.address", read_only=True)
    customer_customer = serializers.CharField(source="vendor.customer", read_only=True)
    customer_vendor = serializers.CharField(source="vendor.vendor", read_only=True)
    customer_email = serializers.CharField(source="vendor.email", read_only=True) #nnnnn
    customer_contact = serializers.CharField(source="vendor.contact", read_only=True) #nnnnn
    client_location_name = serializers.CharField(source="client_Location.location", read_only=True)
    contact = serializers.CharField(source="client_Location.contact", read_only=True)
    address = serializers.CharField(source="client_Location.address", read_only=True)
    city = serializers.CharField(source="client_Location.city", read_only=True)
    state = serializers.CharField(source="client_Location.state", read_only=True)
    country = serializers.CharField(source="client_Location.country", read_only=True)
    product_summaries = ProductSummaryPurchaseSerializerList(many=True, read_only=True)

    class Meta:
        model = PurchaseInvoice
        fields = [
            'id',
            "month",
            "invoice_no",
            "invoice_date",
            "invoice_type",
            "entry_type",
            'attach_e_way_bill',
            'attach_invoice',
            "client_name",
            "customer_name",
            "customer_gst_no",
            "customer_pan",
            "customer_address",
            "customer_customer",
            "customer_vendor",
            "customer_email",  #nnnnn
            "customer_contact",  #nnnnn
            "client_location_name",
            "contact",
            "address",
            "city",
            "state",
            "country",
            "taxable_amount",
            "totalall_gst",
            "total_invoice_value",
            "amount_receivable",
            'tcs',
            'tds',
            'tds_tcs_rate',
            'product_summaries',
            'utilise_edit',
            'utilise_month',

        ]

class PurchaseSerializer2(serializers.ModelSerializer):
    class Meta:
        model = PurchaseInvoice
        fields = ['attach_invoice', 'client']

class PurchaseSerializer2(serializers.ModelSerializer):
    attach_invoice = serializers.FileField()
    class Meta:
        model = PurchaseInvoice
        fields = ['attach_invoice','client']
        
class ProductSummaryPurchaseSerializer(serializers.ModelSerializer):
    # invoice_date = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)
    # month = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)

    gst_rate = serializers.CharField(source='hsn.gst_rate', read_only=True)
    hsn_code = serializers.CharField(source='hsn.hsn_code', read_only=True, allow_null=True)
    product_name = serializers.CharField(source='product.product_name', read_only=True)
    product_amount = serializers.CharField(source='prod_description.product_amount', read_only=True)
    description = serializers.CharField(source='prod_description.description', read_only=True)
    unit = serializers.CharField(source='prod_description.unit', read_only=True)
    rate = serializers.CharField(source='prod_description.rate', read_only=True)

    class Meta:
        model = ProductSummaryPurchase
        fields = ['id', 'hsn', 'product', 'prod_description', 'hsn_code', 'gst_rate', 'product_name', 'product_amount','description', 'unit', 'rate']


#******************************************************Debit Note

class DebitNoteSerializer(serializers.ModelSerializer):
    invoice_date = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)
    po_date = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)
    # utilise_month = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)

    class Meta:
        model = DebitNote
        fields = '__all__'

class DebitNoteSerializer3(serializers.ModelSerializer):
    invoice_date = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)
    po_date = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)
    # utilise_month = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)
    
    class Meta:
        model = DebitNote
        exclude = ['client','client_Location','customer','product_summaries', 'sales_invoice']
        
class ProductSummaryDebitNoteSerializerList(serializers.ModelSerializer):
    hsn_code = serializers.CharField(source="hsn.hsn_code", read_only=True)
    gst_rate = serializers.DecimalField(source="hsn.gst_rate", max_digits=10, decimal_places=2, read_only=True)
    product_name = serializers.CharField(source="product.product_name", read_only=True)
    product_amount = serializers.CharField(source="prod_description.product_amount", read_only=True)
    description_text = serializers.CharField(source="prod_description.description", read_only=True)
    unit = serializers.DecimalField(source="prod_description.unit", max_digits=10, decimal_places=2, read_only=True)
    rate = serializers.DecimalField(source="prod_description.rate", max_digits=10, decimal_places=2, read_only=True)
    cgst = serializers.DecimalField(source="prod_description.cgst", max_digits=10, decimal_places=2, read_only=True)
    sgst = serializers.DecimalField(source="prod_description.sgst", max_digits=10, decimal_places=2, read_only=True)
    igst = serializers.DecimalField(source="prod_description.igst", max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = ProductSummary
        fields = [
            "id",
            "hsn_code",
            "gst_rate",
            "product_name",
            "description_text",
            "unit",
            "rate",
            'cgst',
            'sgst',
            'igst',
            'product_amount'
        ]
        
class DebitNoteSerializerList(serializers.ModelSerializer):
    invoice_date = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)
    po_date = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)
    # utilise_month = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)

    client_name = serializers.CharField(source="client.client_name", read_only=True)
    customer_name = serializers.CharField(source="customer.name", read_only=True)
    customer_gst_no = serializers.CharField(source="customer.gst_no", read_only=True)
    customer_pan = serializers.CharField(source="customer.pan", read_only=True)
    customer_address = serializers.CharField(source="customer.address", read_only=True)
    customer_customer = serializers.CharField(source="customer.customer", read_only=True)
    customer_vendor = serializers.CharField(source="customer.vendor", read_only=True)
    customer_email = serializers.CharField(source="customer.email", read_only=True) #nnnnn
    customer_contact = serializers.CharField(source="customer.contact", read_only=True) #nnnnn
    client_location_name = serializers.CharField(source="client_Location.location", read_only=True)
    contact = serializers.CharField(source="client_Location.contact", read_only=True)
    address = serializers.CharField(source="client_Location.address", read_only=True)
    city = serializers.CharField(source="client_Location.city", read_only=True)
    state = serializers.CharField(source="client_Location.state", read_only=True)
    country = serializers.CharField(source="client_Location.country", read_only=True)
    product_summaries = ProductSummaryDebitNoteSerializerList(many=True, read_only=True)

    class Meta:
        model = DebitNote
        fields = [
            'id',
            # 'month',
            'sales_invoice',
            "invoice_no",
            "invoice_date",
            "invoice_type",
            "entry_type",
            'attach_e_way_bill',
            'attach_invoice',
            "client_name",
            "customer_name",
            "customer_gst_no",
            "customer_pan",
            "customer_address",
            "customer_email",  #nnnnn
            "customer_contact",  #nnnnn
            "customer_customer",
            "customer_vendor",
            "client_location_name",
            "contact",
            "address",
            "po_date",
            "po_no",
            "city",
            "state",
            "country",
            "taxable_amount",
            "totalall_gst",
            "total_invoice_value",
            "amount_receivable",
            'tcs',
            'tds',
            'tds_tcs_rate',
            'product_summaries'
        ]
        
class DebitNoteSerializer2(serializers.ModelSerializer):
    class Meta:
        model = DebitNote
        fields = ['attach_invoice','client', 'sales_invoice']
        
class DebitNoteSerializer2(serializers.ModelSerializer):
    attach_invoice = serializers.FileField()

    class Meta:
        model = DebitNote  # Your model where the file should be saved
        fields = ['attach_invoice', 'client', 'sales_invoice']

class ProductSummaryDebitNoteSerializer(serializers.ModelSerializer):
    gst_rate = serializers.CharField(source='hsn.gst_rate', read_only=True)
    hsn_code = serializers.CharField(source='hsn.hsn_code', read_only=True)
    product_name = serializers.CharField(source='product.product_name', read_only=True)
    product_amount = serializers.CharField(source='prod_description.product_amount', read_only=True)
    description = serializers.CharField(source='prod_description.description', read_only=True)
    unit = serializers.CharField(source='prod_description.unit', read_only=True)
    rate = serializers.CharField(source='prod_description.rate', read_only=True)

    class Meta:
        model = ProductSummaryDebitNote
        fields = ['id', 'hsn', 'product', 'prod_description', 'hsn_code', 'gst_rate', 'product_name', 'product_amount','description', 'unit', 'rate']

#******************************************************Credit Note

class CreditNoteSerializer(serializers.ModelSerializer):
    invoice_date = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)
    month = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)
    utilise_month = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)
    
    class Meta:
        model = CreditNote
        fields = '__all__'

class CreditNoteSerializer3(serializers.ModelSerializer):
    invoice_date = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)
    month = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)
    utilise_month = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)

    class Meta:
        model = CreditNote
        exclude = ['client','client_Location','vendor','product_summaries','purchase_invoice']
        
class ProductSummaryCreditNoteSerializerList(serializers.ModelSerializer):
    hsn_code = serializers.CharField(source="hsn.hsn_code", read_only=True)
    gst_rate = serializers.DecimalField(source="hsn.gst_rate", max_digits=10, decimal_places=2, read_only=True)
    product_name = serializers.CharField(source="product.product_name", read_only=True)
    product_amount = serializers.CharField(source="prod_description.product_amount", read_only=True)
    description_text = serializers.CharField(source="prod_description.description", read_only=True)
    unit = serializers.DecimalField(source="prod_description.unit", max_digits=10, decimal_places=2, read_only=True)
    rate = serializers.DecimalField(source="prod_description.rate", max_digits=10, decimal_places=2, read_only=True)
    cgst = serializers.DecimalField(source="prod_description.cgst", max_digits=10, decimal_places=2, read_only=True)
    sgst = serializers.DecimalField(source="prod_description.sgst", max_digits=10, decimal_places=2, read_only=True)
    igst = serializers.DecimalField(source="prod_description.igst", max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = ProductSummaryCreditNote
        fields = [
            "id",
            "hsn_code",
            "gst_rate",
            "product_name",
            "description_text",
            "unit",
            "rate",
            'cgst',
            'sgst',
            'igst',
            'product_amount'
        ]
        
class CreditNoteSerializerList(serializers.ModelSerializer):
    invoice_date = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)
    month = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)
    utilise_month = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)

    client_name = serializers.CharField(source="client.client_name", read_only=True)
    customer_name = serializers.CharField(source="vendor.name", read_only=True)
    customer_gst_no = serializers.CharField(source="vendor.gst_no", read_only=True)
    customer_pan = serializers.CharField(source="vendor.pan", read_only=True)
    customer_address = serializers.CharField(source="vendor.address", read_only=True)
    customer_customer = serializers.CharField(source="vendor.customer", read_only=True)
    customer_vendor = serializers.CharField(source="vendor.vendor", read_only=True)
    customer_email = serializers.CharField(source="vendor.email", read_only=True) #nnnnn
    customer_contact = serializers.CharField(source="vendor.contact", read_only=True) #nnnnn
    client_location_name = serializers.CharField(source="client_Location.location", read_only=True)
    contact = serializers.CharField(source="client_Location.contact", read_only=True)
    address = serializers.CharField(source="client_Location.address", read_only=True)
    city = serializers.CharField(source="client_Location.city", read_only=True)
    state = serializers.CharField(source="client_Location.state", read_only=True)
    country = serializers.CharField(source="client_Location.country", read_only=True)
    product_summaries = ProductSummaryCreditNoteSerializerList(many=True, read_only=True)

    class Meta:
        model = CreditNote
        fields = [
            'id',
            'purchase_invoice',
            "month",
            "invoice_no",
            "invoice_date",
            "invoice_type",
            "entry_type",
            'attach_e_way_bill',
            'attach_invoice',
            "client_name",
            "customer_name",
            "customer_gst_no",
            "customer_pan",
            "customer_address",
            "customer_customer",
            "customer_vendor",
            "customer_email",  #nnnnn
            "customer_contact",  #nnnnn
            "client_location_name",
            "contact",
            "address",
            "city",
            "state",
            "country",
            "taxable_amount",
            "totalall_gst",
            "total_invoice_value",
            "amount_receivable",
            'tcs',
            'tds',
            'tds_tcs_rate',
            'product_summaries',
            'utilise_edit',
            'utilise_month',
        ]
        
class CreditNoteSerializer2(serializers.ModelSerializer):
    class Meta:
        model = CreditNote 
        fields = ['attach_invoice','client','purchase_invoice']
        
class CreditNoteSerializer2(serializers.ModelSerializer):
    attach_invoice = serializers.FileField()

    class Meta:
        model = CreditNote  # Your model where the file should be saved
        fields = ['attach_invoice', 'client','purchase_invoice']

class ProductSummaryCreditNoteSerializer(serializers.ModelSerializer):
    gst_rate = serializers.CharField(source='hsn.gst_rate', read_only=True)
    hsn_code = serializers.CharField(source='hsn.hsn_code', read_only=True)
    product_name = serializers.CharField(source='product.product_name', read_only=True)
    product_amount = serializers.CharField(source='prod_description.product_amount', read_only=True)
    description = serializers.CharField(source='prod_description.description', read_only=True)
    unit = serializers.CharField(source='prod_description.unit', read_only=True)
    rate = serializers.CharField(source='prod_description.rate', read_only=True)

    class Meta:
        model = ProductSummaryCreditNote
        fields = ['id', 'hsn', 'product', 'prod_description', 'hsn_code', 'gst_rate', 'product_name', 'product_amount','description', 'unit', 'rate']
        
        
#******************************************************Income

class IncomeSerializer(serializers.ModelSerializer):
    invoice_date = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)
    month = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)

    class Meta:
        model = Income
        fields = '__all__'

class IncomeSerializer3(serializers.ModelSerializer):
    invoice_date = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)
    month = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)
    class Meta:
        model = Income
        exclude = ['client','client_Location','customer','product_summaries']
        
class ProductSummaryIncomeSerializerList(serializers.ModelSerializer):
    # invoice_date = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)
    # month = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)

    hsn_code = serializers.CharField(source="hsn.hsn_code", read_only=True)
    gst_rate = serializers.DecimalField(source="hsn.gst_rate", max_digits=10, decimal_places=2, read_only=True)
    product_name = serializers.CharField(source="product.product_name", read_only=True)
    product_amount = serializers.CharField(source="prod_description.product_amount", read_only=True)
    description_text = serializers.CharField(source="prod_description.description", read_only=True)
    unit = serializers.DecimalField(source="prod_description.unit", max_digits=10, decimal_places=2, read_only=True)
    rate = serializers.DecimalField(source="prod_description.rate", max_digits=10, decimal_places=2, read_only=True)
    cgst = serializers.DecimalField(source="prod_description.cgst", max_digits=10, decimal_places=2, read_only=True)
    sgst = serializers.DecimalField(source="prod_description.sgst", max_digits=10, decimal_places=2, read_only=True)
    igst = serializers.DecimalField(source="prod_description.igst", max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = ProductSummaryIncome
        fields = [
            "id",
            "hsn_code",
            "gst_rate",
            "product_name",
            "description_text",
            "unit",
            "rate",
            'cgst',
            'sgst',
            'igst',
            'product_amount'
        ]
        
class IncomeSerializerList(serializers.ModelSerializer):
    invoice_date = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)
    month = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)

    client_name = serializers.CharField(source="client.client_name", read_only=True)
    customer_name = serializers.CharField(source="customer.name", read_only=True)
    customer_gst_no = serializers.CharField(source="customer.gst_no", read_only=True)
    customer_pan = serializers.CharField(source="customer.pan", read_only=True)
    customer_email = serializers.CharField(source="customer.email", read_only=True)
    customer_contact = serializers.CharField(source="customer.contact", read_only=True)
    customer_address = serializers.CharField(source="customer.address", read_only=True)
    customer_customer = serializers.CharField(source="customer.customer", read_only=True)
    customer_vendor = serializers.CharField(source="customer.vendor", read_only=True)
    client_location_name = serializers.CharField(source="client_Location.location", read_only=True)
    contact = serializers.CharField(source="client_Location.contact", read_only=True)
    address = serializers.CharField(source="client_Location.address", read_only=True)
    city = serializers.CharField(source="client_Location.city", read_only=True)
    state = serializers.CharField(source="client_Location.state", read_only=True)
    country = serializers.CharField(source="client_Location.country", read_only=True)
    product_summaries = ProductSummaryIncomeSerializerList(many=True, read_only=True)

    class Meta:
        model = Income
        fields = [
            'id',
            "month",
            "invoice_no",
            "invoice_date",
            "invoice_type",
            "entry_type",
            'attach_e_way_bill',
            'attach_invoice',
            "client_name",
            "customer_name",
            "customer_gst_no",
            "customer_pan",
            "customer_email",
            "customer_contact",
            "customer_address",
            "customer_customer",
            "customer_vendor",
            "client_location_name",
            "contact",
            "address",
            "city",
            "state",
            "country",
            "taxable_amount",
            "totalall_gst",
            "total_invoice_value",
            "amount_receivable",
            'tcs',
            'tds',
            'tds_tcs_rate',
            'product_summaries'
        ]
        
class IncomeSerializer2(serializers.ModelSerializer):
    class Meta:
        model = Income 
        fields = ['attach_invoice','client']
        
class IncomeSerializer2(serializers.ModelSerializer):
    attach_invoice = serializers.FileField()

    class Meta:
        model = Income  # Your model where the file should be saved
        fields = ['attach_invoice', 'client',]

class ProductSummaryIncomeSerializer(serializers.ModelSerializer):
    gst_rate = serializers.CharField(source='hsn.gst_rate', read_only=True)
    hsn_code = serializers.CharField(source='hsn.hsn_code', read_only=True)
    product_name = serializers.CharField(source='product.product_name', read_only=True)
    product_amount = serializers.CharField(source='prod_description.product_amount', read_only=True)
    description = serializers.CharField(source='prod_description.description', read_only=True)
    unit = serializers.CharField(source='prod_description.unit', read_only=True)
    rate = serializers.CharField(source='prod_description.rate', read_only=True)

    class Meta:
        model = ProductSummaryIncome
        fields = ['id', 'hsn', 'product', 'prod_description', 'hsn_code', 'gst_rate', 'product_name', 'product_amount','description', 'unit', 'rate']


#************************************************************Expenses

class ExpensesSerializer(serializers.ModelSerializer):
    invoice_date = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)
    month = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)
    utilise_month = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)


    class Meta:
        model = Expenses
        fields = '__all__'

class ExpensesSerializer3(serializers.ModelSerializer):
    invoice_date = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)
    month = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)
    utilise_month = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)


    class Meta:
        model = Expenses
        exclude = ['client','client_Location','vendor','product_summaries']
        
class ProductSummaryExpensesSerializerList(serializers.ModelSerializer):
    hsn_code = serializers.CharField(source="hsn.hsn_code", read_only=True)
    gst_rate = serializers.DecimalField(source="hsn.gst_rate", max_digits=10, decimal_places=2, read_only=True)
    product_name = serializers.CharField(source="product.product_name", read_only=True)
    product_amount = serializers.CharField(source="prod_description.product_amount", read_only=True)
    description_text = serializers.CharField(source="prod_description.description", read_only=True)
    unit = serializers.DecimalField(source="prod_description.unit", max_digits=10, decimal_places=2, read_only=True)
    rate = serializers.DecimalField(source="prod_description.rate", max_digits=10, decimal_places=2, read_only=True)
    cgst = serializers.DecimalField(source="prod_description.cgst", max_digits=10, decimal_places=2, read_only=True)
    sgst = serializers.DecimalField(source="prod_description.sgst", max_digits=10, decimal_places=2, read_only=True)
    igst = serializers.DecimalField(source="prod_description.igst", max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = ProductSummaryExpenses
        fields = [
            "id",
            "hsn_code",
            "gst_rate",
            "product_name",
            "description_text",
            "unit",
            "rate",
            'cgst',
            'sgst',
            'igst',
            'product_amount'
        ]
        
class ExpensesSerializerList(serializers.ModelSerializer):
    invoice_date = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)
    month = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)
    utilise_month = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)

    client_name = serializers.CharField(source="client.client_name", read_only=True)
    customer_name = serializers.CharField(source="vendor.name", read_only=True)
    customer_gst_no = serializers.CharField(source="vendor.gst_no", read_only=True)
    customer_pan = serializers.CharField(source="vendor.pan", read_only=True)
    customer_email = serializers.CharField(source="vendor.email", read_only=True)
    customer_contact = serializers.CharField(source="vendor.contact", read_only=True)
    customer_address = serializers.CharField(source="vendor.address", read_only=True)
    customer_customer = serializers.CharField(source="vendor.customer", read_only=True)
    customer_vendor = serializers.CharField(source="vendor.vendor", read_only=True)
    client_location_name = serializers.CharField(source="client_Location.location", read_only=True)
    contact = serializers.CharField(source="client_Location.contact", read_only=True)
    address = serializers.CharField(source="client_Location.address", read_only=True)
    city = serializers.CharField(source="client_Location.city", read_only=True)
    state = serializers.CharField(source="client_Location.state", read_only=True)
    country = serializers.CharField(source="client_Location.country", read_only=True)
    product_summaries = ProductSummaryExpensesSerializerList(many=True, read_only=True)
    # product_summaries = serializers.SerializerMethodField()
    # def get_product_summaries(self, obj):
    #     # Ensure you're returning a queryset or iterable
    #     summaries = obj.product_summaries.all()
    #     return ProductSummaryExpensesSerializer(summaries, many=True).data


    class Meta:
        model = Expenses
        fields = [
            'id',
            "month",
            "invoice_no",
            "invoice_date",
            "invoice_type",
            "entry_type",
            'attach_e_way_bill',
            'attach_invoice',
            "client_name",
            "customer_name",
            "customer_gst_no",
            "customer_pan",
            "customer_email",
            "customer_contact",
            "customer_address",
            "customer_customer",
            "customer_vendor",
            "client_location_name",
            "contact",
            "address",
            "city",
            "state",
            "country",
            "taxable_amount",
            "totalall_gst",
            "total_invoice_value",
            "amount_receivable",
            'tcs',
            'tds',
            'tds_tcs_rate',
            'product_summaries',
            'utilise_edit',
            'utilise_month',
        ]
        
class ExpensesSerializer2(serializers.ModelSerializer):
    class Meta:
        model = Expenses
        fields = ['attach_invoice','client']
        
class ExpensesSerializer2(serializers.ModelSerializer):
    attach_invoice = serializers.FileField()

    class Meta:
        model = Expenses  # Your model where the file should be saved
        fields = ['attach_invoice', 'client']

class ProductSummaryExpensesSerializer(serializers.ModelSerializer):
    gst_rate = serializers.CharField(source='hsn.gst_rate', read_only=True)
    hsn_code = serializers.CharField(source='hsn.hsn_code', read_only=True)
    product_name = serializers.CharField(source='product.product_name', read_only=True)
    product_amount = serializers.CharField(source='prod_description.product_amount', read_only=True)
    description = serializers.CharField(source='prod_description.description', read_only=True)
    unit = serializers.CharField(source='prod_description.unit', read_only=True)
    rate = serializers.CharField(source='prod_description.rate', read_only=True)

    class Meta:
        model = ProductSummaryExpenses
        fields = ['id', 'hsn', 'product', 'prod_description', 'hsn_code', 'gst_rate', 'product_name', 'product_amount','description', 'unit', 'rate']
    
        
#******************************************************Income Debit Note

class IncomeDebitNoteSerializer(serializers.ModelSerializer):
    invoice_date = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)
    month = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)

    class Meta:
        model = IncomeDebitNote
        fields = '__all__'

class IncomeDebitNoteSerializer3(serializers.ModelSerializer):
    invoice_date = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)
    month = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)

    class Meta:
        model = IncomeDebitNote
        exclude = ['client','client_Location','customer','product_summaries','income']
        
class ProductSummaryIncomeDebitNoteSerializerList(serializers.ModelSerializer):
    hsn_code = serializers.CharField(source="hsn.hsn_code", read_only=True)
    gst_rate = serializers.DecimalField(source="hsn.gst_rate", max_digits=10, decimal_places=2, read_only=True)
    product_name = serializers.CharField(source="product.product_name", read_only=True)
    product_amount = serializers.CharField(source="prod_description.product_amount", read_only=True)
    description_text = serializers.CharField(source="prod_description.description", read_only=True)
    unit = serializers.DecimalField(source="prod_description.unit", max_digits=10, decimal_places=2, read_only=True)
    rate = serializers.DecimalField(source="prod_description.rate", max_digits=10, decimal_places=2, read_only=True)
    cgst = serializers.DecimalField(source="prod_description.cgst", max_digits=10, decimal_places=2, read_only=True)
    sgst = serializers.DecimalField(source="prod_description.sgst", max_digits=10, decimal_places=2, read_only=True)
    igst = serializers.DecimalField(source="prod_description.igst", max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = ProductSummaryIncomeDebitNote
        fields = [
            "id",
            "hsn_code",
            "gst_rate",
            "product_name",
            "description_text",
            "unit",
            "rate",
            'cgst',
            'sgst',
            'igst',
            'product_amount',
        ]
        
class IncomeDebitNoteSerializerList(serializers.ModelSerializer):
    invoice_date = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)
    month = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)

    client_name = serializers.CharField(source="client.client_name", read_only=True)
    customer_name = serializers.CharField(source="customer.name", read_only=True)
    customer_gst_no = serializers.CharField(source="customer.gst_no", read_only=True)
    customer_pan = serializers.CharField(source="customer.pan", read_only=True)
    customer_address = serializers.CharField(source="customer.address", read_only=True)
    customer_customer = serializers.CharField(source="customer.customer", read_only=True)
    customer_vendor = serializers.CharField(source="customer.vendor", read_only=True)
    customer_email = serializers.CharField(source="customer.email", read_only=True)
    customer_contact = serializers.CharField(source="customer.contact", read_only=True)
    client_location_name = serializers.CharField(source="client_Location.location", read_only=True)
    contact = serializers.CharField(source="client_Location.contact", read_only=True)
    address = serializers.CharField(source="client_Location.address", read_only=True)
    city = serializers.CharField(source="client_Location.city", read_only=True)
    state = serializers.CharField(source="client_Location.state", read_only=True)
    country = serializers.CharField(source="client_Location.country", read_only=True)
    product_summaries = ProductSummaryIncomeDebitNoteSerializerList(many=True, read_only=True)

    class Meta:
        model = IncomeDebitNote
        fields = [
            'id',
            'income',
            'month',
            "invoice_no",
            "invoice_date",
            "invoice_type",
            "entry_type",
            'attach_e_way_bill',
            'attach_invoice',
            "client_name",
            "customer_name",
            "customer_gst_no",
            "customer_pan",
            "customer_address",
            "customer_customer",
            "customer_email",
            "customer_contact",
            "customer_vendor",
            "client_location_name",
            "contact",
            "address",
            "city",
            "state",
            "country",
            "taxable_amount",
            "totalall_gst",
            "total_invoice_value",
            "amount_receivable",
            'tcs',
            'tds',
            'tds_tcs_rate',
            'product_summaries'
        ]
        
class IncomeDebitNoteSerializer2(serializers.ModelSerializer):
    class Meta:
        model = IncomeDebitNote 
        fields = ['attach_invoice','client','income']
        
class IncomeDebitNoteSerializer2(serializers.ModelSerializer):
    attach_invoice = serializers.FileField()

    class Meta:
        model = IncomeDebitNote  # Your model where the file should be saved
        fields = ['attach_invoice', 'client','income']

class ProductSummaryIncomeDebitNoteSerializer(serializers.ModelSerializer):
    gst_rate = serializers.CharField(source='hsn.gst_rate', read_only=True)
    hsn_code = serializers.CharField(source='hsn.hsn_code', read_only=True)
    product_name = serializers.CharField(source='product.product_name', read_only=True)
    product_amount = serializers.CharField(source='prod_description.product_amount', read_only=True)
    description = serializers.CharField(source='prod_description.description', read_only=True)
    unit = serializers.CharField(source='prod_description.unit', read_only=True)
    rate = serializers.CharField(source='prod_description.rate', read_only=True)

    class Meta:
        model = ProductSummaryIncomeDebitNote
        fields = ['id', 'hsn', 'product', 'prod_description', 'hsn_code', 'gst_rate', 'product_name', 'product_amount','description', 'unit', 'rate']



#******************************************************Expenses Credit Note

class ExpensesCreditNoteSerializer(serializers.ModelSerializer):
    invoice_date = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)
    month = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)
    utilise_month = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)

    class Meta:
        model = ExpensesCreditNote
        fields = '__all__'

class ExpensesCreditNoteSerializer3(serializers.ModelSerializer):
    invoice_date = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)
    month = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)
    utilise_month = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)

    class Meta:
        model = ExpensesCreditNote
        exclude = ['client','client_Location','vendor','product_summaries','expenses']
        
class ProductSummaryExpensesCreditNoteSerializerList(serializers.ModelSerializer):
    hsn_code = serializers.CharField(source="hsn.hsn_code", read_only=True)
    gst_rate = serializers.DecimalField(source="hsn.gst_rate", max_digits=10, decimal_places=2, read_only=True)
    product_name = serializers.CharField(source="product.product_name", read_only=True)
    product_amount = serializers.CharField(source="prod_description.product_amount", read_only=True)
    description_text = serializers.CharField(source="prod_description.description", read_only=True)
    unit = serializers.DecimalField(source="prod_description.unit", max_digits=10, decimal_places=2, read_only=True)
    rate = serializers.DecimalField(source="prod_description.rate", max_digits=10, decimal_places=2, read_only=True)
    cgst = serializers.DecimalField(source="prod_description.cgst", max_digits=10, decimal_places=2, read_only=True)
    sgst = serializers.DecimalField(source="prod_description.sgst", max_digits=10, decimal_places=2, read_only=True)
    igst = serializers.DecimalField(source="prod_description.igst", max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = ProductSummaryExpensesCreditNote
        fields = [
            "id",
            "hsn_code",
            "gst_rate",
            "product_name",
            "description_text",
            "unit",
            "rate",
            'cgst',
            'sgst',
            'igst',
            'product_amount'
        ]
        
class ExpensesCreditNoteSerializerList(serializers.ModelSerializer):
    invoice_date = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)
    month = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)
    utilise_month = serializers.DateField(format="%d-%m-%Y", input_formats=["%d-%m-%Y"], required=False)

    client_name = serializers.CharField(source="client.client_name", read_only=True)
    customer_name = serializers.CharField(source="vendor.name", read_only=True)
    customer_gst_no = serializers.CharField(source="vendor.gst_no", read_only=True)
    customer_pan = serializers.CharField(source="vendor.pan", read_only=True)
    customer_address = serializers.CharField(source="vendor.address", read_only=True)
    customer_customer = serializers.CharField(source="vendor.customer", read_only=True)
    customer_email = serializers.CharField(source="vendor.email", read_only=True)
    customer_contact = serializers.CharField(source="vendor.contact", read_only=True)
    customer_vendor = serializers.CharField(source="vendor.vendor", read_only=True)
    client_location_name = serializers.CharField(source="client_Location.location", read_only=True)
    contact = serializers.CharField(source="client_Location.contact", read_only=True)
    address = serializers.CharField(source="client_Location.address", read_only=True)
    city = serializers.CharField(source="client_Location.city", read_only=True)
    state = serializers.CharField(source="client_Location.state", read_only=True)
    country = serializers.CharField(source="client_Location.country", read_only=True)
    product_summaries = ProductSummaryExpensesCreditNoteSerializerList(many=True, read_only=True)

    class Meta:
        model = ExpensesCreditNote
        fields = [
            'id',
            'expenses',
            "invoice_no",
            "invoice_date",
            "invoice_type",
            "entry_type",
            'attach_e_way_bill',
            'attach_invoice',
            "client_name",
            "customer_name",
            "customer_gst_no",
            "customer_pan",
            "customer_address",
            "customer_customer",
            "customer_email",
            "customer_contact",
            "customer_vendor",
            "client_location_name",
            "contact",
            "address",
            "city",
            "state",
            "month",
            "country",
            "taxable_amount",
            "totalall_gst",
            "total_invoice_value",
            "amount_receivable",
            'tcs',
            'tds',
            'tds_tcs_rate',
            'product_summaries',
            'utilise_edit',
            'utilise_month',
        ]
        
class ExpensesCreditNoteSerializer2(serializers.ModelSerializer):
    class Meta:
        model = ExpensesCreditNote 
        fields = ['attach_invoice','client','expenses']
        
class ExpensesCreditNoteSerializer2(serializers.ModelSerializer):
    attach_invoice = serializers.FileField()

    class Meta:
        model = ExpensesCreditNote  # Your model where the file should be saved
        fields = ['attach_invoice', 'client','expenses']

class ProductSummaryExpensesCreditNoteSerializer(serializers.ModelSerializer):
    gst_rate = serializers.CharField(source='hsn.gst_rate', read_only=True)
    hsn_code = serializers.CharField(source='hsn.hsn_code', read_only=True)
    product_name = serializers.CharField(source='product.product_name', read_only=True)
    product_amount = serializers.CharField(source='prod_description.product_amount', read_only=True)
    description = serializers.CharField(source='prod_description.description', read_only=True)
    unit = serializers.CharField(source='prod_description.unit', read_only=True)
    rate = serializers.CharField(source='prod_description.rate', read_only=True)

    class Meta:
        model = ProductSummaryExpensesCreditNote
        fields = ['id', 'hsn', 'product', 'prod_description', 'hsn_code', 'gst_rate', 'product_name', 'product_amount','description', 'unit', 'rate']
        
        

#************************************************************Zip Upload

class ZipUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ZipUpload
        # fields = ['client', 'files', 'date']
        fields = '__all__'
    
class ZipUploadSerializer2(serializers.ModelSerializer):
    files = serializers.FileField()
    
    class Meta:
        model = ZipUpload
        fields = ['client', 'files', 'date']   

#************************************************************Excel File

class ExcelFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExcelFile
        fields = '__all__'


 
        










