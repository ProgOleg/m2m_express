from .forms import UserCreationForm, UserChangeForm
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
from m2m_app.models import *


class PhysicalInline(admin.StackedInline):
    model = UsersProfilePhysicalEntrepreneur


class UsersProfileJuridicalInline(admin.StackedInline):
    model = UsersProfileJuridical


class UsersProfileIndividualEntrepreneurInline(admin.StackedInline):
    model = UsersProfileIndividualEntrepreneur


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('email', 'tel', 'name', 'is_admin', 'mailing_status')
    list_filter = ('is_admin', 'mailing_status')
    inlines = [PhysicalInline, UsersProfileJuridicalInline, UsersProfileIndividualEntrepreneurInline]
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('name', 'tel', 'mailing_status')}),
        (_('Permissions'), {'fields': ('is_admin',)}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('name', 'email', 'tel', 'password1', 'password2')}
        ),
    )
    search_fields = ('email', 'tel')
    ordering = ('-id',)
    filter_horizontal = ()


class OrderAdmin(admin.ModelAdmin):
    models = Order

    list_display = ['id', 'user_func', 'count', 'address_sdek', 'sdek_id', 'is_closed', 'is_finished',
                    'payment_type', 'date_created', 'custom_delivery_message', 'delivery_cost', 'tracking_number']
    list_editable = ['payment_type', 'tracking_number', 'address_sdek', 'is_finished']

    def user_func(self, obj):
        return mark_safe(f'<a href="/admin/m2m_app/customusers/{obj.user.id}/change/">{obj.user.__str__()}.'
                         f' Тип: {CustomUsers.user_role(obj.user)}</a>')
    user_func.short_description = "Пользователь"




admin.site.register(Order, OrderAdmin)
admin.site.register(CustomUsers, UserAdmin)
admin.site.unregister(Group)
admin.site.register(Tariff)
admin.site.register(Comment)
admin.site.register(TechSupport)
# admin.site.register(CustomUsers, CustomUserAdmin)

