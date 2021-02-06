from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import View

from .forms import (PErrorsList, UserCreationFormSiteVersion, UsersProfilePhysicalEntrepreneurForm,
                    UsersProfileIndividualEntrepreneurForm, UsersProfileJuridicalForm, DeliveryForm,
                    DeliveryCustomType, DeliveryStandardType)
from .models import *

from .utils import *
from pycdek3 import Client
from time import time, strftime
from django.core.mail import send_mail
import string
from copy import deepcopy
from django.conf import settings


class AuthUser(LoginView):
    template_name = 'm2m_app/auth_user.html'
    form_class = AuthenticationForm
    success_url = reverse_lazy('index_url')
    redirect_field_name = ''
    redirect_authenticated_user = True


class LogOut(LogoutView):
    pass


def password_restoring_view(request):
    if request.method == 'GET':
        return render(request, 'm2m_app/password_restoring.html')
    if request.method == 'POST' and request.is_ajax():
        username = request.POST.get('username')
        if username:
            try:
                user = CustomUsers.objects.get(email=username)
            except ObjectDoesNotExist:
                return JsonResponse(safe=False, status=200, data={
                    'massage': {"error": "Пользователь с таким email не обнаружен"}})
            new_password = CustomUsers.objects.make_random_password()
            user.set_password(new_password)
            user.save()
            send_mail('Востановление пароля M2M Express',
                      f'{string.capwords(user.name)}, ваш новый пароль для входа на сайт "M2M Express" {new_password}',
                      settings.EMAIL_HOST_USER, [user.email], fail_silently=False)
            return JsonResponse(status=200, data={'massage': {'ok': 'ok'}})
    return HttpResponse(status=403)


@login_required
def index_view(request):
    if request.method == 'GET':
        val = check_user_info(request.user)
        if val:
            return redirect(reverse('select_tariff_url'))
        else:
            return redirect(reverse('user_info_url'))
    elif request.method == 'POST':
        ...


@check_user_is_no_anonimus
def registration_view(request):
    if request.method == 'GET':
        return render(request, 'm2m_app/registration.html', context={
            "form": UserCreationFormSiteVersion(auto_id=False)})

    elif request.method == 'POST':
        data = UserCreationFormSiteVersion(request.POST, auto_id=False, error_class=PErrorsList)
        if data.is_valid():
            user = data.save()
            auth.login(request, user)
            # return redirect(reverse('user_info_url'))
            context = deepcopy(UserInfoView.context)
            context.update(dict(juridical_checked=True))
            context.update(dict(after_registration=True))
            context.update({'user_name': user.name})
            return render(request, 'm2m_app/user_info.html', context)
        else:
            return render(request, 'm2m_app/registration.html', context={
                'form': data, 'data_errors': data.errors.get_json_data})
    return HttpResponse(status=404)


class UserInfoView(View, LoginRequiredMixin):
    context = {
        'physical_form': UsersProfilePhysicalEntrepreneurForm(),
        'individual_entrepreneur_form': UsersProfileIndividualEntrepreneurForm(),
        'juridical_entrepreneur_form': UsersProfileJuridicalForm(),
    }

    def get(self, request):
        context = {
            'physical_form': UsersProfilePhysicalEntrepreneurForm(),
            'individual_entrepreneur_form': UsersProfileIndividualEntrepreneurForm(),
            'juridical_entrepreneur_form': UsersProfileJuridicalForm(),
        }
        if check_user_info(request.user):
            return redirect(reverse('select_tariff_url'))
        context.update(dict(juridical_checked=True))
        return render(request, 'm2m_app/user_info.html', context)

    def post(self, request):
        context = {
            'physical_form': UsersProfilePhysicalEntrepreneurForm(),
            'individual_entrepreneur_form': UsersProfileIndividualEntrepreneurForm(),
            'juridical_entrepreneur_form': UsersProfileJuridicalForm(),
        }
        if check_user_info(request.user):
            return redirect(reverse('select_tariff_url'))
        form_name = request.POST.get('form', '')

        if form_name == 'physical':
            scan = request.FILES.get('scan_copy')
            if scan:
                scan_name = scan.name
                file_extension = scan_name.split('.')[1]
                for key, val in UsersProfilePhysicalEntrepreneur.file_extension.items():
                    if file_extension in val:
                        request.FILES[key] = request.FILES['scan_copy']
                        request.FILES.pop('scan_copy')
                        break
                data = {**request.POST.dict(), "user": request.user.pk}
                form = UsersProfilePhysicalEntrepreneurForm(data, request.FILES, error_class=PErrorsList)
                if form.is_valid():
                    form.save()
                    return redirect(reverse('select_tariff_url'))
                context.update({'physical_checked': True})
                context['physical_form'] = form
                return render(request, 'm2m_app/user_info.html', context)
            context.update({'physical_form': UsersProfilePhysicalEntrepreneurForm(request.POST)})
            context.update(dict(physical_checked=True))
            context.update(dict(file_error=True))
            return render(request, 'm2m_app/user_info.html', context=context)

        elif form_name == 'individual_entrepreneur':
            data = UsersProfileIndividualEntrepreneurForm({**request.POST.dict(), "user": request.user.pk},
                                                          error_class=PErrorsList)
            if data.is_valid():
                data.save()
                return redirect(reverse('select_tariff_url'))
            context.update({'individual_checked': True,
                                 'individual_entrepreneur_form': data})
            return render(request, 'm2m_app/user_info.html', context=context)
        elif form_name == 'juridical_entrepreneur':
            data = UsersProfileJuridicalForm({**request.POST.dict(), "user": request.user.pk}, error_class=PErrorsList)
            if data.is_valid():
                data.save()
                return redirect(reverse('select_tariff_url'))
            context.update({'juridical_checked': True,
                                 'juridical_entrepreneur_form': data})
            return render(request, 'm2m_app/user_info.html', context=context)
        return HttpResponse(status=400)


