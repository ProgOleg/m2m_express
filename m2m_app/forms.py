from django import forms
from django.forms.utils import ErrorList, format_html
from django.urls import reverse, reverse_lazy
from m2m_app.models import (CustomUsers, UsersProfilePhysicalEntrepreneur, UsersProfileIndividualEntrepreneur,
                            UsersProfileJuridical, Order)

from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = CustomUsers
        fields = ('name', 'email', 'tel', 'mailing_status')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def clean_mailing_status(self):
        if self.cleaned_data.get("mailing_status") == 'on' or ['on']:
            return True

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = forms.CharField(label=_('Password'), )

    class Meta:
        model = CustomUsers
        fields = ('name', 'password', 'email', 'tel', 'mailing_status', 'is_active', 'is_admin')

    def clean_password(self):
        return self.initial["password"]


class PErrorsList(ErrorList):

    def __str__(self):
        return self.errors_as_p()

    def errors_as_p(self):
        if not self:
            return ''
        return format_html(''.join([f'<p style="color: red">{e}</p>' for e in self]))


class UserCreationFormSiteVersion(UserCreationForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={
        "type": "password", "class": "input-form", "name": "password1", "placeholder": "Пароль*"
    }))
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput(attrs={
        "type": "password", "class": "input-form", "name": "password2", "placeholder": "Повторите пароль*"}))

    class Meta:
        model = CustomUsers
        fields = ['name', 'tel', 'email', 'password1', 'password2', 'mailing_status']
        widgets = {
            'name': forms.TextInput(attrs={
                "type": "text", "class": "input-form", "name": "name", "placeholder": "Ваше имя*"}),
            'tel': forms.TextInput(attrs={
                "type": "tel", "class": "input-form", "name": "tel", "placeholder": "+7 (000) 000-00-00*"}),
            'email': forms.TextInput(attrs={
                "type": "email", "class": "input-form", "name": "email", "placeholder": "Ваша почта*"}),
            'mailing_status': forms.CheckboxInput(attrs={
                "name": "personaldata", "checked": ""
            })
        }


class UsersProfilePhysicalEntrepreneurForm(forms.ModelForm):
    class Meta:
        model = UsersProfilePhysicalEntrepreneur
        fields = ['full_name', 'tel', 'email', 'scan_copy_img', 'scan_copy_pdf']
        widgets = {
            'full_name': forms.TextInput(attrs={
                "type": "text", "class": "input-form", "name": "full_name", "placeholder": "ФИО*"}),
            'tel': forms.TextInput(attrs={
                "type": "tel", "class": "input-form", "name": "tel", "placeholder": "+7 (000) 000-00-00*",
                'required': ''
            }),
            'email': forms.EmailInput(attrs={
                "type": "email", "class": "input-form", "name": "email", "placeholder": "E-mail*",
                'required': ''})
        }


class FormsCustomFieldsWidgets(forms.ModelForm):
    class Meta:
        model = None
        fields = None
        custom_widget_input_type_text = {"type": "text", "class": "input-form", "required": ""}
        custom_widget_input_type_number = {"type": "number", "class": "input-form", "required": ""}
        widgets = {
            'inn': forms.TextInput(attrs={
                "name": "inn", "placeholder": "ИНН организации*", "id": "entrepr_inn",
                'data-ajax-url': reverse_lazy('indi_entrepr_inn_url'), **custom_widget_input_type_text}),
            'name_company': forms.TextInput(attrs={
                "name": "name_company", "placeholder": "Название компании", **custom_widget_input_type_text}),
            'ogrn': forms.TextInput(attrs={
                "name": "ogrn", "placeholder": "ОГРН", **custom_widget_input_type_text}),
            'kpp': forms.TextInput(attrs={
                "name": "kpp", "placeholder": "КПП", **custom_widget_input_type_text}),
            'address': forms.TextInput(attrs={
                "name": "address", "placeholder": "Адресс", **custom_widget_input_type_text}),
        }


class UsersProfileIndividualEntrepreneurForm(forms.ModelForm):

    class Meta(FormsCustomFieldsWidgets.Meta):
        model = UsersProfileIndividualEntrepreneur
        fields = ['inn', 'name_company', 'ogrn', 'kpp', 'address', 'user']
        widgets = FormsCustomFieldsWidgets.Meta.widgets


class UsersProfileJuridicalForm(forms.ModelForm):
    class Meta(FormsCustomFieldsWidgets.Meta):
        model = UsersProfileJuridical
        fields = ['inn', 'name_company', 'ogrn', 'kpp', 'address', 'user']
        # juridical_entrepreneur
        widgets = FormsCustomFieldsWidgets.Meta.widgets
        widgets['inn'].attrs.update({"id": "juridical_entrepreneur"})


class DeliveryForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['count', 'user', 'tariff', 'address_sdek', 'sdek_id',
                  'is_closed', 'custom_delivery_message', 'delivery_type']


class DeliveryCustomType(forms.Form):
    custom_delivery_message = forms.CharField(max_length=2056, required=True)


class DeliveryStandardType(forms.Form):
    address_sdek = forms.CharField(max_length=1024, required=True)
    sdek_id = forms.CharField(max_length=255, required=True)
    delivery_cost = forms.IntegerField(required=True)

    def clean_delivery_cost(self):
        data = self.cleaned_data['delivery_cost']
        if data < 0:
            raise ValidationError
        return data












