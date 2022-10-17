#! /bin/bash

#ensure openssl, wget, and sed are installed on the system; quit if any are not installed
which openssl 2>&1 > /dev/null
if [ $? -gt 0 ]
then
	echo "Script requires openssl to function properly! Install openssl and try again!"
	exit 1
fi
which wget 2>&1 > /dev/null
if [ $? -gt 0 ]
then
	echo "Script requires wget to function properly! Install wget and try again!"
	exit 1
fi
which sed 2>&1 > /dev/null
if [ $? -gt 0 ]
then
	echo "Script requires sed to function properly! Install sed and try again!"
	exit 1
fi

#remove data from previous executions of script
rm -rf ca 2>/dev/null
rm ca.cert.p12 2>/dev/null

#create temp directory
mkdir ca
cd ca

#get timezone data based on current external IP address
wget -q -O tz.txt https://ipinfo.io
CN=`grep "\"country\"" tz.txt | cut -d":" -f 2 | cut -d "\"" -f 2`
RN=`grep "\"region\"" tz.txt | cut -d":" -f 2 | cut -d "\"" -f 2`
CT=`grep "\"city\"" tz.txt | cut -d":" -f 2 | cut -d "\"" -f 2`

#create openssl.cnf configuration file by downloading template and updating with retrieved timezone data
#set CommonName with first command-line argument, and emailAddress with second command-line argument
wget -q -O openssl.cnf https://jamielinux.com/docs/openssl-certificate-authority/_downloads/root-config.txt
sed -i -e "s/\/root\/ca/`pwd | sed -e 's/\//\\\\\//g'`/" openssl.cnf
sed -i -e "s/countryName_default\s\{0,\}=.*/countryName_default = $CN/" openssl.cnf
sed -i -e "s/stateOrProvinceName_default\s\{0,\}=.*/stateOrProvinceName_default = $RN/" openssl.cnf
sed -i -e "s/localityName_default\s\{0,\}=.*/localityName_default = $CT/" openssl.cnf
sed -i -e "s/0\.organizationName_default\s\{0,\}=.*/0\.organizationName_default = Pentest Ltd\./" openssl.cnf
sed -i -e "s/organizationalUnitName_default\s\{0,\}=.*/organizationalUnitName_default = Pentest Ltd\./" openssl.cnf
sed -i -e "s/emailAddress_default\s\{0,\}=.*/commonName_default = $1\nemailAddress_default = $2/" openssl.cnf
unset CN RN CT

#generate .p12 keystore file ca.cert.p12
mkdir certs crl newcerts private
chmod 700 private
touch index.txt
echo 1000 > serial
export PK=`openssl rand -base64 12 | tr -d "\n"`
openssl genrsa -aes256 -passout env:PK -out private/ca.key.pem 4096 2>&1 > /dev/null
echo -en "\n\n\n\n\n\n\n" | openssl req -config openssl.cnf -key private/ca.key.pem -passin env:PK -new -x509 -days 7300 -sha256 -extensions v3_ca -out certs/ca.cert.pem 2>&1 > /dev/null
openssl x509 -outform PEM -in certs/ca.cert.pem -out certs/ca.crt
openssl pkey -in private/ca.key.pem -passin env:PK -out private/ca.key
unset PK
export P12=`openssl rand -base64 12`
openssl pkcs12 -export -out certs/ca.cert.p12 -passout env:P12 -inkey private/ca.key -in certs/ca.crt
mv certs/ca.cert.p12 ../.
cd ..

#remove temp directory
rm -rf ca

#print success message
echo -e "\n\nPKCS#12 keystore file (`pwd`/ca.cert.p12) generated with password $P12\n"
echo "To import ca.cert.p12 into Burp Proxy, following these instructions:"
echo "   Select \"Import / export CA certificate\" option in Burp Proxy Options menu"
echo "   Select \"Certificate and private key from PKCS#12 keystore\" option under \"Import\" and click Next"
echo "   Select ca.cert.p12 file and enter password $P12"
unset P12

