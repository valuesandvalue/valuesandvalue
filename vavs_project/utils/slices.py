# utils.slices

# UTILS
from .models import IndexSlice

def get_index_slice(name, start=None):
    index_slice, created = IndexSlice.objects.get_or_create(name=name)
    if start != None:
        index_slice.index = start
        index_slice.save()
    return index_slice

