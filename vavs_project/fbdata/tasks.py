# fbdata.tasks

# PYTHON
import logging

# DJANGO
from django.conf import settings
from django.utils.timezone import now

# CELERY
from celery import task

# FBDATA
from .fbids import (
    batch_unnamed,
    get_facebook_graph,
    get_unnamed_fbids
)
from .logs import rotate_log
from .participant import (
    get_participants,
    setup_participants,
    update_participant_data
)

_UNNAMED_SLICE = 100

@task.task(ignore_result=False, name='fbdata.tasks.update_participants')
def update_participants():
    logger = logging.getLogger('vavs.tasks.analytics')
    lines = ['update_participants: %s' % now()]
    setup_participants()
    participants = get_participants()
    for user in participants:
        p, d = update_participant_data(user)
        lines.append('%s status: %s' % (user.username, p.status_str()))
    message = '\n'.join(lines)
    logger.info(message)
                    
@task.task(ignore_result=False, name='fbdata.tasks.update_names')
def update_names():
    logger = logging.getLogger('vavs.tasks.analytics')
    if get_unnamed_fbids().count():
        lines = ['update_names: %s' % now()]
        participants = get_participants()
        for user in participants:
            graph = get_facebook_graph(user)
            unnamed = get_unnamed_fbids()[:_UNNAMED_SLICE]
            if unnamed:
                named, errors = batch_unnamed(graph, unnamed)
                lines.append('%s named: %d, errors: %d' % (
                                    user.username, len(named), len(errors)))
        lines.append('unnamed: %d' % get_unnamed_fbids().count()) 
        message = '\n'.join(lines)
        logger.info(message)

@task.task(ignore_result=False, name='fbdata.tasks.rotate_logs')
def rotate_logs():
    rotate_log('vavs_info')
    rotate_log('vavs_media')
    rotate_log('celeryd_err')
