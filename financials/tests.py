from django.test import TestCase
from django.contrib.auth.models import User
# Create your tests here.


from financials.utils import CalculateGains

g = CalculateGains(User.objects.get(pk=1))