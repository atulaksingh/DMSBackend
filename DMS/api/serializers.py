from rest_framework import serializers
from rest_framework.parsers import MultiPartParser, FormParser
from api.models import *
from rest_framework_simplejwt.tokens import RefreshToken

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
        instance.files.all().delete()
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

        # Clear existing fileinfos and add new ones
        instance.fileinfos.all().delete()
        for fileinfo_data in fileinfos_data:
            # Only create FileInfo if required fields are present
            if any(fileinfo_data.values()):
                files_data = fileinfo_data.pop('files', [])
                file_info = FileInfo.objects.create(client=instance, **fileinfo_data)
                for file_data in files_data:
                    File.objects.create(fileinfo=file_info, **file_data)

        return instance

    # def create(self, validated_data):
    #     files_data = validated_data.pop('files')
    #     files_metadata = self.context['request'].POST.getlist('files_metadata[]')

    #     client = Client.objects.create(**validated_data)

    #     for file_data, metadata in zip(files_data, files_metadata):
    #         file_metadata = json.loads(metadata)

    #         File.objects.create(
    #             client=client,
    #             files=file_data.files,  # Use the file object from the request
    #             document_type=file_metadata.get('files_name'),
    #             login=file_metadata.get('login'),
    #             password=file_metadata.get('password'),
    #             remark=file_metadata.get('remark')
    #         )

    #     return client


# # Attachment Serializer
# class AttachmentSerializer(serializers.ModelSerializer):
#     files = serializers.SerializerMethodField()

#     class Meta:
#         model = Attachment
#         fields = ['id', 'client', 'file_name', 'status', 'files']

#     def get_files(self, obj):
#         files = File.objects.filter(attachment=obj)
#         return FileSerializer(files, many=True).data

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
