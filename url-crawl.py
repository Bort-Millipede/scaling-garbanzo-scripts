#! "C:\Program Files\Python310\python.exe"
#
# Return codes:
# 1: Required arguments missing
# 2: Invalid proxy server address provided
# 3: Unable to open input file
# 4: python-requests or curl not found
# 5: Invalid option provided in argument
# 6: No URLs inputted
# 7: Proxy error on first attempted crawl

import sys
from urllib import parse as up

def _crawl_with_requests(urls,proxy,user_agent,redirects,timeout):
	jar = requests.cookies.RequestsCookieJar()
	sess = requests.Session()
	sess.cookies = jar
	sess.verify = False
	sess.proxies = {'http':proxy,'https':proxy}
	if user_agent:
		sess.headers={'User-Agent':user_agent}
	i=0
	while i<len(urls):
		urls[i] = urls[i].strip()
		try:
			sess.get(urls[i],allow_redirects=redirects,timeout=timeout)
		except requests.exceptions.ConnectionError as ex1:
			if type(ex1).__name__=='ProxyError':
				if i==0:
					sys.stderr.write('Problem detected with proxy server at %s!. Ensure proxy address is correct and re-execute script!\n'%(proxy))
					sys.exit(7)
				else:
					sys.stderr.write('Crawling %s failed due to proxy server error. Ensure proxy server is running and is stable\n'%(urls[i]))
			else:
				try:
					sess.get(urls[i],allow_redirects=redirects,timeout=timeout)
				except Exception as ex2:
					sys.stderr.write("%s\n"%(type(ex1).__name__))
					try:
						sess.get(urls[i],allow_redirects=redirects,timeout=timeout)
					except Exception as ex:
						if type(ex1).__name__=='ProxyError':
							sys.stderr.write('Crawling %s failed due to proxy server error. Ensure proxy server is running and is stable\n'%(urls[i]))
						else:
							sys.stderr.write('Crawling %s failed after 3 attempts (%s exception encountered on third attempt)\n'%(urls[i],type(ex).__name__))
		except requests.exceptions.URLRequired:
			sys.stderr.write('Crawling %s failed due to "URLRequired" error: URL is invalid\n'%(urls[i]))
		except requests.exceptions.MissingSchema:
			sys.stderr.write('Crawling %s failed due to "MissingSchema" error: URL is invalid\n'%(urls[i]))
		except requests.exceptions.TooManyRedirects:
			sys.stderr.write('Crawling %s failed due to too many redirects encountered\n'%(urls[i]))
		except requests.exceptions.ReadTimeout:
			sys.stderr.write('Crawling %s failed due to a read timeout\n'%(urls[i]))
		except requests.exceptions.Timeout:
			sys.stderr.write('Crawling %s timed out and failed\n'%(urls[i]))
		except Exception as ex:
			try:
				sess.get(urls[i],allow_redirects=redirects,timeout=timeout)
			except:
				try:
					sess.get(urls[i],allow_redirects=redirects,timeout=timeout)
				except Exception as ex:
					if type(ex1).__name__=='ProxyError':
						sys.stderr.write('Crawling %s failed due to proxy server error. Ensure proxy server is running and is stable\n'%(urls[i]))
					else:
						sys.stderr.write('Crawling %s failed after 3 attempts (%s exception encountered on third attempt)\n'%(urls[i],type(ex).__name__))
		jar.clear()
		i+=1

def _crawl_with_curl(urls,proxy,user_agent,redirects,timeout):
	curl_args = ['curl','-k','--proxy',proxy,'-m',str(timeout)]
	if user_agent:
		curl_args += ['-A',user_agent]
	if redirects:
		curl_args += ['-L']
	
	i=0
	while i<len(urls):
		urls[i] = urls[i].strip()
		curl_args.append(urls[i])
		#s = subprocess.run(curl_args,shell=False,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False)
		s = subprocess.run(curl_args,shell=False,check=False)
		if s.returncode == 5:
			sys.stderr.write('Problem detected with proxy server at %s (proxy address could not be resolved)!. Ensure proxy address is correct and re-execute script!\n'%(proxy))
			sys.exit(7)
		elif s.returncode == 7:
			if i==0:
				sys.stderr.write('Problem detected with proxy server at %s (connection refused)!. Ensure proxy address is correct and proxy server is running, then re-execute script!\n'%(proxy))
				sys.exit(7)
			else:
				sys.stderr.write('Crawling %s failed due to proxy server error. Ensure proxy server is running and is stable\n'%(urls[i]))
		elif s.returncode == 56:
			if s.stderr != None:
				if 'from proxy' in s.stderr.decode('utf-8'):
					sys.stderr.write('Problem detected with proxy server at %s (unexpected response). Ensure proxy server is running and is stable\n'%(proxy))
		curl_args.pop(len(curl_args)-1)
		i+=1

