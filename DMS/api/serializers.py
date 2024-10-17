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
