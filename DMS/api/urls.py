from django.contrib import admin
from django.urls import path, include
from api.views import *
from api import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
# from .views import UpdateSalesInvoiceAPIView


urlpatterns = [
    path('create-client', create_client, name='clients-create'),
    path('edit-client/<int:pk>',view=edit_client, name='edit-client'),
    path('delete-client/<int:pk>',view=delete_client, name='delete-client'),
    path('list-client',view=list_client, name='list-client'),
    path('detail-client/<int:pk>', view=detail_client, name='detail-client'),
    path('single-fileinfo/<int:pk>/<int:fileinfo_pk>', view=single_fileinfo, name='single-fileinfo'),
    path('delete-fileinfo/<int:pk>/<int:fileinfo_pk>', view=delete_fileinfo, name='delete-fileinfo'),

    path('create-bank/<int:pk>',view=create_bank, name='create-bank'),
    path('edit-bank/<int:pk>/<int:bank_pk>',view=edit_bank, name='edit-bank'),
    path('list-bank/<int:pk>',view=list_bank, name='list-bank'),
    path('single-bank/<int:pk>/<int:bank_pk>',view=single_bank, name='single-bank'),
    path('delete-bank/<int:pk>/<int:bank_pk>', view=delete_bank, name='delete-bank'),

    path('create-owner/<int:pk>',view=create_owner, name='create-owner'),
    path('edit-owner/<int:pk>/<int:owner_pk>',view=edit_owner, name='edit-owner'),
    path('list-owner/<int:pk>',view=list_owner, name='list-owner'),
    path('single-owner/<int:pk>/<int:owner_pk>',view=single_owner, name='single-owner'),
    path('delete-owner/<int:pk>/<int:owner_pk>',view=delete_owner, name='delete-owner'),

    path('user-login', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('users', view=getUsers, name='users'),
    path('user-profile', view=getUserProfile, name='user-profile'),
    path('user-dashboardform', view=dashboarduser, name='dashboard-user'),
    path('user-clientform/<int:pk>', view=clientuser, name='client'),
    path('activate/<uidb64>/<token>',ActivateAccountView.as_view(),name='activate'),
    path('edit-clientuser/<int:pk>/<int:user_pk>', view=edit_clientuser, name='edit-clientuser'),
    path('edit-dashboarduser/<int:user_pk>', view=edit_dashboardUser, name='edit-dashboarduser'),
    path('delete-clientuser/<int:pk>/<int:user_pk>', view=delete_clientuser, name='delete-clientuser'),
    path('delete-dashboarduser/<int:user_pk>', view=delete_dashboarduser, name='delete-dashboarduser'),

    path('create-companydoc/<int:pk>', view=create_companydoc, name='create-companydoc'),
    path('edit-companydoc/<int:pk>/<int:companydoc_pk>', view=edit_companydoc, name='edit-companydoc'),
    path('list-companydoc/<int:pk>', view=list_companydoc, name='list-companydoc'),
    path('delete-companydoc/<int:pk>/<int:companydoc_pk>', view=delete_companydoc, name='delete-companydoc'),

    path('create-branch/<int:pk>', view=create_branch, name='create-branch'),
    path('edit-branch/<int:pk>/<int:branch_pk>',view=edit_branch, name='edit-branch'),
    path('list-branch/<int:pk>',view=list_branch, name='list-branch'),
    path('delete-branch/<int:pk>/<int:branch_pk>', view=delete_branch, name='delete-branch'),
    path('detail-branch/<int:pk>/<int:branch_pk>', view=detail_branch, name='detail-branch'),

    path('create-officelocation/<int:branch_pk>', view=create_officelocation, name='create-officelocation'),
    path('edit-officelocation/<int:branch_pk>/<int:office_pk>',view=edit_officelocation, name='edit-officelocation'),
    path('list-officelocation/<int:pk>/<int:branch_pk>',view=list_officelocation, name='list-officelocation'),
    path('delete-officelocation/<int:pk>/<int:branch_pk>/<int:office_pk>', view=delete_officelocation, name='delete-officelocation'),

    path('create-customer/<int:pk>', view=create_customer, name='create-customer'),
    path('edit-customer/<int:pk>/<int:customer_pk>',view=edit_customer, name='edit-customer'),
    path('list-customer/<int:pk>',view=list_customer, name='list-customer'),
    path('delete-customer/<int:pk>/<int:customer_pk>', view=delete_customer, name='delete-cutomer'),

    path('create-branchdoc/<int:branch_pk>', view=create_branchdoc, name='create-branchdoc'),
    path('edit-branchdoc/<int:branch_pk>/<int:branchdoc_pk>', view=edit_branchdoc, name='edit-branchdoc'),
    path('list-branchdoc/<int:branch_pk>', view=list_branchdoc, name='list-branchdoc'),
    path('single-branchdoc/<int:branch_pk>/<int:branchdoc_pk>', view=single_branchdoc, name='single-branchdoc'),
    path('delete-branchdoc/<int:branch_pk>/<int:branchdoc_pk>', view=delete_branchdoc, name='delete-branchdoc'),

    path('create-incometaxdoc/<int:pk>', view=create_incometaxdoc, name='create-incometaxdoc'),
    path('edit-incometaxdoc/<int:pk>/<int:income_pk>', view=edit_incometaxdoc, name='edit-incometaxdoc'),
    path('list-incometaxdoc/<int:pk>', view=list_incometaxdoc, name='list-incometaxdoc'),
    path('delete-incometaxdoc/<int:pk>/<int:income_pk>', view=delete_incometaxdoc, name='delete-incometaxdoc'),

    path('create-pf/<int:pk>', view=create_pf, name='create-pf'),
    path('create-file/<int:pk>', ExcelImportView.as_view(), name='create-pf'),
    path('edit-pf/<int:pk>/<int:pf_pk>', view=edit_pf, name='edit-pf'),
    path('list-pf/<int:pk>', view=list_pf, name='list-pf'),
    path('delete-pf/<int:pk>/<int:pf_pk>', view=delete_pf, name='delete-pf'),

    path('create-taxaudit/<int:pk>', view=create_taxaudit, name='create-taxaudit'),
    path('edit-taxaudit/<int:pk>/<int:taxaudit_pk>', view=edit_taxaudit, name='edit-taxaudit'),
    path('list-taxaudit/<int:pk>', view=list_taxaudit, name='list-taxaudit'),
    path('single-taxaudit/<int:pk>/<int:taxaudit_pk>', view=single_taxaudit, name='single-taxaudit'),
    path('delete-taxaudit/<int:pk>/<int:taxaudit_pk>', view=delete_taxaudit, name='delete-taxaudit'),

    path('create-air/<int:pk>', view=create_air, name='create-air'),
    path('edit-air/<int:pk>/<int:air_pk>', view=edit_air, name='edit-air'),
    path('list-air/<int:pk>', view=list_air, name='list-air'),
    path('single-air/<int:pk>/<int:air_pk>', view=single_air, name='single-air'),
    path('delete-air/<int:pk>/<int:air_pk>', view=delete_air, name='delete-air'),

    path('create-sft/<int:pk>', view=create_sft, name='create-sft'),
    path('edit-sft/<int:pk>/<int:sft_pk>', view=edit_sft, name='edit-sft'),
    path('list-sft/<int:pk>', view=list_sft, name='list-sft'),
    path('single-sft/<int:pk>/<int:sft_pk>', view=single_sft, name='single-sft'),
    path('delete-sft/<int:pk>/<int:sft_pk>', view=delete_sft, name='delete-sft'),

    path('create-tdspayment/<int:pk>', view=create_tdspayment, name='create-tdspayment'),
    path('edit-tdspayment/<int:pk>/<int:tdspayment_pk>',view=edit_tdspayment, name='edit-tdspayment'),
    path('list-tdspayment/<int:pk>',view=list_tdspayment, name='list-tdspayment'),
    path('single-tdspayment/<int:pk>/<int:tdspayment_pk>', view=single_tdspayment, name='single-tdspayment'),
    path('delete-tdspayment/<int:pk>/<int:tdspayment_pk>', view=delete_tdspayment, name='delete-tdspayment'),

    path('create-tds/<int:pk>', view=create_tds, name='create-tdsreturn'),
    path('edit-tds/<int:pk>/<int:tds_pk>', view=edit_tds, name='edit-tdsreturn'),
    path('list-tds/<int:pk>', view=list_tds, name='list-tdsreturn'),
    path('single-tds/<int:pk>/<int:tds_pk>', view=single_tds, name='single-tdsreturn'),
    path('delete-tds/<int:pk>/<int:tds_pk>', view=delete_tds, name='delete-tdsreturn'),

    path('get-sales/<int:pk>/', view=create_sales_get, name='get-sales'),  # Note the trailing slash
    path('create-sales/<int:pk>', view=create_sale, name='create-sales'),  # Note the trailing slash
    path('create-sales-post/<int:client_pk>/<int:invoice_pk>', view=update_sales_invoice, name='create-sales-post'),
    path('get-sales-invoice/<int:client_pk>/<int:invoice_pk>', view=update_sales_invoice, name='get-sales-invoice'),
    path('create-sales-post2/<int:client_pk>', view=create_sales_invoice2, name='create-sales-post2'),
    path('sales-view/<int:client_pk>/<int:invoice_pk>', view=sales_invoice_detail_view, name='sales-view'),

    # hsn master

    path('create-hsn', view=create_hsn, name='create-hsn'),
    path('create-hsn-excel', view=import_hsn_excel, name='create-hsn-excel'),
    path('edit-hsn/<int:pk>', view=edit_hsn, name='edit-hsn'),

    path('list-hsn', view=list_hsn, name='list-hsn'),
    path('delete-hsn/<int:pk>', view=delete_hsn, name='delete-hsn'),
    # product
    path('create-product', view=create_product, name='create-product'),
    path('edit-product/<int:pk>', view=edit_product, name='edit-product'),

    path('list-product', view=list_product, name='list-product'),
    path('delete-product/<int:pk>', view=delete_product, name='delete-product'),


# Product Description
    path('create-product-description', view=create_product_description, name='create-product-description'),
    path('list-product-description', view=list_product_description, name='list-product-description'),
    path('edit-product-description/<int:pk>', view=edit_product_description, name='edit-product-description'),
    path('delete-product-description/<int:pk>', view=delete_product_description, name='delete-product-description'),


]
