# -*- coding: utf-8 -*-
import json
import hashlib
import datetime
import urllib.request as urllib_request
from urllib.error import HTTPError
from urllib.parse import urlencode
from io import BytesIO
from xml.etree import ElementTree
from abc import abstractmethod


class AbstractOrder():

    def get_number(self):
        """ Номер заказа """
        return getattr(self, 'number')
        
    @abstractmethod
    def get_products(self):
        """ Список товаров """

    def get_sender_name(self):
        """ Наименование отправителя """
        return ''

    def get_sender_address(self):
        """ Адрес отправителя """
        return ''

    def get_sender_city_id(self):
        """ ID города отправителя по базе СДЭК """
        return getattr(self, 'sender_city_id')

    def get_sender_postcode(self):
        """ Почтовый индекс отправителя """
        return getattr(self, 'sender_city_postcode', '')

    def get_recipient_name(self):
        """ Имя получателя """
        return getattr(self, 'recipient_name')

    def get_recipient_phone(self):
        """ Номер телефона получателя """
        return getattr(self, 'recipient_phone')

    def get_recipient_city_id(self):
        """ ID города получателя по базе СДЭК """
        return getattr(self, 'recipient_city_id')

    def get_recipient_postcode(self):
        """ Почтовый индекс получателя """
        return getattr(self, 'recipient_city_postcode', '')

    def get_recipient_address_street(self):
        """ Улица адреса доставки """
        return getattr(self, 'recipient_address_street')

    def get_recipient_address_house(self):
        """ Номер дома адреса доставки """
        return getattr(self, 'recipient_address_house')

    def get_recipient_address_flat(self):
        """ Номер квартиры адреса доставки (необязательное поле)"""
        return getattr(self, 'recipient_address_flat', '')

    def get_pvz_code(self):
        """ Код пункта самовывоза """
        return getattr(self, 'pvz_code')

    def get_shipping_tariff(self):
        """ ID тарифа доставки """
        return getattr(self, 'shipping_tariff')

    def get_shipping_price(self):
        """ Стоимость доставки """
        return getattr(self, 'shipping_price')

    def get_comment(self):
        """ Дополнительные инструкции для доставки """
        return ''


class AbstractOrderLine():

    @abstractmethod
    def get_product_title(self):
        """ Название товара """

    @abstractmethod
    def get_product_upc(self):
        """ Артикул товара """

    @abstractmethod
    def get_product_weight(self):
        """ Вес единицы товара в граммах """

    def get_quantity(self):
        """ Количество """
        return getattr(self, 'quantity')

    @abstractmethod
    def get_product_price(self):
        """ Цена за единицу товара """

    @abstractmethod
    def get_product_payment(self):
        """ Цена за единицу товара, которую клиент должен оплатить при получении """


