from rest_framework import serializers
from rest_framework.parsers import MultiPartParser, FormParser
from api.models import *
from rest_framework_simplejwt.tokens import RefreshToken



# File serializer
class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ['file']


# Client Serializer
class ClientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Client
        fields = ['id','client_name','entity_type','date_of_incorporation','contact_person','designation','contact_no_1','contact_no_2','email','business_detail']

# File Serializer
class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = '__all__'

# Attachment Serializer
class AttachmentSerializer(serializers.ModelSerializer):
    files = serializers.SerializerMethodField()

    class Meta:
        model = Attachment
        fields = ['id', 'client', 'file_name', 'status', 'files']

    def get_files(self, obj):
        files = File.objects.filter(attachment=obj)
        return FileSerializer(files, many=True).data

# Bank Serializer
class BankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields = '__all__'

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
        fields = ['id','username','email','name','first_name','last_name','ca_admin', 'cus_admin', 'token','client']

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

# Branch Document
class BranchDocSerailizer(serializers.ModelSerializer):
    class Meta:
        model = BranchDocument
        fields = '__all__'

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
class PfSerializer(serializers.ModelSerializer):
    class Meta:
        model = PF
        fields = '__all__'
