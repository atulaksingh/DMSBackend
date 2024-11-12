from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from api.models import *
from api.serializers import *
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.contrib.auth.hashers import make_password
# for sending mails and generate token
from django.template.loader import render_to_string # used returns the resulting content as a string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode #  used to safely encode and decode data in a URL-friendly format
from .utils import TokenGenerator, generate_token
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError #  helps in managing string and byte conversions
from django.core.mail import EmailMessage # used to construct and send email messages
from django.conf import settings
from django.views.generic import View
from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import CreateModelMixin
from rest_framework import generics
from openpyxl import load_workbook
from openpyxl import load_workbook
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from .models import Client, PF
from .serializers import PfSerializer
import pandas as pd
from django.http import JsonResponse
from django.db.models import Sum, F
from django.db.models.functions import Coalesce

# *******************************************Client View's***********************************************

# ****************************************Frontend create-client api*************************************
@api_view(['POST'])
def create_client(request):
    if request.method == 'POST':
        print("Received data:", request.data)  # Debugging output
        client_serializer = ClientSerializer(data=request.data)

        if client_serializer.is_valid():
            client = client_serializer.save()
            print('clien_serializer',client)
            # Access fileinfos data
            fileinfos_data = []
            for key in request.POST.keys():
                if key.startswith('fileinfos['):
                    # Parse the index from the key
                    index = key.split('[')[1].split(']')[0]
                    if index.isdigit():
                        fileinfo_str = request.POST.get(f'fileinfos[{index}]')
                        if fileinfo_str:
                            fileinfo_data = json.loads(fileinfo_str)
                            files = request.FILES.getlist(f'fileinfos[{index}].files[]')
                            fileinfos_data.append({
                                'fileinfo': fileinfo_data,
                                'files': files
                            })
            print('clien_serializer222',fileinfos_data)

            # Save FileInfo and File instances
            for entry in fileinfos_data:
                fileinfo = FileInfo.objects.create(client=client, **entry['fileinfo'])
                for file in entry['files']:
                    File.objects.create(fileinfo=fileinfo, files=file)

            return Response(client_serializer.data, status=201)

        return Response(client_serializer.errors, status=400)

# *****************************Backend create-client api*************************************
# @api_view(['POST'])
# def create_client(request):
#     if request.method == 'POST':
#         print("Received data:", request.data)  # Debugging output
#         client_serializer = ClientSerializer(data=request.data)

#         if client_serializer.is_valid():
#             client = client_serializer.save()

#             # Access fileinfos data
#             fileinfos_data = []
#             index = 0
#             while f'fileinfos[{index}].login' in request.POST:
#                 fileinfo_data = {
#                     'login': request.POST.get(f'fileinfos[{index}].login'),
#                     'password': request.POST.get(f'fileinfos[{index}].password'),
#                     'document_type': request.POST.get(f'fileinfos[{index}].document_type'),
#                     'remark': request.POST.get(f'fileinfos[{index}].remark'),
#                 }

#                 files = request.FILES.getlist(f'fileinfos[{index}].files[]')

#                 fileinfos_data.append({
#                     'fileinfo': fileinfo_data,
#                     'files': files
#                 })

#                 index += 1

#             # Save FileInfo and File instances
#             for entry in fileinfos_data:
#                 fileinfo = FileInfo.objects.create(client=client, **entry['fileinfo'])
#                 for file in entry['files']:
#                     File.objects.create(fileinfo=fileinfo, files=file)

#             print('Data', client_serializer.data)

#             return Response(client_serializer.data, status=201)

#         return Response(client_serializer.errors, status=400)


@api_view(['GET'])
def list_client(request):
    if request.method == 'GET':
        client = Client.objects.all()
        hsn = HSNCode.objects.all()
        product = Product.objects.all()
        product_description = ProductDescription.objects.all()

        serializers = ClientSerializer(client, many=True)
        serializers2 = HSNSerializer(hsn, many=True)
        serializers3 = ProductSerializer(product, many=True)
        serializers4 = ProductDescriptionSerializer(product_description, many=True)

        context = {
            'clients':serializers.data,
            'hsn':serializers2.data,
            'product':serializers3.data,
            'product_description':serializers4.data
        }

        return Response(context)

@api_view(['GET', 'POST'])
def edit_client(request, pk):
    try:
        client = Client.objects.get(id=pk)
    except Client.DoesNotExist:
        return Response({"error": "Client not found"}, status=404)

    # Handle GET request: Retrieve the client and pre-populate the frontend form
    if request.method == 'GET':
        client_serializer = ClientSerializer(client)
        return Response(client_serializer.data, status=200)

    # Handle POST request: Update the client and associated FileInfo and File models
    elif request.method == 'POST':
        # Update client fields
        client_serializer = ClientSerializer(client, data=request.data)

        if client_serializer.is_valid():
            print('data', request.POST)
            client_serializer.save()

            # Access fileinfos data for updating
            fileinfos_data = []
            index = 0

            # Loop through fileinfos in request.POST
            while f'fileinfos[{index}].login' in request.POST:
                fileinfo_data = {
                    'login': request.POST.get(f'fileinfos[{index}].login'),
                    'password': request.POST.get(f'fileinfos[{index}].password'),
                    'document_type': request.POST.get(f'fileinfos[{index}].document_type'),
                    'remark': request.POST.get(f'fileinfos[{index}].remark'),
                }

                # Get files associated with this fileinfo
                files = request.FILES.getlist(f'fileinfos[{index}].files')
                fileinfo_id = request.POST.get(f'fileinfos[{index}].id')  # Assuming you have a field to identify the FileInfo
                if fileinfo_id:  # Update existing FileInfo if ID is provided
                    try:
                        fileinfo = FileInfo.objects.get(id=fileinfo_id, client=client)

                        # Update existing FileInfo fields
                        for attr, value in fileinfo_data.items():
                            setattr(fileinfo, attr, value)
                        fileinfo.save()


                    except FileInfo.DoesNotExist:
                        # If FileInfo doesn't exist, create a new one
                        fileinfo = FileInfo.objects.create(client=client, **fileinfo_data)

                else:
                    # Create a new FileInfo if no ID was provided
                    fileinfo = FileInfo.objects.create(client=client, **fileinfo_data)

                # Create new files associated with this FileInfo
                for file in files:
                    File.objects.create(fileinfo=fileinfo, files=file)

                index += 1

            return Response(client_serializer.data, status=200)

        return Response(client_serializer.errors, status=400)

@api_view(['GET'])
def single_fileinfo(request,pk,fileinfo_pk):
    client = Client.objects.get(id = pk)
    fileinfo = FileInfo.objects.get(id=fileinfo_pk, client=client)
    if request.method == 'GET':
        serializer = FileInfoSerializer(fileinfo)
        print(serializer)
        return Response(serializer.data)

