# request-test
Collects responses from URLs with various User-Agents, recording the response

## Installation

1. Make sure you have the prereqs on the machine (python, sqlite, et al)
2. Instantiate the sqlite db with some data: `sqlite3 request-test.db < request-test.sql uatest.sql`
2. That's it! (usually)

## Usage

There is one request test at this time: uatest.py

### uatest

The UA test has two modes:
1. running all untested UA/URL combos as found in the SQLite DB,
2. testing a specific URL with all known UAs

The test is invoked like: `python uatest.py [--untested|http://example.com|https://example.com]`

Data is stored in the 'requests' table and responses are saved in the ./saves
directory.

## Analysis

Once the data is collected, you can perform analysis by connecting to the sqlite
database on the command line (sqlite request-test.db) and reviewing the html
files in the saves dir.

Here are some interesting queries you could perform:

* Find URLs that respond to different mobile User Agents inconsistently:
  `select * from (select urlid, url, count(distinct redirect_chain) redir_count from (select r.id, r.request_made_on, h.url, h.urlid, r.ua_key, u.ua_val, u.form_factor, r.redirect_chain, r.response_body_sha256sum from requests r, user_agents u, urls h where u.ua_key = r.ua_key and h.urlid = r.urlid and u.form_factor = 'Mobile') group by urlid) where redir_count >= 2;`

## Contributing
1. Review [CONTRIBUTING]
2. Fork this repo
3. Create your feature branch: `git checkout -b my-new-feature`
4. Commit your changes: `git commit -am 'Add some feature'`
5. Push to the branch: `git push origin my-new-feature`
6. Submit a pull request!  If I don't respond quickly, send me a ping :)

## License
This sample code is an official Google product and is licensed under the
[Apache 2 License](LICENSE).