class Client(object):
    INTEGRATOR_URL = 'http://integration.cdek.ru'
    CALCULATOR_URL = 'http://api.cdek.ru/calculator/calculate_price_by_json.php'
    CREATE_ORDER_URL = INTEGRATOR_URL + '/new_orders.php'
    DELETE_ORDER_URL = INTEGRATOR_URL + '/delete_orders.php'
    ORDER_STATUS_URL = INTEGRATOR_URL + '/status_report_h.php'
    ORDER_INFO_URL = INTEGRATOR_URL + '/info_report.php'
    ORDER_PRINT_URL = INTEGRATOR_URL + '/orders_print.php'
    DELIVERY_POINTS_URL = INTEGRATOR_URL + '/pvzlist.php'
    CALL_COURIER_URL = INTEGRATOR_URL + '/call_courier.php'
    array_tags = {'State', 'Delay', 'Good', 'Fail', 'Item', 'Package'}
    ALLOWED_REQUEST_METHODS = ('GET', 'POST')

    def __init__(self, login, password):
        self._login = login
        self._password = password

    @classmethod
    def _exec_request(cls, url, data, method='GET'):
        if method not in cls.ALLOWED_REQUEST_METHODS:
            raise NotImplementedError('Unknown method "%s"' % method)
        elif data is None or url is None:
            raise AttributeError(
                'Unsupported value. Check value of url and data before '
                'calling _exec_request. '
                'Current values: url={url}, data={data}'.format(url=url, data=data)
            )
        try:
            request = ''
            if method == 'GET':
                request = urllib_request.Request(url + '?' + urlencode(data))
            elif method == 'POST':
                request = urllib_request.Request(url, data=data.encode('utf-8'))
            return urllib_request.urlopen(request).read()
        except HTTPError as he:
            raise he
        except Exception as e:
            raise Exception(
                'Exception occured during _exec_request: {e}'.format(e=repr(e))
            )

    @classmethod
    def _parse_xml(cls, data):
        try:
            xml = ElementTree.fromstring(data)
        except ElementTree.ParseError:
            pass
        else:
            return xml

    @classmethod
    def _xml_to_dict(cls, xml):
        result = xml.attrib

        for child in xml.getchildren():
            if child.tag in cls.array_tags:
                result[child.tag] = result.get(child.tag, [])
                result[child.tag].append(cls._xml_to_dict(child))
            else:
                result[child.tag] = cls._xml_to_dict(child)

        return result

    def get_shipping_cost_IM(self, sender_city_id, receiver_city_id, tariffs, goods):
        u"""
        Возвращает информацию о стоимости и сроках доставки,
        включая тарифы для Интернет Магазинов (аналогично методу get_shipping_cost)
        :param sender_city_id: ID города отправителя по базе СДЭК
        :param receiver_city_id: ID города получателя по базе СДЭК
        :param tariffs: список тарифов
        :param goods: список товаров
        :return: dict
        """
        auth = self._make_auth(use_time=False)
        params = {
            'version': '1.0',
            'authLogin': auth['Account'],
            'secure': auth['Secure'],
            'dateExecute': auth['Date'],
            'senderCityId': sender_city_id,
            'receiverCityId': receiver_city_id,
            'tariffList': [{'priority': i, 'id': tariff} for i, tariff in enumerate(tariffs, 1)],
            'goods': goods,
        }

        return json.loads(self._exec_request(self.CALCULATOR_URL, json.dumps(params), 'POST').decode('utf-8'))

    @classmethod
    def get_shipping_cost(cls, sender_city_id, receiver_city_id, tariffs, goods):
        """
        Возвращает информацию о стоимости и сроках доставки
        Для отправителя и получателя обязателен один из параметров:
        *_city_id или *_city_postcode внутри *_city_data
        :param sender_city_id: ID города отправителя по базе СДЭК
        :param receiver_city_id: ID города получателя по базе СДЭК
        :param tariffs: список тарифов
        :param goods: список товаров
        :returns dict
        """
        params = {
            'version': '1.0',
            'dateExecute': datetime.date.today().isoformat(),
            'senderCityId': sender_city_id,
            'receiverCityId': receiver_city_id,
            'tariffList': [{'priority': i, 'id': tariff} for i, tariff in enumerate(tariffs, 1)],
            'goods': goods,
        }

        return json.loads(cls._exec_request(cls.CALCULATOR_URL, json.dumps(params), 'POST').decode('utf-8'))

    @classmethod
    def get_delivery_points(cls, city_id=None):
        """
        Возвращает списков пунктов самовывоза для указанного города,
        либо для всех если город не указан
        :param city_id: ID города по базе СДЭК
        :returns list
        """
        response = cls._exec_request(
            cls.DELIVERY_POINTS_URL,
            {'cityid': city_id} if city_id else {}
        )
        xml = cls._parse_xml(response)

        return [cls._xml_to_dict(point) for point in xml.findall('Pvz')]

    def _xml_to_string(self, xml):
        buff = BytesIO()
        ElementTree.ElementTree(xml).write(buff, encoding='UTF-8',
                                           xml_declaration=False)

        return b'<?xml version="1.0" encoding="UTF-8" ?>' + buff.getvalue()

    def _exec_xml_request(self, url, xml_element):
        auth = self._make_auth(use_time=True)
        xml_element.attrib['Date'] = auth['Date']
        xml_element.attrib['Account'] = auth['Account']
        xml_element.attrib['Secure'] = auth['Secure']

        response = self._exec_request(
            url,
            urlencode({'xml_request': self._xml_to_string(xml_element)}),
            method='POST'
        )
        return self._parse_xml(response)

    def _make_auth(self, use_time=False):
        u"""
        Формирует данные авторизации для ИМ, необходимые для запросов
        :return: dict
        """
        format_string = '%Y-%m-%dT%H:%M:%S' if use_time else '%Y-%m-%d'
        date = datetime.datetime.now().strftime(format_string)
        return {
            "Date": date,
            "Account": self._login,
            "Secure": self._make_secure(date),
        }

    def _make_secure(self, date):
        code = '{}&{}'.format(date, self._password)
        if isinstance(code, str):
            code = code.encode('utf-8')

        return hashlib.md5(code).hexdigest()

    def create_order(self, order):
        """
        Создать заказ
        :param order: экземпляр класса AbstractOrder
        :returns dict
        """
        delivery_request_element = ElementTree.Element(
            'DeliveryRequest',
            Number=str(order.get_number()),
            OrderCount='1'
        )

        # 1.7 "Регистрация заказа от интернет магазина" - док-я v1.5
        # Заказ
        order_element = ElementTree.SubElement(delivery_request_element, 'Order')
        order_element.attrib['Number'] = str(order.get_number())
        order_element.attrib['SendCityCode'] = str(order.get_sender_city_id())
        order_element.attrib['SendCityPostCode'] = str(order.get_sender_postcode())
        order_element.attrib['RecCityCode'] = str(order.get_recipient_city_id())
        order_element.attrib['RecCityPostCode'] = str(order.get_recipient_postcode())

        # 1.7.16
        order_element.attrib['RecipientName'] = order.get_recipient_name()
        # 1.7.18
        order_element.attrib['Phone'] = str(order.get_recipient_phone())
        order_element.attrib['TariffTypeCode'] = str(order.get_shipping_tariff())

        # 1.7.27 - Адрес доставки
        address_element = ElementTree.SubElement(order_element, 'Address')
        if order.get_pvz_code():
            address_element.attrib['PvzCode'] = order.get_pvz_code()
        else:
            address_element.attrib['Street'] = order.get_recipient_address_street()
            address_element.attrib['House'] = str(order.get_recipient_address_house())
            address_element.attrib['Flat'] = str(order.get_recipient_address_flat())

        # 1.7.28 - Упаковка
        package_element = ElementTree.SubElement(
            order_element,
            'Package',
            Number='%s1' % order.get_number(),
            BarCode='%s1' % order.get_number()
        )

        total_weight = 0
        # 1.7.28.7 - Товары
        for product in order.get_products():
            item_element = ElementTree.SubElement(
                package_element,
                'Item',
                Amount=str(product.get_quantity())
            )
            item_element.attrib['Weight'] = str(product.get_product_weight())
            item_element.attrib['WareKey'] = str(product.get_product_upc())[:30]
            item_element.attrib['Cost'] = str(product.get_product_price())
            item_element.attrib['Payment'] = str(product.get_product_payment())
            item_element.attrib['Comment'] = str(product.get_product_title())

            total_weight += product.get_product_weight()

        package_element.attrib['Weight'] = str(total_weight)

        order_element.attrib['DeliveryRecipientCost'] = str(order.get_shipping_price())
        order_element.attrib['Comment'] = order.get_comment()

        xml = self._exec_xml_request(self.CREATE_ORDER_URL, delivery_request_element)
        return self._xml_to_dict(xml.find('Order'))

    def delete_order(self, order):
        """
        Удалить заказ
        :param order: экземпляр класса AbstractOrder
        :returns dict
        """
        delete_request_element = ElementTree.Element(
            'DeleteRequest',
            Number=str(order.get_number()),
            OrderCount='1'
        )
        ElementTree.SubElement(
            delete_request_element,
            'Order',
            Number=str(order.get_number())
        )

        xml = self._exec_xml_request(self.DELETE_ORDER_URL, delete_request_element)
        return self._xml_to_dict(xml.find('Order'))

    def get_orders_info(self, orders_dispatch_numbers):
        """
        Информация по заказам
        :param orders_dispatch_numbers: список номеров отправлений СДЭК
        :returns list
        """
        info_request = ElementTree.Element('InfoRequest')
        for dispatch_number in orders_dispatch_numbers:
            ElementTree.SubElement(
                info_request,
                'Order',
                DispatchNumber=str(dispatch_number)
            )

        xml = self._exec_xml_request(self.ORDER_INFO_URL, info_request)
        return [self._xml_to_dict(order) for order in xml.findall('Order')]

    def get_orders_statuses(self, orders_dispatch_numbers, show_history=True):
        """
        Статусы заказов
        :param orders_dispatch_numbers: список номеров отправлений СДЭК
        :param show_history: получать историю статусов
        :returns list
        """
        status_report_element = ElementTree.Element(
            'StatusReport',
            ShowHistory=str(int(show_history))
        )
        for dispatch_number in orders_dispatch_numbers:
            ElementTree.SubElement(
                status_report_element,
                'Order',
                DispatchNumber=str(dispatch_number)
            )

        xml = self._exec_xml_request(self.ORDER_STATUS_URL, status_report_element)
        return [self._xml_to_dict(order) for order in xml.findall('Order')]

    def get_orders_print(self, orders_dispatch_numbers, copy_count=1):
        """
        Печатная форма квитанции к заказу
        :param orders_dispatch_numbers: список номеров отправлений СДЭК
        :param copy_count: количество копий
        """
        date = datetime.datetime.now().isoformat()
        orders_print_element = ElementTree.Element(
            'OrdersPrint',
            OrderCount=str(len(orders_dispatch_numbers)),
            CopyCount=str(copy_count),
            Date=date,
            Account=self._login,
            Secure=self._make_secure(date)
        )

        for dispatch_number in orders_dispatch_numbers:
            ElementTree.SubElement(
                orders_print_element,
                'Order',
                DispatchNumber=str(dispatch_number)
            )

        response = self._exec_request(
            self.ORDER_PRINT_URL,
            urlencode({'xml_request': self._xml_to_string(orders_print_element)}),
            method='POST'
        )

        return response if not response.startswith(b'<?xml') else None

    def call_courier(self, call_params, dispatch_number=None, comment=''):
        """
        Вызов курьера
        :param call_params: dict с описанием параметров вызова курьера с полями:
            - date: дата ожидания курьера - REQUIRED
            - time_beg: время начала ожидания курьера - REQUIRED
            - time_end: время окончания ожидания курьера - REQUIRED
            - send_city_code: код города отправителя
                - REQUIRED if not dispatch_number
            - send_city_postcode: почтовый индекс города отправителя - REQUIRED
            - send_phone: контактный телефон отправителя
                - REQUIRED if not dispatch_number or
                (dispatch_number и телефон не указан в накладной)
            - sender_name: отправитель (ФИО)
                - REQUIRED if not dispatch_number or
                (dispatch_number и ФИО не указаны в накладной)
            - weight: общий вес, в граммах - REQUIRED if not dispatch_number
            - address: адрес отправителя - REQUIRED:
                - street - улица отправителя - REQUIRED
                - house - дом, корпус, строение отправителя - REQUIRED
                - flat - квартира/офис отправителя - REQUIRED
        :param dispatch_number: str с номером привязанного заказа
        :param comment: комментарий
        :returns xml с ответом (None в случае исключения во время запроса)
        """

        if not call_params or not isinstance(call_params, dict):
            raise AttributeError('Неверный словарь параметров для вызова курьера')

        # Обязательные параметры
        required_keys = [
            'date', 'time_beg', 'time_end',
            'send_city_postcode', 'address'
        ]
        # Обязательные параметры адреса
        required_keys_address = ('street', 'house', 'flat')
        # Обязательные параметры при отсутствии dispatch_number
        if not dispatch_number:
            required_keys += [
                'send_city_code', 'send_phone', 'sender_name', 'weight'
            ]

        # Проверяем словарь с параметрами:
        for key in required_keys:
            if key not in call_params:
                raise AttributeError(
                    'Отсутствует обязательный параметр {key} '
                    'для вызова курьера'.format(key=key)
                )
            if key == 'address':
                for address_key in required_keys_address:
                    if address_key not in call_params[key]:
                        raise AttributeError(
                            'Отсутствует обязательный параметр адреса {key} '
                            'для вызова курьера'.format(key=address_key)
                        )

        # Формируем XML для запроса
        call_courier_element = ElementTree.Element('CallCourier', CallCount='1')
        call_element = ElementTree.SubElement(
            call_courier_element,
            'Call',
            Date=call_params['date'].isoformat(),
            TimeBeg=call_params['time_beg'].isoformat(),
            TimeEnd=call_params['time_end'].isoformat()
        )
        call_element.attrib['SendCityPostCode'] = str(call_params['send_city_postcode'])

        # Необязательные параметры запроса
        if 'send_city_code' in call_params:
            call_element.attrib['SendCityCode'] = str(call_params['send_city_code'])
        if 'send_phone' in call_params:
            call_element.attrib['SendPhone'] = str(call_params['send_phone'])
        if 'sender_name' in call_params:
            call_element.attrib['SenderName'] = str(call_params['sender_name'])
        if 'weight' in call_params:
            call_element.attrib['Weight'] = str(call_params['weight'])
        if dispatch_number:
            call_element.attrib['DispatchNumber'] = str(dispatch_number)
        call_element.attrib['Comment'] = comment

        # Адрес отправителя
        ElementTree.SubElement(
            call_element,
            'Address',
            Street=str(call_params['address']['street']),
            House=str(call_params['address']['house']),
            Flat=str(call_params['address']['flat'])
        )

        try:
            xml = self._exec_xml_request(self.CALL_COURIER_URL, call_courier_element)
        except HTTPError:
            return None
        else:
            return self._xml_to_dict(xml.find('Call'))


class TestClient(Client):
    u"""
    Переопределенный класс клиента для тестирования
    """
    INTEGRATOR_URL = 'https://integration.edu.cdek.ru'
    CALCULATOR_URL = 'http://api.edu.cdek.ru/calculator/calculate_price_by_json.php'
    CREATE_ORDER_URL = INTEGRATOR_URL + '/new_orders.php'
    DELETE_ORDER_URL = INTEGRATOR_URL + '/delete_orders.php'
    ORDER_STATUS_URL = INTEGRATOR_URL + '/status_report_h.php'
    ORDER_INFO_URL = INTEGRATOR_URL + '/info_report.php'
    ORDER_PRINT_URL = INTEGRATOR_URL + '/orders_print.php'
    DELIVERY_POINTS_URL = INTEGRATOR_URL + '/pvzlist.php'
    CALL_COURIER_URL = INTEGRATOR_URL + '/call_courier.php'
