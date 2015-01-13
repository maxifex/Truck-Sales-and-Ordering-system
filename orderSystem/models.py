from django.db import models
from django.contrib.auth.models import User, UserManager
from django.contrib.sessions.backends.db import SessionStore

#Please notw here  that the Agents model class here refers to Staff
class Employee(models.Model):

    STATUS = (
        ('A', 'Active'),
        ('D', 'Deleted'), #Active/ Deleted
    )

    POSITIONS = (
        # (4, 'SALES REPRESENTATIVE'),
        # (8, 'ADMINISTRATOR'),
        (16, 'Sales Representative'),
        (32, 'Administrator'),
    )
    user = models.OneToOneField(User)
    email = models.EmailField(max_length=100, null=True)
    phone_number = models.CharField(max_length=20)
    avatar = models.ImageField(upload_to="profile")
    signature = models.ImageField(upload_to="signature")
    created_date = models.DateTimeField('Date record was created', auto_now_add=True)
    # created_by = models.ForeignKey(User, related_name='%(app_label)s_%(class)s_create_related')
    # modified_date = models.DateTimeField('Date record was modified', auto_now_add=True)
    # modified_by = models.ForeignKey(User, related_name='%(app_label)s_%(class)s_related')
    status = models.CharField(max_length=1, choices=STATUS, default='A')
    position = models.IntegerField(max_length=3, choices=POSITIONS, default=16)
    role = models.CharField(max_length=100, null=True)

    # def __unicode__(self):
    #     return unicode(self.pk)

class Trouble(models.Model):
    name = models.CharField(null=False, max_length=7)


class Country(models.Model):
    STATUS = (
        ('A', 'Active'),
        ('D', 'Deleted'), #Active/Deleted
    )
    name = models.CharField(max_length=100)
    iso2code = models.CharField(max_length=2, null=True)
    port_name = models.CharField(max_length=100, null=True)
    created_date = models.DateTimeField('Date that country was created', auto_now_add=True)
    created_by = models.ForeignKey(User)
    modified_date = models.DateTimeField('Date country was modified', auto_now_add=True)
    modified_by = models.ForeignKey(User, related_name='%(app_label)s_%(class)s_related')
    status = models.CharField(max_length=1, choices=STATUS, default='A')

    def __str__(self):
        return '%s' % (self.name)


class Client(models.Model):

    STATUS = (
        ('A', 'Active'),
        ('D', 'Deleted'), #Active/Deleted
    )

    client_id = models.CharField(max_length=50, unique=True)
    company_name = models.CharField(max_length=200)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.EmailField(max_length=100, null=True)
    alt_email = models.EmailField(max_length=100, null=True)
    mobile_phone = models.CharField(max_length=20, null=True)
    business_phone = models.CharField(max_length=20, null=True)
    fax = models.CharField(max_length=20, null=True)
    address = models.CharField(max_length=500, null=True)
    country = models.ForeignKey(Country)
    city = models.CharField(max_length=100, null= True)
    about = models.CharField(max_length=500, null= True)
    created_date = models.DateTimeField('Date that customer was created', auto_now_add=True)
    created_by = models.ForeignKey(User)
    modified_date = models.DateTimeField('Date record was modified',auto_now_add=True)
    modified_by = models.ForeignKey(User, related_name='%(app_label)s_%(class)s_related')
    status = models.CharField(max_length=1, choices=STATUS, default='A')

    def _get_full_name(self):
        "Returns the person's full name."
        return '%s %s' % (self.first_name, self.last_name)
    contact_person = property(_get_full_name)


class PaymentTerm(models.Model):
    STATUS = (
        ('A', 'Active'),
        ('D', 'Deleted'), #Active/Deleted
    )
    duration = models.IntegerField(max_length=10)
    rate = models.FloatField(max_length=10)
    extra_bank_rate = models.FloatField(max_length=10)
    description = models.CharField(max_length=50)
    status = models.CharField(max_length=1, choices=STATUS, default='A')

class DutyType(models.Model):
    STATUS = (
        ('A', 'Active'),
        ('D', 'Deleted'), #Active/Deleted
    )
    name = models.CharField(max_length=200)
    percent = models.FloatField(max_length=8)
    vat_percentage = models.FloatField(max_length=8)
    status = models.CharField(max_length=1, choices=STATUS, default='A')

class DeliveryTime(models.Model):
    STATUS = (
        ('A', 'Active'),
        ('D', 'Deleted'), #Active/Deleted
    )
    name = models.CharField(max_length=200)
    status = models.CharField(max_length=1, choices=STATUS, default='A')

