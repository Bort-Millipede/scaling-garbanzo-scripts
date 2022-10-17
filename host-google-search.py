#! /usr/bin/env python3

import sys
import os
try:
	from googlesearch import search
except:
	sys.stderr.write("Script requires googlesearch-python v1.0.1 package, which also requires beautifulsoup4 and requests! Please install these via:\n")
	sys.stderr.write("\tpip3 install beautifulsoup4\n\tpip install requests\n\tpip3 install --no-deps googlesearch-python==1.0.1\n")
	sys.exit(1)

if __name__ == '__main__':
	if len(sys.argv)<3:
		sys.stderr.write("Automated Google Search by host (\"site:www.abc.com\")\n")
		sys.stderr.write("Usage: %s [OPTIONS] hostname number_of_expected_results\n"%(sys.argv[0]))
		sys.stderr.write("\nOptions:\n\t--inurl=PATH1,PATH2,...,PATHn: include \"inurl:\" option(s) to restrict results to URLs containing PATH1,...,PATHn\n")
		sys.stderr.write("\t--notinurl=PATH1,PATH2,...,PATHn: include \"-inurl:\" option(s) to restrict results to URLs NOT containing PATH1,...,PATHn\n")
		sys.stderr.write("\t--outfile=OUTFILE: override default \"hostname_google_links.txt\" out filename with OUTFILE\n")
		sys.stderr.write("\nUsage Notes:\n* It is recommended to perform the intended Google search in a web browser first, then observe the number of results pages and specify the \"number_of_expected_results\" option as [number_of_pages]*10\n")
		sys.stderr.write("* To avoid potentially having your IP blacklisted by Google (HTTP 429 error), it is recommended to only execute this script a minimal number of times and only after performing the manual search in a web browser first\n")
		sys.exit(2)
	
	hostname = sys.argv[len(sys.argv)-2]
	filename = '%s_google_links.txt'%(hostname)
	inurl = None
	notinurl = None
	if len(sys.argv)>3:
		i=1
		while i<len(sys.argv)-2:
			j=0
			arg_split = sys.argv[i].split('=',1)
			if arg_split[0] == '--outfile':
				filename = arg_split[1]
			elif arg_split[0] == '--inurl':
				inurl = arg_split[1].split(',')
				while j<len(inurl):
					inurl[j] = inurl[j].strip()
					if ' ' in inurl[j]:
						sys.stderr.write("Invalid option: \"inurl:\" operand \"%s\" contains space(s) which is unsupported\n"%(inurl[j]))
						sys.exit(3)
					j+=1
			elif arg_split[0] == '--notinurl':
				notinurl = arg_split[1].split(',')
				while j<len(notinurl):
					notinurl[j] = notinurl[j].strip()
					if ' ' in notinurl[j]:
						sys.stderr.write("Invalid option: \"-inurl:\" operand \"%s\" contains space(s) which is unsupported\n"%(notinurl[j]))
						sys.exit(3)
					j+=1
			else:
				sys.stderr.write("Unknown option: %s\n"%(sys.argv[i]))
				sys.exit(3)
			i+=1
	
	num_results = None
	try:
		num_results = int(sys.argv[len(sys.argv)-1])
	except(ValueError):
		sys.stderr.write("invalid number %s\n"%(sys.argv[len(sys.argv)-1]))
		sys.exit(4)
	
	query = ["site:%s"%(hostname)]
	if inurl != None:
		i=0
		while i<len(inurl):
			query += ["inurl:%s"%(inurl[i])]
			i+=1
	if notinurl != None:
		i=0
		while i<len(notinurl):
			query += ["-inurl:%s"%(notinurl[i])]
			i+=1
	query = ' '.join(query)
	
	outfile = open(filename,'w')
	written = False
	results = None
	try:
		results = search(query,num_results=num_results)
		if len(results)>0:
			results.sort()
			i=0
			while i<len(results):
				sys.stdout.write("%s\n"%(results[i]))
				outfile.write('%s\n'%(results[i]))
				written = True
				i+=1
		else:
			sys.stderr.write("search returned 0 results\n")
	except KeyboardInterrupt:
		pass
	except Exception as e:
		sys.stderr.write("search failed (Unknown Error: %s)\n"%(type(e).__name__))
	
	outfile.close()
	if written:
		sys.stderr.write("%i results saved to file %s\n"%(len(results),filename))
	else:
		os.remove(filename)

