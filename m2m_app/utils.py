from django.conf import settings
from dadata import Dadata
from django.shortcuts import redirect
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
import requests
import json
from django.http import HttpResponse
from .models import *
from django.template.response import SimpleTemplateResponse
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives


class EntrepreneurInfo:
    errors = {
        'data not found': {'error': 'По данному ИНН данных не обнаруженно'},
        'unknown error': {'error': 'Неизвестная ошибка'},
    }
    count_resp = 3

    def __init__(self, query, token=settings.DADATA_API_TOKEN):
        self._token = token
        self.ddata = Dadata(token=self._token)
        self.query = query

    def entrepreneur_info(self):
        data = self._attempt_response()
        data = self._parse_entrepreneur_info(data)
        return data

    def _parse_entrepreneur_info(self, data):
        try:
            name_company = data[0]['value']
            ogrn = data[0]['data']['ogrn']
            kpp = data[0]['data']['kpp']
            address = data[0]['data']['address']['value']
        except KeyError:
            return self.errors['data not found']
        except TypeError:
            return self.errors['unknown error']
        return {"entrepreneur_info": {
           "name_company": name_company,
            "ogrn": ogrn,
            "kpp": kpp,
            "address": address
        }}

    def _attempt_response(self, count=count_resp):
        for _ in range(count):
            data = self._resp()
            if data:
                return data
        return

    def _resp(self):
        response = self.ddata.find_by_id("party", query=self.query)
        return response

#     dda.suggest("address", "москва моховая 13")


class ParseDadataAddress:

    def __call__(self, query: str, token=settings.DADATA_API_TOKEN):
        self._token = token
        self.ddata = Dadata(token=self._token)
        self.query = query
        response = self._get_request()
        data = self._parse_response(response)
        return data

    def _get_request(self):
        response = self.ddata.suggest("address", self.query)
        return response

    @staticmethod
    def _parse_response(response):
        try:
            value = response[0].get("data")
        except IndexError:
            return
        postal_code = value.get('postal_code', '')
        city = value.get('city', '')
        geo_lat = value.get('geo_lat', '')
        geo_lon = value.get('geo_lon', '')
        city_fias_id = value.get('city_fias_id', '')
        return {'postal_code': postal_code, 'city': city,
                'city_fias_id': city_fias_id,
                'location': {
                    'lat': float(geo_lat), 'lng': float(geo_lon),
                }}


def check_valid_reverse_url(request, data, url, context=None):
    if data.is_valid():
        data.save()
        return redirect(reverse(url))
    return


def check_user_info(user):
    fields_related = ['physical', 'juridical_entrepreneur', 'individual_entrepreneur']
    for field in fields_related:
        try:
            value = user.__getattr__(field)
            if value:
                return value
        except ObjectDoesNotExist:
            continue
        return None


def parse_city_code_for_cdek(city, city_fias_id, country_code='RU'):
    data = {'cityName': city,
            'fiasGuid': city_fias_id,
            'countryCode': country_code}
    response = requests.get('http://integration.cdek.ru/v1/location/cities/json?', params=data)
    if response.status_code == 200:
        data = response.json()
        if data:
            # print(f'parse_city_code_for_cdek: {data}')
            city_code = data[0].get('cityCode', '')
            return city_code
    return


def parse_point_geolocation_pvz_cdek(city_id, city):
    response = requests.get('https://integration.cdek.ru/pvzlist/v1/json?', params={"cityid": int(city_id)})
    if response.status_code == 200:
        response = response.json()
        if response:
            pvz_array = response.get('pvz')
            data = []
            for el in pvz_array:
                assert city == el.get('city', '')
                address = el.get('fullAddress', '')
                lng = el.get('coordX', '')
                lat = el.get('coordY', '')
                code = el.get('code', '')
                data.append({'address': address,
                             'location': {'lng': float(lng), 'lat': float(lat)},
                             'code': code})
            return data
    return


def delivery_cost_calculation(receiver_city_id, sender_city_id="44"):
    # tariff_id
    body = {
        "version": "1.0",
        "senderCityId": sender_city_id,
        "receiverCityId": receiver_city_id,
        "tariffId": "10",
        "goods":
            [{
                "weight": "0.1",
                "length": "0.1",
                "width": "0.1",
                "height": "0.1"
            }]
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post('http://api.cdek.ru/calculator/calculate_price_by_json.php', headers=headers, json=body)
    if response.status_code == 200:
        response = response.json()
        price = response.get('result', {}).get('price', '')
        return price
    return ''


def check_not_closed_order_exist_and_tariff_is_selected(f):
    def wrap(*args, **kwargs):
        user_pk = args[0].user.pk
        have_not_closed_order = Order.objects.filter(user=user_pk, is_closed=False).exists()
        if have_not_closed_order:
            order_tariff_exist = Order.objects.filter(user=user_pk, is_closed=False).values('tariff_id')
            if order_tariff_exist[0].get('tariff_id'):
                return f(*args, **kwargs)
        return redirect(reverse('select_tariff_url'))
    return wrap


def context_loader():
    comments = Comment.objects.filter(is_active=True).values('owner', 'specification', 'link')
    tech_tel = TechSupport.objects.filter(is_active=True).values('tel')
    comments = SimpleTemplateResponse('m2m_app/commnts.html', context={'comments': comments})
    return {'comments': comments, 'tech_tel': tech_tel}


def check_user_is_no_anonimus(f):
    def wrap(*args, **kwargs):
        if not args[0].user.is_anonymous:
            return redirect(reverse('select_tariff_url'))
        return f(*args, **kwargs)
    return wrap


class SendEmailMessage:
    mail_from_send = settings.EMAIL_HOST_USER
    template = 'm2m_app/mail_template.html'

    def __init__(self, context, mail_to_send=None):
        if mail_to_send:
            self.mail_to_send = mail_to_send
        else:
            obj = ManagerMail.objects.filter(is_active=True).values('mail')
            self.mail_to_send = obj[0].get('mail')
        self.context = context
        self.header = f'Новый Ордер ID-{context.get("order").get("id")}'

    def send_message(self):
        html_content = render_to_string(self.template, self.context)
        text_content = strip_tags(html_content)
        msg = EmailMultiAlternatives(self.header, text_content, self.mail_from_send, [self.mail_to_send])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

