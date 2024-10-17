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
