from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from tld import get_tld
from datetime import datetime
from time import sleep
from subprocess import call
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


def pr_color(FLAG, id, color, text):
    """
    make the texts colorful; read more here:
    https://stackoverflow.com/questions/287871/print-in-terminal-with-colors
    """
    if FLAG:
        # define colors
        if color == 'L_R':
            color = '\x1b[0;33;44m'
        if color == 'P_B':
            color = '\x1b[0;30;45m'
        if color == 'R_O':
            color = '\x1b[1;37;41m'
        if color == 'G_B':
            color = '\x1b[7;37;41m'
        if color == 'G_O':
            color = '\x1b[1;33;42m'
        if color == 'G_W':
            color = '\x1b[6;37;42m'
        if color == 'N_G':
            color = '\x1b[7;30;46m'
        if color == 'N_W':
            color = '\x1b[7;30;47m'
        # define restart
        END = '\x1b[0m'
        if type(id) == int:
            print(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' - ' + '\x1b[0;30;43m' + ' T' + str(id) + ' ' + END + '\t' + color + text + END)
        else:
            print(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' -    ' + '\t' + color + text + END)


class Website(object):

    def domain_validator(self, FLAG, id):
        """
        this function validates the url if the tld is valid or not.
        """
        try:
            # get the domain name from the list
            return True, get_tld(self, as_object=True, fix_protocol=True)
        except:
            pr_color(FLAG, id, 'R_O', 'Error_01: "{}" is not a valid domain.'.format(self))
            return False, self

    # checks if the domain is not duplicated (e.g. google.com and google.co.uk)
    def duplicated_domain_finder(self, FLAG, id):
        """
        it checks if the domain, regardless the tld, is checked previously
        or not.
        """
        try:
            dom = Website.domain_validator(self, FLAG, id)
            if dom[0] and (dom[1].domain not in pure_domains):
                pure_domains.append(dom[1].domain)
                return True
            elif dom[1].domain in pure_domains:
                pr_color(FLAG, id, 'R_O', 'Error_02: "{}" is duplicated.'.format(self))
                return False
        # in case of unkown tld (e.g. xn--j1ahfl.xn--p1ai)
        except:
            pr_color(FLAG, id, 'R_O', 'Error_03: error in duplication of "{}"'.format(self))
            pass

    def category_parser(self, FLAG, id):
        """
        it parses the category of the domain as well as the Alexa rank of
        it from Alexa website. The random sleep and user-agent of browser
        are for assuring the Alexa that it is not an attack to its service.
        """
        sleep(random.randint(10, 40))

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

        pr_color(FLAG, id, 'L_R', 'Getting the category and rank of "{}" from Alexa'.format(self))

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
        temp0 = dumped.find(
            "img", title="Global rank icon").find("strong")
        rank = temp0.contents[2][1:-14].replace(',', '')

        try:
            # gets part of the data related to categories
            temp1 = dumped.find("table", id="category_link_table")
            temp1 = temp1.find("tbody").find("tr").find("td")
            category = temp1.find("a").string

            # if the category part is not empty and is not an adult website
            if temp1 and (category != "Adult"):
                pr_color(FLAG, id, 'G_W', 'Data of "{}" are retrived from Alexa'.format(self))
                # returns the category and rank
                return True, category, rank
        # if the domain doesn't exist in the database
        except:
            rank = temp0.contents[2][1:-14].replace(',', '')
            category = "NA"
            pr_color(FLAG, id, 'R_O', 'Error_5: the category of "{}" is unknown'.format(self))
            return False, category, rank

    def download_site(self, FLAG, id):
        """
        downloads the site using wget command (on Linux); for learning
        more about the parameters visit
        https://www.gnu.org/software/wget/manual/wget.html:
        --server-response: shows the HTTP header sent by server
        --recursive: recursively download all files and folders
        --accept: download only specific file types
        --convert-links: convert (internal) links after downloading
        --max-redirect: sets the max of redirection of the url
        --timeout: set the timeout of the network
        --no-parent: don't follow links outside the directory
        --no-clobber: don't overwrite any existing files
        --html-extension: save files with the .html extension
        --span-hosts: (read more: https://stackoverflow.com/a/10872187)
        """
        try:
            com = """
                wget \
                --recursive \
                --no-clobber \
                --accept "*.html, *.htm, *.css, *.js" \
                --html-extension \
                --convert-links \
                --max-redirect=3 \
                --timeout=3 \
                --server-response \
                --domains {} \
                --no-parent \
                --span-hosts \
                {}""".format(self, self)
            pr_color(FLAG, id, 'G_O', '"{}" is preparing for download'.format(self))
            call(com, shell=True)
        except:
            pr_color(FLAG, id, 'R_O', 'ERROR_04: error in downloading "{}"'.format(self))


