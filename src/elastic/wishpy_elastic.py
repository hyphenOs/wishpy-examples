"""
A simple utility that dumps Dissected Packets from a PCAPish file to Elastic.
"""
import os
import json
import sys
import logging

import elasticsearch
from wishpy.wireshark.lib.dissector import (
        WishpyDissectorFile,
        setup_process,
        cleanup_process)


_MAPPINGS_FILE = "dyn_mappings.json"

_logger = logging.getLogger()

class PcapFileElasticDumper:
    """Class that dumps packets from a PCAP file into Elastic with dynamic mappings.
    """

    def __init__(self, dissector, **kw):
        """
        Args:
            dissector: The dissector class that is going to output packets as json.
            **kw: Keyword arguments passed to ElasticSearch constructor.
        """
        self._dissector = dissector
        filename = kw.pop('filename', 'foo.pcap')
        self._index_name = "pcap-" + \
                os.path.basename(os.path.splitext(filename)[0])
        self._elastic_handle = elasticsearch.Elasticsearch(**kw)

    def init(self):

        mappings_file_path = os.path.join(os.path.dirname(
                    os.path.abspath(__file__)), _MAPPINGS_FILE)

        with open(mappings_file_path, "r") as f:
            mappings_doc = f.read()

        try:
            self._index = self._elastic_handle.indices.create(
                self._index_name,
                body=mappings_doc,
                ignore=[])
        except Exception as e:
            _logger.exception("init")
            raise

    def run(self):
        count = 0
        for packet in self._dissector.run():
            try:
                self._elastic_handle.index(self._index_name, packet)
                count += 1
                if count % 1000 == 0:
                    print("processed {} packets".format(count))

            except Exception as e:
                _logger.exception(e)


def main(args):

    filename = args[1]

    logging.basicConfig()

    try:
        setup_process()

        dissector = WishpyDissectorFile(filename)
        dissector.set_elasticky(True)

        # FIXME : Get it from wishpy dissector when it supports it.
        dumper = PcapFileElasticDumper(dissector, filename=filename)
        dumper.init()

        dumper.run()

        cleanup_process()

        return 0

    except Exception as e:
        _logger.exception(e)
        return 1


if __name__ == '__main__':

    if len(sys.argv) < 2:
        print("Usage wishpy_elastic.py <pcap-file>")
        sys.exit(1)

    sys.exit(main(sys.argv))
