from . import BaseStore

class DjangoStore(BaseStore):
    django_klass = None  # can specify as class level variable or in constructor-- whatever you want

    def __init__(self, django_klass=None):
        super(DjangoStore, self).__init__()
        self.django_klass = django_klass or self.__class__.django_klass

    def _all(self): 
        return self.django_klass.objects.all()
    
    def _single_create(self, dobj):
        obj = self.django_klass(**dobj)
        obj.save()
        return obj

    def _single_update(self, obj, dchanges):
        for k,v in dchanges.iteritems(): setattr(obj, k, v)
        obj.save()
        return obj

    def _single_delete(self, obj):
        obj.delete()
        return obj
