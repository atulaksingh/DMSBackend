from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from api.models import *
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# Register your models here.

admin.site.register(CompanyDocument)

# class ClientUserAdmin(admin.ModelAdmin):
#     model = ClientUser
#     list_display = ('id', 'name', 'email', 'client', 'is_active', 'is_staff')
# admin.site.register(ClientUser, ClientUserAdmin)

# class DashboardUserAdmin(UserAdmin):
#     model = DashboardUser
#     list_display = ('id', 'first_name','last_name', 'email', 'is_active', 'is_staff')
#     search_fields = ('first_name','last_name', 'email')
#     list_editable = ('is_active', 'is_staff')
#     fieldsets = (
#         (None, {'fields': ('email', 'password')}),
#         ('Personal Info', {'fields': ('first_name','last_name')}),
#         ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
#         ('Important dates', {'fields': ('last_login', 'date_joined')}),
#     )
#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),
#             'fields': ('email', 'first_name','last_name', 'password1', 'password2'),
#         }),
#     )
#     ordering = ('id',)

# admin.site.register(DashboardUser, DashboardUserAdmin)
class CommonUserAdmin(UserAdmin):
    model = CommonUser
    list_display = ('id', 'name', 'email','role', 'is_active', 'is_staff')
    # search_fields = ('email')
    list_editable = ('is_active', 'is_staff')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        # ('Personal Info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )

    ordering = ('id',)

admin.site.register(CommonUser, CommonUserAdmin)
admin.site.register(Branch)
admin.site.register(BranchDocument)
admin.site.register(OfficeLocation)
admin.site.register(Customer)
admin.site.register(Owner)
admin.site.register(Bank)
admin.site.register(TaxAudit)
admin.site.register(SFT)
admin.site.register(AIR)
admin.site.register(Others)
admin.site.register(TDSPayment)
admin.site.register(TDSReturn)
admin.site.register(TDSSection)
admin.site.register(ExcelFile)
# admin.site.register(Acknowledgement)
admin.site.register(PF)
admin.site.register(Product) ##############
admin.site.register(ProductDescription) ###############
admin.site.register(HSNCode) ##################
class ZipUploadAdmin(admin.ModelAdmin):
    readonly_fields = ('date',)  # Makes the date field read-only in the admin

admin.site.register(ZipUpload, ZipUploadAdmin)

from django.contrib import admin
from .models import Acknowledgement, Files

class FilesInline(admin.TabularInline):  # or admin.StackedInline for a different UI
    model = Files
    extra = 1  # Number of empty forms shown to add new files
    fields = ('return_file', 'computation_file')  # Only show these fields

class AcknowledgementAdmin(admin.ModelAdmin):
    list_display = ('client', 'return_type', 'from_date', 'to_date', 'status')
    inlines = [FilesInline]

admin.site.register(Acknowledgement, AcknowledgementAdmin)

# class CustomUserAdmin(UserAdmin):
#     model = CustomUser
#     list_display = ('id', 'email','name', 'is_active', 'is_staff')
#     search_fields = ('email', 'name')
#     ordering = ('id',)

# admin.site.register(CustomUser, CustomUserAdmin)



# Inline for File model to manage file uploads
class FileInline(admin.TabularInline):
    model = File
    extra = 1  # Allows adding extra file slots directly in the admin

# Inline for managing FileInfo entries associated with a Client
class FileInfoInline(admin.StackedInline):
    model = FileInfo
    extra = 1  # Allows adding extra fileInfo slots directly in the admin
    inlines = [FileInline]  # Add FileInline here to manage files within FileInfo

# Admin for Client model
@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['client_name', 'entity_type', 'date_of_incorporation', 'contact_person', 'email', 'status']
    inlines = [FileInfoInline]  # Include FileInfoInline to manage FileInfo directly

# Register FileInfo model
@admin.register(FileInfo)
class FileInfoAdmin(admin.ModelAdmin):
    list_display = ['document_type', 'login', 'remark', 'client']
    inlines = [FileInline]  # Allows managing files for each FileInfo

# Register the File model
@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ['fileinfo', 'files']  # Displays associated FileInfo and file


class ProductSummaryInline(admin.TabularInline): ##############
    model = SalesInvoice.product_summaries.through  # Access the through model
    extra = 0
    readonly_fields = ['prod_description_display']

    def prod_description_display(self, instance):
        return instance.productsummary.prod_description.description if instance.productsummary.prod_description else "No Description"

    prod_description_display.short_description = "Product Description"

