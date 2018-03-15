import io
import pycurl
import os
import sys
import random
from stem.control import Controller
from stem.util import system

import stem.process
from stem.util import term
import datetime

# import mongodb_client


SOCKS_PORT = 7000
CONTROL_PORT = 6969

# sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))

# USER_AGENTS_FILE = '../common/user_agents.txt'
USER_AGENTS = []

from lxml import html as lh


"""Uses pycurl to fetch a site using the proxy on the SOCKS_PORT"""
def query(url):

  output = io.BytesIO()


  through = False
  tor_c = 0
  seen_time = datetime.datetime.utcnow()
  # print ("TEST")
  # while not through:
  try:

    query = pycurl.Curl()
    query.setopt(pycurl.URL, url)
    query.setopt(pycurl.CONNECTTIMEOUT, 15)
    query.setopt(pycurl.TIMEOUT, 25)
    query.setopt(pycurl.FOLLOWLOCATION, 1)
    query.setopt(pycurl.HTTPHEADER, getHeaders())
    query.setopt(pycurl.PROXY, 'torpool')
    query.setopt(pycurl.PROXYPORT, 5566)
    # query.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_HTTP)

    query.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5_HOSTNAME)
    query.setopt(pycurl.WRITEFUNCTION, output.write)
    query.perform()
    # http_code = query.getinfo(pycurl.HTTP_CODE)
    # print (200)
    http_code = query.getinfo(pycurl.HTTP_CODE)
    response = output.getvalue()
    html = response.decode('iso-8859-1')
    # header_len = query.getinfo(pycurl.HEADER_SIZE)
    # header = resp[0: header_len]
    # html = resp[header_len:]
    if http_code == 200:
        # through = True
        try:
            dom = lh.fromstring(html)
            title = dom.cssselect('title')

            if title:
                title = title[0].text_content()
                # result['title'] = title

            body = dom.body.text_content()
            resp = {"url": url, "html": html, 'body': body,
                     "title": title,"status": http_code,
                    "seen_time": seen_time}

        except:
            resp = {"url": url, "html": html, "status": http_code, "seen_time": seen_time}
        return resp

    else:
        # renew tor to retry
        print ('error httpcode:' +str(http_code))
        # renew_tor()
        # tor_c = tor_c + 1
        # if tor_c > 2:
        #   through=True
        resp = {"url": url, "status": http_code, "seen_time": seen_time}
          # time.sleep(3)
        return resp


  # except pycurl.error as exc:
  except:
    # print (url)
    # print ("pycurl error in tor_scraper.py %s" % exc)
    # pass
    resp = {"url": url, "status": 503, "seen_time": seen_time}
    return resp
    # return "Unable to reach %s (%s)" % (url, exc)



  # return output.getvalue()


"""print tor bootstrap info"""
def print_bootstrap_lines(line):
  if "Bootstrapped " in line:
    print(term.format(line, term.Color.BLUE))


"""get user-agent and httpheader string list"""
def getHeaders():
  # ua = random.choice(USER_AGENTS)  # select a random user agent
  ua = "Mozilla/5.0 (Windows NT 6.1; rv:45.0) Gecko/20100101 Firefox/45.0"
  headers = [
    "Connection: close",
    "User-Agent: %s"%ua
  ]
  # print headers
  return headers


"""start tor process"""
def start_tor():
  tor_process = system.pid_by_port(SOCKS_PORT)
  if  tor_process is None:
    tor_process = system.pid_by_name('tor')
  if  tor_process is None:
    tor_process = stem.process.launch_tor_with_config(
      config={
        'SocksPort': str(SOCKS_PORT),
        'ControlPort': str(CONTROL_PORT),
        'ExitNodes': '{ru}',
      },
      init_msg_handler=print_bootstrap_lines,
    )
  else:
    print ("tor already running, no need to start")


"""renew tor circuit"""
def renew_tor():
   """
   Create a new tor circuit
   """
   try:
      stem.socket.ControlPort(port = CONTROL_PORT)
   except stem.SocketError as exc:
      print ("Tor", "[!] Unable to connect to port %s (%s)" %(CONTROL_PORT , exc))
   with Controller.from_port(port = CONTROL_PORT) as controller:
      controller.authenticate()
      controller.signal(stem.Signal.NEWNYM)
      print ("TorTP", "[+] New Tor circuit created")
      # print ('renewed:' + query("http://icanhazip.com")


"""stop tor process"""
def stop_process_on_name():
  process =  system.pid_by_name('tor')
  if  process is not None:
    os.kill(process, 2)

# """read user-agent"""
# with open(USER_AGENTS_FILE, 'rb') as uaf:
#     for ua in uaf.readlines():
#         if ua:
#             USER_AGENTS.append(ua.strip())
# random.shuffle(USER_AGENTS)


# """start tor instance when called this module"""
# start_tor()
#
# query("www.zillow.com")
#
# db = None
# db = mongodb_client.getDB()
# if  db is None:
#   print "fail"
# else:
#   print "succeed"
#
