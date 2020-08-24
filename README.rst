wishpy Examples
===============

Supported wishpy version - ``0.1.1``

This repository contains various examples for using ``wishpy``.

The reason this is kept separate is to avoid having to 'install' the
client libraries in the original ``wishpy`` repo and we are trying to
keep that repo as much Pure Python as possible.

This repository will try to be up-to-date with the latest version of ``wishpy`` available on `pypi <https://pypi.org/project/wishpy/>`_.

In future it may be possible that some or others of this becomes their
own repository, for now this is good enough.

Wishpy + Redis
--------------

An example code that picks up packets from the interface specified on the command line and dumps dissected json to a Redis queue named ``packet_queue:${interface_name}`` - ``src/redis/redis_json.py``

Wishpy + Elastic
----------------

A very simple version of code that dumps Packets from a PCAP to Elastic - ``src/elastic/wishpy_elastic.py``. **Note: This is very very early!**
