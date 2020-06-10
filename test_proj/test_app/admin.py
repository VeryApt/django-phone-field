from django.contrib import admin
from .models import TestModel, Business, Employee


admin.site.register(TestModel)


class EmployeeInline(admin.TabularInline):
    model = Employee


class BusinessAdmin(admin.ModelAdmin):
    inlines = (EmployeeInline,)


admin.site.register(Business, BusinessAdmin)
