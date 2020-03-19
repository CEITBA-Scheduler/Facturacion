from django.conf import settings
from django.conf.urls import url, include
from django.views.i18n import javascript_catalog
from django.views.static import serve

from facturacion.admin.FacturacionAdmin import facturacionadmin

js_info_dict = {
    'packages': ('facturacion',),
}

urlpatterns = [
    url(r'^select2/', include('django_select2.urls')),
    url(r'^jsi18n/$', javascript_catalog, js_info_dict, name='javascript-catalog'),

    url(r'^bar/', include('bar.urls', namespace='bar_api')),

    url(r'^informacion/', include('informacion.urls', namespace='informacion_api')),

    url(r'^', facturacionadmin.urls)
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
                      url(r'^__debug__/', include(debug_toolbar.urls)),
                      url(r'^media/(?P<path>.*)$', serve, {
                          'document_root': settings.MEDIA_ROOT,
                      }),
                  ] + urlpatterns
