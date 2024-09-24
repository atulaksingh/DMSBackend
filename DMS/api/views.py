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

# from django.views.decorators.csrf import csrf_exempt


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
        serializers = ClientSerializer(client, many=True)
        return Response(serializers.data)


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
            client_serializer.save()

            # Access fileinfos data for updating
            fileinfos_data = []
            index = 0
            while f'fileinfos[{index}].login' in request.POST:
                fileinfo_data = {
                    'login': request.POST.get(f'fileinfos[{index}].login'),
                    'password': request.POST.get(f'fileinfos[{index}].password'),
                    'document_type': request.POST.get(f'fileinfos[{index}].document_type'),
                    'remark': request.POST.get(f'fileinfos[{index}].remark'),
                }

                files = request.FILES.getlist(f'fileinfos[{index}].files[]')

                fileinfos_data.append({
                    'fileinfo': fileinfo_data,
                    'files': files
                })

                index += 1

            # Clear existing FileInfos and Files for the client
            FileInfo.objects.filter(client=client).delete()

            # Save new FileInfo and File instances
            for entry in fileinfos_data:
                fileinfo = FileInfo.objects.create(client=client, **entry['fileinfo'])
                for file in entry['files']:
                    File.objects.create(fileinfo=fileinfo, files=file)

            return Response(client_serializer.data, status=200)

        return Response(client_serializer.errors, status=400)


@api_view(['DELETE'])
def delete_client(request,pk):
    if request.method == 'DELETE':
        client = Client.objects.get(id=pk)
        client.delete()
        return Response ({'Message':'Company Deleted'})
    return Response ({'Message':'Fail to delete'}, status=status.HTTP_400_BAD_REQUEST)


# ***********************************************Bank View's******************************************************

