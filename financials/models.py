from __future__ import unicode_literals

from django.db import models
from redwood import settings
from django.utils.translation import ugettext_lazy as _
from django.core.validators import RegexValidator

# Create your models here.
USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')

class CompanyMaster(models.Model):
	scrip_code = models.CharField(max_length=255, blank=True, null=True)
	scrip_name = models.CharField(max_length=255, blank=True, null=True)
	yahoo_code = models.CharField(max_length=255, blank=True, null=True)

	def __str__(self):
		return '%s %s' % (self.scrip_code, self.scrip_code)

class StockValues(models.Model):
	scrip_code = models.CharField(max_length=255, blank=True, null=True)
	date = models.DateTimeField(_("Date"), blank=True, null=True)
	open_value = models.FloatField(blank=True, null=True, default=0.0)
	high_value = models.FloatField(blank=True, null=True, default=0.0)
	low_value = models.FloatField(blank=True, null=True, default=0.0)
	close_value = models.FloatField(blank=True, null=True, default=0.0)
	volume = models.FloatField(blank=True, null=True, default=0.0)


class Transactions(models.Model):
	scrip_code = models.CharField(max_length=255, blank=True, null=True)
	user = models.ForeignKey(USER_MODEL)
	date_created = models.DateTimeField(_("Created Date"), blank=True, null=True)
	date_updated = models.DateTimeField(_("updated Date"),auto_now_add = True ,blank=True, null=True)
	quantity = models.CharField(max_length=10, blank=True, null=True)
	price = models.CharField(max_length=255, blank=True, null=True)
	amount = models.CharField(max_length=255, blank=True, null=True)
	transaction_type = models.CharField(max_length=255, blank=True, null=True)


class CustomerProfile(models.Model):
	user = models.ForeignKey(USER_MODEL)
	full_name = models.CharField(max_length=255, blank=True, null=True)
	phone_regex = RegexValidator(
		regex=r"^\d{10}$", message="Only 10 digits are allowed. Invalid Number")
	phone_number = models.CharField(
		_("Phone Number"), max_length=10, validators=[phone_regex])
	date_joined = models.DateTimeField(_("Joined Date"), blank=True, null=True)
	commited_amount = models.CharField(max_length=255, blank=True, null=True)
	total_amount = models.CharField(max_length=255, blank=True, null=True)
	client_code = models.CharField(max_length=255, blank=True, null=True)
	broker = models.CharField(max_length=255, blank=True, null=True)
	broker_email = models.CharField(max_length=255, blank=True, null=True)
	broker_phone = models.CharField(
		_("Broker Number"), max_length=10, validators=[phone_regex])
	pan = models.CharField(max_length=255, blank=True, null=True)
	fixed_fee_cost = models.CharField(max_length=255, blank=True, null=True)
	performance_cost = models.CharField(max_length=255, blank=True, null=True)
	fee_structure = models.CharField(max_length=255, blank=True, null=True)
	entry_load = models.CharField(max_length=255, blank=True, null=True)
	exit_load = models.CharField(max_length=255, blank=True, null=True)
