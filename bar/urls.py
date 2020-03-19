from django.conf.urls import url

from bar.views import JsonAPIMenuViewV1, JsonAPIProductView, JsonAPIMenuViewV2

urlpatterns = [
    url(
        r'^api/menu/v1',
        JsonAPIMenuViewV1.as_view(),
        name='menu_api_v2'
    ),

    url(
        r'^api/menu/v2',
        JsonAPIMenuViewV2.as_view(),
        name='menu_api_v2'
    ),

    url(
        r'^api/products',
        JsonAPIProductView.as_view(),
        name='product_api'
    ),

]
