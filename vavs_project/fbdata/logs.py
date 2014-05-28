# fbdata.logs

# PYTHON
import os
import shutil

# LOCKFILE
from lockfile import LockFile

# DJANGO
from django.conf import settings
from django.core.mail import send_mail
from django.utils.timezone import now

def touch(fname, times=None):
    with open(fname, 'a'):
        os.utime(fname, times)

def rotate_log(log_name):
    logfile = os.path.join(settings.LOG_ROOT, '%s.log' % log_name)
    if os.path.exists(logfile) and os.path.isfile(logfile):
        logarchive = os.path.join(settings.LOG_ROOT, 
            '%s_%s.log' % (log_name, now().strftime('%Y-%m-%d_%H-%M-%S')))
        with open(logfile, 'r') as f:
            message = f.read()
        with LockFile(logfile) as lock: 
            shutil.copy2(logfile, logarchive)
            with open(logfile, 'w') as f:
                f.write('')
        if not message:
            message = "no data in logfile"
        send_mail('VAVS %s' % log_name, message, settings.VAVS_EMAIL_FROM,
                            ['simon@lipparosa.org'], fail_silently=False)
        
