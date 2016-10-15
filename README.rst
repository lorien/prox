Prox - the tool to check how bad your proxy list is
===================================================

Installation
------------

Clone repo. Run `make build`. Activate created virtualenv.


How to check the proxy list
---------------------------

You have to provide at least the type and location of proxy list.

If the proxylist located at http://example.com/abc.txt:

.. code:: bash

    ./check_plist.py socks URL http://example.com/abc.txt

If the list is in local file:

.. code:: bash

    ./check_plist.py socks path/to/file.txt


How to check multiple lists
---------------------------

Create file foo.yml like:

.. code:: yml

    - proxy_type: socks
      plist_url: var/gate-rusdot.txt
      limit: 100

    - proxy_type: http
      plist_url: var/gate-million10-1.txt
      limit: 100

It should by YML list of tasks. Each task contains key names same
as check_plist.py command line arguments.

Run the command:

.. code:: bash

    ./check_task.py foo.yml