@admin.register(SalesInvoice) ################
class SalesInvoiceAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_name', 'invoice_no', 'invoice_date']

    def customer_name(self, obj):
        return obj.customer.name if obj.customer else "No Customer"
    customer_name.short_description = "Customer"  # Optional: Set a custom column header

@admin.register(ProductSummary) #####################3
class ProductSummaryAdmin(admin.ModelAdmin):
    list_display = ['id', 'hsn_code', 'gst_rate', 'product_name', 'description_text', 'unit', 'rate']
    readonly_fields = ['hsn_code', 'gst_rate', 'product_name', 'description_text', 'unit', 'rate']
    
    
    
# ############################# Purchase

class ProductPurchaseSummaryInline(admin.TabularInline): ##############
    model = PurchaseInvoice.product_summaries.through  # Access the through model
    extra = 0
    readonly_fields = ['prod_description_display']

    def prod_description_display(self, instance):
        return instance.productsummary.prod_description.description if instance.productsummary.prod_description else "No Description"

    prod_description_display.short_description = "Product Description"

@admin.register(PurchaseInvoice) ################
class PurchaseInvoiceAdmin(admin.ModelAdmin):
    list_display = ['id', 'vendor_name', 'invoice_no', 'invoice_date']

    def vendor_name(self, obj):
        return obj.vendor.name if obj.vendor else "No Vendor"
    vendor_name.short_description = "Vendor"  # Optional: Set a custom column header

@admin.register(ProductSummaryPurchase) #####################3
class ProductSummaryAdmin(admin.ModelAdmin):
    list_display = ['id', 'hsn_code', 'gst_rate', 'product_name', 'description_text', 'unit', 'rate']
    readonly_fields = ['hsn_code', 'gst_rate', 'product_name', 'description_text', 'unit', 'rate']
    

# ############################Debit Note

class DebitNotePurchaseSummaryInline(admin.TabularInline): ##############
    model = DebitNote.product_summaries.through  # Access the through model
    extra = 0
    readonly_fields = ['prod_description_display']

    def prod_description_display(self, instance):
        return instance.productsummary.prod_description.description if instance.productsummary.prod_description else "No Description"

    prod_description_display.short_description = "Product Description"

@admin.register(DebitNote) ################
class DebitNoteAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_name', 'invoice_no', 'invoice_date']

    def customer_name(self, obj):
        return obj.customer.name if obj.customer else "No Customer"
    customer_name.short_description = "Customer"  # Optional: Set a custom column header

@admin.register(ProductSummaryDebitNote) #####################3
class ProductSummaryDebitNoteAdmin(admin.ModelAdmin):
    list_display = ['id', 'hsn_code', 'gst_rate', 'product_name', 'description_text', 'unit', 'rate']
    readonly_fields = ['hsn_code', 'gst_rate', 'product_name', 'description_text', 'unit', 'rate']

    
# #########################################Credit Note

class CreditNotePurchaseSummaryInline(admin.TabularInline): ##############
    model = CreditNote.product_summaries.through  # Access the through model
    extra = 0
    readonly_fields = ['prod_description_display']

    def prod_description_display(self, instance):
        return instance.productsummary.prod_description.description if instance.productsummary.prod_description else "No Description"

    prod_description_display.short_description = "Product Description"

@admin.register(CreditNote) ################
class CreditNoteAdmin(admin.ModelAdmin):
    list_display = ['id', 'vendor_name', 'invoice_no', 'invoice_date']

    def vendor_name(self, obj):
        return obj.vendor.name if obj.vendor else "No Vendor"
    vendor_name.short_description = "Vendor"  # Optional: Set a custom column header

@admin.register(ProductSummaryCreditNote) #####################3
class ProductSummaryCreditNoteAdmin(admin.ModelAdmin):
    list_display = ['id', 'hsn_code', 'gst_rate', 'product_name', 'description_text', 'unit', 'rate']
    readonly_fields = ['hsn_code', 'gst_rate', 'product_name', 'description_text', 'unit', 'rate']

# #########################################Income

