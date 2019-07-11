import logging
import re
from urllib.parse import urlparse
from corpus import Corpus
import lxml.html
from urllib.parse import parse_qs

logger = logging.getLogger(__name__)


class Crawler:
    """
    This class is responsible for scraping urls from the next available link in frontier and adding the scraped links to
    the frontier
    """

    def __init__(self, frontier):
        self.frontier = frontier
        self.corpus = Corpus()

    def start_crawling(self):
        """
        This method starts the crawling process which is scraping urls from the next available link in frontier and adding
        the scraped links to the frontier
        """

        out_file = open('analytics.txt', 'w')

        subdomin_dict = dict()
        url_list = []
        trap_set = set()
        max_outlink_num = 0
        max_outlink_page = ''

        while self.frontier.has_next_url():
            url = self.frontier.get_next_url()
            logger.info("Fetching URL %s ... Fetched: %s, Queue size: %s", url, self.frontier.fetched,
                        len(self.frontier))
            url_data = self.fetch_url(url)

            # track subdomain count
            if urlparse(url).netloc in subdomin_dict.keys():
                subdomin_dict[urlparse(url).netloc] += 1
            else:
                subdomin_dict[urlparse(url).netloc] = 1

            # track downloaded url
            url_list.append(url)

            link_num = 0
            for next_link in self.extract_next_links(url_data):
                if self.corpus.get_file_name(next_link) is not None:
                    if self.is_valid(next_link):
                        self.frontier.add_url(next_link)
                        link_num += 1
                    else:
                        trap_set.add(next_link)

            # track page with max outlink
            if link_num > max_outlink_num:
                max_outlink_num = link_num
                max_outlink_page = url

        # write data to file
        out_file.write('Subdomin count\n------------------\n')
        for i in subdomin_dict.keys():
            out_file.write(i + '\t' + str(subdomin_dict[i]) + '\n')
        out_file.write('Url list\n------------------\n')
        for i in url_list:
            out_file.write(i + '\n')
        out_file.write('Trap list\n------------------\n')
        for i in trap_set:
            out_file.write(i + '\n')
        out_file.write('Max out link page\n------------------\n')
        out_file.write(max_outlink_page + '\t' + str(max_outlink_num))

        out_file.close()

    def fetch_url(self, url):
        """
        This method, using the given url, should find the corresponding file in the corpus and return a dictionary
        containing the url, content of the file in binary format and the content size in bytes
        :param url: the url to be fetched
        :return: a dictionary containing the url, content and the size of the content. If the url does not
        exist in the corpus, a dictionary with content set to None and size set to 0 can be returned.
        """
        url_data = {
            "url": url,
            "content": None,
            "size": 0
        }

        path = self.corpus.get_file_name(url)
        if path != None:
            file = open(path, 'rb')
            url_data['content'] = file.read()
            file.close()

            url_data['size'] = len(url_data['content'])

        return url_data

    def extract_next_links(self, url_data):
        """
        The url_data coming from the fetch_url method will be given as a parameter to this method. url_data contains the
        fetched url, the url content in binary format, and the size of the content in bytes. This method should return a
        list of urls in their absolute form (some links in the content are relative and needs to be converted to the
        absolute form). Validation of links is done later via is_valid method. It is not required to remove duplicates
        that have already been fetched. The frontier takes care of that.

        Suggested library: lxml
        """
        outputlinks = []
        if url_data['content'] != None:
            html = lxml.html.fromstring(url_data['content'])
            html.make_links_absolute(url_data['url'])
            for i in html.xpath('//a/@href'):
                if re.match(r'^javascript:popUp', i):
                    outputlinks.append(re.search(r'(https?://)[a-zA-Z0-9_./\?=&-]*', i).group(0))
                else:
                    outputlinks.append(i)

            # for i in html.xpath('//link/@href'):
            #     outputlinks.append(i)

        return outputlinks

    def is_valid(self, url):
        """
        Function returns True or False based on whether the url has to be fetched or not. This is a great place to
        filter out crawler traps. Duplicated urls will be taken care of by frontier. You don't need to check for duplication
        in this method
        # """
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        if len(parsed.path.split('/')) != len(set(parsed.path.split('/'))):
            return False

        if parsed.query != '':
            for i in parse_qs(parsed.query).values():#token
                for j in i:
                    if re.match('^[a-zA-Z0-9]{10}[a-zA-Z0-9]*$', j) and not re.match('^[a-zA-Z]*$', j):
                        return False

        if parsed.query != '':
            if 'day' in parse_qs(parsed.query).keys() \
                    or 'month' in parse_qs(parsed.query).keys() \
                    or 'year' in parse_qs(parsed.query).keys():
                return False

        if parsed.query != '':
            if len(parse_qs(parsed.query).keys()) != len(set(parse_qs(parsed.query).keys())):
                return False

        try:
            return ".ics.uci.edu" in parsed.hostname \
                   and not re.match(".*\.(css|js|bmp|gif|jpe?g|ico" + "|png|tiff?|mid|mp2|mp3|mp4" \
                                    + "|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf" \
                                    + "|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso|epub|dll|cnf|tgz|sha1" \
                                    + "|thmx|mso|arff|rtf|jar|csv" \
                                    + "|rm|smil|wmv|swf|wma|zip|rar|gz|pdf)$", parsed.path.lower())

        except TypeError:
            print("TypeError for ", parsed)
            return False

