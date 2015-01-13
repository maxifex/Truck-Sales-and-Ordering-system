from django.contrib import admin
# from testApp.models import Apps, Admin
# Register your models here.

# admin.site.register(Apps)
# admin.site.register(Admin)

from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from orderSystem.models import Employee, Client, Country, DeliveryTime, SpecialDiscount, Discount, Currency, DutyType, TruckAge, PaymentTerm, Depreciation, CustomConfiguration, CustomsRate


# Define an inline admin descriptor for Employee model
# which acts a bit like a singleton
class EmployeeInline(admin.StackedInline):
    model = Employee
    can_delete = False
    verbose_name_plural = 'employee'

# Define a new User admin
class UserAdmin(UserAdmin):
    inlines = (EmployeeInline,)

class ClientAdmin(admin.ModelAdmin):
    list_display = ('company_name','contact_person')

class CountryAdmin(admin.ModelAdmin):
    list_display = ('name','name')

class DeliveryTimeAdmin(admin.ModelAdmin):
    list_display = ('name','name')

class DiscountAdmin(admin.ModelAdmin):
    list_display = ('name','percent')

class DepreciationAdmin(admin.ModelAdmin):
    list_display = ('year','percent')

class SpecialDiscountAdmin(admin.ModelAdmin):
    list_display = ('percent','percent')

class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('name','code')

class DutyTypeAdmin(admin.ModelAdmin):
    list_display = ('name','name')

class TruckAgeAdmin(admin.ModelAdmin):
    list_display = ('year','year')

class PaymentTermAdmin(admin.ModelAdmin):
    list_display = ('duration','description')

class CustomConfigurationAdmin(admin.ModelAdmin):
    list_display = ('configuration', 'value')

class CustomsRateAdmin(admin.ModelAdmin):
    list_display = ('name', 'percent')

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(Country, CountryAdmin)

admin.site.register(DeliveryTime, DeliveryTimeAdmin)
admin.site.register(SpecialDiscount, SpecialDiscountAdmin)
admin.site.register(Discount, DiscountAdmin)
admin.site.register(Depreciation, DepreciationAdmin)
admin.site.register(Currency, CurrencyAdmin)
admin.site.register(DutyType, DutyTypeAdmin)
admin.site.register(TruckAge, TruckAgeAdmin)
admin.site.register(PaymentTerm, PaymentTermAdmin)
admin.site.register(CustomConfiguration, CustomConfigurationAdmin)
admin.site.register(CustomsRate, CustomsRateAdmin)
