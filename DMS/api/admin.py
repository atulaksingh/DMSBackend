from django.contrib import admin
from api.models import *

# Register your models here.

# class FileInline(admin.StackedInline):
#     model = File
#     extra = 1

# class FileAdmin(admin.ModelAdmin):
#     inlines = [FileInline]
#     # list_display = ('file_name', 'status', 'client')
#     # search_fields = ('file_name', 'client_name')

# admin.site.register(Client)
# admin.site.register(Attachment, AttachmentAdmin)
# admin.site.register(File)
admin.site.register(CompanyDocument)
admin.site.register(CustomUser)
admin.site.register(Branch)
admin.site.register(OfficeLocation)
admin.site.register(Customer)
admin.site.register(Owner)
admin.site.register(TaxAudit)
admin.site.register(SFT)
admin.site.register(AIR)
admin.site.register(TDSPayment)
admin.site.register(TDSReturn)
# admin.site.register(SalesInvoice)
admin.site.register(Product)
admin.site.register(ProductDescription)
admin.site.register(HSNCode)
# admin.site.register(ProductSummary)
# @admin.register(ProductSummary)
# class ProductSummaryAdmin(admin.ModelAdmin):
#     list_display = ['id', 'hsn_code', 'gst_rate', 'product_name', 'description_text', 'unit', 'rate']
#     readonly_fields = ['hsn_code', 'gst_rate', 'product_name', 'description_text', 'unit', 'rate']

# admin.site.register(HSNCode)
# admin.site.register(SalesInvoice)
# admin.site.register(PurchaseInvoice)
# admin.site.register(BranchDocument)

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



# class ProductSummaryInline(admin.TabularInline):
#     model = SalesInvoice.product_summaries.through  # Use the through model for many-to-many
#     extra = 0  # Remove empty extra rows

#     def get_queryset(self, request):
#         # Limit the queryset to only show related ProductSummary objects
#         qs = super().get_queryset(request)
#         return qs

#     # Optionally, if you want to display specific fields from ProductSummary
#     readonly_fields = ('hsn', 'product', 'prod_description')
#     fields = ('hsn', 'product', 'prod_description')



# class SalesInvoiceAdmin(admin.ModelAdmin):
#     inlines = [ProductSummaryInline]  # Include the inline for related ProductSummaries

#     # Customize list_display, search_fields, etc., if needed
#     list_display = ('invoice_no', 'invoice_date', 'total_invoice_value')

# admin.site.register(SalesInvoice, SalesInvoiceAdmin)
class ProductSummaryInline(admin.TabularInline):
    model = SalesInvoice.product_summaries.through  # Access the through model
    extra = 0
    readonly_fields = ['prod_description_display']

    # Custom method to display the product description
    def prod_description_display(self, instance):
        return instance.productsummary.prod_description.description if instance.productsummary.prod_description else "No Description"

    prod_description_display.short_description = "Product Description"  # Label for admin display

@admin.register(SalesInvoice)
class SalesInvoiceAdmin(admin.ModelAdmin):
    list_display = ['id', 'client_Location', 'customer', 'invoice_no', 'invoice_date']
    inlines = [ProductSummaryInline]  # Inline to show associated ProductSummary entries

@admin.register(ProductSummary)
class ProductSummaryAdmin(admin.ModelAdmin):
    list_display = ['id', 'hsn_code', 'gst_rate', 'product_name', 'description_text', 'unit', 'rate']
    readonly_fields = ['hsn_code', 'gst_rate', 'product_name', 'description_text', 'unit', 'rate']
