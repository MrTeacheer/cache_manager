from django.core.cache import cache
from rest_framework.response import Response
from . import cache_manager
from django.db import models



class RedisCacheManagerWithLan(cache_manager.RedisCacheManager):

    def save_to_cache(self, instance):
        cache_key = self.get_cache_key(instance.pk)
        data = self.get_filtred_data(instance)
        cache.set(cache_key, data,timeout=None)

    def get_filtred_data(self,instance):
        data = {'translation': {}}
        for lan in ('ru', 'en', 'ky'):
            data['translation'][lan] = {}
        for field in instance._meta.fields:
            if any(f'_{lan}' in field.name for lan in ('ru', 'en', 'ky')):
                for lan in ('ru', 'en', 'ky'):
                    if f'_{lan}' in field.name:
                        data['translation'][lan][field.name[:-3]] = getattr(instance, field.name)
            elif isinstance(field, models.URLField):
                url_field = getattr(instance, field.name)
                data[field.name] = url_field if url_field else None
            elif isinstance(field,models.ImageField):
                data[field.name] = getattr(instance,field.name).url

            elif not isinstance(field,models.CharField) and not isinstance(field,models.TextField) and not isinstance(field,models.BigAutoField):
                data[field.name] = getattr(instance, field.name)
        return data

    def list_view(self,queryset,serializer,lan):
        cache_data = self.get_all_from_cache()
        if cache_data:
            data = [
            {**item['translation'][lan], **{key: value for key, value in item.items() if key != 'translation'}} for item in cache_data]
            return Response(data)
        serialized = serializer(queryset, many=True)
        return Response(serialized.data)
