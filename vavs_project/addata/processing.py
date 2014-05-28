# addata.processing

# PYTHON
import json
import logging
from urlparse import urlparse

# DATEUTIL
import dateutil.parser
from dateutil import tz

# FBDATA
from fbdata.utils import (
    padded_date_range,
    timestamp_to_datetime
)

# ADDATA
from .models import (
    AdHourlyActivity,
    AdRecord,
    DomainName,
    FBAd,
    FBAdImage,
    FBAdLink,
    FBListing,
    FBSponsored,
    RawData
)

def get_tldextract():
    import tldextract
    return tldextract.TLDExtract(suffix_list_url=False)

def parse_datestr(datestr):
    d = dateutil.parser.parse(datestr)
    d = d.replace(tzinfo=tz.tzlocal())
    return d.astimezone(tz.tzutc())
    
def extract_domain(urlstr, default=''):
    parts = urlparse(urlstr)
    return parts.hostname or default
    
def make_domain(url, tldextractor, default=''):
    hostname = tldextractor(url).registered_domain or default
    domain, created = DomainName.objects.get_or_create(name=hostname)
    return domain
    
def data_to_adrecord(user, data, tldextractor):
    try:
        timestamp = parse_datestr(data[0])
    except ValueError, e:
        logger = logging.getLogger('vavs.tasks.analytics')
        logger.error("data_to_adrecord: %s, date: '%s'" % (user, data[0]))
        raise
    ref_url = data[1]
    url = data[2]
    try:
        adrecord, created = AdRecord.objects.get_or_create(
                                    _user_id = user.id,
                                    date = timestamp,
                                    ref_url = ref_url,
                                    url = url)
    except AdRecord.MultipleObjectsReturned, e:
        return AdRecord.objects.filter(
                                    _user_id = user.id,
                                    date = timestamp,
                                    ref_url = ref_url,
                                    url = url)[0]
    else:
        if created:
            adrecord.method = data[3]
            adrecord.content_type = data[4]
            adrecord.cookie_url = data[5]
            adrecord.is_ajax = data[6]
            adrecord._ref_domain_id = make_domain(ref_url, tldextractor).id
            adrecord._domain_id = make_domain(url, tldextractor).id
            adrecord.save()
        return adrecord

def make_fbadimage(url, tldextractor):
    domain = make_domain(url, tldextractor, default='facebook.com')
    obj, created = FBAdImage.objects.get_or_create(domain=domain, url=url)
    return obj
    
def make_fbadlink(url, tldextractor):
    domain = make_domain(url, tldextractor, default='facebook.com')
    obj, created = FBAdLink.objects.get_or_create(domain=domain, url=url)
    return obj
    
def data_to_fbad(user, data, tldextractor):  
    timestamp = timestamp_to_datetime(int(data[0])*0.001)
    adid = data[1]
    fbad, created = FBAd.objects.get_or_create(
                            user = user,
                            date = timestamp,
                            adid = adid)
    if created:
        fbad.text = data[2]
        fbad.title = data[3]
        images = data[4]
        links = data[5]
        for url in images:
            fbad.images.add(make_fbadimage(url, tldextractor))
        for url in links:
            fbad.links.add(make_fbadlink(url, tldextractor))
        fbad.save()
    return fbad
    
def data_to_fbsponsored(user, data, tldextractor):
    try: 
        timestamp = timestamp_to_datetime(float(data[0]))
    except ValueError:
        logger = logging.getLogger('vavs.tasks.analytics')
        logger.error("data_to_fbsponsored: %s, date: '%s', text: %s" % (
                                                        user, data[0], data[4]))
        raise
    title = data[5]
    fbsp, created = FBSponsored.objects.get_or_create(
                            user = user,
                            date = timestamp,
                            title = title)
    if created:
        fbsp.actor = data[1]
        fbsp.target = data[2]
        fbsp.type_id = data[3]
        fbsp.text = data[4]
        images = data[6]
        links = data[7]
        for url in images:
            fbsp.images.add(make_fbadimage(url, tldextractor))
        for url in links:
            fbsp.links.add(make_fbadlink(url, tldextractor))
        fbsp.save()
    return fbsp

def data_to_fblisting(user, data, tldextractor=None):
    try: 
        timestamp = timestamp_to_datetime(float(data['timestamp'])*0.001)
    except ValueError:
        logger = logging.getLogger('vavs.tasks.analytics')
        logger.error("data_to_fblisting: %s, date: '%s', text: %s" % (
                            user, data['timestamp'], data['list']))
        raise
    fblist, created = FBListing.objects.get_or_create(user=user, 
                                            date=timestamp)
    if created:
        fblist.listing = data['list']
        fblist.save()
    return fblist
        
def get_earliest_raw_data(status=RawData.STATUS_NEW):
    try:
        return RawData.objects.filter(status=status).earliest('created')
    except RawData.DoesNotExist:
        return None
        
def get_raw_data_slice(start, end, status=RawData.STATUS_NEW):
    return RawData.objects.filter(pk__gte=start, pk__lt=end, status=status)
    
_raw_data_handlers = {
    RawData.DATA_URLS: data_to_adrecord,
    RawData.DATA_FBADS: data_to_fbad,
    RawData.DATA_FB: data_to_fbsponsored,
    RawData.DATA_FBLISTING: data_to_fblisting
}

def process_raw_datatype(user, datatype, tldextractor=None):
    rdset = RawData.objects.filter(
            user=user, datatype=datatype, status=RawData.STATUS_NEW)
    return process_raw_data_set(rdset, tldextractor=tldextractor)
            
def process_raw_data(user, tldextractor=None):
    rdset = RawData.objects.filter(user=user, status=RawData.STATUS_NEW)
    return process_raw_data_set(rdset, tldextractor=tldextractor)
    
def process_raw_data_set(rdset, tldextractor=None):
    proc_ok = []
    proc_error = []
    proc_unproc = []
    tldextractor = tldextractor or get_tldextract()
    for rd in rdset:
        _proc_rd(rd, proc_ok, proc_error, proc_unproc, tldextractor)
    return (proc_ok, proc_error, proc_unproc)

def _proc_rd(rd, proc_ok, proc_error, proc_unproc, tldextractor):
    try:
        jdata = json.loads(rd.data)
    except Exception, e:
        rd.error = unicode(e)
        rd.status = RawData.STATUS_ERROR
        rd.save()
        proc_error.append(rd)
    else:
        func = _raw_data_handlers.get(rd.datatype, None)
        if func:
            if isinstance(jdata, dict) or not isinstance(
                                    jdata[0], (tuple, list, set)):
                try:
                    func(rd.user, jdata, tldextractor)
                except Exception, e:
                    rd.error = unicode(e)
                    rd.status = RawData.STATUS_ERROR
                    rd.save()
                    proc_error.append(rd)
                    return
            else:
                for data in jdata:
                    try:
                        func(rd.user, data, tldextractor)
                    except Exception, e:
                        rd.error = unicode(e)
                        rd.status = RawData.STATUS_ERROR
                        rd.save()
                        proc_error.append(rd)
                        return
            rd.status = RawData.STATUS_DONE
            proc_ok.append(rd)
        else:
            rd.status = RawData.STATUS_UNPROCESSED
            proc_unproc.append(rd)
    finally:
        rd.save()
            
def purge_raw_data(user, datatype, status=RawData.STATUS_DONE):
    RawData.objects.filter(user=user, datatype=datatype, status=status).delete()
    
def report_raw_data_errors():
    pass

