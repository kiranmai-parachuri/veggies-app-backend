import django;
django.setup()

from veggies_service.service_apis_handler import order_handler

from veggies_service.db.veggies_models.models import Slot, User
from unittest import TestCase

from datetime import datetime, timedelta
today = datetime.now()
todays_day = today.weekday()

# test_cases = {0: today+}

class TestOrder(TestCase):
    def test_get_delivery_dates_for_slot_return_slots_for_0(self):
        s, t = Slot.objects.get_or_create(day=2, created_by=User.objects.first())
        print order_handler.get_delivery_dates_for_slot(s, 4)
