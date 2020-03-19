from django.conf.urls import url

from informacion.views import JsonAPIMediaObjects

urlpatterns = [
    url(
        r'^api/media_objects',
        JsonAPIMediaObjects.as_view(),
        name='media_objects'
    ),

]
