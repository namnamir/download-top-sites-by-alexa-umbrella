from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from tld import get_tld
from datetime import datetime
from time import sleep
from subprocess import call
import sys
import threading
import argparse
import random

"""
sets a global variable to keep the non-duplicated list of domains
and keep the list of the domains proccessed worked on
"""
pure_domains = list()
worked_urls = list()
start_point = [1, 2, 3, 4, 5]

# output file
out_file = 'cleared_list.csv'


class Website(object):

    def domain_validator(self):
        try:
            # get the domain name from the list
            return True, get_tld(self, as_object=True, fix_protocol=True)
        except:
            return False, "Weird_Domain_Name"

    # checks if the domain is not duplicated (e.g. google.com and google.co.uk)
    def duplicated_domain_finder(self):

        try:
            dom = Website.domain_validator(self)
            if dom[0] and (dom[1].domain not in pure_domains):
                pure_domains.append(dom[1].domain)
                return True
            else:
                return False

        # in case of unkown tld (e.g. xn--j1ahfl.xn--p1ai)
        except:
            print("Unexpected error:", sys.exc_info()[0])
            # raise
            pass

    def category_parser(self):

        sleep(random.randint(40, 100))

        ag1 = """Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X)
            AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0
            Mobile/14E304 Safari/602.1"""
        ag2 = """Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0)
            Gecko/20100101 Firefox/47.0","Mozilla/5.0 (Macintosh;
            Intel Mac OS X x.y; rv:42.0) Gecko/20100101 Firefox/42.0"""
        ag3 = """Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36
            (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"""
        ag4 = """Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36
            (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36
            OPR/38.0.2220.41"""
        ag5 = """Mozilla/5.0 (compatible; MSIE 9.0; Windows Phone
            OS 7.5; Trident/5.0; IEMobile/9.0)"""
        ag6 = """Mozilla/5.0 (Linux; U; Android 1.5; de-de; HTC Magic
            Build/CRB17) AppleWebKit/528.5+ (KHTML, like Gecko)
            Version/3.1.2 Mobile Safari/525.20.1"""

        acc = """text/html,application/xhtml+xml,application/
            xml;q=0.9,*/*;q=0.8"""

        # creates a random header
        age = random.choice([ag1, ag2, ag3, ag4, ag5, ag6])
        request_headers = {
            "Accept-Language": "en-US,en;q=0.5",
            "User-Agent": age,
            "Accept": acc,
            "Connection": "keep-alive"
        }

        #####################
        # Alexa.com
        #####################
        # format of the URL
        url = 'https://www.alexa.com/siteinfo/{}'.format(self)
        # creates the request with the header
        request = Request(
            url,
            data=None,
            headers=request_headers)
        site = urlopen(request)
        # parses the site
        dumped = BeautifulSoup(
            site.read(),
            'html.parser')
        # gets part of the data related to global rank
        temp0 = dumped.find("img", title="Global rank icon").find("strong")
        rank = temp0.contents[2][1:-14].replace(',', '')

        try:
            # gets part of the data related to categories
            temp1 = dumped.find("table", id="category_link_table")
            temp1 = temp1.find("tbody").find("tr").find("td")
            category = temp1.find("a").string

            # if the category part is not empty and is not an adult website
            if temp1 and (category != "Adult"):
                # returns the category and rank
                return True, category, rank
        # if the domain doesn't exist in the database
        except:
            rank = temp0.contents[2][1:-14].replace(',', '')

            category = "NA"
            return False, category, rank

    def download_site(self):
        """
        downloads the site using wget command (on Linux); for learning
        more about the parameters visit
        https://www.gnu.org/software/wget/manual/wget.html:
        --progress: show the progress bar/dot
        --server-response: shows the HTTP header sent by server
        --recursive: recursively download all files and folders
        --accept: download only specific file types
        --convert-links: convert (internal) links after downloading
        --no-cache: don't get the cached pages
        --max-redirect: sets the max of redirection of the url
        --timeout: set the timeout of the network
        """
        com = """wget --progress=bar --recursive --accept "*.html, *.htm, *.css, *.js" --no-cache --convert-links --max-redirect=3 --timeout=3 --server-response """ + self
        call(com, shell=True)


def worker(domains_list, output_file, start_point, id):
    start = min(start_point)
    for i in range(start-1, len(domains_list)):
        url = str(Website.domain_validator(domains_list[i])[1])
        dup = Website.duplicated_domain_finder(url)
        if (url not in worked_urls) and dup:
            # add the url to the list to prevent duplication work of processes
            worked_urls.append(url)
            # prints (url, category, rank, date) into the file
            with open(output_file, 'a') as out:
                out.write(url + ',' + Website.category_parser(url)[0] + ',' + Website.category_parser(url)[1] + ',' + datetime.now().strftime("%Y-%m-%d") + '\n')
            Website.download_site(url)
            # prints on the screen
            print(
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"), url,
                " in category ", Website.category_parser(url)[0],
                " at rank ", Website.category_parser(url)[1],
                " is downloaded.")
    # updates the list to prevent
    start_point[id] = start + 1


if __name__ == '__main__':
    """
    gives options to the user to select among different sources for
    downloading the latest top opne million sites.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-a", "--alexa", help="Get list of the domains from Alexa",
        action="store_true")
    parser.add_argument(
        "-c", "--cisco", help="Get list of the domains from Cisco",
        action="store_true")
    parser.add_argument(
        "-s", "--statvoo", help="Get list of the domains from Statvoo",
        action="store_true")
    args = parser.parse_args()

    """
    based on the selection of the user, download the file, unzip it
    and remove the source file.
    """
    if args.statvoo:
        file = 'https://siteinfo.statvoo.com/dl/top-1million-sites.csv.zip'
        call(
            'wget {} -O file.zip; unzip ./file.zip; rm file.zip;'.format(file),
            shell=True)
        in_file = 'top-1million-sites.csv'
    elif args.cisco:
        file = 'http://s3-us-west-1.amazonaws.com/umbrella-static/top-1m.csv.zip'
        call(
            'wget {} -O file.zip; unzip ./file.zip; rm file.zip;'.format(file),
            shell=True)
        in_file = 'top-1m.csv'
    else:
        file = 'http://s3.amazonaws.com/alexa-static/top-1m.csv.zip'
        # call(
        #     'wget {} -O file.zip; unzip ./file.zip; rm file.zip;'.format(file),
        #     shell=True)
        in_file = 'top-1m.csv'
        in_file = 'test.csv'

    with open(in_file) as f:
        domains = f.readlines()
        """
        removes the rank from the beginning and \n from the end of
        the line (e.g. '999970,sflowm.com\n') and make a list
        """
        domains = [line.split(',')[-1][:-1] for line in domains]

    # writes the header of the file
    with open(out_file, 'w') as output:
        output.write("URL,Category,Rank,Date\n")

    threads = []
    for i in range(5):
        thread = threading.Thread(
            target=worker,
            args=(domains, out_file, start_point, i,))
        threads.append(thread)
        sleep(15)
        thread.start()
