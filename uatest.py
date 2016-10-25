# Copyright 2016 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""A program to collect web server responses for a set of User Agents.

The UA test has two modes:
  1. running all untested UA/URL combos as found in the SQLite DB,
  2. testing a specific URL with all known UAs

Usage: python uatest.py [--untested|http://example.com|https://example.com]

Data is stored in the 'requests' table and responses are saved in the ./saves
directory.

See uatest.sql for initial data, and request-test.sql for data structure

"""

import hashlib
import os
import os.path
import re
import sys

import requests
import sqlite3


def main(args):
  if not os.path.isfile('request-test.db'):
    print ('Please run '
           '``sqlite3 request-test.db < request-test.sql uatest.sql\'\' or '
           'cd to the directory where request-test.db is located')
    return 5

  if not args:
    print 'Usage: uatest.py [http://example.com|--untested]'
    return 1
  elif len(args) != 1:
    print 'Usage: uatest.py [http://example.com|--untested]'
    return 2

  arg = args[0]
  conn = sqlite3.connect('request-test.db')
  c = conn.cursor()
  weburl_re = re.compile(
      r'^[hH][tT][tT][pP][sS]?://[][._~:/?#@~$&\'()*+,;=0-9a-zA-Z-]+$'
  )
  if arg == '--untested':
    # Do all untested URLs
    # iterate over untested url+ua combos
    c.execute('select u.urlid, u.url, ua.ua_key, ua.ua_val '
              'from urls u, user_agents ua '
              'where ua.ua_key not in '
              '(select ua_key from requests where urlid = u.urlid)')
  elif weburl_re.match(arg):
    # Test only the given URL
    # Make sure the URL is in the database, if not, add it
    c.execute('INSERT OR IGNORE INTO urls (url) VALUES (?)', [arg])
    c.execute('select u.urlid, u.url, ua.ua_key, ua.ua_val '
              'from urls u, user_agents ua where u.url = ?', [arg])
  else:
    print 'Usage: uatest.py [http://example.com|--untested]'
    return 3

  for row in c:
    urlid, url, ua_key, ua_val = row
    hc = conn.cursor()
    print url
    try:
      test_url(urlid, url, ua_key, ua_val, hc)
      # Commit the changes to DB
      conn.commit()
    except Exception:
      print 'error!'
      for i in sys.exc_info():
        print i


def test_url(urlid, url, ua_key, useragent, hc):
  """Tests the URL with the given useragent."""
  print ua_key
  r = requests.get(url, headers={'User-Agent': useragent}, allow_redirects=True)
  redirect_chain = None
  if r.history:
    redirect_chain = ' -> '.join(map(lambda i: i.request.url, r.history))
    print redirect_chain
  sha256sum = hashlib.sha256(r.text.encode('utf-8')).hexdigest()
  print sha256sum
  hc.execute('INSERT INTO requests '
             '(urlid, ua_key, redirect_chain, response_body_sha256sum) '
             'VALUES (?, ?, ?, ?)', (urlid, ua_key, redirect_chain, sha256sum))
  requestid = hc.lastrowid
  print requestid
  for header_key, header_val in r.headers.iteritems():
    hc.execute('INSERT INTO response_headers '
               '(requestid, header_key, header_val) '
               'VALUES (?, ?, ?)', (requestid, header_key, header_val))
  # Save the file
  filename = 'saves/' + sha256sum + '.html'
  print filename
  if not os.path.isfile(filename):
    with open(filename, 'wb') as fd:
      for chunk in r.iter_content():
        fd.write(chunk)
  else:
    # Duplicate response (or hash collision)
    pass

if __name__ == '__main__':
  sys.exit(main(sys.argv[1:]))