@login_required
def individual_entrepreneur_info(request):
    if request.method == 'POST' and request.is_ajax():
        query = request.POST.get('query')
        if query:
            data = EntrepreneurInfo(query)
            data = data.entrepreneur_info()
            return JsonResponse(data=data, safe=False)
    return HttpResponse(status=403)


@login_required
def select_tariff(request):
    if request.method == 'GET':
        not_closed_order = Order.objects.filter(user=request.user.pk, is_closed=False).values('tariff_id', 'count')
        tariffs = Tariff.objects.filter(is_active=True).values('name', 'locations', 'sms', 'megabyte', 'cost', 'pk')
        if not_closed_order and not_closed_order[0]['tariff_id']:
            context = {'tariffs': tariffs, 'tariff_checked': not_closed_order[0]['tariff_id'],
                       'count': not_closed_order[0]['count']}
        else:
            context = {'tariffs': tariffs, 'tariff_checked': tariffs[0]['pk'], 'count': 0}

        return render(request, 'm2m_app/select_tariff.html', context=context)
    elif request.method == 'POST':
        data = request.POST
        tariff_pk = data.get('tariff_pk')
        count = data.get('count')
        if tariff_pk and int(count) > 0:
            if Tariff.objects.filter(pk=tariff_pk).exists():
                not_closed_order = Order.objects.filter(user=request.user.pk, is_closed=False)
                if not_closed_order.exists():
                    not_closed_order.update(count=count, tariff_id=tariff_pk)
                else:
                    Order.objects.create(count=count, tariff_id=tariff_pk, user_id=request.user.pk)
                return redirect(reverse('delivery_url'))
    return HttpResponse(status=404)


