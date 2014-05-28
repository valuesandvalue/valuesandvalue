"""
A list of the custom settings used on the site.
    
Many of the external libraries have their own settings, see library 
documentation for details.
"""

VAVS_EMAIL_FROM = 'address shown in reply-to field of emails'
VAVS_EMAIL_TO = 'list of staff addresses to send reports to'
VAVS_EMAIL_SURVEYS = 'address to send surveys to'
VAVS_ROOT = 'path to root directory of site' 
VAVS_DOWNLOAD_DIR = 'path to download directory'
VAVS_THUMBNAILS_DIR = 'path tothumbnail directory'
VAVS_THUMBNAILS_SIZE = 'size of thumbnails as tuple: (width, height)'
FBDATA_LIKES_LIMIT = 'maximum number of likes to show in listings'
FBDATA_INITIAL_PERIOD = 'number of days to backdate data collection to'
FBDATA_MIN_PERIOD = 'minimum duration, as timedelta, between updates'
