# accounts.tasks

# PYTHON
from datetime import timedelta
import logging

# DJANGO
from django.contrib.auth.models import User
from django.utils.timezone import now

# CELERY
from celery import task

# ACCOUNTS
from .sys_stats import (
    get_db_size,
    get_disc_usage
)

@task.task(ignore_result=False, 
        name='accounts.tasks.purge_nonconsenting_participants')
def purge_nonconsenting_participants():
    logger = logging.getLogger('vavs.tasks.analytics')
    cutoff = now() - timedelta(days=7)
    users = User.objects.filter(is_staff=False, useranalysis__isnull=False,
                            useranalysis__consent=False)
    if users:
        logger.info('Deleting expired new users: %d' % users.count())
        users.delete()
    else:
        logger.info('No expired new users')
        
@task.task(ignore_result=False, name='accounts.tasks.disc_usage')
def disc_usage():
    logger = logging.getLogger('vavs.tasks.analytics')
    logger.info('\n'.join(get_disc_usage()))
    logger.info('DB usage: %s' % get_db_size())
