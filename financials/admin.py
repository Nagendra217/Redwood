from django.contrib import admin

from financials.models import *
# Register your models here.

class TrxnAdmin(admin.ModelAdmin):
    list_display = ('scrip_code', 'user', 'transaction_type','quantity','price','amount','date_created','date_updated')

admin.site.register(Transactions,TrxnAdmin)

class MasterAdmin(admin.ModelAdmin):
    list_display = ('scrip_code', 'scrip_name', 'yahoo_code')

admin.site.register(CompanyMaster,MasterAdmin)

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone_number', 'date_joined','commited_amount','total_amount','client_code','broker','broker_email','broker_phone')

admin.site.register(CustomerProfile,ProfileAdmin)
