from __future__ import print_function
from socket import gethostbyname_ex as ghbnex
import argparse
import logging

# Log to stdout
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
streamformater = logging.Formatter("[%(levelname)s] %(message)s")

logstreamhandler = logging.StreamHandler()
logstreamhandler.setLevel(logging.INFO)
logstreamhandler.setFormatter(streamformater)
logger.addHandler(logstreamhandler)


class GetFQDN:
    found = False
    default_search_domains = {'hec.sap.biz', 'rot.hec.sap.biz', 'ams.hec.sap.biz', 'stl.hec.sap.biz', 'sac.hec.sap.biz',
                              'tyo.hec.sap.biz', 'osa.hec.sap.biz', 'syd.hec.sap.biz', 'mcc.rot.hec.sap.biz',
                              'rot2.hec.sap.biz', 'syd2.hec.sap.biz', 'mow.hec.sap.biz', 'mow2.hec.sap.biz',
                              'yyz.hec.sap.biz', 'grizmin.org', 'int.grizmin.org'}

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
                hostinfo = ghbnex(possible_fqdn)
                self.found = True
                return hostinfo
            except:
                # print(possible_fqdn + 'is not the FQDN')
                pass

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('shortName', nargs='+', help='host or hosts')
    parser.add_argument('--long', '-l',action='store_const', help='long format (list of ips included)',const=True, default=False)
    arg = parser.parse_args()

    # TODO: Add multiprocessing

    for sn in arg.shortName:
        sn = GetFQDN(sn)
        if sn.found:
            if arg.long:
                print(sn.fqdn[0], sn.fqdn[2])
            else:
                print(sn.fqdn[0])

if __name__ == '__main__':
    main()