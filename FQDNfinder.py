#!/usr/bin/env python2
from __future__ import print_function
from socket import gethostbyname_ex as ghbnex
from socket import gaierror as GAIError
from multiprocessing.pool import ThreadPool
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
    default_top_domain = 'hec.sap.biz'
    landscape_list = ['rot', 'ams', 'stl', 'sac', 'tyo', 'osa', 'syd', 'mcc', 'rot2', 'irl', 'us1', 'syd2', 'mow',
                      'mow2', 'yyz', 'syd3', 'us4', 'us3', 'us2', 'fra', 'yyz2']
    default_search_domains = ['grizmin.org', 'int.grizmin.org']

    default_search_domains += [landscape + '.' + default_top_domain for landscape in landscape_list]

    def __init__(self, short_name, search_domain_list=set()):
        self.search_domain_list = search_domain_list
        self.shortName = short_name
        if not search_domain_list:
            self.search_domain_list = self.default_search_domains
        self.fqdn = self.get_fqdn()

    def get_fqdn(self):
        """
        return 1st found resolvable FQDN

        :return: triple
        """

        if any([self.shortName.endswith(sn) for sn in self.default_search_domains]):
            logger.warn('{0} FQDN found in short names list.'.format(self.shortName))
            self.found = True
            return ghbnex(self.shortName)

        for search_domain in self.search_domain_list:
            possible_fqdn = self.shortName + '.' + search_domain
            try:
                logger.debug("Processing {0}".format(possible_fqdn))
                hostinfo = ghbnex(possible_fqdn)
                self.found = True
                return hostinfo
            except GAIError:
                logger.debug(possible_fqdn, 'is not the FQDN')
            finally:
                if not self.found:
                    return (None, None, None)

    def __repr__(self):
        return self.fqdn[0], self.fqdn[1], ''.join(self.fqdn[2])

    def __str__(self):
        return "{}, ({}), {}".format(self.fqdn[0], " ".join(self.fqdn[1]), ''.join(self.fqdn[2]))

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
        # TODO: Add thread names in logger - DONE
        # TODO: use async and implment timeouts


        if arg.debug:
            logger.info("Loglevel set to DEBUG")
            logger.setLevel(logging.DEBUG)
            logger.handlers[0].setFormatter(logging.Formatter("[%(levelname)s] %(relativeCreated)6d %(threadName)s  %(message)s"))

        logger.debug("Starting {0} on {1} with arguments: {2}".format(sys.argv[0], datetime.datetime.today(), vars(arg)))

        pool = ThreadPool(processes=10)
        multiple_results = pool.map(FQDN, arg.shortName)
        for sn in multiple_results:
            if sn.found:
                if not arg.long:
                    print(sn.fqdn[0])
                else:
                    print(sn)
            else:
                if not arg.warn:
                    logger.warning('{0} not found'.format(sn.shortName))
    main()