@api_view(['POST'])
def create_bank(request, pk):
    client = get_object_or_404(Client, id=pk)
    if request.method == 'POST':
        # client = Client.objects.get(id=client_pk)
        bank_serializer = BankSerializer(data=request.data)
        if bank_serializer.is_valid():
            bank_serializer.save(client=client)
            return Response({'Message':'Bank Created',"data":bank_serializer.data}, status=status.HTTP_201_CREATED)
        return Response(bank_serializer.error,status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST','GET'])
def edit_bank(request,pk,bank_pk):
    client = get_object_or_404(Client, id=pk)
    bank = Bank.objects.get(id = bank_pk)
    bank_serializer = BankSerializer(data=request.data, instance=bank)
    if request.method == 'POST':
        if bank_serializer.is_valid():
            bank_serializer.save(client=client)
            return Response({'Message':'Bank Updated'})
        return Response(bank_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'GET':
        bank_ser = BankSerializer(bank)
        return Response (bank_ser.initial_data)

@api_view(['GET'])
def list_bank(request, pk):
    client = Client.objects.get(id=pk)
    if request.method == 'GET':
        bank_list = Bank.objects.filter(client=client)
        serializers = BankSerializer(bank_list,many=True)
        print(serializers)
        return Response(serializers.data)

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
    if request.method == 'POST':
        owner_serializer = OwnerSerializer(data=request.data)
        if owner_serializer.is_valid():
            # sum of a for loop values of share of all the owners created
            total_shares = sum([owner.share for owner in Owner.objects.all()])
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
        user = CustomUser.objects.create(first_name=data['fname'],last_name=data['lname'],username=data['email'],
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
    user = CustomUser.objects.get(id = user_pk)
    user_serializer = UserSerializerWithToken(data=request.data, instance=user)
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
    doc_list = CompanyDocument.objects.filter(client=client)
    serializer = CompanyDocSerailizer(doc_list,many=True)
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
        return Response({'Error':'Fail to update branch'}, status=status.HTTP_400_BAD_REQUEST)
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
        return Response ({'Error':'Fail to create Office Location'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST', 'GET'])
def edit_officelocation(request,branch_pk,office_pk):
    branch = Branch.objects.get(id=branch_pk)
    office = OfficeLocation.objects.get(id=office_pk)
    officeLocation_serializer = OfficeLocationSerializer(instance=office, data=request.data)
    if request.method == 'POST':
        if officeLocation_serializer.is_valid():
            officeLocation_serializer.save(branch=branch)
            return Response({'Message':'Office Loaction Update'})
        return Response ({'Error':'Fail to update Office Location'}, status=status.HTTP_400_BAD_REQUEST)
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
        return Response ({'Error':'Fail to create Customer or Vendor'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST', 'GET'])
def edit_customer(request, pk, customer_pk):
    client = Client.objects.get(id=pk)
    customer = Customer.objects.get(id=customer_pk)
    customer_serializer = CustomerVendorSerializer(instance=customer, data=request.data)
    if request.method == 'POST':
        if customer_serializer.is_valid():
            customer_serializer.save(client=client)
            return Response({'Message':'Customer or Vendor Updated'})
        return Response({'Error':'Fail to update Customer or Vendor'}, status=status.HTTP_400_BAD_REQUEST)
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
def create_branchdoc(request,pk,branch_pk):
    client = Client.objects.get(id=pk)
    branch = Branch.objects.get(id=branch_pk, client=client)
    if request.method == 'POST':
        branchdoc_serializer = BranchDocSerailizer(data=request.data)
        if branchdoc_serializer.is_valid():
            branchdoc_serializer.save(branch=branch)
            return Response({'Message':'Branch Document Created', 'Data' : branchdoc_serializer.data}, status=status.HTTP_201_CREATED)
        return Response(branchdoc_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST','GET'])
def edit_branchdoc(request,pk, branch_pk, branchdoc_pk):
    client = Client.objects.get(id=pk)
    branch = Branch.objects.get(id=branch_pk, client=client)
    branchdoc = BranchDocument.objects.get(id = branchdoc_pk, branch=branch)
    branchdoc_serializer = BranchDocSerailizer(instance=branchdoc, data=request.data)
    if request.method == 'POST':
        if branchdoc_serializer.is_valid():
            branchdoc_serializer.save(branch=branch)
            return Response({'Message':'Branch Document updated'})
        return Response(branchdoc_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'GET':
        branchdoc_ser = BranchDocSerailizer(branchdoc)
        return Response(branchdoc_ser.data)

@api_view(['GET'])
def list_branchdoc(request, pk, branch_pk):
    client = Client.objects.get(id=pk)
    branch = Branch.objects.get(id = branch_pk, client=client)
    # branchdoc = BranchDocument.objects.get(id = branchdoc_pk, branch=branch)
    if request.method == 'GET':
        list_branchdoc = BranchDocument.objects.filter(branch=branch)
        branchdoc_serializer = BranchDocSerailizer(list_branchdoc, many=True)
        print(branchdoc_serializer)
        return Response(branchdoc_serializer.data)

@api_view(['DELETE'])
def delete_branchdoc(request, pk ,branch_pk, branchdoc_pk ):
    client = Client.objects.get(id=pk)
    branch = Branch.objects.get(id = branch_pk, client=client)
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
        return Response({'Error':'Fail to update'}, status=status.HTTP_400_BAD_REQUEST)
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
        return Response ({'Error':'Fail to create Pf'},status=status.HTTP_400_BAD_REQUEST)

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
        return Response({'Error':'Fail to update'}, status=status.HTTP_400_BAD_REQUEST)
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

# ***********************************************Detail page API's*********************************************
@api_view(['GET'])
def detail_client(request,pk):
    client = Client.objects.get(id=pk)
    view_bank = Bank.objects.filter(client=client)
    view_owner = Owner.objects.filter(client=client)
    view_clientuser = CustomUser.objects.filter(client=client)
    view_companydoc = CompanyDocument.objects.filter(client=client)
    view_branch = Branch.objects.filter(client=client)
    view_customer = Customer.objects.filter(client=client)
    view_income = IncomeTaxDocument.objects.filter(client=client)
    view_pf = PF.objects.filter(client=client)
    # view_attachment = Attachment.objects.filter(client=client)
    # view_branchdoc = BranchDocument.objects.filter()

    client_serializer = ClientSerializer(client)
    bank_serializer = BankSerializer(view_bank, many=True)
    owner_serializer = OwnerSerializer(view_owner, many=True)
    clientuser = UserSerializerWithToken(view_clientuser, many=True)
    companydoc = CompanyDocSerailizer(view_companydoc, many=True)
    branch_serializer = BranchSerailizer(view_branch, many=True)
    customer_serializer = CustomerVendorSerializer(view_customer, many=True)
    income_serializer = IncomeTaxDocumentSerializer(view_income, many=True)
    pf_serializer = PfSerializer(view_pf, many=True)
    # attachment_serializer = AttachmentSerializer(view_attachment, many=True)

    data ={
        'Client' : client_serializer.data,
        'Bank' : bank_serializer.data,
        'Owner' : owner_serializer.data,
        'ClientUser' : clientuser.data,
        'Company Document' : companydoc.data,
        'Branch' : branch_serializer.data,
        'Customer or Vendor' : customer_serializer.data,
        'Income Tax Document' : income_serializer.data,
        'PF' : pf_serializer.data,
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
        'Client Name' :client.client_name, # to only retrive client name
        'Branch' : branch_serializer.data,
        'Office Location' : officeloaction_serializer.data,
        'Branch Document' : branchdoc_serializer.data,
    }
    return Response(data)


