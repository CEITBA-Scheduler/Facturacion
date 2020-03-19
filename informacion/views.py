from django.http import JsonResponse
from django.views import View

from informacion.models import MediaObject


class JsonAPIMediaObjects(View):
    def get(self, request):

        media_objects = MediaObject.objects.all()

        filter = request.GET.get('filtro', None)

        if filter is not None:
            if filter == 'tv':
                media_objects = media_objects.filter(published_tv=True)
            elif filter == 'web':
                media_objects = media_objects.filter(published_web=True)
            elif filter == 'apuntes':
                media_objects = media_objects.filter(published_apuntes=True)

        response = []

        for media_object in media_objects:
            response += [{
                'url': media_object.media_file.url,
                'screen_time': media_object.screen_time,
            }]

        return JsonResponse(response, safe=False)
