__author__ = "Geoffroy Couprie"
__copyright__ = "Copyright 2010, Geoffroy Couprie"
__license__ = "GPL v2"
__version__ = "0.0.1"
__maintainer__ = "Geoffroy Couprie"
__email__ = "geo.couprie@gmail.com"
__status__ = "Prototype"

import sqlite3
import os


try:
    os.remove('example.db')
except:
    pass

conn = sqlite3.connect('example.db')

c = conn.cursor()

# Create table
c.execute('create table package \
 (id integer, parent integer, name text)')
c.execute('create table class \
    (id integer, pk_id integer, name text,\
    inherits text, imports text)')
c.execute('create table method \
    (cl_id integer, name text, category text, \
    args text, comments text, code text)')

c.execute("insert into package \
    values(1, 0, 'first package')")
c.execute("insert into package \
    values(2, 0, '2 pak')")
c.execute("insert into package \
    values(3, 1, 'package 3')")
c.execute("insert into package \
    values(4, 1, 'p4ck4ge')")
c.execute("insert into package \
    values(5, 3, 'fifth package')")
c.execute("insert into package \
    values(6, 3, 'pack de biere')")
c.execute("insert into package \
    values(7, 0, 'pack de sept')")

c.execute("insert into class \
    values(1, 1, 'firstclass','','pouet,truc')")
c.execute("insert into class \
    values(2, 1, 'economicclass','','')")
c.execute("insert into class \
    values(3, 1, 'lowcostclass','economicclass','')")

c.execute("insert into method \
    values(1, 'init', 'init-release', 'self', 'quack','print aaa')")

c.execute("insert into method \
    values(1, 'prnt', 'show', 'self,str', 'quack','print WWWW')")

# Save (commit) the changes
conn.commit()

# We can also close the cursor if we are done with it
c.close()

conn.close()