class ProductSummaryIncomeInline(admin.TabularInline): ##############
    model = Income.product_summaries.through  # Access the through model
    extra = 0
    readonly_fields = ['prod_description_display']

    def prod_description_display(self, instance):
        return instance.productsummary.prod_description.description if instance.productsummary.prod_description else "No Description"

    prod_description_display.short_description = "Product Description"

@admin.register(Income) ################
class IncomeAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_name', 'invoice_no', 'invoice_date']

    def customer_name(self, obj):
        return obj.customer.name if obj.customer else "No Customer"
    customer_name.short_description = "Customer"  # Optional: Set a custom column header

@admin.register(ProductSummaryIncome) #####################3
class ProductSummaryIncomeAdmin(admin.ModelAdmin):
    list_display = ['id', 'hsn_code', 'gst_rate', 'product_name', 'description_text', 'unit', 'rate']
    readonly_fields = ['hsn_code', 'gst_rate', 'product_name', 'description_text', 'unit', 'rate']
    
# ############################# Expenses

class ProductSummaryExpensesInline(admin.TabularInline): ##############
    model = Expenses.product_summaries.through  # Access the through model
    extra = 0
    readonly_fields = ['prod_description_display']

    def prod_description_display(self, instance):
        return instance.productsummary.prod_description.description if instance.productsummary.prod_description else "No Description"

    prod_description_display.short_description = "Product Description"

@admin.register(Expenses) ################
class ExpensesAdmin(admin.ModelAdmin):
    list_display = ['id', 'vendor_name', 'invoice_no', 'invoice_date']

    def vendor_name(self, obj):
        return obj.vendor.name if obj.vendor else "No Vendor"
    vendor_name.short_description = "Vendor"  # Optional: Set a custom column header

@admin.register(ProductSummaryExpenses) #####################3
class ProductSummaryExpensesAdmin(admin.ModelAdmin):
    list_display = ['id', 'hsn_code', 'gst_rate', 'product_name', 'description_text', 'unit', 'rate']
    readonly_fields = ['hsn_code', 'gst_rate', 'product_name', 'description_text', 'unit', 'rate']
    

# ############################Income Debit Note

class IncomeDebitNotePurchaseSummaryInline(admin.TabularInline): ##############
    model = IncomeDebitNote.product_summaries.through  # Access the through model
    extra = 0
    readonly_fields = ['prod_description_display']

    def prod_description_display(self, instance):
        return instance.productsummary.prod_description.description if instance.productsummary.prod_description else "No Description"

    prod_description_display.short_description = "Product Description"

@admin.register(IncomeDebitNote) ################
class IncomeDebitNoteAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_name', 'invoice_no', 'invoice_date']

    def customer_name(self, obj):
        return obj.customer.name if obj.customer else "No Customer"
    customer_name.short_description = "Customer"  # Optional: Set a custom column header

@admin.register(ProductSummaryIncomeDebitNote) #####################3
class ProductSummaryIncomeDebitNoteAdmin(admin.ModelAdmin):
    list_display = ['id', 'hsn_code', 'gst_rate', 'product_name', 'description_text', 'unit', 'rate']
    readonly_fields = ['hsn_code', 'gst_rate', 'product_name', 'description_text', 'unit', 'rate']
    
# #########################################Expenses Credit Note

class ExpensesCreditNotePurchaseSummaryInline(admin.TabularInline): ##############
    model = ExpensesCreditNote.product_summaries.through  # Access the through model
    extra = 0
    readonly_fields = ['prod_description_display']

    def prod_description_display(self, instance):
        return instance.productsummary.prod_description.description if instance.productsummary.prod_description else "No Description"

    prod_description_display.short_description = "Product Description"

@admin.register(ExpensesCreditNote) ################
class ExpensesCreditNoteAdmin(admin.ModelAdmin):
    list_display = ['id', 'vendor_name', 'invoice_no', 'invoice_date']

    def vendor_name(self, obj):
        return obj.vendor.name if obj.vendor else "No Vendor"
    vendor_name.short_description = "Vendor"  # Optional: Set a custom column header

@admin.register(ProductSummaryExpensesCreditNote) #####################3
class ProductSummaryExpensesCreditNoteAdmin(admin.ModelAdmin):
    list_display = ['id', 'hsn_code', 'gst_rate', 'product_name', 'description_text', 'unit', 'rate']
    readonly_fields = ['hsn_code', 'gst_rate', 'product_name', 'description_text', 'unit', 'rate']
