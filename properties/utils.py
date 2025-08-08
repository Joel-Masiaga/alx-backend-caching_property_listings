from django.core.cache import cache
from .models import Property
import logging
from django_redis import get_redis_connection
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)

def get_all_properties():
    properties = cache.get('all_properties')
    if properties is None:
        properties = list(Property.objects.all())
        cache.set('all_properties', properties, 3600)  # 1 hour
    return properties


def get_redis_cache_metrics():
    try:
        conn = get_redis_connection("default")
        info = conn.info("stats")
        keyspace_hits = info.get("keyspace_hits", 0)
        keyspace_misses = info.get("keyspace_misses", 0)
        total_requests = keyspace_hits + keyspace_misses

        hit_ratio = (keyspace_hits / total_requests) if total_requests > 0 else 0

        metrics = {
            "keyspace_hits": keyspace_hits,
            "keyspace_misses": keyspace_misses,
            "hit_ratio": round(hit_ratio, 2),
        }

        logger.info("Redis Cache Metrics: %s", metrics)
        return metrics

    except RedisError as e:
        logger.error("Failed to get Redis cache metrics: %s", e)
        return {
            "keyspace_hits": 0,
            "keyspace_misses": 0,
            "hit_ratio": 0,
        }
