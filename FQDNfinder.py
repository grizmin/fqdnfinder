#!/usr/bin/env python2
from __future__ import print_function
from socket import gethostbyname_ex as ghbnex
import socket
from multiprocessing.pool import ThreadPool, Queue
import argparse
import logging
import datetime
import sys

# Log to stdout
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
streamformater = logging.Formatter("[%(levelname)s] %(message)s")

logstreamhandler = logging.StreamHandler()
logstreamhandler.setFormatter(streamformater)
logger.addHandler(logstreamhandler)


class FQDN(object):
    found = False
    default_search_domains = ['hec.sap.biz', 'rot.hec.sap.biz', 'ams.hec.sap.biz', 'stl.hec.sap.biz', 'sac.hec.sap.biz',
                              'tyo.hec.sap.biz', 'osa.hec.sap.biz', 'syd.hec.sap.biz', 'mcc.rot.hec.sap.biz',
                              'rot2.hec.sap.biz', 'syd2.hec.sap.biz', 'mow.hec.sap.biz', 'mow2.hec.sap.biz',
                              'yyz.hec.sap.biz', 'grizmin.org', 'int.grizmin.org']

    def __init__(self, shortName, search_domain_list = set()):
        self.search_domain_list = search_domain_list
        self.shortName = shortName
        if not search_domain_list:
            self.search_domain_list = self.default_search_domains
        self.fqdn = self.get_fqdn()

    def get_fqdn(self):
        """
        return 1st found resolveable FQDN

        :return: triple
        """
        for search_domain in self.search_domain_list:
            possible_fqdn = self.shortName + '.' + search_domain
            try:
                logger.debug("Processing {0}".format(search_domain))
                hostinfo = ghbnex(possible_fqdn)
                self.found = True
                return hostinfo
            except socket.gaierror:
                logger.debug(possible_fqdn + 'is not the FQDN')
                pass

    def get(self):
        return self.fqdn

if __name__ == '__main__':

    def main():
        parser = argparse.ArgumentParser()
        parser.add_argument('shortName', nargs='+', help='host or hosts')
        parser.add_argument('--long', '-l',action='store_const', help='long format (list of ips included)',const=True,
                            default=False)
        parser.add_argument('--debug', '-d', action='store_const', help='print debug info', const=True,
                            default=False)
        parser.add_argument('--warn', '-w', action='store_const', help='suppress warnings', const=False,
                            default=True)

        arg = parser.parse_args()

        # TODO: Add multiprocessing - DONE
        # TODO: Add thread names in logger
        # TODO: use async and implment timeouts


        if arg.debug:
            logger.info("Loglevel set to DEBUG")
            logger.setLevel(logging.DEBUG)

        logger.debug("Starting {0} on {1} with arguments: {2}".format(sys.argv[0], datetime.datetime.today(), vars(arg)))

        pool = ThreadPool(processes=20)
        multiple_results = pool.map(FQDN, arg.shortName)
        for sn in multiple_results:
            if sn.found:
                if not arg.long:
                    print(sn.fqdn[0])
                else:
                    print(sn.fqdn[0], sn.fqdn[2])
            else:
                if not arg.warn:
                    logger.warning('{0} not found'.format(sn.shortName))
    main()
