import os
from os.path import join, split

D= '/var/django_www/webbefunde'

ignore_files = [
'urls.py',
'views.py',
'walk.py',
]

ignore_dirs = [
'scripts',
'tmp',
'log',
'static',
'media',

]

for root, dirs, files in os.walk(D):
    #if split(root)[1] in ignore_dirs:
    #    continue
    dirs.sort()
    
    #print split(root)[1]
    files.sort()
    for f in files:
        if not f.endswith('.py') or f=='__init__.py':
            continue
        if f in ignore_files:
            continue
#        if not f[0].isupper():
#            continue
        basef = os.path.splitext(f)[0]
        cur = root[len(D)+1:]
        print join(cur, basef) 
        #print cur



