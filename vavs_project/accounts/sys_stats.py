# accounts.sys_stats

# PYTHON
import os
import subprocess

# DJANGO
from django.conf import settings
from django.db import connection

def get_disc_usage():
    lines = []
    process = subprocess.Popen(
                    ['df', '-h'], shell=False, stdout=subprocess.PIPE)
    result = process.communicate()
    lines.append('Total disc usage:')
    lines.append(result[0])
    # downloads
    dirpath = os.path.join(settings.VAVS_ROOT, 'downloads')
    process = subprocess.Popen(
                    ['du', '-h', dirpath], 
                    shell=False, stdout=subprocess.PIPE)
    result = process.communicate()
    lines.append('Downloads:')
    lines.append(result[0])
    # media
    process = subprocess.Popen(
                    ['du', '-ch', settings.MEDIA_ROOT], 
                    shell=False, stdout=subprocess.PIPE)
    result = process.communicate()
    lines.append('Media:')
    lines.append(result[0])
    return lines

def get_db_name():
    return settings.DATABASES['default']['NAME']
  
def get_db_size():
    cursor = connection.cursor()
    dbname = cursor.db.settings_dict['NAME']
    cursor.execute("SELECT pg_size_pretty(pg_database_size(%s))", [dbname])
    row = cursor.fetchone()
    if row:
        return row[0]
    else:
        return 'no size'
