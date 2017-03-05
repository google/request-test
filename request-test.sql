CREATE TABLE urls (urlid INTEGER PRIMARY KEY ASC, url TEXT UNIQUE);
CREATE TABLE user_agents (ua_key TEXT UNIQUE, form_factor TEXT, ua_val TEXT);
CREATE TABLE requests (id INTEGER PRIMARY KEY ASC, urlid INTEGER, request_made_on DATETIME default CURRENT_TIMESTAMP, ua_key TEXT, redirect_chain TEXT, response_body_sha256sum TEXT);
CREATE TABLE response_headers (requestid INTEGER, header_key TEXT, header_val TEXT);
