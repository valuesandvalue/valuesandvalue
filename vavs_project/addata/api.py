# addata.api

# DJANGO
from django.contrib.auth import get_user_model

# TASTYPIE
from tastypie import fields
from tastypie.api import Api
from tastypie.authentication import ApiKeyAuthentication
from tastypie.authorization import (
    Authorization,
    DjangoAuthorization,
    ReadOnlyAuthorization
)
from tastypie.exceptions import Unauthorized
from tastypie.models import ApiKey
from tastypie.resources import ModelResource

# FBDATA
from fbdata.participant import has_participant_consent

# ADDATA
from .models import ( 
    DomainName,
    FBSponsored,
    FBAd,
    RawData
)

###############
# AUTHORIZATION
###############
class LoginAuthorization(ReadOnlyAuthorization):
    def read_list(self, object_list, bundle):
        return object_list.filter(id=bundle.request.user.id)

    def read_detail(self, object_list, bundle):
        return bundle.obj.id == bundle.request.user.id

class UserObjectsOnlyAuthorization(Authorization):
    def read_list(self, object_list, bundle):
        return object_list.filter(user=bundle.request.user)

    def read_detail(self, object_list, bundle):
        return bundle.obj.user == bundle.request.user

    def create_list(self, object_list, bundle):
        return object_list

    def create_detail(self, object_list, bundle):
        return bundle.obj.user == bundle.request.user

    def update_list(self, object_list, bundle):
        allowed = []
        for obj in object_list:
            if obj.user == bundle.request.user:
                allowed.append(obj)
        return allowed

    def update_detail(self, object_list, bundle):
        return bundle.obj.user == bundle.request.user

    def delete_list(self, object_list, bundle):
        raise Unauthorized("Sorry, no deletes.")

    def delete_detail(self, object_list, bundle):
        raise Unauthorized("Sorry, no deletes.")

###############
# API KEY
###############
def get_api_key(user):
    if has_participant_consent(user):
        apikey, created = ApiKey.objects.get_or_create(user=user)
        if created:
            apikey.save()
        return apikey.key
    return None
    
def reset_api_key(user):
    if has_participant_consent(user):
        apikey, created = ApiKey.objects.get_or_create(user=user)
        if created:
            apikey.save()
        else:
            apikey.delete()
            apikey = ApiKey.objects.create(user=user)
        return apikey.key
    return None
    
###############
# RESOURCES
###############
class UserResource(ModelResource):
    class Meta:
        queryset = get_user_model().objects.all()
        resource_name = 'user'
        allowed_methods = ['get']
        fields = ['username']
        authorization = DjangoAuthorization()
        authentication = ApiKeyAuthentication()
        
class LoginResource(ModelResource):
    class Meta:
        queryset = get_user_model().objects.all()
        resource_name = 'login'
        allowed_methods = ['get']
        fields = ['username']
        authorization = LoginAuthorization()
        authentication = ApiKeyAuthentication()
        
    def apply_authorization_limits(self, request, object_list):
        return object_list.filter(id=request.user.id)
                
class URLRecordResource(ModelResource):
    user = fields.ForeignKey(UserResource, 'user')
    
    class Meta:
        queryset = RawData.objects.filter(datatype=RawData.DATA_URLS)
        allowed_methods = ['post', 'patch', 'put']
        resource_name = 'urlrecords'
        excludes = ['user']
        authorization = UserObjectsOnlyAuthorization()
        authentication = ApiKeyAuthentication()
        
    def apply_authorization_limits(self, request, object_list):
        return object_list.filter(user=request.user)
        
    def obj_create(self, bundle, **kwargs):
        return super(URLRecordResource, self).obj_create(bundle, 
                            user=bundle.request.user,
                            datatype=RawData.DATA_URLS)

class FBSponsoredResource(ModelResource):
    user = fields.ForeignKey(UserResource, 'user')
    
    class Meta:
        queryset = RawData.objects.filter(datatype=RawData.DATA_FB)
        allowed_methods = ['post', 'patch', 'put']
        resource_name = 'fbsponsored'
        excludes = ['user']
        authorization = UserObjectsOnlyAuthorization()
        authentication = ApiKeyAuthentication()
        
    def apply_authorization_limits(self, request, object_list):
        return object_list.filter(user=request.user)
        
    def obj_create(self, bundle, **kwargs):
        return super(FBSponsoredResource, self).obj_create(bundle, 
                            user=bundle.request.user,
                            datatype=RawData.DATA_FB)  
        
class FBAdResource(ModelResource):
    user = fields.ForeignKey(UserResource, 'user')
    
    class Meta:
        queryset = RawData.objects.filter(datatype=RawData.DATA_FBADS)
        allowed_methods = ['post', 'patch', 'put']
        resource_name = 'fbad'
        excludes = ['user']
        authorization = UserObjectsOnlyAuthorization()
        authentication = ApiKeyAuthentication()
        
    def apply_authorization_limits(self, request, object_list):
        return object_list.filter(user=request.user)
        
    def obj_create(self, bundle, **kwargs):
        return super(FBAdResource, self).obj_create(bundle, 
                            user=bundle.request.user,
                            datatype=RawData.DATA_FBADS)  
                            
class FBListingResource(ModelResource):
    user = fields.ForeignKey(UserResource, 'user')
    
    class Meta:
        queryset = RawData.objects.filter(datatype=RawData.DATA_FBLISTING)
        allowed_methods = ['post', 'patch', 'put']
        resource_name = 'fblisting'
        excludes = ['user']
        authorization = UserObjectsOnlyAuthorization()
        authentication = ApiKeyAuthentication()
        
    def apply_authorization_limits(self, request, object_list):
        return object_list.filter(user=request.user)
        
    def obj_create(self, bundle, **kwargs):
        return super(FBListingResource, self).obj_create(bundle, 
                            user=bundle.request.user,
                            datatype=RawData.DATA_FBLISTING)  
                            
###############
# API URLS
###############
def get_api():
    addata_api = Api(api_name='v1')
    addata_api.register(LoginResource())
    addata_api.register(URLRecordResource())
    addata_api.register(FBAdResource())
    addata_api.register(FBSponsoredResource()) 
    addata_api.register(FBListingResource()) 
    return addata_api           