class Discount(models.Model):
    STATUS = (
        ('A', 'Active'),
        ('D', 'Deleted'), #Active/Deleted
    )
    name = models.CharField(max_length=100)
    percent = models.CharField(max_length=10)
    status = models.CharField(max_length=1, choices=STATUS, default='A')

class SpecialDiscount(models.Model):
    STATUS = (
        ('A', 'Active'),
        ('D', 'Deleted'), #Active/Deleted
    )
    percent = models.CharField(max_length=10)
    status = models.CharField(max_length=1, choices=STATUS, default='A')


class Currency(models.Model):
    STATUS = (
        ('A', 'Active'),
        ('D', 'Deleted'), #Active/Deleted
    )
    DEFAULT = (
        ('Y', 'Yes'),
        ('N', 'No'), #Active/Deleted
    )
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=3)
    symbol = models.CharField(max_length=3)
    is_default = models.CharField(max_length=1, choices=DEFAULT, default='N')
    status = models.CharField(max_length=1, choices=STATUS, default='A')


class TruckAge(models.Model):
    STATUS = (
        ('A', 'Active'),
        ('D', 'Deleted'), #Active/Deleted
    )
    year = models.CharField(max_length=50)
    status = models.CharField(max_length=1, choices=STATUS, default='A')

class Depreciation(models.Model):
    STATUS = (
        ('A', 'Active'),
        ('D', 'Deleted'), #Active/Deleted
    )
    year = models.CharField(max_length=50)
    number = models.IntegerField(default=1)
    percent = models.FloatField(max_length=8)
    status = models.CharField(max_length=1, choices=STATUS, default='A')

class CustomConfiguration(models.Model):
    STATUS = (
        ('A', 'Active'),
        ('D', 'Deleted'), #Active/Deleted
    )
    configuration = models.CharField(max_length=200)
    value = models.CharField(max_length=200)
    status = models.CharField(max_length=1, choices=STATUS, default='A')

class CustomsRate(models.Model):
    STATUS = (
        ('A', 'Active'),
        ('D', 'Deleted'), #Active/Deleted
    )
    name = models.CharField(max_length=200)
    percent = models.FloatField(max_length=8)
    status = models.CharField(max_length=1, choices=STATUS, default='A')


class Order(models.Model):

    STATUS = (
        ('A', 'Active'),
        ('D', 'Deleted'), #Active/Deleted
    )

    ORDER_STATUS = (
        ('P', 'Pending'),
        ('C', 'Completed'),
    )


    order_number = models.CharField(max_length=100, unique=True)
    client = models.ForeignKey(Client)
    man_truck_model = models.CharField(max_length=200)
    order_truck_subscr = models.CharField(max_length=200)
    gfz_number = models.CharField(max_length=200)
    duty_type = models.ForeignKey(DutyType)
    payment_term = models.ForeignKey(PaymentTerm)
    estimated_delivery_time = models.ForeignKey(DeliveryTime)
    quantity = models.IntegerField(default=1)
    discount = models.ForeignKey(Discount)
    special_discount = models.ForeignKey(SpecialDiscount)
    country = models.ForeignKey(Country)
    manex_basic_vehicle_price = models.CharField(max_length=20, null= True)
    currency = models.ForeignKey(Currency)
    additional_equipment = models.CharField(max_length=200)
    external_equipment = models.CharField(max_length=200)
    other_to_be_equipment = models.CharField(max_length=200)
    truck_age = models.ForeignKey(TruckAge)
    selling_price = models.CharField(max_length=20, null= True)
    order_date = models.DateTimeField('Date Order was made', auto_now_add=True)
    created_date = models.DateTimeField('Date Order was made', auto_now_add=True)
    created_by = models.ForeignKey(User)
    modified_date = models.DateTimeField('Date record was modified',auto_now_add=True)
    modified_by = models.ForeignKey(User, related_name='%(app_label)s_%(class)s_related')
    status = models.CharField(max_length=1, choices=STATUS, default='A')
    order_status = models.CharField(max_length=1, choices=ORDER_STATUS, default='P')

# MOF-PRICE	UNIT PRICE EXW	UNIT PRICE + DUTIES+ VAT+EXTRA COSTS	DUTIES+VAT	MARGIN (%)	MARGIN P.U. (EUR)
# TOTAL MARGIN (EUR)	SELLING PRICE P.U.	TOTAL SELLING PRICE  	EXCHANGE RATE USED	VAT FROM MBG 	VAT FROM CUSTOMER
# VAT OUTGOING	PROFORMA	PROFORMA DATE	QSF 	QSF DATE	MOF 	MOF DATE	ORDERSTATUS	DATE LAST MODIFIED
