from rest_framework import serializers
from rest_framework.parsers import MultiPartParser, FormParser
from api.models import *
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime
import json

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


# # Bank Serializer
# class BankSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Bank
#         fields = '__all__'

# Bank
class BankSerializer(serializers.ModelSerializer):
    files = serializers.SerializerMethodField()

    class Meta:
        model = Bank
        fields = ['id','client','bank_name','account_no','ifsc','account_type','branch','files']

    def get_files(self, obj):
        files = Files.objects.filter(bank=obj)
        return FilesSerializer(files, many=True).data


# Owner Serializer
class OwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Owner
        fields = '__all__'

# User Serializer
class UserSerializerWithToken(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(read_only= True)
    token = serializers.SerializerMethodField(read_only = True)
    ca_admin = serializers.SerializerMethodField()
    cus_admin = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id','username','email','name','first_name','password','last_name','ca_admin', 'cus_admin', 'token','client']

    def get_name(self, obj):
        firstname = obj.first_name
        lastname = obj.last_name
        name = firstname + ' ' + lastname
        if name==' ':
            name = 'Set Your Name'
        return name

    def get_ca_admin(self,obj):
        return obj.is_staff

    def get_cus_admin(self, obj):
        return obj.is_staff

    def get_token(self, obj):
        token = RefreshToken.for_user(obj)
        return str(token.access_token)


# Company Document
class CompanyDocSerailizer(serializers.ModelSerializer):
    class Meta:
        model = CompanyDocument
        fields ='__all__'

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

    # def create(self, validated_data):
    #     branch_id = validated_data.get('branchID')
    #     if branch_id:
    #         branch = Branch.objects.get(id=branch_id)
    #         validated_data['branchID'] = branch  # Set the branch object

    #     return super().create(validated_data)
class FilesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Files
        fields = '__all__'
#         fields = ['id', 'files']
# from rest_framework import serializers

# class FilesSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Files
#         fields = ['id', 'files', 'branch_doc', 'tax_audit', 'air', 'sft','tds','bank']

#     def to_representation(self, instance):
#         # Get the original representation
#         representation = super().to_representation(instance)

#         # Check which model is being serialized and remove null fields
#         if representation['tax_audit'] is not None:
#             # If it's TaxAudit, remove AIR and SFT fields
#             representation.pop('air', None)
#             representation.pop('sft', None)
#             representation.pop('tds', None)
#             representation.pop('branch_doc', None)
#             representation.pop('bank', None)
#         elif representation['air'] is not None:
#             # If it's AIR, remove TaxAudit and SFT fields
#             representation.pop('tax_audit', None)
#             representation.pop('sft', None)
#             representation.pop('tds', None)
#             representation.pop('branch_doc', None)
#             representation.pop('bank', None)
#         elif representation['sft'] is not None:
#             # If it's SFT, remove TaxAudit and AIR fields
#             representation.pop('tax_audit', None)
#             representation.pop('air', None)
#             representation.pop('tds', None)
#             representation.pop('branch_doc', None)
#             representation.pop('bank', None)
#         elif representation['tds'] is not None:
#             representation.pop('tax_audit', None)
#             representation.pop('air', None)
#             representation.pop('sft', None)
#             representation.pop('branch_doc', None)
#             representation.pop('bank', None)
#         elif representation['branch_doc'] is not None:
#             representation.pop('tax_audit', None)
#             representation.pop('air', None)
#             representation.pop('sft', None)
#             representation.pop('tds', None)
#             representation.pop('bank', None)
#         elif representation['bank'] is not None:
#             representation.pop('tax_audit', None)
#             representation.pop('air', None)
#             representation.pop('sft', None)
#             representation.pop('tds', None)
#             representation.pop('branch_doc', None)

#         return representation


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
class CustomerVendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

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
    date_of_joining = DateFromDateTimeField()

    class Meta:
        model = PF
        fields = [
            'id','employee_code', 'employee_name', 'uan', 'pf_number', 'pf_deducted',
            'date_of_joining', 'status', 'month', 'gross_ctc', 'basic_pay',
            'hra', 'statutory_bonus', 'special_allowance', 'pf', 'gratuity',
            'total_gross_salary', 'number_of_days_in_month', 'present_days',
            'lwp', 'leave_adjustment', 'gender', 'basic_pay_monthly', 'hra_monthly',
            'statutory_bonus_monthly', 'special_allowance_monthly',
            'total_gross_salary_monthly', 'provident_fund', 'professional_tax',
            'advance', 'esic_employee', 'tds','total_deduction', 'net_pay', 'advance_esic_employer_cont'
            ]

# # Tax Audit
# class TaxAuditSerializer(serializers.ModelSerializer):
#     files = serializers.SerializerMethodField()

#     class Meta:
#         model = TaxAudit
#         fields = ['id','client','financial_year','month','files']

#     def get_files(self, obj):
#         files = Files.objects.filter(tax_audit=obj)
#         return FilesSerializer(files, many=True).data

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

# TDS Payment
class TDSPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TDSPayment
        fields = '__all__'

# TDS Return
class TDSReturnSerializer(serializers.ModelSerializer):
    files = serializers.SerializerMethodField()

    class Meta:
        model = TDSReturn
        fields = ['id','client','challan_date','challan_no','challan_type','tds_section','amount','last_filed_return_ack_no','last_filed_return_ack_date','files']

    def get_files(self, obj):
        files = Files.objects.filter(tds=obj)
        return FilesSerializer(files, many=True).data

# Sales Invoice
class SalesSerializer(serializers.ModelSerializer):

    class Meta:
        model = SalesInvoice
        fields = '__all__'

class SalesSerializer3(serializers.ModelSerializer):
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

class SalesSerializerList(serializers.ModelSerializer):
    client_name = serializers.CharField(source="client.client_name", read_only=True)
    customer_name = serializers.CharField(source="customer.name", read_only=True)
    customer_gst_no = serializers.CharField(source="customer.gst_no", read_only=True)
    customer_pan = serializers.CharField(source="customer.pan", read_only=True)
    customer_address = serializers.CharField(source="customer.address", read_only=True)
    customer_customer = serializers.CharField(source="customer.customer", read_only=True)
    customer_vendor = serializers.CharField(source="customer.vendor", read_only=True)
    client_location_name = serializers.CharField(source="client_Location.location", read_only=True)
    contact = serializers.CharField(source="client_Location.contact", read_only=True)
    address = serializers.CharField(source="client_Location.address", read_only=True)
    city = serializers.CharField(source="client_Location.city", read_only=True)
    state = serializers.CharField(source="client_Location.state", read_only=True)
    country = serializers.CharField(source="client_Location.country", read_only=True)
    product_summaries = ProductSummarySerializerList(many=True, read_only=True)

    class Meta:
        model = SalesInvoice
        fields = [
            'id',
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

# Sales Invoice
    # def get_product_summaries(self, obj):
    #     # Access related product summaries
    #     product_summaries = obj.product_summaries.all()
    #     # Serialize product summaries as needed, e.g., return a list of dictionaries
    #     return [
    #         {
    #             "hsn": ps.hsn.hsn_code if ps.hsn else None,
    #             "product_name": ps.product.product_name if ps.product else None,
    #             "description": ps.prod_description,
    #             # "quantity": ps.quantity,
    #             # "rate": ps.rate,
    #             # "amount": ps.amount,
    #         }
    #         for ps in product_summaries
    #     ]

    # def get_product_summaries_names(self, obj):
    #     # Ensure this returns a list of product names as a serializable value
    #     return [str(product.product_name) for product in obj.product_summaries.all()]

# class SalesSerializer(serializers.ModelSerializer):
#     product_summaries = serializers.PrimaryKeyRelatedField(queryset=ProductSummary.objects.all(), many=True)

#     class Meta:
#         model = SalesInvoice
#         fields = [
#             'client_Location',
#             'customer',
#             'invoice_no',
#             'invoice_date',
#             'invoice_type',
#             'entry_type',
#             'taxable_amount',
#             'total_gst',
#             'total_invoice_value',
#             'tds_tcs_rate',
#             'tds',
#             'tcs',
#             'amount_receivable',
#             'product_summaries'
#         ]


class SalesSerializer2(serializers.ModelSerializer):
    class Meta:
        model = SalesInvoice
        fields = ['attach_e_way_bill','client']
class SalesSerializer2(serializers.ModelSerializer):
    attach_e_way_bill = serializers.FileField()

    class Meta:
        model = SalesInvoice  # Your model where the file should be saved
        fields = ['attach_e_way_bill', 'client']


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
            raise serializers.ValidationError("A product with this name and HSN code already exists.")
        return data



# class ProductSerializer(serializers.ModelSerializer):
#     hsn_code = serializers.CharField(source='hsn.hsn_code', read_only=True)
#     class Meta:
#         model = Product
#         fields = ['id', 'product_name', 'hsn_code','hsn','unit_of_measure']

# class ProductDescriptionSerializer2(serializers.ModelSerializer):

#     class Meta:
#         model = ProductDescription
#         fields = ['id', 'description', 'unit', 'rate']

# class ProductSerializer2(serializers.ModelSerializer):
#     hsn_code = serializers.CharField(source='hsn.hsn_code', read_only=True)
#     gst_rate = serializers.CharField(source='hsn.gst_rate', read_only=True)
#     description_name = serializers.CharField(source='ProductDescription.description', read_only=True)
#     class Meta:
#         model = Product
#         fields = ['id', 'product_name', 'hsn_code','gst_rate','hsn','description','description_name']



class ProductDescriptionSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.product_name', read_only=True)

    class Meta:
        model = ProductDescription
        fields = ['id', 'description', 'unit', 'rate','product_name','product','product_amount','cgst','sgst','igst']



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
    class Meta:
        model = PurchaseInvoice
        fields = '__all__'

class PurchaseSerializer3(serializers.ModelSerializer):
    class Meta:
        model = PurchaseInvoice
        exclude = ['client','client_Location','vendor','product_summeries']

class PurchaseSerializerList(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.client_name', read_only= True)
    customer_name = serializers.CharField(source='customer.name', read_only= True)
    customer_gst_no = serializers.CharField(source='customer.gst_no', read_only = True)
    customer_pan = serializers.CharField(source= 'customer.pan', read_only=True)
    customer_address = serializers.CharField(source='customer.address', read_only= True)
    customer_customer = serializers.CharField(source='customer.customer', read_only=True)
    customer_vendor = serializers.CharField(source='customer.vendor', read_only=True)
    client_location_name = serializers.CharField(source='client_Location.location', read_only=True)
    contact = serializers.CharField(source='client_Location.contact', read_only=True)
    address = serializers.CharField(source='client_Location.address', read_only=True)
    city = serializers.CharField(source='client_Location.city',read_only=True)
    state = serializers.CharField(source='cliet_Location.state', read_only=True)
    country = serializers.CharField(source='client_Location.country', read_only=True)
    product_summaries = ProductSummarySerializerList(many=True, read_only= True)
    class Meta:
        model = PurchaseInvoice
        fields = [
           'id',
            "invoice_no",
            "invoice_date",
            "invoice_type",
            "entry_type",
            'attach_e_way_bill',
            "client_name",
            "customer_name",
            "customer_gst_no",
            "customer_pan",
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
        ]

class PurchaseSerializer2(serializers.ModelSerializer):
    class Meta:
        model = PurchaseInvoice
        fields = ['attach_e_way_bill', 'client']

class PurchaseSerializer2(serializers.ModelSerializer):
    attach_e_way_bill = serializers.FileField()
    class Meta:
        model = PurchaseInvoice
        fields = ['attach_e_way_bill','client']
        
class ProductSummaryPurchaseSerializer(serializers.ModelSerializer):
    gst_rate = serializers.CharField(source='hsn.gst_rate', read_only=True)
    hsn_code = serializers.CharField(source='hsn.hsn_code', read_only=True)
    product_name = serializers.CharField(source='product.product_name', read_only=True)
    product_amount = serializers.CharField(source='prod_description.product_amount', read_only=True)
    description = serializers.CharField(source='prod_description.description', read_only=True)
    unit = serializers.CharField(source='prod_description.unit', read_only=True)
    rate = serializers.CharField(source='prod_description.rate', read_only=True)

    class Meta:
        model = ProductSummaryPurchase
        fields = ['id', 'hsn', 'product', 'prod_description', 'hsn_code', 'gst_rate', 'product_name', 'product_amount','description', 'unit', 'rate']


# class HSNSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = HSNCode
#         fields = ['id','hsn_code','gst_rate']


