# "Scaling Garbanzo" Scripts
Collection of homegrown scripts I had not seen or tracked down elsewhere

## Scripts

* **generate-4096-burp-ca.sh:** Generate a self-signed 4096-bit CA certificate for use in Burp Suite. Has proven helpful for mobile application testing.
* **host-google-search.py:** Perform a "site:" google search and print out the results to the terminal and to a file. Supports "inurl:" and "-inurl:" options (see command Usage). Performs search via googlesearch-python 1.0.1 (see command Usage for recommended installation commands).
* **sort-unique.py:** Read a txt file, sort the lines, and remove duplicates, and remove blank links (nearly identical to *nix "sort" utility by default). Contains special options specifically for sorting, expanding, and filtering full HTTP/HTTPS URLs (see command Usage).
* **url-crawl.py:** Issue GET requests through a proxy to a list of full URLs read in from a file. Crawling performed via Python Requests or curl. Useful for populating Burp Suite Target tab with requests/responses (in place of built-in crawling), especially on Windows systems where bash one-liners are not available.

## Disclaimer
The developer provides the software for free without warranty, and assumes no responsibility for any damage caused to systems by using the software. It is the responsibility of the user to abide by all local, state and federal laws while using the software.


