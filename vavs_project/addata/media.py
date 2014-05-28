# addata.media

# PYTHON 
import os
from time import time
import urllib
from urlparse import urlparse

# DJANGO
from django.conf import settings

# PILLOW
from PIL import Image

from .models import (
    AdRecord,
    FBAdImage
)

_IMAGE_TYPES = [
    'image/gif', 
    'image/jpeg',
    'image/png',
]

_MEDIA_TYPES = [
    'application/x-shockwave-flash',
]

_DYNAMIC_TYPES = [
    'text/javascript',
    'text/javascript; charset=UTF-8',
    'text/html',
    'text/html; charset=UTF-8',
]

_CTYPE_EXTS = {
    'image/gif': '.gif',
    'image/jpeg': '.jpg',
    'image/png': '.png',
    'application/x-shockwave-flash': '.swf'
}

_FORMAT_EXTS = {
    'GIF': '.gif',
    'JPEG': '.jpg',
    'PNG': '.png'
}

_MEDIA_EXTS = ['.gif', '.jpg', '.png', '.swf']
  
def is_image_file(adrecord):
    return adrecord.content_type in _IMAGE_TYPES
    
def is_dynamic(adrecord):
    if adrecord.method == "POST" or adrecord.is_ajax:
        return True
    if adrecord.content_type in _DYNAMIC_TYPES:
        return True
    return False

def ext_from_ctype(ctype, default=''):
    return _CTYPE_EXTS.get(ctype, default)
    
def get_extension(url, ctype=None):
    ext = os.path.splitext(urlparse(url).path)[1]
    if not ext:
        return ext_from_ctype(ctype)
    else:
        return ext
    
def make_local_name():
    return str(int(time()*1000000))

def remove_download(filename):
    filepath = os.path.join(settings.VAVS_ROOT, 
                        settings.VAVS_DOWNLOAD_DIR, filename)
    os.remove(filepath)
    
def remove_thumb(filename):
    filepath = os.path.join(settings.VAVS_ROOT, 
                        settings.VAVS_THUMBNAILS_DIR, filename)
    os.remove(filepath)
    
def download_media(src, ctype=None):
    localname = make_local_name()
    dst = '%s%s' % (localname, get_extension(src))
    dstpath = os.path.join(settings.VAVS_ROOT, settings.VAVS_DOWNLOAD_DIR, dst)
    try:
         urllib.urlretrieve(src, dstpath)
    except Exception, e:
        print e
        return (localname, None)
    else:
        dst = verify_filename(dst)
        return (localname, dst)
        
def make_thumbnail(filename, localname):
    infile = os.path.join(settings.VAVS_ROOT,
                        settings.VAVS_DOWNLOAD_DIR, filename)
    thumbfile = '%s.jpg' % localname
    outfile = os.path.join(settings.MEDIA_ROOT,
                        settings.VAVS_THUMBNAILS_DIR, thumbfile)
    try:
        im = Image.open(infile)
        im.thumbnail(settings.VAVS_THUMBNAILS_SIZE)
        im.convert("RGB").save(outfile, "JPEG")
    except IOError, e:
        print e
        return None
    else:
        return thumbfile

def is_tracker_image(filename):
    infile = os.path.join(settings.VAVS_ROOT,
                        settings.VAVS_DOWNLOAD_DIR, filename)
    try:
        im = Image.open(infile)
    except IOError, e:
        print e
        return False
    return im.size[0] < 10 and im.size[1] < 10
        
def download_adrecord(adrecord):
    if is_dynamic(adrecord):
        adrecord.ad_type = AdRecord.TYPE_DYNAMIC
    elif is_image_file(adrecord):
        localname, dst = download_media(
                                adrecord.url, ctype=adrecord.content_type)
        if dst:
            adrecord.localfile = dst
            if is_tracker_image(dst):
                adrecord.ad_type = AdRecord.TYPE_TRACKER
                remove_download(dst)
            else:
                adrecord.ad_type = AdRecord.TYPE_AD
                thumbfile = make_thumbnail(dst, localname)
                if thumbfile:
                    adrecord.thumbfile = thumbfile
                    adrecord.status = AdRecord.STATUS_HAS_MEDIA
                else:
                    adrecord.status = AdRecord.STATUS_NO_THUMB
        else:
            adrecord.status = AdRecord.STATUS_NO_DOWNLOAD
    else:
        adrecord.status = AdRecord.STATUS_NO_MEDIA
    adrecord.save()
        
def download_fbadimage(fbadimage):
    localname, dst = download_media(fbadimage.url)
    if dst:
        fbadimage.localfile = dst
        thumbfile = make_thumbnail(dst, localname)
        if thumbfile:
            fbadimage.thumbfile = thumbfile
            fbadimage.status = FBAdImage.STATUS_HAS_MEDIA
        else:
            fbadimage.status = FBAdImage.STATUS_NO_THUMB
    else:
        fbadimage.status = FBAdImage.STATUS_NO_DOWNLOAD
    fbadimage.save()
  
def ext_from_format(filename):
    infile = os.path.join(settings.VAVS_ROOT,
                        settings.VAVS_DOWNLOAD_DIR, filename)
    try:
        im = Image.open(infile)
    except IOError, e:
        print e
        return ''
    return _FORMAT_EXTS.get(im.format, '')

def change_ext(filename, new_ext):
    name = os.path.splitext(filename)[0]
    return '%s%s' % (name, new_ext)

def rename_file(oldname, newname):
    oldfile = os.path.join(settings.VAVS_ROOT,
                        settings.VAVS_DOWNLOAD_DIR, oldname)
    newfile = os.path.join(settings.VAVS_ROOT,
                        settings.VAVS_DOWNLOAD_DIR, newname)
    os.rename(oldfile, newfile)
    
def verify_filename(filename):
    ext = os.path.splitext(filename)[1]
    if ext and ext in _MEDIA_EXTS:
        return filename
    else:
        new_ext = ext_from_format(filename)
        newname = change_ext(filename, new_ext)
        rename_file(filename, newname)
        return newname
        
