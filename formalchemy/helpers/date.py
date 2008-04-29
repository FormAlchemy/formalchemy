"""Date/Time Helpers"""
# Last synced with Rails copy at Revision 6080 on Feb 8th, 2007.
# Note that the select_ tags are purposely not ported as they're very totally useless
# and inefficient beyond comprehension.

from datetime import datetime
import time

DEFAULT_PREFIX = 'date'

def distance_of_time_in_words(from_time, to_time=0, include_seconds=False):
    """
    Reports the approximate distance in time between two datetime objects or
    integers as seconds.

    Set ``include_seconds`` to True for more more detailed approximations when
    distance < 1 min, 29 secs

    Distances are reported based on the following table:

    0 <-> 29 secs                                                           => less than a minute
    30 secs <-> 1 min, 29 secs                                              => 1 minute
    1 min, 30 secs <-> 44 mins, 29 secs                                     => [2..44] minutes
    44 mins, 30 secs <-> 89 mins, 29 secs                                   => about 1 hour
    89 mins, 29 secs <-> 23 hrs, 59 mins, 29 secs                           => about [2..24] hours
    23 hrs, 59 mins, 29 secs <-> 47 hrs, 59 mins, 29 secs                   => 1 day
    47 hrs, 59 mins, 29 secs <-> 29 days, 23 hrs, 59 mins, 29 secs          => [2..29] days
    29 days, 23 hrs, 59 mins, 30 secs <-> 59 days, 23 hrs, 59 mins, 29 secs => about 1 month
    59 days, 23 hrs, 59 mins, 30 secs <-> 1 yr minus 31 secs                => [2..12] months
    1 yr minus 30 secs <-> 2 yrs minus 31 secs                              => about 1 year
    2 yrs minus 30 secs <-> max time or date                                => over [2..X] years

    With ``include_seconds`` set to True and the difference < 1 minute 29
    seconds:

    0-4   secs    => less than 5 seconds
    5-9   secs    => less than 10 seconds
    10-19 secs    => less than 20 seconds
    20-39 secs    => half a minute
    40-59 secs    => less than a minute
    60-89 secs    => 1 minute

    Examples:

        >>> from datetime import datetime, timedelta
        >>> from_time = datetime.now()
        >>> distance_of_time_in_words(from_time, from_time + timedelta(minutes=50))
        'about 1 hour'
        >>> distance_of_time_in_words(from_time, from_time + timedelta(seconds=15))
        'less than a minute'
        >>> distance_of_time_in_words(from_time, from_time + timedelta(seconds=15), include_seconds=True)
        'less than 20 seconds'

    Note: ``distance_of_time_in_words`` calculates one year as 365.25 days.
    """
    if isinstance(from_time, int):
        from_time = time.time()+from_time
    else:
        from_time = time.mktime(from_time.timetuple())
    if isinstance(to_time, int):
        to_time = time.time()+to_time
    else:
        to_time = time.mktime(to_time.timetuple())
    
    distance_in_minutes = int(round(abs(to_time-from_time)/60))
    distance_in_seconds = int(round(abs(to_time-from_time)))
    
    if distance_in_minutes <= 1:
        if include_seconds:
            for remainder in [5, 10, 20]:
                if distance_in_seconds < remainder:
                    return "less than %s seconds" % remainder
            if distance_in_seconds < 40:
                return "half a minute"
            elif distance_in_seconds < 60:
                return "less than a minute"
            else:
                return "1 minute"
        else:
            if distance_in_minutes == 0:
                return "less than a minute"
            else:
                return "1 minute"
    elif distance_in_minutes < 45:
        return "%s minutes" % distance_in_minutes
    elif distance_in_minutes < 90:
        return "about 1 hour"
    elif distance_in_minutes < 1440:
        return "about %d hours" % (round(distance_in_minutes / 60.0))
    elif distance_in_minutes < 2880:
        return "1 day"
    elif distance_in_minutes < 43220:
        return "%d days" % (round(distance_in_minutes / 1440))
    elif distance_in_minutes < 86400:
        return "about 1 month"
    elif distance_in_minutes < 525600:
        return "%d months" % (round(distance_in_minutes / 43200))
    elif distance_in_minutes < 1051200:
        return "about 1 year"
    else:
        return "over %d years" % (round(distance_in_minutes / 525600))

def time_ago_in_words(from_time, include_seconds=False):
    """
    Like distance_of_time_in_words, but where ``to_time`` is fixed to ``datetime.now()``.
    """
    return distance_of_time_in_words(from_time, datetime.now(), include_seconds)

__all__ = ['distance_of_time_in_words', 'time_ago_in_words']
