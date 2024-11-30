from django.core.cache import cache
from rest_framework.response import Response


class RedisCacheManager:
    def __init__(self, model):
       self.model = model

    def get_cache_key(self, instance_id):
        return f"{self.model.__name__.lower()}:{instance_id}"

    def save_to_cache(self, instance,serializer):
        cache_key = self.get_cache_key(instance.pk)
        data = serializer(instance).data
        cache.set(cache_key, data,timeout=None)

    def delete_from_cache(self, instance_id):
        cache_key = self.get_cache_key(instance_id)
        cache.delete(cache_key)

    def get_all_from_cache(self):
        keys = cache.keys(f"{self.model.__name__.lower()}:*")
        if not keys:
            return None
        data =[cache.get(key) for key in keys]
        return data

    def list_view(self,queryset,serializer):
        cache_data = self.get_all_from_cache()
        if cache_data:
            return Response(cache_data)
        serialized = serializer(queryset, many=True)
        return Response(serialized.data)