def worker(FLAG, domains_list, output_file, start_point, id):
    """
    it gives tasks to each thread.
    """
    start = start_point[id]
    for i in range(start-1, len(domains_list), 5):
        # url = str(Website.domain_validator(domains_list[i], FLAG, id)[1])
        url = domains_list[i]
        pr_color(FLAG, int(id), 'P_B', 'Working on "{}", ({}/{})'.format(url, i+1, len(domains_list)))
        dup = Website.duplicated_domain_finder(url, FLAG, id)
        if dup:
            # prints (url, category, rank, date) into the output file
            with open(output_file, 'a') as out:
                out.write(url + ',' + Website.category_parser(url, FLAG, id)[1] + ',' + Website.category_parser(url, FLAG, id)[2] + ',' + datetime.now().strftime("%Y-%m-%d") + '\n')

            Website.download_site(url, FLAG, id)
            # prints on the screen
            text = url + " in category " + Website.category_parser(url, FLAG, id)[1] + " at rank " + Website.category_parser(url, FLAG, id)[2] + " is downloaded."
            pr_color(FLAG, id, 'G_B', text)


if __name__ == '__main__':
    """
    gives options to the user to select among different sources for
    downloading the latest top opne million sites.
    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-a", "--alexa", help="Get list of the domains from Alexa",
        action="store_true", default=False)
    parser.add_argument(
        "-c", "--cisco", help="Get list of the domains from Cisco",
        action="store_true", default=False)
    parser.add_argument(
        "-s", "--statvoo", help="Get list of the domains from Statvoo",
        action="store_true", default=False)
    parser.add_argument(
        "-F", "--file", help="Go for the custom file e.g. /path/to/top.csv",
        nargs='?', type=str, default="top.csv")
    # read more here: https://stackoverflow.com/a/15301183
    parser.add_argument(
        "-S", "--show", help="Show the log",
        nargs='?', const=1, type=int, default=1)

    args = parser.parse_args()

    """
    based on the selection of the user, download the file, unzip it
    and remove the source file.
    """
    if args.statvoo:
        file = 'https://siteinfo.statvoo.com/dl/top-1million-sites.csv.zip'
        call(
            'wget {} -O file.zip; unzip ./file.zip; rm file.zip;'.format(
                file),
            shell=True)
        in_file = 'top-1million-sites.csv'
    elif args.cisco:
        file = 'http://s3-us-west-1.amazonaws.com/umbrella-static/top-1m.csv.zip'
        call(
            'wget {} -O file.zip; unzip ./file.zip; rm file.zip;'.format(
                file),
            shell=True)
        in_file = 'top-1m.csv'
    elif args.alexa:
        file = 'http://s3.amazonaws.com/alexa-static/top-1m.csv.zip'
        call(
            'wget {} -O file.zip; unzip ./file.zip; rm file.zip;'.format(
                file),
            shell=True)
        in_file = 'top-1m.csv'
    elif args.file:
        in_file = args.file
    else:
        in_file = 'top.csv'
    # checks if the the user wants to see the output or not
    if args.show:
        FLAG = True
    else:
        FLAG = False

    with open(in_file) as f:
        domains = f.readlines()
        """
        removes the rank from the beginning and \n from the end of
        the line (e.g. '999970,sflowm.com\n') and make a list
        """
        domains = [line.split(',')[-1][:-1] for line in domains]
        pr_color(FLAG, 'F', 'N_W', 'The list of the domains is obtained.')

    # writes the header of the file
    with open(out_file, 'w') as output:
        output.write("URL,Category,Rank,Date\n")
        pr_color(FLAG, 'F', 'N_W', 'The output file is created.')

    threads = []
    for i in range(5):
        pr_color(FLAG, i, 'N_G', 'Thread is initiating.')
        thread = threading.Thread(
            target=worker,
            args=(FLAG, domains, out_file, start_point, i,))
        threads.append(thread)
        thread.start()
        sleep(5)
