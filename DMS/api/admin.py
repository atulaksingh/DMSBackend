from django.contrib import admin
from api.models import *

# Register your models here.
admin.site.register(Client)

class FileInline(admin.StackedInline):
    model = File
    extra = 1

class AttachmentAdmin(admin.ModelAdmin):
    inlines = [FileInline]
    list_display = ('file_name', 'status', 'client')
    search_fields = ('file_name', 'client_name')

admin.site.register(Attachment, AttachmentAdmin)
admin.site.register(File)
admin.site.register(CompanyDocument)
admin.site.register(CustomUser)
admin.site.register(Branch)
admin.site.register(OfficeLocation)
admin.site.register(Customer)
# admin.site.register(HSNCode)
# admin.site.register(SalesInvoice)
# admin.site.register(PurchaseInvoice)
# admin.site.register(BranchDocument)

