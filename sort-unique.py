#! /usr/bin/env python3

import sys
import urllib.parse as up
import re

def _is_in_scope(url,scope):
	if scope == None:
		return True #No scope set, so everything is in scope
	elif scope == []:
		return True #No scope set, so everything is in scope
	u = up.urlparse(url.strip())
	
	for s in scope:
		protocol = None
		if '://' in s:
			s_split = s.split('://',1)
			protocol = s_split[0]
			s = s_split[1]
			
		if u.netloc == s: 
			if (protocol != None) and (u.scheme != protocol): #hostname matches but protocol does not: not in scope, check others (if any)
				continue
			return True #hostname matches and protocols are ignored: in scope, stop checking
		else:
			try:
				if (s.index('*.') == 0) and (len(s)>2):
					s_esc = re.escape(s[2:])
					if re.match('(.+\.%s)|(^%s)'%(s_esc,s_esc),u.netloc): #URL hostname matches domain and any subdomain: in scope
						return True
			except ValueError: #hostname does not start with wildcard, so not in scope
				continue
	return False

def unique(lines,scope=None):
	o = []
	i=0
	while i<len(lines):
		lines[i] = lines[i].strip()
		if len(lines[i])>0:
			if (lines[i] not in o) and (_is_in_scope(lines[i],scope)):
				o += [lines[i]]
		i+=1
	return o

def add_base(lines):
	o = []
	i=0
	while i<len(lines):
		lines[i] = lines[i].strip()
		if len(lines[i])>0:
			if lines[i] not in o:
				o += [lines[i]]
			r = up.urlparse(lines[i])
			url = up.urlunparse(r._replace(query=''))
			if url not in o:
				o += [url]
		i+=1
	return o

def add_redir_dirs(lines):
	o = []
	i=0
	while i<len(lines):
		lines[i] = lines[i].strip()
		if len(lines[i])>0:
			if lines[i] not in o:
				o += [lines[i]]
			r = up.urlparse(lines[i])
			p = r.path.rstrip('/')
			if len(p)>0:
				url = up.urlunparse(r._replace(path=r.path.rstrip('/'),query=''))
				if url not in o:
					o += [url]
		i+=1
	return o

def strip_query(lines):
	o = []
	i=0
	while i<len(lines):
		lines[i] = lines[i].strip()
		if len(lines[i])>0:
			r = up.urlparse(lines[i])
			url = up.urlunparse(r._replace(query=''))
			if url not in o:
				o += [url]
		i+=1
	return o

def strip_same_parameters(lines):
	a = {}
	o = []
	
	i=0
	while i<len(lines):
		lines[i] = lines[i].strip()
		if len(lines[i])>0:
			r = up.urlparse(lines[i])
			url = up.urlunparse(r._replace(query=''))
			
			try:
				url_qsl = a[url]
				qsr = up.parse_qsl(r.query)
				match = False
				j=0
				while j<len(url_qsl):
					url_qsr = up.parse_qsl(url_qsl[j])
					if len(qsr) == len(url_qsr):
						param_match = True
						k=0
						while k<len(qsr):
							if qsr[k][0] != url_qsr[k][0]:
								param_match = False
							k+=1
						if param_match:
							match = True
					j+=1
				if not match:
					url_qsl += [r.query]
					a[url] = url_qsl
			except KeyError:
				if r.query != '':
					a[url] = [r.query]
				else:
					a[url] = ['']
		i+=1
	
	urls = list(a.keys())
	i=0
	while i<len(urls):
		url_qsl = a[urls[i]]
		r = up.urlparse(urls[i])
		j=0
		while j<len(url_qsl):
			o += [up.urlunparse(r._replace(query=url_qsl[j]))]
			j+=1
		i+=1
	return o

if __name__ == '__main__':
	if len(sys.argv)<2:
		sys.stderr.write("Usage: %s [OPTIONS] infile.txt\n"%(sys.argv[0]))
		sys.stderr.write("Options:\n")
		sys.stderr.write("\t--outfile=OUTFILE: write output results to OUTFILE, rather than overwrite infile.txt\n")
		sys.stderr.write("\t--scope=SCOPE: limit results to those covered under SCOPE (can either be a hostname or protocol://hostname; SCOPE with path and/or query string is not supported)\n")
		sys.stderr.write("\t--base-urls-only: Remove all query strings and only output unique base URLs; enabling this ignores all other options besides --outfile and --scope\n")
		sys.stderr.write("\t--add-base-urls: Add all URLs with query strings removed to results\n")
		sys.stderr.write("\t--unique-params: Output unique URLs with unique parameter names, counts, and orders\n")
		sys.stderr.write("\t--add-redir-dirs: Add directory URLs with trailing '/' omitted (attempting to initiate HTTP 301 redirect)\n")
		sys.stderr.write("\nDefault options are to overwrite input file with unique values only\n")
		sys.exit(1)
	
	out_filename = sys.argv[len(sys.argv)-1]
	add_base_urls = False
	base_urls_only = False
	unique_params = False
	redir_dirs = False
	scope = None
	if len(sys.argv)>2:
		i=1
		while i<len(sys.argv)-1:
			arg_split = sys.argv[i].split('=')
			if arg_split[0] == '--outfile': #do not overwrite original file, save results to new file
				if len(arg_split)>2: #if out filename contains '=' character
					arg_split[1] = '='.join(arg_split[1:])
				out_filename = arg_split[1]
			elif arg_split[0] == '--scope':
				scope = []
				if len(arg_split)>2: #if scope input contains '=' character
					arg_split[1] = '='.join(arg_split[1:])
				s_split = arg_split[1].split(',')
				for h in s_split:
					s = up.urlparse(h)
					if (s.scheme == '') and (s.netloc == '') and (s.path != ''):
						s_split = s.path.split('/')
						scope += [s_split[0].strip()]
					elif (s.scheme == '') and (s.netloc != ''):
						scope += [s.netloc.strip()]
					elif (s.scheme != '') and (s.netloc != ''):
						scope += [up.urlunparse(s._replace(path='',params='',query='',fragment='')).strip()]
			elif arg_split[0] == '--base-urls-only':
				base_urls_only = True
			elif arg_split[0] == '--add-base-urls':
				add_base_urls = True
			elif arg_split[0] == '--unique-params':
				unique_params = True
			elif arg_split[0] == '--add-redir-dirs':
				redir_dirs = True
			else:
				sys.stderr.write("Unknown option: %s"%(sys.argv[i]))
				sys.exit(2)
			i+=1
	
	infile = sys.stdin
	if out_filename == '-':
		sys.stderr.write("Invalid option: cannot read from stdin without specifying \'--outfile=OUTFILE\' option, or with \'--outfile=-\' option.\n")
		sys.exit(3)
	if sys.argv[len(sys.argv)-1] != '-':
		infile = open(sys.argv[len(sys.argv)-1],'r')
	lines = infile.readlines()
	if infile != sys.stdin:
		infile.close()
	
	results = []
	if base_urls_only:
		results += strip_query(lines)
	else:
		if add_base_urls:
			results += add_base(lines)
		if unique_params:
			results += strip_same_parameters(lines)
		if redir_dirs:
			results += add_redir_dirs(lines)
		if (add_base_urls or unique_params or redir_dirs) != True: #no additional options were set
			results = lines
	results = unique(results,scope)
	results.sort()
	
	outfile = open(out_filename,'w')
	i=0
	while i<len(results):
		outfile.write("%s\n"%(results[i]))
		i+=1
	outfile.close()
