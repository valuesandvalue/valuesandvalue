# fbdata.participant

# PYTHON 
from datetime import timedelta

# DJANGO
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.utils.timezone import now

# DJANGO FACEBOOK
from django_facebook.models import FacebookProfile

# FBDATA
from .collation import collate_updates
from .fbids import (
    get_fbuser_from_djuser,
    load_user_friends
)
from .models import (
    UserAnalysis
)
                                
def setup_participants():
    users = User.objects.filter(is_active=True, is_staff=False, 
                                                useranalysis__isnull=True)
    for user in users:
        get_participant_profile(user)
        
def get_participants():
    return User.objects.filter(is_active=True, 
                            useranalysis__isnull=False,
                            useranalysis__consent=True)
    
def setup(user):
    fbuser = get_fbuser_from_djuser(user)
    load_user_friends(user)
    user_analysis = UserAnalysis.objects.create(user=user, fbuser=fbuser)
    
def get_participant_profile(user):
    user_analysis, created = UserAnalysis.objects.get_or_create(user=user)
    if created:
        user_analysis.fbuser = get_fbuser_from_djuser(user)
        load_user_friends(user)
        user_analysis.save()
    return user_analysis

def has_participant_consent(user):
    participant = get_participant_profile(user)
    return participant.consent
   
def update_participant_data(user, force=False, collate=False):
    participant = get_participant_profile(user)
    start_date = participant.end_time
    end_date = now()
    if not start_date:
        start_date = end_date - timedelta(days=settings.FBDATA_INITIAL_PERIOD)
    elif not force and end_date - start_date < settings.FBDATA_MIN_PERIOD:
        participant.status = UserAnalysis.STATUS_UNDERTIME
        participant.save()
        return (participant, None)
    data = collate_updates(user, start_date, end_date=end_date, collate=collate)
    if data:
        if not participant.start_time:
            participant.start_time = start_date
        participant.end_time = end_date
        participant.status = UserAnalysis.STATUS_SUCCESS
        participant.save()
    else:
        participant.status = UserAnalysis.STATUS_ERROR
        participant.save()
    return (participant, data)
    
        
