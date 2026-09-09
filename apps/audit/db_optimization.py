# HealthSphere Enterprise Query Optimization & Indexing Guidelines
from django.db import models

class OptimizedQueryManager(models.Manager):
    def select_essentials(self, *relations):
        return self.get_queryset().select_related(*relations)
        
    def prefetch_essentials(self, *relations):
        return self.get_queryset().prefetch_related(*relations)

def analyze_query_performance(qs):
    import time
    start = time.perf_counter()
    count = qs.count()
    duration = (time.perf_counter() - start) * 1000
    return {"count": count, "duration_ms": round(duration, 2)}
