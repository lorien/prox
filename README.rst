Prox -  the tool to check how bad your proxy list is
====================================================

Installation
------------

Clone repo. Run `make build`.


How to check something
----------------------

If the proxylist located at http://example.com/abc.txt::

    ./check_plist.py socks URL http://example.com/abc.txt

If the list is in local file::
    ./check_plist.py socks URL path/to/file.txt


How to check multiple lists
---------------------------

Create file foo.yml like::

    - proxy_type: socks
      plist_url: var/gate-rusdot.txt
      limit: 100

    - proxy_type: http
      plist_url: var/gate-million10-1.txt
      limit: 100

It should by YML list of tasks. Each task contains key names same
as check_plist.py command line arguments.

Run the command:

    ./check_task.py foo.yml
