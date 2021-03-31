import openpyxl
from num2words import num2words
import contextlib


class Parser:

    INVOICE_NUMBER = None
    INVOICE_DATE = None
    CUSTOMER_INFO = None
    PRODUCT_NAME = None
    PRODUCT_COUNT = None
    PRODUCT_PRICE = None

    RU_MONTH_VALUES = {
        'января': "01",
        'февраля': "02",
        'марта': "03",
        'апреля': "04",
        'мая': "05",
        'июня': "06",
        'июля': "07",
        'августа': "08",
        'сентября': "09",
        'октября': "10",
        'ноября': "11",
        'декабря': "12",
    }

    FILE_TEMPLATE_PATH = "invoice_temlate.xlsx"
    COORDINATE = {
        "invoice_number_date": "B11",
        "customer_info": "H17",
        "customer_delivery": "H19",
        "product_name": "D22",
        "product_count": "Y22",
        "product_price": "AD22",
        "product_total_price_table": "AH22",
        "delivery_price": "AH23",
        "product_total_price_row": "AH24",
        "product_total_price_count_row": "B25",
        "product_total_price_literal": "B26",
    }

    def __init__(
            self,
            path: str,
            product_price: [int, float],
            product_count: int = "",
            delivery_price: [int, float] = 0,
            invoice_number: str = "",
            invoice_date: str = "",
            customer_info: str = "",
            product_name: str = "",
    ):
        self.invoice_number = invoice_number
        self.invoice_date = self.format_ru_months(invoice_date)
        self.customer_info = customer_info
        self.product_name = product_name
        self.product_count = product_count
        self.product_price = product_price
        self.delivery_price = delivery_price
        total_price = self.product_count * self.product_price + self.delivery_price
        self.total_price = round(total_price, 2) if isinstance(total_price, float) else total_price
        product_total_price = self.product_count * self.product_price
        self.product_total_price = round(product_total_price, 2) if isinstance(product_total_price, float) else product_total_price
        self.product_total_price_literal = Parser.price_formatting(self.total_price)
        self.path = path

    @staticmethod
    def price_formatting(value: [str, float]) -> str:

        if isinstance(value, int):
            return f"{num2words(value, lang='ru').capitalize()} руб."

        if isinstance(value, float):
            whole_part, fractional_part = str(value).split(".")
            whole_part, fractional_part = (int(whole_part), int(fractional_part))
            return f"{num2words(whole_part, lang='ru').capitalize()} руб. {fractional_part} коп."

    @contextlib.contextmanager
    def file_manager(self, file=FILE_TEMPLATE_PATH):

        wb = openpyxl.load_workbook(file)
        try:
            yield wb
        # except Exception as ex:
        #     print(ex)
        finally:
            wb.close()

    def format_ru_months(self, date: str) -> str:
        splited_data = date.split("-")
        months = splited_data[1]
        for key, val in Parser.RU_MONTH_VALUES.items():
            if months == val:
                splited_data[1] = key
                return " ".join(splited_data)
        return date

    def parsing_page(self):
        with self.file_manager() as wb:
            _ = wb.sheetnames
            template = wb.active
            data = f"Счет на оплату № ЛП-{self.invoice_number} от {self.invoice_date} г."
            template[Parser.COORDINATE["invoice_number_date"]].value = data

            template[Parser.COORDINATE["customer_info"]].value = self.customer_info
            template[Parser.COORDINATE["customer_delivery"]].value = self.customer_info
            template[Parser.COORDINATE["product_name"]].value = self.product_name
            template[Parser.COORDINATE["product_count"]].value = self.product_count
            template[Parser.COORDINATE["product_price"]].value = self.product_price
            template[Parser.COORDINATE["product_total_price_table"]].value = self.product_total_price
            template[Parser.COORDINATE["product_total_price_row"]].value = self.total_price
            template[Parser.COORDINATE["delivery_price"]].value = self.delivery_price

            data = f"Всего наименований 1, на сумму {self.total_price} руб."
            template[Parser.COORDINATE["product_total_price_count_row"]].value = data
            template[Parser.COORDINATE["product_total_price_literal"]].value = self.product_total_price_literal
            wb.save(self.path)