@login_required
@check_not_closed_order_exist_and_tariff_is_selected
def delivery(request):
    if request.method == 'GET':
        not_closed_order = Order.objects.filter(user=request.user.pk, is_closed=False).values('tariff__cost', 'count')
        context = {'total': int(not_closed_order[0]['tariff__cost']) * int(not_closed_order[0]['count'])}
        return render(request, 'm2m_app/delivery.html', context=context)
    elif request.method == 'POST' and request.is_ajax():
        delivery_type = request.POST.get('delivery_type', '')
        if delivery_type == 'CUSTOM_TYPE':
            form = DeliveryCustomType(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                Order.objects.filter(user=request.user.pk, is_closed=False).update(
                    sdek_id=None, address_sdek='-', delivery_type=Order.CUSTOM_TYPE,
                    custom_delivery_message=data['custom_delivery_message'], delivery_cost=0
                )
                return JsonResponse({'reverse': reverse("payment_url")})
        elif delivery_type == 'STANDARD_TYPE':
            form = DeliveryStandardType(request.POST)
            if form.is_valid():
                Order.objects.filter(user=request.user.pk, is_closed=False).update(
                    delivery_type=Order.STANDARD_TYPE, custom_delivery_message=None,
                    **form.cleaned_data
                )
                return JsonResponse({'reverse': reverse("payment_url")})
        return JsonResponse({'reverse': reverse('delivery_url')})


@login_required
def get_point_geolocation_pvz(request):
    start = time()
    if request.method == 'GET' and request.is_ajax():
        address = request.GET.get('address', '')
        if address:
            user_point = ParseDadataAddress()
            user_point = user_point(address)
            if user_point:
                city_id = parse_city_code_for_cdek(user_point.get('city', ''), user_point.get('city_fias_id', ''))
                if city_id:
                    pvz = parse_point_geolocation_pvz_cdek(city_id, user_point.get('city', ''))
                    if pvz:
                        print(f"I'm workded -- {time() - start}msec.")
                        return JsonResponse(data={'user_point': user_point, 'pvz': pvz, 'city_id': city_id}, safe=False)
    return HttpResponse(status=403)


@login_required
def get_delivery_cost(request):
    if request.method == 'GET' and request.is_ajax():
        city_id = request.GET.get('city_id')
        if city_id:
            price = delivery_cost_calculation(city_id)
            return JsonResponse({'price': price}, safe=False)
    return HttpResponse(status=403)


@login_required
@check_not_closed_order_exist_and_tariff_is_selected
def order_approval(request):
    if request.method == 'GET':
        order = Order.objects.filter(user=request.user.pk, is_closed=False).values(
            'tariff__cost', 'tariff__name', 'tariff__locations', 'count', 'address_sdek',
            'delivery_cost', 'delivery_type', 'payment_type')
        data = order[0]
        delivery_type = data.get('delivery_type')
        address_sdek = data.get('address_sdek', '') if data.get('address_sdek', '') else '-'
        total = int(data.get('tariff__cost', 0)) * int(data.get('count', 0))
        user = CustomUsers.objects.filter(pk=request.user.pk).values_list(
            'physical__full_name', 'juridical_entrepreneur__name_company',
            'individual_entrepreneur__name_company')
        user = [el for el in user[0] if el][0]
        if delivery_type == Order.STANDARD_TYPE:
            total = int(data.get('tariff__cost', 0)) * int(data.get('count', 0)) + int(data.get('delivery_cost', 0))
        context = {
            "total": total,
            "count": data.get('count', 0),
            "tariff": f"{data.get('tariff__name', '')} ({data.get('tariff__locations', '')})",
            "user": user,
            "address_sdek": address_sdek,
            'payment_type': data.get('payment_type', '')
        }
        return render(request, 'm2m_app/order_approval.html', context=context)

    elif request.method == 'POST':
        Order.objects.filter(user=request.user.pk, is_closed=False).update(is_closed=True)
        # send Order.json
        return redirect(reverse('order_history_url'))
    return HttpResponse(status=403)


@login_required
def order_history(request):
    if request.method == 'GET':
        orders = Order.objects.filter(user=request.user.pk, is_closed=True).values(
            'id', 'date_created', 'count', 'tariff__name', 'address_sdek', 'tariff__cost', 'tracking_number',
            'delivery_cost', 'delivery_type', 'payment_type'
        )
        for order in orders:
            total = int(order.get('tariff__cost', 0)) * int(order.get('count', 0))
            if order.get('delivery_type', '') == Order.STANDARD_TYPE:
                total = total + int(order.get('delivery_cost', 0))
                order.update({'total': total})
            # order.update({'tracking_number': order.ger('tracking_number') if order.ger('tracking_number') else '-'})
            # order.update({'tracking_number': order.ger('tracking_number') if order.ger('tracking_number') else '-'})
        return render(request, 'm2m_app/order_history.html', context={"orders": orders})


@login_required
def repeat_order(request):
    if request.method == 'POST' and request.POST.get('order_id'):
        order = Order.objects.filter(user=request.user.pk, pk=request.POST.get('order_id')).values(
            'count', 'user_id', 'tariff_id', 'address_sdek', 'sdek_id', 'is_closed', 'custom_delivery_message',
            'delivery_type', 'delivery_cost', 'tracking_number', 'payment_type')
        order[0]['tracking_number'] = '-'
        if order:
            new_order = Order(**order[0])
            new_order.save()
            # send Order.json
            return redirect(reverse('order_history_url'))


def get_context(request):
    if request.method == "GET" and request.is_ajax():
        comments = Comment.objects.filter(is_active=True).values('owner', 'specification', 'link')
        tech_tel = TechSupport.objects.filter(is_active=True).values('tel')
        tech_tel = tech_tel[0].get('tel', '')
        comments = SimpleTemplateResponse('m2m_app/comments.html', context={'comments': comments})
        comments = comments.rendered_content
        return JsonResponse({'comments': comments, 'tech_tel': tech_tel})
        # return render(request, 'm2m_app/comments.html', context={'comments': comments})


@login_required
@check_not_closed_order_exist_and_tariff_is_selected
def payment(request):
    if request.method == 'GET':
        order = Order.objects.filter(user=request.user.pk, is_closed=False).values(
            'id', 'count', 'tariff__cost', 'delivery_cost', 'delivery_type', 'payment_type')
        order = order[0]
        total = int(order.get('tariff__cost', 0)) * int(order.get('count', 0))
        if order.get('delivery_type', '') == Order.STANDARD_TYPE:
            total = total + int(order.get('delivery_cost', 0))
        context = {'total': total}
        if order.get('payment_type') == Order.INVOICE:
            context.update(dict(payment_type=order.get('payment_type')))
        return render(request, 'm2m_app/payment.html', context)
    if request.method == 'POST':
        data = request.POST.get('pay_value')
        choices_val = [const for const, foo in Order.PAYMENT_TYPE_CHOICES]
        if data not in choices_val:
            return HttpResponse(status=400)
        foo = Order.objects.get(user=request.user.pk, is_closed=False)
        foo.payment_type = data
        foo.save()
        return redirect(reverse('order_approval_url'))
    return HttpResponse(404)












