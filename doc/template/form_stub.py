# -*- coding: utf-8 -*-

import random
import time

def strTimeProp(start, end, format, prop):
    """Get a time at a proportion of a range of two formatted times.

    start and end should be strings specifying times formated in the
    given format (strftime-style), giving an interval [start, end].
    prop specifies how a proportion of the interval to be taken after
    start.  The returned time will be in the specified format.
    """

    stime = time.mktime(time.strptime(start, format))
    etime = time.mktime(time.strptime(end, format))

    ptime = stime + prop * (etime - stime)

    return time.strftime(format, time.localtime(ptime))


def randomDate(start, end, prop):
    return strTimeProp(start, end, '%m/%d/%Y %I:%M %p', prop)


event_types = ['Esportivo', 'Teatro', 'Cinema','Tecnologia','Inovação','Governo']
status = ['Iniciando', 'Encerrado','Pendente']

for i in range(25):
    if(i % 2):
        print('<tr class ="odd">')
    else:
        print('<tr class ="even">')

    event_date = '<div class="muted">'+randomDate("1/1/2017 1:30 PM", "7/1/2017 4:50 AM", random.random()) + ' - ' + randomDate("7/2/2017 1:30 PM", "1/1/2018 4:50 AM", random.random()) + '</div>'
    print('<td class ="sorting_1"><div><a href="dashboard.html">Evento ' + random.choice(event_types) + '</a><div>' + event_date +'</td>')
    print('<td>' + random.choice(status) + '</td>')
    print('</tr>')