if __name__ == '__main__':
	if len(sys.argv)<3:
		sys.stderr.write('Usage: %s [OPTIONS] urls.txt http_proxy_address\n'%(sys.argv[0]))
		sys.stderr.write('Options:\n\t--crawler=CRAWLER: use CRAWLER ("requests" for python-requests; "curl" for curl) to crawl URLs (default is to use python-requests)\n')
		sys.stderr.write('\t--user-agent=USERAGENT: use specific User-Agent instead of crawler default ("python-requests/VERSION" for python-requests or "curl/VERSION" for curl)\n')
		sys.stderr.write('\t--no-redirects: do not follow redirects (default behavior is to follow redirects)\n')
		sys.stderr.write('\t--timeout=SECONDS: set request timeout to SECONDS seconds (default: 15 seconds)\n')
		sys.stderr.write('\n"urls.txt" can be specified as "-" to read input URLs from stdin instead\n')
		sys.exit(1)
	
	crawler = 'requests'
	user_agent = ''
	redirects = True
	timeout = 15
	proxy = None
	pr = up.urlparse(sys.argv[len(sys.argv)-1])
	if (pr.scheme == '') and (pr.netloc == ''):
		sys.stderr.write('Invalid HTTP/HTTPS proxy server address \'%s\': must be in format protocol://host:port with protocol being http or https\n'%(sys.argv[2]))
		sys.exit(2)
	elif (pr.scheme != 'http') and (pr.scheme != 'https'):
		sys.stderr.write('Invalid HTTP/HTTPS proxy server address \'%s\': must be in format protocol://host:port with protocol being http or https\n'%(sys.argv[2]))
		sys.exit(2)
	else:
		proxy = up.urlunparse(pr._replace(path='',params='',query='',fragment='')).strip()
	filename = sys.argv[len(sys.argv)-2]
	i=1
	while i<len(sys.argv)-2:
		arg_split = sys.argv[i].split('=',1)
		if arg_split[0] == '--crawler':
			if arg_split[1] == 'curl':
				crawler = 'curl'
				import subprocess
				try:
					subprocess.run('curl',shell=False,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
				except FileNotFoundError:
					sys.stderr.write('curl executable not found on system! Ensure it is installed and correctly added to the PATH environment variable!\n')
					sys.exit(4)
			elif arg_split[1] != 'requests':
				sys.stderr.write("Invalid CRAWLER value: '%s'\n"%(arg_split[1]))
				sys.exit(5)
		elif arg_split[0] == '--user-agent':
			user_agent = arg_split[1]
		elif arg_split[0] == '--no-redirects':
			redirects = False
		elif arg_split[0] == '--timeout':
			try:
				timeout = int(arg_split[1])
			except:
				sys.stderr.write("Invalid SECONDS value '%s'\n"%(arg_split[1]))
				sys.exit(5)
		else:
			sys.stderr.write("Unknown option: '%s'\n"%(sys.argv[i]))
			sys.exit(5)
		i+=1
	
	if crawler == 'curl':
		import subprocess
		try:
			subprocess.run('curl',shell=False,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		except FileNotFoundError:
			sys.stderr.write('curl executable not found on system! Ensure it is installed and correctly added to the PATH environment variable!\n')
			sys.exit(4)
	else:
		try:
			import requests
		except:
			sys.stderr.write('Script requires python-requests package! Please install it via:\n\tpip install python-requests\n')
			sys.exit(4)
		requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
	
	infile = sys.stdin
	if filename != '-':
		try:
			infile = open(filename,'r')
		except:
			sys.stderr.write("Cannot open file %s\n"%(filename))
			sys.exit(3)
	urls = infile.readlines()
	if infile != sys.stdin:
		infile.close()
	
	blank = 0
	i=0
	while i<len(urls):
		urls[i] = urls[i].strip()
		if len(urls[i])==0:
			blank+=1
		i+=1
	if len(urls)>0:
		sys.stdout.write('%i URLs read from %s for crawling\n'%(len(urls)-blank,'stdin' if filename=='-' else filename))
	else:
		sys.stderr.write('No URLs read from %s, so nothing to crawl\n'%('stdin' if filename=='-' else filename))
		sys.exit(6)
	
	if crawler == 'requests':
		_crawl_with_requests(urls,proxy,user_agent,redirects,timeout)
	else:
		_crawl_with_curl(urls,proxy,user_agent,redirects,timeout)
