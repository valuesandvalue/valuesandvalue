# addata.tasks

# PYTHON
from datetime import timedelta
import logging

# DJANGO
from django.conf import settings
from django.utils.timezone import now

# CELERY
from celery import task

# UTILS
from utils.slices import get_index_slice

# FBDATA
from fbdata.participant import get_participants
from fbdata.utils import padded_date_range

# ADDATA
from .activity import process_all_hourly_activity
from .processing import (
    get_earliest_raw_data,
    get_raw_data_slice,
    get_tldextract,
    process_raw_data,
    process_raw_data_set
)
from .media import (
    download_adrecord,
    download_fbadimage
)
from .models import (
    AdRecord,
    FBAdImage,
    RawData
)

_RD_SLICE = 200
_AR_SLICE = 100
_FBAD_SLICE = 100

@task.task(ignore_result=False, name='addata.tasks.async_process_raw_data')
def async_process_raw_data():
    logger = logging.getLogger('vavs.tasks.analytics')
    earliest = get_earliest_raw_data()
    if not earliest:
        return
    start = earliest.pk
    end = start + _RD_SLICE
    start_time = now()
    tldextractor = get_tldextract()
    rdset = get_raw_data_slice(start, end)
    ok, error, unproc = process_raw_data_set(rdset, tldextractor=tldextractor)
    end_time = now()
    lines = ['async_process_raw_data: %s to %s' % (start, end)]
    lines.append('time: %s duration: %s' % (start_time, end_time-start_time))
    lines.append('processed OK: %d ERRORS: %d' % (len(ok), len(error)))
    lines.append('unprocessed: %d' % len(unproc))
    message = '\n'.join(lines)
    logger.info(message)

@task.task(ignore_result=False, name='addata.tasks.async_purge_raw_data')
def async_purge_raw_data():
    logger = logging.getLogger('vavs.tasks.analytics')
    cutoff = now() - timedelta(days=2)
    RawData.objects.filter(created__lte=cutoff, 
                    status=RawData.STATUS_DONE).delete()
    logger.info('async_purge_raw_data')
                    
@task(ignore_result=True, name='addata.tasks.aysnc_download_adrecord_media')
def aysnc_download_adrecord_media():
    logger = logging.getLogger('vavs.tasks.media')
    try:
        earliest = AdRecord.objects.filter(
                                status=FBAdImage.STATUS_NEW).earliest('id')
    except AdRecord.DoesNotExist:
        return
    index = earliest.id
    adrecords = AdRecord.objects.filter(id__range=(index, index+_AR_SLICE),
                        status=AdRecord.STATUS_NEW)
    lines = ['aysnc_download_adrecord_media: %d %d, %s' % (index, 
                                                     adrecords.count(), now())]
    for adrecord in adrecords:
        download_adrecord(adrecord)
        lines.append("AdRecord %d %s %s" % (adrecord.id, adrecord.status_str(),
                                    adrecord.content_type))
    message = '\n'.join(lines)
    logger.info(message)
    
@task(ignore_result=True, name='addata.tasks.aysnc_download_fbadimage_media')
def aysnc_download_fbadimage_media():
    logger = logging.getLogger('vavs.tasks.media')
    try:
        earliest = FBAdImage.objects.filter(
                                status=FBAdImage.STATUS_NEW).earliest('id')
    except FBAdImage.DoesNotExist:
        return
    index = earliest.id
    fbadimages = FBAdImage.objects.filter(id__range=(index, index+_FBAD_SLICE),
                        status=FBAdImage.STATUS_NEW)
    lines = ['aysnc_download_fbadimage_media: %d %d, %s' % (index, 
                                                     fbadimages.count(), now())]
    for fbadimage in fbadimages:
        if len(fbadimage.url) > 1:
            download_fbadimage(fbadimage)
            lines.append("FBAdImage %d %s" % (
                                        fbadimage.id, fbadimage.status_str()))
        else:
            lines.append("FBAdImage %d no URL, deleted" % fbadimage.id)
            fbadimage.delete()
    message = '\n'.join(lines)
    logger.info(message) 
                    
@task.task(ignore_result=False, 
                name='addata.tasks.aysnc_update_hourly_activity')
def aysnc_update_hourly_activity():
    logger = logging.getLogger('vavs.tasks.analytics')
    end = now()
    start = end - timedelta(days=1)
    lines = ['aysnc_update_hourly_activity: %s' % end]
    lines.append('Date: %s (%s - %s)' % (end.date(), start, end))
    participants = get_participants()
    for user in participants:
        activities = process_all_hourly_activity(user, start, end)
        lines.append('%s activities' % user.username)
        lines.append('\tads:\t%d' % len(activities['ad_activities']))
        lines.append('\tfbsp:\t%d' % len(activities['fbsp_activities']))
        lines.append('\tfbad:\t%d' % len(activities['fbad_activities']))
    message = '\n'.join(lines)
    logger.info(message)
