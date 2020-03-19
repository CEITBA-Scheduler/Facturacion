from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse
from django.views import View
from datetime import date

from constance import config

from bar.models import Menu, BarProduct, MenuDescription

if not settings.DEBUG:
    from datadog import statsd

MENU_V1_CACHE_KEY = "cached_menu_v1_response"
MENU_V2_CACHE_KEY = "cached_menu_v2_response"
PRODUCT_CACHE_KEY = 'cached_productlist_response'


class JsonAPIMenuViewV1(View):
    def get(self, request):

        cached_response = cache.get(MENU_V1_CACHE_KEY)

        if cached_response is None:
            descriptions = MenuDescription.objects \
                .filter(for_date__gte=date.today()) \
                .order_by('-for_date') \
                .select_related('menu') \
                .all()

            response = []

            for i, description in enumerate(descriptions):
                response += [{
                    'menuDate': description.for_date,
                    'comments': description.description,
                    'description': description.menu.name,
                    'price': description.menu.price,
                    # 'order': description.menu.order,
                    'CampusID': description.menu.sede,
                }]

                cache.set(MENU_V1_CACHE_KEY, response, config.BAR_CACHE_TIMEOUT)
        else:
            response = cached_response

        if not settings.DEBUG:
            statsd.increment("ceitba.bar.api.menu.v1.hit")

        return JsonResponse(response, safe=False)


class JsonAPIMenuViewV2(View):
    def get(self, request):

        cached_response = cache.get(MENU_V2_CACHE_KEY)

        if cached_response is None:
            menues = Menu.objects.all()
            response = {}

            for menu in menues:

                menu_descriptions = []
                descriptions = menu.menudescription_set.filter(for_date__gte=date.today()).order_by('-for_date').all()

                for i, description in enumerate(descriptions):
                    menu_descriptions += [{
                        'for_date': description.for_date,
                        'description': description.description,
                    }]

                response[menu.name] = {
                    'name': menu.name,
                    'price': menu.price,
                    'order': menu.order,
                    'sede': menu.sede,
                    'descriptions': menu_descriptions
                }

                cache.set(MENU_V2_CACHE_KEY, response, config.BAR_CACHE_TIMEOUT)
        else:
            response = cached_response

        if not settings.DEBUG:
            statsd.increment("ceitba.bar.api.menu.v2.hit")

        return JsonResponse(response)


class JsonAPIProductView(View):
    def get(self, request):

        cached_response = cache.get(PRODUCT_CACHE_KEY)

        if cached_response is None:

            products = BarProduct.objects.filter(important=True)

            response = []

            for product in products:
                response += [{
                    'name': product.name,
                    'price': product.price
                }]

            cache.set(PRODUCT_CACHE_KEY, response, config.BAR_CACHE_TIMEOUT)

        else:
            response = cached_response

        if not settings.DEBUG:
            statsd.increment("ceitba.bar.api.products.hit")

        return JsonResponse(response, safe=False)
