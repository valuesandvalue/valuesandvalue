# fbdata.fields

# DJANGO
from django.db import models
from django.utils import six

# SOUTH
from south.modelsinspector import add_introspection_rules

    
class IntegerListField(models.Field):
    description = "Integer List"

    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 120
        super(IntegerListField, self).__init__(*args, **kwargs)

    def db_type(self, connection):
        return 'char(%s)' % self.max_length

    def get_internal_type(self):
        return 'CharField'
        
    def to_python(self, value):
        if isinstance(value, basestring):
            return [int(s) for s in value.split(',') if s.isdigit()]
        elif isinstance(value, list):
            return value
        
    def get_prep_value(self, value):
        return ','.join([str(v) for v in value])
        
    def pre_save(self, model_instance, add):
        value = getattr(model_instance, self.attname)
        if not value and self.default:
            value = list(self.default)
            setattr(model_instance, self.attname, value)
        return value
    
    def get_prep_lookup(self, lookup_type, value):
        # We only handle 'exact' and 'in'. All others are errors.
        if lookup_type == 'exact':
            return self.get_prep_value(value)
        elif lookup_type == 'in':
            return [self.get_prep_value(v) for v in value]
        else:
            raise TypeError('Lookup type %r not supported.' % lookup_type)
        
    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)
        
    def formfield(self, **kwargs):
        defaults = {'max_length': self.max_length}
        defaults.update(kwargs)
        return super(IntegerListField, self).formfield(**defaults)

add_introspection_rules([
    (
        [IntegerListField], # Class(es) these apply to
        [],         # Positional arguments (not used)
        {},         # Keyword argument
    ),
], ["^fbdata\.fields\.IntegerListField"])   
