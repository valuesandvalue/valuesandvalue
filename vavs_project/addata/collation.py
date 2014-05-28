# addata.collation

# ADDATA
from .models import (
    AdRecord,
    FBAd,
    FBSponsored
)

def collate_ads(user, start_date, end_date):
    return None
    
def collate_fbads(user, start_date, end_date):
    return None
    
def collate_fbsps(user, start_date, end_date):
    return None

def collate_addata(user, start_date, end_date=None):
    end_date = end_date or start_date
    fbads = collate_fbads(user, start_date, end_date)
    fbsps = collate_fbsps(user, start_date, end_date)
    ads = collate_ads(user, start_date, end_date)
    return {
            'fbads': fbads,
            'fbsps': fbsps,
            'ads': ads
        }
