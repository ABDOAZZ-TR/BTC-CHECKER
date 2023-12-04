# pip install base58 / ecdsa
# tested in python 3
#hackers are using this methot for finding btc address. Dont trust BTC and other coins

import os, binascii, hashlib, base58, ecdsa, requests

from bs4 import BeautifulSoup

import time


def ripemd160(x):
    d = hashlib.new('ripemd160')
    d.update(x)
    return d


num_keys = int(input('Enter the number of wallets to generate: '))
for n in range(num_keys):

    # generate private key , uncompressed WIF starts with "5"
    priv_key = os.urandom(32)
    print(f'Generating wallet {n+1}/{num_keys}...')
    fullkey = '80' + binascii.hexlify(priv_key).decode('utf-8')
    sha256a = hashlib.sha256(binascii.unhexlify(fullkey.encode('utf-8'))).hexdigest()
    sha256b = hashlib.sha256(binascii.unhexlify(sha256a.encode('utf-8'))).hexdigest()
    WIF = base58.b58encode(binascii.unhexlify(fullkey.encode('utf-8') + sha256b[:8].encode('utf-8')))
    print('Wallet successfully generated.')

    # get public key , uncompressed address starts with "1"
    sk = ecdsa.SigningKey.from_string(priv_key, curve=ecdsa.SECP256k1)
    vk = sk.get_verifying_key()
    publ_key = '04' + binascii.hexlify(vk.to_string()).decode('utf-8')
    hash160 = ripemd160(hashlib.sha256(binascii.unhexlify(publ_key)).digest()).digest()
    publ_addr_a = b"\x00" + hash160
    checksum = hashlib.sha256(hashlib.sha256(publ_addr_a).digest()).digest()[:4]
    publ_addr_b = base58.b58encode(publ_addr_a + checksum)
    i = n + 1
    # print('Private Key    ', str(i) + ": " + WIF)
    # print("Bitcoin Address", str(i) + ": " + publ_addr_b)

    url = ("https://www.blockchain.com/btc/address/%s" % publ_addr_b)
    html = requests.get(url, headers={'User-agent': 'Mozilla/5.0'}).text
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("div", {"class": "col-md-4 col-xs-12"})
    if table is not None:
        value2 = table.findAll('td')[4].text.split(' ')[0].strip()
        value = table.findAll('td')[7].text.split(' ')[0].strip()

        amount = float(value)
        amount2 =float(value2)

    file1 = open("BTC_PRV_ADR.txt", "a")
file1.write('private Key = ' + WIF.decode('utf-8') + ' address = ' + publ_addr_b.decode('utf-8') + ' ' + str(amount) + '\n')

if amount > 0:
        print("------------------")
        print("      FOUND       ")
        print("Private Key       = ") + WIF
        print("Address           = 0x") + publ_addr_b
        print("Ethereum Amount   = ") + str(amount)
        print("------------------")

        file2 = open("BTC_Found.txt", "a")
        file2.write(WIF + " " + publ_addr_b + " " + str(amount) + "\n")
        file2.close()
else:
        print(str(i) + (" ") + ("prv_key = ") + WIF + (" ") + ("addr = ") + publ_addr_b + ("  ") + str(
            amount)+("   ")+("Toplam Alinan =")+str(amount2))
time.sleep(0.2)

file1.close()