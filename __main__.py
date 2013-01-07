from bitdeli.widgets import set_theme, Description, Title
from bitdeli.chain import Profiles
from collections import Counter, defaultdict
from datetime import datetime, timedelta
import GeoIP

set_theme('eighties')

TIMELINE_DAYS = 30 
TFORMAT = '%Y-%m-%d'
               
geoip = GeoIP.open('/usr/share/geoip/GeoLiteCity.dat', GeoIP.GEOIP_STANDARD)

text = {'window': TIMELINE_DAYS}

def countries(profiles):
    stats = Counter()
    for profile in profiles:
        country = geoip.record_by_addr(profile.uid)
        if country:
            stats[country['country_code']] += 1
    yield stats

def activity(profiles):
    limit = datetime.now() - timedelta(days=TIMELINE_DAYS)
    limit_str = limit.strftime(TFORMAT)
        
    def recent_days(visits):
        for visit in visits:
            day = visit['tstamp'].split('T')[0]
            if day >= limit_str:
                yield day
    
    def timeline(stats):
        for i in range(TIMELINE_DAYS + 1):
            day = (limit + timedelta(days=i)).strftime(TFORMAT)
            yield day, stats[day]

    def popularity(repos):
        for repo, visits in repos.iteritems():
            yield sum(visits.itervalues()), repo
                
    repos = defaultdict(Counter)
    for profile in profiles:
        for repo, visits in profile['repos'].iteritems():
            repos[repo].update(frozenset(recent_days(visits)))

    if repos:
        pop = list(popularity(repos))
        text['popular'] = max(pop)
        text['total'] = sum(visits for visits, repo in pop)
        
        yield {'type': 'text',
               'size': (12, 1),
               'head': 'Daily Unique Visitors'}
        
        for repo, stats in sorted(repos.iteritems()):
            yield {'type': 'line',
                   'label': repo.split('/')[1],
                   'data': list(timeline(stats)),
                   'size': (6, 2)}
    else:
        yield {'type': 'text',
               'size': (12, 1),
               'color': 3,
               'head': 'Bummer! No data yet'}
        yield {'type': 'text',
               'size': (12, 2),
               'text': """It may take an hour for the first
                          visits to appear after you have added the badge
                          for the first time."""}
                
Profiles().map(activity).show()    

Profiles().map(countries).show('map',
                               label='Visitors',
                               size=(12, 4))

if total in text:
    Title("Repos have {total} daily unique visitors in total over the last "
          "{window} days",
          text)
    Description("The most popular repository is *{popular[1]}* with "
                "{popular[0]} visitors.",
                text)
else:
    Title("First badge added!")
    Description("It takes about an hour for the real data to start flowing in.")
