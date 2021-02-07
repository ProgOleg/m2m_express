from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
from django.utils.translation import gettext_lazy as _
from time import time
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ObjectDoesNotExist


def pdf_path(instance, filename):
    filename_date = str(int(time()))
    return f'scan_copy/pdf/{filename_date}.{filename.split(".")[-1]}'


class CustomUserManager(BaseUserManager):
    def create_user(self, name, email, tel, password=None):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            tel=tel,
            name=name
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, name, email, tel, password):
        user = self.create_user(
            email=email,
            password=password,
            tel=tel,
            name=name
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class CustomUsers(AbstractBaseUser):

    name = models.CharField(verbose_name='Имя', max_length=255)
    email = models.EmailField(verbose_name='email', max_length=255, unique=True)
    tel = models.CharField(verbose_name='Номер телефона', max_length=30, unique=True)
    mailing_status = models.BooleanField(verbose_name='Статус рассылки', default=False)
    date_created = models.DateTimeField(verbose_name='Дата создания', auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(verbose_name='Администраци', default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'tel']

    def __str__(self):
        return f'{self.name}, {self.tel}'

    @staticmethod
    def user_role(obj):
        fields_related = ['physical', 'juridical_entrepreneur', 'individual_entrepreneur']
        value = ''
        for field in fields_related:
            try:
                value = obj.__getattribute__(field)._meta.original_attrs['verbose_name']
                if value:
                    return value
            except ObjectDoesNotExist:
                continue
        return value if value else ''

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')


class UsersProfile(models.Model):

    class Meta:
        abstract = True

    inn = models.CharField(verbose_name="ИНН", unique=True, max_length=255)
    name_company = models.CharField(verbose_name="Название компании", max_length=255)
    ogrn = models.CharField(verbose_name="ОГРН", max_length=255)
    kpp = models.CharField(verbose_name="КПП", max_length=255)
    address = models.CharField(verbose_name="Адресс", max_length=1000)
    date_created = models.DateTimeField(verbose_name="Дата создания", auto_now=True)

    def __str__(self):
        return f'{self.inn}, {self.name_company}'


class IsActiveField(models.Model):

    is_active = models.BooleanField("Активно на страницу", default=True)

    class Meta:
        abstract = True


class UsersProfileIndividualEntrepreneur(UsersProfile):
    user = models.OneToOneField(
        'CustomUsers', verbose_name='Пользователь', on_delete=models.SET_NULL,
        null=True, default=None, related_name='individual_entrepreneur')

    class Meta:
        verbose_name = 'ИП'
        verbose_name_plural = 'ИП'


class UsersProfileJuridical(UsersProfile):
    user = models.OneToOneField(
        'CustomUsers', verbose_name='Пользователь', on_delete=models.SET_NULL,
        null=True, default=None, related_name='juridical_entrepreneur')

    class Meta:
        verbose_name = 'Юридическое лицо'
        verbose_name_plural = 'Юридическое лицо'


class UsersProfilePhysicalEntrepreneur(models.Model):

    full_name = models.CharField(verbose_name='ФИО', max_length=255)
    tel = models.CharField(verbose_name='Номер телефона', max_length=255)
    email = models.EmailField(verbose_name='email', max_length=255, unique=True)
    scan_copy_img = models.ImageField(verbose_name="Скан фото", upload_to='scan_copy/img/', null=True,
                                      blank=True,)
    scan_copy_pdf = models.FileField(
        verbose_name="Скфан pdf", upload_to=pdf_path,
        validators=[FileExtensionValidator(['pdf'])], null=True, blank=True)
    user = models.OneToOneField(
        'CustomUsers', verbose_name='Пользователь', on_delete=models.SET_NULL,
        null=True, default=None, related_name='physical')

    def __str__(self):
        return f'{self.full_name}, {self.tel}'

    class Meta:
        verbose_name = 'Физическое Лицо'
        verbose_name_plural = 'Физическое Лицо'

    file_extension = {'scan_copy_img': ['jpg', 'png', 'jpeg'],
                      'scan_copy_pdf': ['pdf']}


class Comment(IsActiveField):

    owner = models.CharField(verbose_name="Название компании", max_length=255)
    specification = models.CharField(verbose_name="Описание", max_length=255)
    link = models.CharField(verbose_name="Ссылка", max_length=2000)

    def __str__(self):
        return f'{self.owner}, {self.specification[:20]}'

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'


class Tariff(models.Model):

    name = models.CharField(verbose_name="Наименование", max_length=255)
    locations = models.CharField(verbose_name="Локации", max_length=255)
    sms = models.CharField(verbose_name="Стоимость SMS", max_length=255)
    megabyte = models.CharField(verbose_name="Стоимость MB", max_length=255)
    cost = models.IntegerField(verbose_name="Стоимость")
    is_active = models.BooleanField(verbose_name="Активен на странице", default=True)
    date_created = models.DateTimeField(verbose_name="Дата создания", auto_now=True)

    def __str__(self):
        return f'{self.name}, {self.cost}, {"Aктивен" if self.is_active else "Не активен"}'

    class Meta:
        verbose_name = 'Тариф'
        verbose_name_plural = 'Тарифы'


class Order(models.Model):

    CUSTOM_TYPE = 'CUSTOM_TYPE'
    STANDARD_TYPE = 'STANDARD_TYPE'

    DELIVERY_TYPE_CHOICES = [
        (CUSTOM_TYPE, _("Custom")),
        (STANDARD_TYPE, _("Standard"))
    ]

    NOT_SELECTED = 'NOT_SELECTED'
    INVOICE = 'INVOICE'
    BANK_CARD = 'BANK_CARD'

    PAYMENT_TYPE_CHOICES = [
        (NOT_SELECTED, 'Не выбрано'),
        (INVOICE, 'Счет'),
        (BANK_CARD, 'Карта')
    ]

    count = models.IntegerField(verbose_name="Количество")
    user = models.ForeignKey('CustomUsers', verbose_name='Пользователь', on_delete=models.SET_NULL,
                             null=True, default=None)
    tariff = models.ForeignKey('Tariff', verbose_name='Тариф', on_delete=models.SET_NULL,
                               null=True, default=None)
    address_sdek = models.CharField(verbose_name="Адресс СДЭК", max_length=1000, default='-', null=True, blank=True)
    sdek_id = models.CharField(verbose_name="ID отделения", max_length=255, default=None, null=True, blank=True)
    is_closed = models.BooleanField(verbose_name="Закрыт клиентом", default=False)
    is_finished = models.BooleanField(verbose_name="Завершен", default=False)
    date_created = models.DateTimeField(verbose_name="Дата создания", auto_now_add=True)
    date_changed = models.DateTimeField(verbose_name="Дата изменения", auto_now=True)
    custom_delivery_message = models.CharField(verbose_name="Условия доставки", max_length=2056,
                                               default=None, null=True, blank=True)
    delivery_type = models.CharField(verbose_name="Тип доставки", max_length=13, choices=DELIVERY_TYPE_CHOICES,
                                     default=STANDARD_TYPE)
    delivery_cost = models.IntegerField(verbose_name="Стоимость доставки", default=0)
    tracking_number = models.CharField(verbose_name="Трекинг номер", default='-', null=True, max_length=255)
    payment_type = models.CharField(verbose_name="Тип оплаты", choices=PAYMENT_TYPE_CHOICES, max_length=63,
                                    default=NOT_SELECTED)

    def __str__(self):
        return f'{self.user.email}, {self.tariff.name}, {self.address_sdek or self.custom_delivery_message[:20]}'

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-date_created']


class TechSupport(IsActiveField):

    tel = models.CharField(verbose_name='Номер телефона', max_length=18)

    def save(self, *args, **kwargs):
        if self.is_active:
            objs = self.__class__.objects.filter(is_active=True)
            if objs.exists():
                objs.update(is_active=False)
        return super(self.__class__, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.tel}, {self.is_active}'

    class Meta:
        verbose_name_plural = "Телефон тех поддержки"


class ManagerMail(IsActiveField):

    mail = models.CharField(verbose_name="почта", max_length=255)

    def save(self, *args, **kwargs):
        if self.is_active:
            objs = self.__class__.objects.filter(is_active=True)
            if objs.exists():
                objs.update(is_active=False)
        return super(self.__class__, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.mail}'

    class Meta:
        verbose_name = "Почта менеджера"
        verbose_name_plural = "Почта менеджера"