@api_view(['DELETE'])
def delete_fileinfo(request,pk,fileinfo_pk):
    if request.method == 'DELETE':
        client = Client.objects.get(id=pk)
        fileinfo = FileInfo.objects.get(id=fileinfo_pk, client=client)
        fileinfo.delete()
        return Response ({'Message':'Fileinfo Deleted'})
    return Response ({'Message':'Fail to delete'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def delete_client(request,pk):
    if request.method == 'DELETE':
        client = Client.objects.get(id=pk)
        client.delete()
        return Response ({'Message':'Company Deleted'})
    return Response ({'Message':'Fail to delete'}, status=status.HTTP_400_BAD_REQUEST)


# ***********************************************Bank View's******************************************************

# @api_view(['POST'])
# def create_bank(request, pk):
#     client = get_object_or_404(Client, id=pk)
#     if request.method == 'POST':
#         # client = Client.objects.get(id=client_pk)
#         bank_serializer = BankSerializer(data=request.data)
#         if bank_serializer.is_valid():
#             bank_serializer.save(client=client)
#             return Response({'Message':'Bank Created',"data":bank_serializer.data}, status=status.HTTP_201_CREATED)
#         return Response(bank_serializer.error,status=status.HTTP_400_BAD_REQUEST)

# @api_view(['POST','GET'])
# def edit_bank(request,pk,bank_pk):
#     client = get_object_or_404(Client, id=pk)
#     bank = Bank.objects.get(id = bank_pk)
#     bank_serializer = BankSerializer(data=request.data, instance=bank)
#     if request.method == 'POST':
#         if bank_serializer.is_valid():
#             bank_serializer.save(client=client)
#             return Response({'Message':'Bank Updated'})
#         return Response(bank_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#     elif request.method == 'GET':
#         bank_ser = BankSerializer(bank)
#         return Response (bank_ser.data)

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def create_bank(request,pk):
    client = Client.objects.get(id=pk)
    instance_data = request.data
    data = {key: value for key, value in instance_data.items()}

    serializer = BankSerializer(data=data)
    if serializer.is_valid(raise_exception=True):
        bank_instance = serializer.save(client=client)
        print(request.data)

        if request.FILES:
            files = dict((request.FILES).lists()).get('files',None)
            # files = request.FILES.getlist('files')
            if files:
                for file in files:
                    file_data = {
                        'bank' : bank_instance.pk,
                        'files' : file
                    }
                    file_serializer= FilesSerializer(data=file_data)
                    if file_serializer.is_valid(raise_exception=True):
                        file_serializer.save()

            return Response(serializer.data)
    return Response(serializer.errors)

@api_view(['POST', 'GET'])
@parser_classes([MultiPartParser, FormParser])
def edit_bank(request, pk, bank_pk):
    try:
        client = Client.objects.get(id=pk)
        bank = Bank.objects.get(id=bank_pk, client=client)
    except Client.DoesNotExist:
        return Response({'error': 'Client not found'}, status=status.HTTP_404_NOT_FOUND)
    except Bank.DoesNotExist:
        return Response({'error': 'Bank not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'POST':
        # Update branch document fields
        print('kjjkkj')
        bank_serializer = BankSerializer(instance=bank, data=request.data)
        if bank_serializer.is_valid():
            bank_serializer.save(client=client)

            # Handle file updates separately
            if request.FILES.getlist('files'):
                # Delete the old files if required
                Files.objects.filter(bank=bank).delete()

                # Add the new files
                files = request.FILES.getlist('files')
                for file in files:
                    file_data = {
                        'bank': bank.pk,
                        'files': file
                    }
                    file_serializer = FilesSerializer(data=file_data)
                    if file_serializer.is_valid():
                        file_serializer.save()
                    else:
                        return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            return Response({'Message': 'TDS Return and Files updated successfully'}, status=status.HTTP_200_OK)
        else:
            return Response(bank_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET':
        serializer = BankSerializer(bank)
        return Response(serializer.data)

@api_view(['GET'])
def list_bank(request, pk):
    client = Client.objects.get(id=pk)
    off=OfficeLocation.objects.filter(branch__client=client)
    print('gh',off)
    # for i in off:
    #     print('fff',i)
    if request.method == 'GET':
        bank_list = Bank.objects.filter(client=client)
        serializers = BankSerializer(bank_list,many=True)
        print(serializers)
        return Response(serializers.data)

@api_view(['GET'])
def single_bank(request, pk, bank_pk):
    client = Client.objects.get(id=pk)
    bank = Bank.objects.get(id=bank_pk, client=client)
    if request.method == 'GET':
        serializer = BankSerializer(bank)
        print(serializer)
        return Response(serializer.data)

@api_view(['DELETE'])
def delete_bank(request,pk, bank_pk):
    client = get_object_or_404(Client, id=pk)
    bank = Bank.objects.get(id=bank_pk)
    if request.method == 'DELETE':
        bank.delete()
        return Response({'Message':'Bank is Deleted'})
    return Response({'Error':'Fail to Delete Bank'}, status=status.HTTP_400_BAD_REQUEST)

# **********************************************Owners View's*******************************************

@api_view(['POST'])
def create_owner(request, pk):
    client = get_object_or_404(Client, id=pk)
    print('pkkkkk',pk)
    if request.method == 'POST':
        owner_serializer = OwnerSerializer(data=request.data)
        if owner_serializer.is_valid():
            # sum of a for loop values of share of all the owners created
            total_shares = Owner.objects.filter(client=client).aggregate(
            total_share=Coalesce(Sum(F('share')), 0))['total_share']
            # total_shares = sum([owner.share for owner in Owner.objects.all()])
            # calculating remaining shares by subtracting total shares by 100
            remaining_shares = 100 - total_shares
            # new share means the value of share while creating this owner
            new_share = owner_serializer.validated_data['share']

            if new_share > remaining_shares:
                # if enterd shares are greater then remaining share send a message of remaining shares
                return Response ({
                    'error': f'Cannot assign {new_share}%. Only {remaining_shares}% is left for assigning'
                }, status=status.HTTP_400_BAD_REQUEST)
            # save the all the data
            owner_serializer.save(client=client)
            return Response({'Message':'Owner Created',"data":owner_serializer.data}, status=status.HTTP_201_CREATED)
        # show error if given data is not valid
        return Response(owner_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST','GET'])
def edit_owner(request, pk, owner_pk):
    client = get_object_or_404(Client, id= pk)
    owner = Owner.objects.get(id = owner_pk)
    if request.method == 'POST':
        owner_serializer = OwnerSerializer(data=request.data, instance=owner)
        if owner_serializer.is_valid():
            owner_serializer.save(client=client)
            return Response({'Message':'Owner Updated'})
        return Response(owner_serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'GET':
        owner_serializer1 =OwnerSerializer(owner)
        return Response(owner_serializer1.data)

@api_view(['GET'])
def list_owner(request, pk):
    client = Client.objects.get(id = pk)
    owner_list = Owner.objects.filter(client=client)
    serializers = OwnerSerializer(owner_list, many=True)
    print(serializers)
    return Response(serializers.data)

@api_view(['GET'])
def single_owner(request, pk, owner_pk):
    client = Client.objects.get(id = pk)
    owner = Owner.objects.get(id = owner_pk)
    if request.method == 'GET':
        serializer = OwnerSerializer(owner)
        print(serializer)
        return Response(serializer.data)

@api_view(['DELETE'])
def delete_owner(request, pk, owner_pk):
    client = get_object_or_404(Client, id=pk)
    owner = Owner.objects.get(id = owner_pk)
    try :
        # storing the value of current owner shares in a variable
        owner_share = owner.share
        owner.delete()
        # for loop for providing the remainig shares left
        total_shares = sum([owner.share for owner in Owner.objects.all()])
        remaining_shares = 100 - total_shares
        return Response({'message': f'Owner is deleted.{owner_share}% share is added back. Avaliable shares: {remaining_shares}%'}, status=status.HTTP_200_OK)
    except :
        return Response('Owner not found',status=status.HTTP_400_BAD_REQUEST )

# ******************************************User's Views*******************************************

# Login
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        serializer = UserSerializerWithToken(self.user).data
        for k,v in serializer.items():
             data[k]=v
        return data

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

# User Profile
@api_view(['GET'])
@permission_classes([IsAuthenticated]) # the user should be valid
def getUserProfile(request):
    user = request.user # to get the specific user
    serializer = UserSerializerWithToken(user, many=False)
    return Response(serializer.data)

# Users List
@api_view(['GET'])
@permission_classes([IsAdminUser]) # the user should be an admin only
def getUsers(request):
    user = CustomUser.objects.all() # to get the list of all users
    serializer = UserSerializerWithToken(user, many=True)
    return Response(serializer.data)

# Dashboard User Form
@api_view(['POST'])
def dashboarduser(request):
    data = request.data
    try:
        user = CustomUser.objects.create(first_name=data['first_name'],last_name=data['last_name'],username=data['email'],
                                     email=data['email'],password=make_password(data['password']), is_active=False)
        # generate token for email sending
        email_subject = "Activate You Account"
        message = render_to_string(
            "activate.html",
            {
                'user': user,
                'domain': '127.0.0.1:8000',
                'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
                'token' : generate_token.make_token(user),
            }
        )
        # print(message)
        email_message = EmailMessage(email_subject,message,settings.EMAIL_HOST_USER,[data['email']])
        email_message.send()
        serializer = UserSerializerWithToken(user, many=False)
        return Response({'Message':'User Registered kindly activate ur account', 'Data': serializer.data})
    except:
        message = {'User Already Exist'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)

# Client User Form
@api_view(['POST'])
def clientuser(request,pk):
    client = get_object_or_404(Client, id=pk)
    data = request.data
    try:
        user = CustomUser.objects.create(first_name=data['first_name'],last_name=data['last_name'],username=data['email'],
                                     email=data['email'],password=make_password(data['password']), is_active=False, client=client)
        # generate token for email sending
        email_subject = "Activate You Account"
        message = render_to_string(
            "activate.html",
            {
                'user': user,
                'domain': '127.0.0.1:8000',
                'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
                'token' : generate_token.make_token(user),
            }
        )
        # print(message)
        email_message = EmailMessage(email_subject,message,settings.EMAIL_HOST_USER,[data['email']])
        email_message.send()
        serializer = UserSerializerWithToken(user, many=False)
        return Response({'Message':'User Registered kindly activate ur account','Data': serializer.data})
    except:
        message = {'User Already Exist'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)

# Email Activations
class ActivateAccountView(View):
    def get(self, request, uidb64, token):
        try:
            uid= force_text(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
        except Exception as identifier:
            user=None
        if user is not None and generate_token.check_token(user,token):
            user.is_active=True
            user.save()
            return render(request,"activatesuccess.html")
        else:
            return render(request,"activatefail.html")

# Clientuser Update
@api_view(['POST', 'GET'])
def edit_clientuser(request, pk, user_pk):
    client = Client.objects.get(id=pk)
    user = CustomUser.objects.get(id = user_pk, client=client)
    user_serializer = UserSerializerWithToken(data=request.data, instance=user, partial=True)
    if request.method == 'POST':
        if user_serializer.is_valid():
            user_serializer.save(client=client)
            return Response({'Message':'Client User Updated'})
        return Response(user_serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'GET':
        user_ser = UserSerializerWithToken(user)
        return Response(user_ser.data)

# DashboardUser Update
@api_view(['POST', 'GET'])
def edit_dashboardUser(request, user_pk):
    # client = Client.objects.get(id=pk)
    user = CustomUser.objects.get(id=user_pk)
    user_serializer = UserSerializerWithToken(data=request.data, instance=user)
    if request.method == 'POST':
        if user_serializer.is_valid():
            user_serializer.save()
            return Response({'Message':'Dashboard User Updated'})
        return Response(user_serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'GET':
        user_ser = UserSerializerWithToken(user)
        return Response(user_ser.data)

# ClientUser Delete
@api_view(['DELETE'])
def delete_clientuser(request,pk,user_pk):
    client = Client.objects.get(id=pk)
    user = CustomUser.objects.get(id = user_pk)
    if request.method == 'DELETE':
        user.delete()
        return Response ({'Message':'Client User is deleted'})
    return Response ({'Error':'Failed to delete Client User'},status=status.HTTP_400_BAD_REQUEST)

# DashboardUser Delete
@api_view(['DELETE'])
def delete_dashboarduser(request, user_pk):
    user = CustomUser.objects.get(id = user_pk)
    if request.method == 'DELETE':
        user.delete()
        return Response({'Message':'Dashboard User deleted'})
    return Response ({'Error':'Failed to delete dashboard user'},status=status.HTTP_400_BAD_REQUEST)

# ******************************************Company Document **************************************

@api_view(['POST'])
def create_companydoc(request,pk):
    client = Client.objects.get(id=pk)
    if request.method == 'POST':
        doc_serializer = CompanyDocSerailizer(data=request.data)
        if doc_serializer.is_valid():
            doc_serializer.save(client=client)
            return Response({'Message':'Company Document Created'}, status=status.HTTP_201_CREATED)
        return Response (doc_serializer.errors,status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST', 'GET'])
def edit_companydoc(request,pk,companydoc_pk):
    client = Client.objects.get(id=pk)
    doc = CompanyDocument.objects.get(id=companydoc_pk)
    doc_serializer = CompanyDocSerailizer(instance=doc, data=request.data)
    if request.method == 'POST':
        if doc_serializer.is_valid():
            doc_serializer.save()
            return Response ({'Message':"Document Updated"})
        return Response (doc_serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'GET':
        doc_ser = CompanyDocSerailizer(doc)
        return Response(doc_ser.data)

@api_view(['GET'])
def list_companydoc(request,pk):
    client = Client.objects.get(id=pk)
    doc_list = FileInfo.objects.filter(client=client)
    serializer = FileInfoSerializer(doc_list,many=True)
    print(serializer)
    return Response(serializer.data)

@api_view(['DELETE'])
def delete_companydoc(request,pk,companydoc_pk):
    client = Client.objects.get(id=pk)
    doc = CompanyDocument.objects.get(id=companydoc_pk, client=client)
    if request.method == 'DELETE':
        doc.delete()
        return Response({'Message':"Document Deleted"})
    return Response({'Error':"Failed to delete document"},status=status.HTTP_400_BAD_REQUEST)

# ************************************** Branch View's ********************************************

@api_view(['POST'])
def create_branch(request, pk):
    client = Client.objects.get(id=pk)
    if request.method == 'POST':
        branch_serializer = BranchSerailizer(data=request.data)
        if branch_serializer.is_valid():
            branch_serializer.save(client=client)
            return Response({'Message':'Branch Created', 'Data': branch_serializer.data}, status=status.HTTP_201_CREATED)
        return Response(branch_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST', 'GET'])
def edit_branch(request,pk,branch_pk):
    client = Client.objects.get(id=pk)
    branch = Branch.objects.get(id = branch_pk)
    if request.method == 'POST':
        branch_serializer = BranchSerailizer(instance=branch, data=request.data)
        if branch_serializer.is_valid():
            branch_serializer.save(client=client)
            return Response({'Message':'Branch Updated'},status=status.HTTP_200_OK)
        return Response({'Error':branch_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'GET':
        branch_ser = BranchSerailizer(branch)
        return Response (branch_ser.data)

@api_view(['GET'])
def list_branch(request,pk):
    client = Client.objects.get(id=pk)
    if request.method == 'GET':
        branch_list = Branch.objects.filter(client=client)
        branch_serializer = BranchSerailizer(branch_list, many=True)
        print(branch_serializer)
        return Response(branch_serializer.data)

@api_view(['DELETE'])
def delete_branch(request,pk,branch_pk):
    client = Client.objects.get(id=pk)
    branch = Branch.objects.get(id=branch_pk)
    if request.method == 'DELETE':
        branch.delete()
        return Response ({'Message':'Branch deleted'})
    return Response ({'Error':'Fail to delete branch'},status=status.HTTP_400_BAD_REQUEST)

# *************************************Office Location**********************************************

@api_view(['POST'])
def create_officelocation(request,branch_pk):
    branch = Branch.objects.get(id=branch_pk)
    if request.method == 'POST':
        officeLocation_serializer = OfficeLocationSerializer(data=request.data)
        if officeLocation_serializer.is_valid():
            officeLocation_serializer.save(branch=branch)
            return Response({'Message':'Office Location Created', 'Data': officeLocation_serializer.data}, status=status.HTTP_201_CREATED)
        return Response ({'Error':'Fail to create Office Location','Error':officeLocation_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST', 'GET'])
def edit_officelocation(request,branch_pk,office_pk):
    branch = Branch.objects.get(id=branch_pk)
    office = OfficeLocation.objects.get(id=office_pk)
    officeLocation_serializer = OfficeLocationSerializer(instance=office, data=request.data)
    if request.method == 'POST':
        if officeLocation_serializer.is_valid():
            officeLocation_serializer.save(branch=branch)
            return Response({'Message':'Office Loaction Update'})
        return Response ({'Error':'Fail to update Office Location','Error':officeLocation_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'GET':
        office_ser = OfficeLocationSerializer(office)
        return Response (office_ser.data)

@api_view(['GET'])
def list_officelocation(request,pk, branch_pk):
    client = Client.objects.get(id=pk)
    branch = Branch.objects.get(id = branch_pk, client=client)
    if request.method == 'GET':
        list_officelocation= OfficeLocation.objects.filter(branch=branch)
        officeLocation_serializer = OfficeLocationSerializer(list_officelocation, many=True)
        print(officeLocation_serializer)
        return Response(officeLocation_serializer.data)

@api_view(['DELETE'])
def delete_officelocation(request,pk, branch_pk, office_pk):
    client = Client.objects.get(id=pk)
    branch = Branch.objects.get(id=branch_pk, client=client)
    office = OfficeLocation.objects.get(id = office_pk, branch = branch)
    if request.method == 'DELETE':
        office.delete()
        return Response({'Message':'Office Location deleted'})
    return Response ({'Error':'Failed to delete office location'}, status=status.HTTP_400_BAD_REQUEST)

# *************************************Customer Or Vendor **************************************

@api_view(['POST'])
def create_customer(request, pk):
    client = Client.objects.get(id=pk)
    if request.method == 'POST':
        customer_serializer = CustomerVendorSerializer(data=request.data)
        if customer_serializer.is_valid():
            customer_serializer.save(client=client)
            return Response({'Message':'Customer or Vendor Created', 'Data' : customer_serializer.data}, status=status.HTTP_201_CREATED)
        return Response ({'Error':'Fail to create Customer or Vendor','Error':customer_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST', 'GET'])
def edit_customer(request, pk, customer_pk):
    client = Client.objects.get(id=pk)
    customer = Customer.objects.get(id=customer_pk)
    customer_serializer = CustomerVendorSerializer(instance=customer, data=request.data)
    if request.method == 'POST':
        if customer_serializer.is_valid():
            customer_serializer.save(client=client)
            return Response({'Message':'Customer or Vendor Updated'})
        return Response({'Error':'Fail to update Customer or Vendor','Error':customer_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'GET':
        customer_ser = CustomerVendorSerializer(customer)
        return Response(customer_ser.data)

@api_view(['GET'])
def list_customer(request, pk):
    client = Client.objects.get(id=pk)
    if request.method == 'GET':
        list_customer = Customer.objects.filter(client=client)
        customer_serializer = CustomerVendorSerializer(list_customer, many=True)
        print(customer_serializer)
        return Response(customer_serializer.data)

@api_view(['DELETE'])
def delete_customer(request,pk, customer_pk):
    client = Client.objects.get(id=pk)
    customer = Customer.objects.get(id=customer_pk)
    if request.method == 'DELETE':
        customer.delete()
        return Response({'Message':'Customer or Vendor deleted'})
    return Response({'Error':'Fail to delete Customer or Vendor'},status=status.HTTP_400_BAD_REQUEST)

# **********************************************Branch Document*********************************************
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def create_branchdoc(request,branch_pk):
    branch = Branch.objects.get(id=branch_pk)
    instance_data = request.data
    data = {key: value for key, value in instance_data.items()}

    serializer = BranchDocSerailizer(data=data)
    if serializer.is_valid(raise_exception=True):
        doc_instance = serializer.save(branch=branch)
        print(request.data)

        if request.FILES:
            files = dict((request.FILES).lists()).get('files',None)
            # files = request.FILES.getlist('files')
            if files:
                for file in files:
                    file_data = {
                        'branch_doc' : doc_instance.pk,
                        'files' : file
                    }
                    file_serializer= FilesSerializer(data=file_data)
                    if file_serializer.is_valid(raise_exception=True):
                        file_serializer.save()

            return Response(serializer.data)
    return Response(serializer.errors)

@api_view(['POST', 'GET'])
@parser_classes([MultiPartParser, FormParser])
def edit_branchdoc(request, branch_pk, branchdoc_pk):
    try:
        branch = Branch.objects.get(id=branch_pk)
        branchdoc = BranchDocument.objects.get(id=branchdoc_pk, branch=branch)
    except Branch.DoesNotExist:
        return Response({'error': 'Branch not found'}, status=status.HTTP_404_NOT_FOUND)
    except BranchDocument.DoesNotExist:
        return Response({'error': 'Branch Document not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'POST':
        # Update branch document fields
        branchdoc_serializer = BranchDocSerailizer(instance=branchdoc, data=request.data)
        if branchdoc_serializer.is_valid():
            branchdoc_serializer.save(branch=branch)

            # Handle file updates separately
            if request.FILES.getlist('files'):
                # Delete the old files if required
                Files.objects.filter(branch_doc=branchdoc).delete()

                # Add the new files
                files = request.FILES.getlist('files')
                for file in files:
                    file_data = {
                        'branch_doc': branchdoc.pk,
                        'files': file
                    }
                    file_serializer = FilesSerializer(data=file_data)
                    if file_serializer.is_valid():
                        file_serializer.save()
                    else:
                        return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            return Response({'Message': 'Branch Document and Files updated successfully'}, status=status.HTTP_200_OK)
        else:
            return Response(branchdoc_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET':
        branchdoc_serializer = BranchDocSerailizer(branchdoc)
        return Response(branchdoc_serializer.data)

@api_view(['GET'])
def list_branchdoc(request, branch_pk):
    branch = Branch.objects.get(id = branch_pk)
    # branchdoc = BranchDocument.objects.get(id = branchdoc_pk, branch=branch)
    if request.method == 'GET':
        list_branchdoc = BranchDocument.objects.filter(branch=branch)
        branchdoc_serializer = BranchDocSerailizer(list_branchdoc, many=True)
        print(branchdoc_serializer)
        return Response(branchdoc_serializer.data)

@api_view(['GET'])
def single_branchdoc(request, branch_pk, branchdoc_pk):
    branch = Branch.objects.get(id=branch_pk)
    doc = BranchDocument.objects.get(id = branchdoc_pk, branch=branch)
    if request.method == 'GET':
        ser = BranchDocSerailizer(doc)
        print(ser)
        return Response(ser.data)

@api_view(['DELETE'])
def delete_branchdoc(request,branch_pk, branchdoc_pk ):
    branch = Branch.objects.get(id = branch_pk)
    branchdoc = BranchDocument.objects.get(id = branchdoc_pk, branch=branch)
    if request.method == 'DELETE':
        branchdoc.delete()
        return Response({'Messgae':'Branch Document Delete'})
    return Response({'Message':'Fail to delete branch document'} ,status=status.HTTP_400_BAD_REQUEST)

# **********************************************# Income Tax Document******************************************
@api_view(['POST'])
def create_incometaxdoc(request,pk):
    client = Client.objects.get(id = pk)
    if request.method == 'POST':
        income_serializer = IncomeTaxDocumentSerializer(data=request.data)
        if income_serializer.is_valid():
            income_serializer.save(client=client)
            return Response({'Message':'Income Tax Document created', 'Data': income_serializer.data})
        return Response ({'Error':'Fail to create income tax'},status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST','GET'])
def edit_incometaxdoc(request, pk, income_pk):
    client = Client.objects.get(id=pk)
    income = IncomeTaxDocument.objects.get(id = income_pk, client=client)
    income_serializer = IncomeTaxDocumentSerializer(instance=income, data=request.data)
    if request.method == 'POST':
        if income_serializer.is_valid():
            income_serializer.save(income=income)
            return Response({'Message':'Income tax document updated'})
        return Response({'Error':'Fail to update','Error': income_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'GET':
        income_ser = IncomeTaxDocumentSerializer(income)
        return Response(income_ser.data)

@api_view(['GET'])
def list_incometaxdoc(request,pk):
    client = Client.objects.get(id=pk)
    if request.method == 'GET':
        list_income = IncomeTaxDocument.objects.filter(client=client)
        income_serializer = IncomeTaxDocumentSerializer(list_income, many=True)
        print(income_serializer)
        return Response(income_serializer.data)

@api_view(['DELETE'])
def delete_incometaxdoc(request,pk,income_pk):
    client = Client.objects.get(id=pk)
    income = IncomeTaxDocument.objects.get(id=income_pk)
    if request.method == 'DELETE':
        income.delete()
        return Response({'Message':'Income tax document deleted'})
    return Response ({'Message':'Fail to delete Income tax document'}, status=status.HTTP_400_BAD_REQUEST)

#*****************************************************PF*******************************************************
@api_view(['POST'])
def create_pf(request,pk):
    client = Client.objects.get(id = pk)
    if request.method == 'POST':
        pf_serializer = PfSerializer(data=request.data)
        if pf_serializer.is_valid():
            pf_serializer.save(client=client)
            return Response({'Message':'Pf created', 'Data' : pf_serializer.data})
        return Response (pf_serializer.errors,status=status.HTTP_400_BAD_REQUEST)

# class ExcelImportView(APIView):
#     parser_classes = [MultiPartParser]

#     def post(self, request, pk, *args, **kwargs):
#         # Get the client using the pk from the URL
#         try:
#             client = Client.objects.get(pk=pk)
#         except Client.DoesNotExist:
#             return Response({"error": "Client not found"}, status=404)

#         file = request.FILES['file']

#         # Load the workbook and select the active worksheet
#         wb = load_workbook(file)
#         ws = wb.active

#         pf_entries = []

#         # Iterate through the rows in the Excel file and create/update PF objects
#         for row in ws.iter_rows(min_row=2):  # Skip the header row
#             employee_code = row[0].value
#             employee_name = row[1].value

#             # Skip rows without essential fields
#             if not employee_code or not employee_name:
#                 continue

#             # Get the rest of the values
#             uan = row[2].value
#             pf_number = row[3].value
#             pf_deducted = row[4].value
#             date_of_joining = row[5].value
#             status = row[6].value
#             month = row[7].value
#             gross_ctc = row[8].value
#             basic_pay = row[9].value
#             hra = row[10].value
#             statutory_bonus = row[11].value
#             special_allowance = row[12].value
#             pf = row[13].value
#             gratuity = row[14].value
#             total_gross_salary = row[15].value
#             number_of_days_in_month = row[16].value
#             present_days = row[17].value
#             lwp = row[18].value
#             leave_adjustment = row[19].value
#             gender = row[20].value
#             basic_pay_monthly = row[21].value
#             hra_monthly = row[22].value
#             statutory_bonus_monthly = row[23].value
#             special_allowance_monthly = row[24].value
#             total_gross_salary_monthly = row[25].value
#             provident_fund = row[26].value
#             professional_tax = row[27].value
#             advance = row[28].value
#             esic_employee = row[29].value
#             tds = row[30].value
#             total_deduction = row[31].value
#             net_pay = row[32].value
#             advance_esic_employer_cont = row[33].value

#             # Check if the PF entry for the employee_code and month already exists
#             existing_pf_entry = PF.objects.filter(employee_code=employee_code, month=month).first()

#             if existing_pf_entry:
#                 # If it exists, update the existing entry
#                 existing_pf_entry.employee_name = employee_name
#                 existing_pf_entry.uan = uan
#                 existing_pf_entry.pf_number = pf_number
#                 existing_pf_entry.pf_deducted = pf_deducted
#                 existing_pf_entry.date_of_joining = date_of_joining
#                 existing_pf_entry.status = status
#                 existing_pf_entry.gross_ctc = gross_ctc
#                 existing_pf_entry.basic_pay = basic_pay
#                 existing_pf_entry.hra = hra
#                 existing_pf_entry.statutory_bonus = statutory_bonus
#                 existing_pf_entry.special_allowance = special_allowance
#                 existing_pf_entry.pf = pf
#                 existing_pf_entry.gratuity = gratuity
#                 existing_pf_entry.total_gross_salary = total_gross_salary
#                 existing_pf_entry.number_of_days_in_month = number_of_days_in_month
#                 existing_pf_entry.present_days = present_days
#                 existing_pf_entry.lwp = lwp
#                 existing_pf_entry.leave_adjustment = leave_adjustment
#                 existing_pf_entry.gender = gender
#                 existing_pf_entry.basic_pay_monthly = basic_pay_monthly
#                 existing_pf_entry.hra_monthly = hra_monthly
#                 existing_pf_entry.statutory_bonus_monthly = statutory_bonus_monthly
#                 existing_pf_entry.special_allowance_monthly = special_allowance_monthly
#                 existing_pf_entry.total_gross_salary_monthly = total_gross_salary_monthly
#                 existing_pf_entry.provident_fund = provident_fund
#                 existing_pf_entry.professional_tax = professional_tax
#                 existing_pf_entry.advance = advance
#                 existing_pf_entry.esic_employee = esic_employee
#                 existing_pf_entry.tds = tds
#                 existing_pf_entry.total_deduction = total_deduction
#                 existing_pf_entry.net_pay = net_pay
#                 existing_pf_entry.advance_esic_employer_cont = advance_esic_employer_cont
#                 existing_pf_entry.save()

#                 pf_entries.append(existing_pf_entry)

#             else:
#                 # If it doesn't exist, create a new PF entry
#                 pf_entry = PF(
#                     client=client,
#                     employee_code=employee_code,
#                     employee_name=employee_name,
#                     uan=uan,
#                     pf_number=pf_number,
#                     pf_deducted=pf_deducted,
#                     date_of_joining=date_of_joining,
#                     status=status,
#                     month=month,
#                     gross_ctc=gross_ctc,
#                     basic_pay=basic_pay,
#                     hra=hra,
#                     statutory_bonus=statutory_bonus,
#                     special_allowance=special_allowance,
#                     pf=pf,
#                     gratuity=gratuity,
#                     total_gross_salary=total_gross_salary,
#                     number_of_days_in_month=number_of_days_in_month,
#                     present_days=present_days,
#                     lwp=lwp,
#                     leave_adjustment=leave_adjustment,
#                     gender=gender,
#                     basic_pay_monthly=basic_pay_monthly,
#                     hra_monthly=hra_monthly,
#                     statutory_bonus_monthly=statutory_bonus_monthly,
#                     special_allowance_monthly=special_allowance_monthly,
#                     total_gross_salary_monthly=total_gross_salary_monthly,
#                     provident_fund=provident_fund,
#                     professional_tax=professional_tax,
#                     advance=advance,
#                     esic_employee=esic_employee,
#                     tds=tds,
#                     total_deduction=total_deduction,
#                     net_pay=net_pay,
#                     advance_esic_employer_cont=advance_esic_employer_cont,
#                 )
#                 pf_entry.save()
#                 pf_entries.append(pf_entry)

#         return Response({"status": "success", "data": PfSerializer(pf_entries, many=True).data})

class ExcelImportView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, pk, *args, **kwargs):
        # Get the client using the pk from the URL
        try:
            client = Client.objects.get(pk=pk)
        except Client.DoesNotExist:
            return Response({"error": "Client not found"}, status=404)

        file = request.FILES['file']

        # Load the workbook and select the active worksheet
        wb = load_workbook(file)
        ws = wb.active

        pf_entries = []

        # Define the fields in a list to optimize the entry creation
        fields = [
            'employee_code', 'employee_name', 'uan', 'pf_number', 'pf_deducted',
            'date_of_joining', 'status', 'month', 'gross_ctc', 'basic_pay',
            'hra', 'statutory_bonus', 'special_allowance', 'pf', 'gratuity',
            'total_gross_salary', 'number_of_days_in_month', 'present_days',
            'lwp', 'leave_adjustment', 'gender', 'basic_pay_monthly',
            'hra_monthly', 'statutory_bonus_monthly', 'special_allowance_monthly',
            'total_gross_salary_monthly', 'provident_fund', 'professional_tax',
            'advance', 'esic_employee', 'tds', 'total_deduction', 'net_pay',
            'advance_esic_employer_cont'
        ]

        # Iterate through the rows in the Excel file and create or update PF objects
        for row in ws.iter_rows(min_row=2):  # Skip the header row
            # Create a dictionary for the current row
            data = {field: row[i].value for i, field in enumerate(fields)}

            employee_code = data['employee_code']
            month = data['month']

            # Skip rows without essential fields
            if not employee_code or not month:
                continue

            # Check if an entry with the same employee_code and month exists
            instance = PF.objects.filter(employee_code=employee_code, month=month).first()

            if instance:
                # Update existing entry
                for field, value in data.items():
                    setattr(instance, field, value)
                instance.save()
            else:
                # Create new PF entry and associate it with the client
                pf_entry = PF(client=client, **data)
                pf_entry.save()
                pf_entries.append(pf_entry)

        return Response({"status": "success", "data": PfSerializer(pf_entries, many=True).data})



@api_view(['POST','GET'])
def edit_pf(request, pk, pf_pk):
    client = Client.objects.get(id=pk)
    # income = IncomeTaxDocument.objects.get(id = pf_pk, client=client)
    pf = PF.objects.get(id = pf_pk, client=client)
    pf_serializer = PfSerializer(instance=pf, data=request.data)
    if request.method == 'POST':
        if  pf_serializer.is_valid():
            pf_serializer.save()
            return Response({'Message':'Pf updated'})
        return Response(pf_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'GET':
        pf_ser = PfSerializer(pf)
        return Response(pf_ser.data)

@api_view(['GET'])
def list_pf(request,pk):
    client = Client.objects.get(id=pk)
    if request.method == 'GET':
        list_pf = PF.objects.filter(client=client)
        pf_serializer = PfSerializer(list_pf, many=True)
        print(pf_serializer)
        return Response(pf_serializer.data)

@api_view(['DELETE'])
def delete_pf(request,pk,pf_pk):
    client = Client.objects.get(id=pk)
    pf = PF.objects.get(id=pf_pk)
    if request.method == 'DELETE':
        pf.delete()
        return Response({'Message':'Pf deleted'})
    return Response ({'Message':'Fail to delete Pf'}, status=status.HTTP_400_BAD_REQUEST)
# ***********************************************Tax Audit***************************************************
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def create_taxaudit(request,pk):
    client = Client.objects.get(id=pk)
    instance_data = request.data
    data = {key: value for key, value in instance_data.items()}

    serializer = TaxAuditSerializer(data=data)
    if serializer.is_valid(raise_exception=True):
        tax_instance = serializer.save(client=client)
        print(request.data)

        if request.FILES:
            files = dict((request.FILES).lists()).get('files',None)
            # files = request.FILES.getlist('files')
            if files:
                for file in files:
                    file_data = {
                        'tax_audit' : tax_instance.pk,
                        'files' : file
                    }
                    file_serializer= FilesSerializer(data=file_data)
                    if file_serializer.is_valid(raise_exception=True):
                        file_serializer.save()

            return Response({'Message':'taxaudit created','Data':serializer.data})
    return Response(serializer.errors)

@api_view(['POST', 'GET'])
@parser_classes([MultiPartParser, FormParser])
def edit_taxaudit(request, pk, taxaudit_pk):
    try:
        client = Client.objects.get(id=pk)
        taxaudit = TaxAudit.objects.get(id=taxaudit_pk, client=client)
    except Client.DoesNotExist:
        return Response({'error': 'Client not found'}, status=status.HTTP_404_NOT_FOUND)
    except TaxAudit.DoesNotExist:
        return Response({'error': 'Tax Aduit not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'POST':
        # Update branch document fields
        taxaudit_serializer = TaxAuditSerializer(instance=taxaudit, data=request.data)
        if taxaudit_serializer.is_valid():
            taxaudit_serializer.save(client=client)

            # Handle file updates separately
            if request.FILES.getlist('files'):
                # Delete the old files if required
                Files.objects.filter(tax_audit=taxaudit).delete()

                # Add the new files
                files = request.FILES.getlist('files')
                for file in files:
                    file_data = {
                        'tax_audit': taxaudit.pk,
                        'files': file
                    }
                    file_serializer = FilesSerializer(data=file_data)
                    if file_serializer.is_valid():
                        file_serializer.save()
                    else:
                        return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            return Response({'Message': 'Tax Audit and Files updated successfully'}, status=status.HTTP_200_OK)
        else:
            return Response(taxaudit_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET':
        taxaudit_serializer = TaxAuditSerializer(taxaudit)
        return Response(taxaudit_serializer.data)

@api_view(['GET'])
def list_taxaudit(request, pk):
    client = Client.objects.get(id = pk)
    if request.method == 'GET':
        list_taxaudit = TaxAudit.objects.filter(client=client)
        taxaudit_serializer = TaxAuditSerializer(list_taxaudit, many=True)
        print(taxaudit_serializer)
        return Response(taxaudit_serializer.data)

@api_view(['GET'])
def single_taxaudit(request, pk, taxaudit_pk):
    client = Client.objects.get(id=pk)
    taxaudit = TaxAudit.objects.get(id = taxaudit_pk, client=client)
    if request.method == 'GET':
        ser = TaxAuditSerializer(taxaudit)
        print(ser)
        return Response(ser.data)

@api_view(['DELETE'])
def delete_taxaudit(request, pk, taxaudit_pk ):
    client = Client.objects.get(id = pk)
    taxaudit = TaxAudit.objects.get(id = taxaudit_pk, client=client)
    if request.method == 'DELETE':
        taxaudit.delete()
        return Response({'Messgae':'Tax Audit Delete'})
    return Response({'Message':'Fail to delete Tax Audit'} ,status=status.HTTP_400_BAD_REQUEST)

# ******************************************************AIR****************************************************
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def create_air(request,pk):
    client = Client.objects.get(id=pk)
    instance_data = request.data
    data = {key: value for key, value in instance_data.items()}

    serializer = AIRSerializer(data=data)
    if serializer.is_valid(raise_exception=True):
        air_instance = serializer.save(client=client)
        print(request.data)

        if request.FILES:
            files = dict((request.FILES).lists()).get('files',None)
            # files = request.FILES.getlist('files')
            if files:
                for file in files:
                    file_data = {
                        'air' : air_instance.pk,
                        'files' : file
                    }
                    file_serializer= FilesSerializer(data=file_data)
                    if file_serializer.is_valid(raise_exception=True):
                        file_serializer.save()

            return Response({'Message':'taxaudit created','Data':serializer.data})
    return Response(serializer.errors)

@api_view(['POST', 'GET'])
@parser_classes([MultiPartParser, FormParser])
def edit_air(request, pk, air_pk):
    try:
        client = Client.objects.get(id=pk)
        air = AIR.objects.get(id=air_pk, client=client)
    except Client.DoesNotExist:
        return Response({'error': 'Client not found'}, status=status.HTTP_404_NOT_FOUND)
    except AIR.DoesNotExist:
        return Response({'error': 'AIR not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'POST':
        # Update branch document fields
        air_serializer = AIRSerializer(instance=air, data=request.data)
        if air_serializer.is_valid():
            air_serializer.save(client=client)

            # Handle file updates separately
            if request.FILES.getlist('files'):
                # Delete the old files if required
                Files.objects.filter(air=air).delete()

                # Add the new files
                files = request.FILES.getlist('files')
                for file in files:
                    file_data = {
                        'air': air.pk,
                        'files': file
                    }
                    file_serializer = FilesSerializer(data=file_data)
                    if file_serializer.is_valid():
                        file_serializer.save()
                    else:
                        return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            return Response({'Message': 'AIR and Files updated successfully'}, status=status.HTTP_200_OK)
        else:
            return Response(air_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET':
        air_serializer = AIRSerializer(air)
        return Response(air_serializer.data)

@api_view(['GET'])
def list_air(request, pk):
    client = Client.objects.get(id = pk)
    if request.method == 'GET':
        list_air = AIR.objects.filter(client=client)
        air_serializer = AIRSerializer(list_air, many=True)
        print(air_serializer)
        return Response(air_serializer.data)

@api_view(['GET'])
def single_air(request, pk, air_pk):
    client = Client.objects.get(id=pk)
    air = AIR.objects.get(id = air_pk, client=client)
    if request.method == 'GET':
        ser = AIRSerializer(air)
        print(ser)
        return Response(ser.data)

@api_view(['DELETE'])
def delete_air(request, pk, air_pk ):
    client = Client.objects.get(id = pk)
    air = AIR.objects.get(id = air_pk, client=client)
    if request.method == 'DELETE':
        air.delete()
        return Response({'Messgae':'AIR Delete'})
    return Response({'Message':'Fail to delete AIR'} ,status=status.HTTP_400_BAD_REQUEST)

# ******************************************************SFT****************************************************
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def create_sft(request,pk):
    client = Client.objects.get(id=pk)
    instance_data = request.data
    data = {key: value for key, value in instance_data.items()}

    serializer = SFTSerializer(data=data)
    if serializer.is_valid(raise_exception=True):
        sft_instance = serializer.save(client=client)
        print(request.data)

        if request.FILES:
            files = dict((request.FILES).lists()).get('files',None)
            # files = request.FILES.getlist('files')
            if files:
                for file in files:
                    file_data = {
                        'sft' : sft_instance.pk,
                        'files' : file
                    }
                    file_serializer= FilesSerializer(data=file_data)
                    if file_serializer.is_valid(raise_exception=True):
                        file_serializer.save()

            return Response({'Message':'taxaudit created','Data':serializer.data})
    return Response(serializer.errors)

@api_view(['POST', 'GET'])
@parser_classes([MultiPartParser, FormParser])
def edit_sft(request, pk, sft_pk):
    try:
        client = Client.objects.get(id=pk)
        sft = SFT.objects.get(id=sft_pk, client=client)
    except Client.DoesNotExist:
        return Response({'error': 'Client not found'}, status=status.HTTP_404_NOT_FOUND)
    except SFT.DoesNotExist:
        return Response({'error': 'SFT not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'POST':
        # Update branch document fields
        sft_serializer = SFTSerializer(instance=sft, data=request.data)
        if sft_serializer.is_valid():
            sft_serializer.save(client=client)

            # Handle file updates separately
            if request.FILES.getlist('files'):
                # Delete the old files if required
                Files.objects.filter(sft=sft).delete()

                # Add the new files
                files = request.FILES.getlist('files')
                for file in files:
                    file_data = {
                        'sft': sft.pk,
                        'files': file
                    }
                    file_serializer = FilesSerializer(data=file_data)
                    if file_serializer.is_valid():
                        file_serializer.save()
                    else:
                        return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            return Response({'Message': 'SFT and Files updated successfully'}, status=status.HTTP_200_OK)
        else:
            return Response(sft_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET':
        sft_serializer = SFTSerializer(sft)
        return Response(sft_serializer.data)

@api_view(['GET'])
def list_sft(request, pk):
    client = Client.objects.get(id = pk)
    if request.method == 'GET':
        list_sft = SFT.objects.filter(client=client)
        sft_serializer = SFTSerializer(list_sft, many=True)
        print(sft_serializer)
        return Response(sft_serializer.data)

@api_view(['GET'])
def single_sft(request, pk, sft_pk):
    client = Client.objects.get(id=pk)
    sft = SFT.objects.get(id = sft_pk, client=client)
    if request.method == 'GET':
        ser = SFTSerializer(sft)
        print(ser)
        return Response(ser.data)

@api_view(['DELETE'])
def delete_sft(request, pk, sft_pk ):
    client = Client.objects.get(id = pk)
    sft = SFT.objects.get(id = sft_pk, client=client)
    if request.method == 'DELETE':
        sft.delete()
        return Response({'Messgae':'SFT Delete'})
    return Response({'Message':'Fail to delete SFT'} ,status=status.HTTP_400_BAD_REQUEST)


# *************************************************TDS Payment***********************************************
@api_view(['POST'])
def create_tdspayment(request, pk):
    client = Client.objects.get(id=pk)
    if request.method == 'POST':
        serializer = TDSPaymentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(client=client)
            return Response ({'Message':'TDS Payment created', 'Data': serializer.data})
        return Response({'Error':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST'])
def edit_tdspayment(request, pk, tdspayment_pk):
    client = Client.objects.get(id=pk)
    payment = TDSPayment.objects.get(id=tdspayment_pk, client=client)
    serializer = TDSPaymentSerializer(instance=payment, data=request.data)
    if request.method == 'GET':
        tds_serializer = TDSPaymentSerializer(payment)
        print(tds_serializer.data)
        return Response (tds_serializer.data)
    elif request.method == 'POST':
        if serializer.is_valid():
            serializer.save(client=client)
            return Response ({'Message':'TDS Paymen Updated'})
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def list_tdspayment(request, pk):
    client = Client.objects.get(id=pk)
    if request.method == 'GET':
        list_tdspayment = TDSPayment.objects.filter(client=client)
        tds_ser = TDSPaymentSerializer(list_tdspayment, many = True)
        return Response(tds_ser.data)

@api_view(['GET'])
def single_tdspayment(request, pk, tdspayment_pk):
    client = Client.objects.get(id=pk)
    tds = TDSPayment.objects.get(id=tdspayment_pk)
    if request.method == 'GET':
        ser = TDSPaymentSerializer(tds)
        return Response(ser.data)

@api_view(['DELETE'])
def delete_tdspayment(request, pk, tdspayment_pk):
    client = Client.objects.get(id=pk)
    tds = TDSPayment.objects.get(id=tdspayment_pk)
    if request.method == 'DELETE':
        tds.delete()
        return Response({'Message':'TDS Payment delete'})
    return Response (status=status.HTTP_400_BAD_REQUEST)

# *************************************************TDS Return**************************************************
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def create_tds(request,pk):
    client = Client.objects.get(id=pk)
    instance_data = request.data
    data = {key: value for key, value in instance_data.items()}

    serializer = TDSReturnSerializer(data=data)
    if serializer.is_valid(raise_exception=True):
        tds_instance = serializer.save(client=client)
        print(request.data)

        if request.FILES:
            files = dict((request.FILES).lists()).get('files',None)
            # files = request.FILES.getlist('files')
            if files:
                for file in files:
                    file_data = {
                        'tds' : tds_instance.pk,
                        'files' : file
                    }
                    file_serializer= FilesSerializer(data=file_data)
                    if file_serializer.is_valid(raise_exception=True):
                        file_serializer.save()

            return Response({'Message':'taxaudit created','Data':serializer.data})
    return Response(serializer.errors)

@api_view(['POST', 'GET'])
@parser_classes([MultiPartParser, FormParser])
def edit_tds(request, pk, tds_pk):
    try:
        client = Client.objects.get(id=pk)
        tds = TDSReturn.objects.get(id=tds_pk, client=client)
    except Client.DoesNotExist:
        return Response({'error': 'Client not found'}, status=status.HTTP_404_NOT_FOUND)
    except TDSReturn.DoesNotExist:
        return Response({'error': 'TDS Return not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'POST':
        # Update branch document fields
        tds_serializer = TDSReturnSerializer(instance=tds, data=request.data)
        if tds_serializer.is_valid():
            tds_serializer.save(client=client)

            # Handle file updates separately
            if request.FILES.getlist('files'):
                # Delete the old files if required
                Files.objects.filter(tds=tds).delete()

                # Add the new files
                files = request.FILES.getlist('files')
                for file in files:
                    file_data = {
                        'tds': tds.pk,
                        'files': file
                    }
                    file_serializer = FilesSerializer(data=file_data)
                    if file_serializer.is_valid():
                        file_serializer.save()
                    else:
                        return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            return Response({'Message': 'TDS Return and Files updated successfully'}, status=status.HTTP_200_OK)
        else:
            return Response(tds_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET':
        tdsreturn_serializer = TDSReturnSerializer(tds)
        return Response(tdsreturn_serializer.data)

@api_view(['GET'])
def list_tds(request, pk):
    client = Client.objects.get(id = pk)
    if request.method == 'GET':
        list_tds = TDSReturn.objects.filter(client=client)
        tds_serializer = TDSReturnSerializer(list_tds, many=True)
        # print(sft_serializer)
        return Response(tds_serializer.data)

@api_view(['GET'])
def single_tds(request, pk, tds_pk):
    client = Client.objects.get(id=pk)
    tds = TDSReturn.objects.get(id = tds_pk, client=client)
    if request.method == 'GET':
        ser = TDSReturnSerializer(tds)
        print(ser)
        return Response(ser.data)

@api_view(['DELETE'])
def delete_tds(request, pk, tds_pk ):
    client = Client.objects.get(id = pk)
    tds = TDSReturn.objects.get(id = tds_pk, client=client)
    if request.method == 'DELETE':
        tds.delete()
        return Response({'Messgae':'TDS Return Delete'})
    return Response({'Message':'Fail to delete TDS Return'} ,status=status.HTTP_400_BAD_REQUEST)

# ***********************************************Sales*******************************************
# @api_view(['GET', 'POST'])
# def create_sales(request, pk):
#     try:
#         client = Client.objects.get(id=pk)
#     except Client.DoesNotExist:
#         return Response({"error": "Client not found."}, status=404)

#     if request.method == 'GET':
#         off = OfficeLocation.objects.filter(branch__client=client)
#         customer = Customer.objects.filter(client=client, customer=True)
#         product = Product.objects.all()

#         serializer_customer = CustomerVendorSerializer(customer, many=True)
#         serializer = OfficeLocationSerializer(off, many=True)
#         product_serializer = ProductSerializer(product, many=True)

#         # Retrieve query parameters
#         received_value = request.GET.get('newValue')
#         product_id = request.GET.get('productID')


#         print("Received newValue:", received_value)
#         print("Received productID:", product_id)  # Check if productID is received
#         if product_id:
#             print('eysss')
#             try:

#                 hsn_cc = Product.objects.get(id = product_id).hsn
#                 # hsn_cc_serializer = HSNSerializer(hsn_cc)
#                 return Response({
#                     "message": "Product HSN found",
#                     "hsn": HSNSerializer(hsn_cc).data
#                 })

#                 # print('products',hsn_cc_serializer)
#             except(ValueError, Product.DoesNotExist):
#                 return Response({"error": "Invalid Product ID."},status=400)

#         # Process received_value
#         if received_value:
#             try:
#                 received_value = int(received_value)
#                 location = OfficeLocation.objects.get(id=received_value)
#                 return Response({
#                     "message": "Location found",
#                     "location": OfficeLocationSerializer(location).data
#                 })
#             except (ValueError, OfficeLocation.DoesNotExist):
#                 return Response({"error": "Invalid location ID."}, status=400)
#         # Return all if no specific location is selected
#         context = {
#             'serializer_customer': serializer_customer.data,
#             'serializer': serializer.data,
#             'product_serializer': product_serializer.data
#         }
#         return Response(context)

@api_view(['GET', 'POST'])
def create_sales_get(request, pk):
    try:
        client = Client.objects.get(id=pk)
    except Client.DoesNotExist:
        return Response({"error": "Client not found."}, status=404)

    if request.method == 'GET':
        # Initialize response context with default values
        context = {
            'serializer_customer': [],
            'serializer': [],
            'product_serializer': [],
            'message': None,
            'hsn': None,
            'location': None
        }

        # Retrieve query parameters
        received_value = request.GET.get('newValue')
        product_id = request.GET.get('productID')

        # Process productID if it exists
        if product_id:
            try:
                hsn_cc = Product.objects.get(id=product_id).hsn
                context.update({
                    "message": "Product HSN found",
                    "hsn": HSNSerializer(hsn_cc).data
                })
            except (ValueError, Product.DoesNotExist):
                return Response({"error": "Invalid Product ID."}, status=400)

        # Process received_value if it exists
        if received_value:
            try:
                received_value = int(received_value)
                location = OfficeLocation.objects.get(id=received_value)
                context.update({
                    "message": "Location found",
                    "location": OfficeLocationSerializer(location).data
                })
            except (ValueError, OfficeLocation.DoesNotExist):
                return Response({"error": "Invalid location ID."}, status=400)

        # Add data only if productID and received_value were not provided
        if not product_id and not received_value:
            off = OfficeLocation.objects.filter(branch__client=client)
            customer = Customer.objects.filter(client=client, customer=True)
            product = Product.objects.all()
            branch = Branch.objects.all()

            serializer_customer = CustomerVendorSerializer(customer, many=True)
            serializer = OfficeLocationSerializer(off, many=True)
            product_serializer = ProductSerializer(product, many=True)
            branch_serializer = BranchSerailizer(branch, many=True)

            context.update({
                'serializer_customer': serializer_customer.data,
                'serializer': serializer.data,
                'product_serializer': product_serializer.data,
                'branch_serializer': branch_serializer.data
            })

        return Response(context)


# @api_view(['POST'])
# def create_sale(request, pk):
#     client = Client.objects.get(id=pk)
#     if request.method == 'POST':
#         serializers = SalesSerializer(data=request.data)
#         if serializers.is_valid():
#             serializers.save(client=client)
#             return Response({'Message':'Sales E-way bill uploaded', 'Data':serializers.data})
#         return Response({'Error':serializers.errors}, status=status.HTTP_400_BAD_REQUEST)
# @api_view(['POST'])
# def create_sale(request, pk):
#     client = Client.objects.get(id=pk)
#     if request.method == 'POST':
#         # Assuming 'files' is a list of file data sent in the request
#         files = request.FILES.getlist('files')  # Get the list of files from the request

#         # Check if files are uploaded
#         if not files:
#             return Response({'Error': 'No files uploaded'}, status=status.HTTP_400_BAD_REQUEST)

#         # Create an empty list to store all the serializers for each file
#         created_entries = []

#         # Loop through the uploaded files and create individual sale entries
#         for file in files:
#             # Create a separate serializer for each file
#             sale_data = request.data.copy()  # Make a copy of the request data
#             sale_data['file'] = file  # Add the current file to the data

#             serializer = SalesSerializer(data=sale_data)
#             if serializer.is_valid():
#                 # Save each entry separately, associating the sale with the client
#                 created_entry = serializer.save(client=client)
#                 created_entries.append(created_entry)
#             else:
#                 return Response({'Error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

#         # If all files are uploaded successfully, return a success response with the created entries
#         return Response({'Message': 'Sales E-way bill uploaded for multiple files', 'Data' :serializer.data})


@api_view(['POST'])
def create_sale(request, pk):
    client = Client.objects.get(id=pk)

    # Check if 'attach_e_way_bill' is in the request files
    if 'attach_e_way_bill' in request.FILES:
        # Iterate through each file in the 'attach_e_way_bill' field
        for e_way_bill in request.FILES.getlist('attach_e_way_bill'):
            # Prepare data for each file
            sale_data = {
                'attach_e_way_bill': e_way_bill,  # The file being uploaded
                'client': client.id,  # Associate the file with the client
            }

            # Initialize the serializer for each file
            serializer = SalesSerializer2(data=sale_data)

            # Check if the serializer is valid
            if serializer.is_valid():
                # Save each file as a separate object
                serializer.save()
            else:
                return Response({'Error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        # If all files are processed, return success response
        return Response({'Message': 'Sales E-way bill(s) uploaded successfully.'}, status=status.HTTP_201_CREATED)
    else:
        return Response({'Error': 'No files uploaded in the request.'}, status=status.HTTP_400_BAD_REQUEST)

# @api_view(['POST'])
# def create_sales_post(request,pk):

#     if request.method=='POST':
#         print('this is post',request.data)
#         form_data = request.data.get('formData', {})
#         off_serializer = OfficeLocationSerializer(data=form_data)
#         if off_serializer.is_valid():

#             off_serializer.save()

#         print('vendor data',off_serializer)
#         return Response({'Message':'working'})




from decimal import Decimal, InvalidOperation

# Helper function to safely convert to Decimal
def safe_decimal(value, default='0'):
    try:
        return Decimal(value)
    except (ValueError, InvalidOperation):
        return Decimal(default)

@api_view(['POST'])
def create_sales_post(request, pk):
    if request.method == 'POST':
        print('this post', request.data)
        form_data = request.data.get('formData', {})
        vendor_data = request.data.get('vendorData', {})
        rows = request.data.get('rows', [])

        off_loc_id = form_data.get('offLocID')
        location = form_data.get('location')
        branch_id = form_data.get('branchID')
        vendor_id = vendor_data.get('vendorID')

        location_exists = False
        vendor_exists = False
        off_location = None  # Initialize off_location to None
        off_serializer = None  # Initialize off_serializer to None
        print('locc id', off_loc_id)

        # Check for existing location
        if off_loc_id:
            existing_location = OfficeLocation.objects.filter(id=off_loc_id, location=location).first()
            if existing_location:
                location_exists = True
                off_location = existing_location  # Assign the existing location

        # Check for existing vendor
        if vendor_id:
            existing_vendor = Customer.objects.filter(id=vendor_id, client=pk).first()
            if existing_vendor:
                vendor_exists = True
                vendor = existing_vendor  # Assign the existing vendor

        # Retrieve related instances for saving new records
        branch_instance = Branch.objects.get(id=branch_id) if branch_id else None
        client_instance = Client.objects.get(id=pk) if pk else None

        # Create vendor if it doesn't exist
        if not vendor_exists:
            vendor_serializer = CustomerVendorSerializer(data=vendor_data)
            if vendor_serializer.is_valid():
                vendor = vendor_serializer.save(client=client_instance)  # Save and assign vendor
            else:
                return Response(vendor_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Create location if it doesn't exist
        if not location_exists:
            off_serializer = OfficeLocationSerializer(data=form_data)
            if off_serializer.is_valid():
                off_location = off_serializer.save(branch=branch_instance)  # Save and assign location
            else:
                return Response(off_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Process rows and create ProductSummaries
        product_summaries = []
        for row in rows:
            hsn_code = row.get('hsnCode')
            gst_rate = safe_decimal(row.get('gstRate', '0'))
            product_name = row.get('product')
            description_text = row.get('description')
            unit_value = safe_decimal(row.get('unit', '0'))

            hsn_code_obj, _ = HSNCode.objects.get_or_create(hsn_code=hsn_code, defaults={'gst_rate': gst_rate})
            product_obj, _ = Product.objects.get_or_create(product_name=product_name, defaults={'hsn': hsn_code_obj})
            product_description_obj, _ = ProductDescription.objects.get_or_create(
                product=product_obj, description=description_text, defaults={'unit': unit_value})

            product_summary = ProductSummary.objects.create(
                hsn=hsn_code_obj, product=product_obj, prod_description=product_description_obj)
            product_summaries.append(product_summary)

        # Prepare the sales invoice data with the correct PK values
        sales_invoice_data = {
            'client_Location': off_location.id if off_location else None,  # Use location ID if exists
            'customer': vendor.id if vendor else None,  # Use vendor ID if exists
            'product_summaries': [ps.id for ps in product_summaries],  # Use only the IDs for product summaries
            'invoice_no': form_data.get('invoiceNo'),
            'invoice_date': form_data.get('invoiceDate'),
            'invoice_type': form_data.get('invoiceType'),
            'entry_type': form_data.get('entryType'),
            'taxable_amount': form_data.get('taxableAmount'),
            'cgst': form_data.get('cgst'),
            'sgst': form_data.get('sgst'),
            'igst': form_data.get('igst'),
            'total_invoice_value': form_data.get('totalInvoiceValue'),
            'tds_tcs_rate': form_data.get('tdsTcsRate'),
            'tds_tcs_section': form_data.get('tdsTcsSection'),
            'tds': form_data.get('tds'),
            'tcs': form_data.get('tcs'),
            'amount_receivable': form_data.get('amountReceivable'),
        }

        sales_invoice_serializer = SalesSerializer(data=sales_invoice_data)
        if sales_invoice_serializer.is_valid():
            sales_invoice = sales_invoice_serializer.save()
        else:
            return Response(sales_invoice_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Prepare response data
        response_data = {
            'Message': 'Location, Vendor, and Sales Invoice created',
            'location_data': off_serializer.data if off_serializer else {},  # Only include location data if created
            'vendor_data': vendor_serializer.data if not vendor_exists else {},  # Only include vendor data if created
            'sales_invoice_data': sales_invoice_serializer.data,
            'product_summaries': [{'id': summary.id, 'product_name': summary.product_name()} for summary in product_summaries]
        }

        return Response(response_data, status=status.HTTP_201_CREATED)



# important view dont delete
# @api_view(['POST'])
# def create_sales_post(request, pk):
#     if request.method == 'POST':
#         print('This is post:', request.data)  # Print the entire request data for debugging
#         form_data = request.data.get('formData', {})
#         vendorData = request.data.get('vendorData', {})

#         # Extract fields for existence check
#         off_loc_id = form_data.get('offLocID')
#         location = form_data.get('location')
#         branch_id = form_data.get('branchID')

#         print('Branch ID:', branch_id)
#         vendor_id = vendorData.get('vendorID')
#         print('vendor ID:', vendor_id)
#         print('pkk ID:', pk)

#         # Flags to track existence
#         location_exists = False
#         vendor_exists = False

#         # Check for existing location
#         if off_loc_id:
#             existing_location = OfficeLocation.objects.filter(id=off_loc_id, location=location).first()
#             if existing_location:
#                 location_exists = True
#                 print('Location already exists:', existing_location)

#         # Check for existing vendor
#         if vendor_id:
#             existing_vendor = Customer.objects.filter(id=vendor_id, client=pk).first()
#             if existing_vendor:
#                 vendor_exists = True
#                 print('Vendor already exists:', existing_vendor)

#         # Retrieve related instances for saving new records
#         branch_instance = Branch.objects.get(id=branch_id) if branch_id else None
#         client_instance = Client.objects.get(id=pk) if pk else None

#         # If vendor does not exist, create it
#         if not vendor_exists:
#             vendor_serializer = CustomerVendorSerializer(data=vendorData)
#             if vendor_serializer.is_valid():
#                 vendor = vendor_serializer.save(client=client_instance)  # Assuming `client` is the foreign key
#                 print('New vendor created:', vendor_serializer.data)
#             else:
#                 return Response(vendor_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#         # If location does not exist, create it
#         if not location_exists:
#             off_serializer = OfficeLocationSerializer(data=form_data)
#             if off_serializer.is_valid():
#                 off_serializer.save(branch=branch_instance)  # Pass the Branch instance
#                 print('New location created:', off_serializer.data)
#                 return Response({
#                     'Message': 'Location and/or Vendor created',
#                     'location_data': off_serializer.data,
#                     'vendor_data': vendor_serializer.data if not vendor_exists else {}
#                 }, status=status.HTTP_201_CREATED)
#             else:
#                 return Response(off_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#         # If both location and vendor already exist
#         return Response({'Message': 'Location and Vendor already exist'}, status=status.HTTP_200_OK)







    # if request.method == 'POST':
    #     serializer = SalesInvoiceSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=201)
    #     return Response(serializer.errors, status=400)


# ***********************************************Detail page API's*********************************************
@api_view(['GET'])
def detail_client(request,pk):
    client = Client.objects.get(id=pk)
    view_bank = Bank.objects.filter(client=client)
    view_owner = Owner.objects.filter(client=client)
    view_clientuser = CustomUser.objects.filter(client=client)
    view_companydoc = FileInfo.objects.filter(client=client)
    view_branch = Branch.objects.filter(client=client)
    view_customer = Customer.objects.filter(client=client)
    view_income = IncomeTaxDocument.objects.filter(client=client)
    view_pf = PF.objects.filter(client=client)
    view_taxaudit = TaxAudit.objects.filter(client=client)
    view_air = AIR.objects.filter(client=client)
    view_sft = SFT.objects.filter(client=client)
    view_tdspayment = TDSPayment.objects.filter(client=client)
    view_tds = TDSReturn.objects.filter(client=client)
    # view_attachment = Attachment.objects.filter(client=client)
    # view_branchdoc = BranchDocument.objects.filter()

    client_serializer = ClientSerializer(client)
    bank_serializer = BankSerializer(view_bank, many=True)
    owner_serializer = OwnerSerializer(view_owner, many=True)
    clientuser = UserSerializerWithToken(view_clientuser, many=True)
    companydoc = FileInfoSerializer(view_companydoc, many=True)
    branch_serializer = BranchSerailizer(view_branch, many=True)
    customer_serializer = CustomerVendorSerializer(view_customer, many=True)
    income_serializer = IncomeTaxDocumentSerializer(view_income, many=True)
    pf_serializer = PfSerializer(view_pf, many=True)
    taxaudit_serializer = TaxAuditSerializer(view_taxaudit, many=True)
    air_serializer = AIRSerializer(view_air, many=True)
    sft_serializer = SFTSerializer(view_sft, many=True)
    tdspayment_serializer = TDSPaymentSerializer(view_tdspayment, many=True)
    tds_serializer = TDSReturnSerializer(view_tds, many=True)
    # attachment_serializer = AttachmentSerializer(view_attachment, many=True)

    data ={
        'Client' : client_serializer.data,
        'Bank' : bank_serializer.data,
        'Owner' : owner_serializer.data,
        'ClientUser' : clientuser.data,
        'Company_Document' : companydoc.data,
        'Branch' : branch_serializer.data,
        'Customer_or_Vendor' : customer_serializer.data,
        'Income_Tax_Document' : income_serializer.data,
        'PF' : pf_serializer.data,
        'Tax_Audit' : taxaudit_serializer.data,
        'AIR' : air_serializer.data,
        'SFT' : sft_serializer.data,
        'TDS_Payment' : tdspayment_serializer.data,
        'TDS_Return' : tds_serializer.data,
        # 'Attachment' : attachment_serializer.data
    }
    return Response(data)

@api_view(['GET'])
def detail_branch(request, pk, branch_pk):
    client = Client.objects.get(id = pk)
    branch = Branch.objects.get(id = branch_pk, client=client)
    officeloaction = OfficeLocation.objects.filter(branch = branch)
    view_branchdoc = BranchDocument.objects.filter(branch=branch)

    branch_serializer = BranchSerailizer(branch)
    officeloaction_serializer = OfficeLocationSerializer(officeloaction, many=True)
    branchdoc_serializer = BranchDocSerailizer(view_branchdoc, many=True)

    data = {
        'Client_Name' :client.client_name, # to only retrive client name
        'Branch' : branch_serializer.data,
        'Branch_Document' : branchdoc_serializer.data,
        'Office_Location' : officeloaction_serializer.data,
    }
    return Response(data)


@api_view(['POST'])
def import_hsn_excel(request):
    if request.method == 'POST':
        # Check if an Excel file is provided
        if 'file' not in request.FILES:
            return Response({'Error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        # Get the uploaded Excel file
        excel_file = request.FILES['file']

        try:
            # Read the Excel file using pandas
            df = pd.read_excel(excel_file)

            # List to hold successful imports and errors
            successful_imports = []
            errors = []

            # Ensure there are at least two columns
            if df.shape[1] < 2:
                return Response({'Error': 'The Excel file must contain at least two columns'}, status=status.HTTP_400_BAD_REQUEST)

            # Iterate through each row and create a new record
            for index, row in df.iterrows():
                data = {}

                # Assign the first column to hsn_code and the second to gst_rate
                try:
                    data['hsn_code'] = int(row[0])  # Convert to int
                    data['gst_rate'] = float(row[1])  # Convert to float
                except ValueError as ve:
                    errors.append({'row': index + 1, 'error': str(ve)})
                    continue  # Skip this row if there's a conversion error

                # Use the serializer to validate and save data
                serializer = HSNSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()
                    successful_imports.append(data)
                else:
                    errors.append({'row': index + 1, 'errors': serializer.errors})

            # Prepare response
            response_message = {'Message': 'HSN records imported successfully', 'Imported': successful_imports}
            if errors:
                response_message['Errors'] = errors

            return Response(response_message, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'Error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST','GET'])
def create_hsn(request):
    if request.method == 'POST':
        serializer = HSNSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response ({'Message':'TDS Payment created', 'Data': serializer.data})
        return Response({'Error':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
def edit_hsn(request, pk):
    hsn = HSNCode.objects.get(id=pk)
    serializer = HSNSerializer(instance=hsn, data=request.data)
    if request.method == 'GET':
        hsn_serializer = HSNSerializer(hsn)
        # print(tds_serializer.data)
        return Response (hsn_serializer.data)
    elif request.method == 'POST':
        if serializer.is_valid():
            serializer.save()
            return Response ({'Message':'hsn Code Updated'})
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def list_hsn(request):
    if request.method == 'GET':
        hsn_code = HSNCode.objects.all()
        serializer = HSNSerializer(hsn_code, many=True)
        return Response(serializer.data)



@api_view(['DELETE'])
def delete_hsn(request, pk):
    hsn = HSNCode.objects.get(id = pk)
    if request.method == 'DELETE':
        hsn.delete()
        return Response({'Messgae':'HSN Return Delete'})
    return Response({'Message':'Fail to delete HSN Return'} ,status=status.HTTP_400_BAD_REQUEST)




@api_view(['POST','GET'])
def create_product(request):
    if request.method=="GET":
        hsn_list = HSNCode.objects.all()
        serializer =HSNSerializer(hsn_list,many=True)
        return Response(serializer.data)
    if request.method == 'POST':
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response ({'Message':'Product Payment created', 'Data': serializer.data})
        return Response({'Error':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)




@api_view(['GET', 'POST'])
def edit_product(request, pk):
    product = Product.objects.get(id=pk)
    serializer = ProductSerializer(instance=product, data=request.data)
    if request.method == 'GET':
        product_serializer = ProductSerializer(product)
        # print(tds_serializer.data)
        return Response (product_serializer.data)
    elif request.method == 'POST':
        if serializer.is_valid():
            serializer.save()
            return Response ({'Message':'Product Updated'})
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def list_product(request):
    if request.method == 'GET':
        product = Product.objects.all()
        serializer = ProductSerializer(product, many=True)
        print(serializer.data,'lklklkk')
        return Response(serializer.data)



@api_view(['DELETE'])
def delete_product(request, pk):
    product = Product.objects.get(id = pk)
    if request.method == 'DELETE':
        product.delete()
        return Response({'Messgae':'Product Return Delete'})
    return Response({'Message':'Fail to delete HSN Return'} ,status=status.HTTP_400_BAD_REQUEST)




@api_view(['POST','GET'])
def create_product_description(request):
    if request.method=="GET":
        product = Product.objects.all()
        serializer =ProductSerializer(product,many=True)
        return Response(serializer.data)
    if request.method == 'POST':
        serializer = ProductDescriptionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response ({'Message':'Product Description created', 'Data': serializer.data})
        return Response({'Error':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def list_product_description(request):
    if request.method == 'GET':
        product_description = ProductDescription.objects.all()
        serializer = ProductDescriptionSerializer(product_description, many=True)
        print(serializer.data,'lklklkk')
        return Response(serializer.data)

@api_view(['GET', 'POST'])
def edit_product_description(request, pk):
    product_description = ProductDescription.objects.get(id=pk)
    serializer = ProductDescriptionSerializer(instance=product_description, data=request.data)
    if request.method == 'GET':
        product_serializer = ProductDescriptionSerializer(product_description)
        # print(tds_serializer.data)
        return Response (product_serializer.data)
    elif request.method == 'POST':
        if serializer.is_valid():
            serializer.save()
            return Response ({'Message':'Product Description Updated'})
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_product_description(request, pk):
    product_description = ProductDescription.objects.get(id = pk)
    if request.method == 'DELETE':
        product_description.delete()
        return Response({'Messgae':'Product Description Return Delete'})
    return Response({'Message':'Fail to delete Product Description Return'} ,status=status.HTTP_400_BAD_REQUEST)





@api_view(['GET'])
def sales_invoice_list(request):
    """
    View to list all sales invoices with their related product summaries.
    """
    # Fetch all sales invoices with related data (optimized query with prefetch_related)
    sales_invoices = SalesInvoice.objects.prefetch_related(
        'product_summaries', 'product_summaries__product', 'product_summaries__hsn',
        'product_summaries__prod_description', 'customer', 'client_location'
    ).all()

    # Serialize the data
    serializer = SalesSerializer(sales_invoices, many=True)

    # Return the serialized data
    return Response(serializer.data, status=status.HTTP_200_OK)
