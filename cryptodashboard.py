import requests
import json
import sys
import time
import argparse

###########################################################################################
#                                 DPoS Dashboard
#                                 Version 0.97
#                                 By Delegate Thamar
###########################################################################################

if sys.version_info[0] < 3:
    print('python2 not supported, please use python3')
    sys.exit()

# Parse command line args
parser = argparse.ArgumentParser(description='Crypto Dashboard')
parser.add_argument('-c', metavar='config.json', dest='cfile', action='store',
                    default='config.json',
                    help='set a config file (default: config.json)')
# parser.add_argument('-y', dest='alwaysyes', action='store_const',
#                     default=False, const=True,
#                     help='automatic yes for log saving (default: no)')

args = parser.parse_args()

# Load the config file
try:
    conf = json.load(open(args.cfile, 'r'))
except:
    print('Unable to load config file.')
    sys.exit()

if 'logfile' in conf:
    LOGFILE = conf['logfile']
else:
    LOGFILE = 'cdashboard.json'

# Load the blockchain explorer db file
try:
    blockchainexplorerdb = json.load(open("blockchainexplorer.json", 'r'))
except:
    print('Unable to load the blockchain explorer db file: blockchainexplorer.json.')
    sys.exit()


def handle_error(ex, msg, exit):
    error_msg = time.strftime('%Y-%m-%d %H:%M:%S: ') + msg
    if ex is not None:
        error_msg += ': ' + str(ex)
    print(error_msg)
    if exit:
        sys.exit()


def loadLog():
    try:
        data = json.load(open(LOGFILE, 'r'))
    except:
        data = {
            "cryptodashboard_file_version": 0.95,
            "lasttimecalculated": 0,
            "coins": {}
        }
    return data


def savelog(log, filename):
    json.dump(log, open(filename, 'w'), indent=4, separators=(',', ': '))


def get_node_url(url):
    node_url = url
    if not node_url.startswith('http'):
        handle_error(None, 'node_url needs to be in the format http://localhost:<port>', False)
    if node_url.endswith('/'):
        node_url = node_url[:-1]

    return node_url


##############################################################################3
# get_actual_share_perc
# http: // verifier.dutchpool.io / lwf / report.json
# http: // verifier.dutchpool.io / shift / report.json
# forg? = not forging?
# n.a. = not available / wrong verifier link

def get_actual_share_perc(delegatename, coinname):
    verifierbaseurl = 'http://verifier.dutchpool.io/' + coinname.lower() + "/report.json"
    verified_sharing_perc = "forg?"
    try:
        response = requests.get(verifierbaseurl)
        if response.status_code == 200:
            response_json = response.json()
            for item in response_json["delegates"]:
                if item["name"] == delegatename:
                    verified_sharing_perc = item["percentage"]
                    break
            return str(verified_sharing_perc)
        else:
            print("Error: " + verifierbaseurl + ' ' + str(response.status_code) + ', response not 200')
            return "n.a."
    except:
        print("Error: url is probably not correct: " + verifierbaseurl)
        return "n.a."


##############################################################################3
# get_walletbalance
# This function expects an url which is complete and  returns only one number, the balance!
# most API's have two ways to show balance's: a complete website or explicit values of the address.
# You need the API part which shows the explicit values.
#   "explorer": {
#     "bitcoin blockchain": {
#       "exploreraddress": "https://blockchain.info",
#       "api-getbalance": "/q/addressbalance/<address>",
#       "outputvaluesatoshi": "true"
#     },
#     "ether blockchain": {
#       "exploreraddress": "https://api.ethplorer.io",
#       "api-getbalance": "/getAddressInfo/<address>?apiKey=freekey",
#       "1-json-eth": "ETH",
#       "2-json-eth-balance": "balance",
#       "outputvaluesatoshi": "false"
#     }
#   }


def get_walletbalance(url, address):
    walletbalance_exploreraddress = url + address
    # get the base_url of the url which is provided
    from urllib.parse import urlsplit
    base_url = get_node_url("{0.scheme}://{0.netloc}/".format(urlsplit(url)))
    returnfloatdevide = 1

    for explorer in blockchainexplorerdb["explorer"]:
        if blockchainexplorerdb["explorer"][explorer]["exploreraddress"] == base_url:
            walletbalance_exploreraddress = base_url + blockchainexplorerdb["explorer"][explorer][
                "api-getbalance"].replace("<address>", address)
            if blockchainexplorerdb["explorer"][explorer]["outputvaluesatoshi"].lower() == "true":
                returnfloatdevide = 100000000
            break

    try:
        response = requests.get(walletbalance_exploreraddress)
        if response.status_code == 200:
            response_json = response.json()

            # handle the specials: hopefuly not that much!!!
            if base_url == "https://api.ethplorer.io":
                j1 = blockchainexplorerdb["explorer"]["ether blockchain"]["1-json-eth"]
                j2 = blockchainexplorerdb["explorer"]["ether blockchain"]["2-json-eth-balance"]
                response_json_value = response_json[j1][j2]
            elif base_url == "https://explorer.zensystem.io":
                j1 = blockchainexplorerdb["explorer"]["zencash blockchain"]["json-level-1"]
                response_json_value = response_json[j1]
            else:
                response_json_value = response_json

            return float(response_json_value) / returnfloatdevide
        else:
            return float(0)
    except:
        return float(0)


##############################################################################
# get_walletlasttransaction
# This function expects an url which is complete and  returns two numbers, the time and the amount!
# This function expects
def get_walletlasttransaction(url, walletaddress):
    # get the base_url of the url which is provided
    from urllib.parse import urlsplit
    base_url = "{0.scheme}://{0.netloc}/".format(urlsplit(url))

    amountreceived = float(0.0)

    # Get the latest transaction for this Address
    try:
        response = requests.get(base_url + "ext/getaddress/" + walletaddress)
        if response.status_code == 200:
            response_json = response.json()
            last_txs_nr = len(response_json["last_txs"])
            addresses = response_json["last_txs"][last_txs_nr - 1]["addresses"]

            # Get with this address the latest Blockhash for this Address
            response2 = requests.get(base_url + "api/getrawtransaction?txid=" + addresses + "&decrypt=1")
            if response2.status_code == 200:
                response_json2 = response2.json()
                blockhash = response_json2["blockhash"]

                # Get with this address the latest time and amount for the last txid
                response3 = requests.get(base_url + "api/getblock?hash=" + blockhash)
                if response3.status_code == 200:
                    response_json3 = response3.json()
                    timereceived = response_json3.get("time", 0)
                    for payment in response_json2["vout"]:
                        x = payment["scriptPubKey"].get("addresses")
                        if x:
                            for voutaddresses in x:
                                if voutaddresses == walletaddress:
                                    amountreceived = payment["value"]
                    return timereceived, amountreceived
                else:
                    return 0, 0
            else:
                return 0, 0
        else:
            if base_url == "https://chainz.cryptoid.info/":
                # Get the latest transaction for this Address
                # Currently an API key is needed and is not available to receive by email (dd April 9, 2018)
                #            response = requests.get(base_url + "???" + walletaddress)
                #            if response.status_code == 200:
                #                response_json = response.json()
                return 0, 0
            return 0, 0
    except:
        return 0, 0


##############################################################################
# compare dictionary's
# x = dict(a=1, b=2)
# y = dict(a=2, b=2)
# added, removed, modified, same = dict_compare(x, y)
#############################################################################
def dict_compare(d1, d2):
    d1_keys = set(d1.keys())
    d2_keys = set(d2.keys())
    intersect_keys = d1_keys.intersection(d2_keys)
    added = d1_keys - d2_keys
    removed = d2_keys - d1_keys
    modified = {o: (d1[o], d2[o]) for o in intersect_keys if d1[o] != d2[o]}
    same = set(o for o in intersect_keys if d1[o] == d2[o])
    return added, removed, modified, same


##############################################################################
# get_dpos_api_info
# specific for Dpos nodes and their API
# node_url: is the base of the API without the /, which is stripped earlier
# address: can be several identifications: the public address; the publickey
# api_info : indicates which part of the API we use (see the elif statement)
#
# a bit adhoc, but it should work https://node08.lisk.io/api/blocks

# https://wallet.mylisk.com/api/transactions?recipientId=139289198949001083L&toTimestamp=1540633350&limit=10&offset=0&sort=amount%3Adesc
# https://explorer.mylisk.com/api/getBlockStatus
# https://node01.lisk.io/api/transactions?senderIdOrRecipientId=139289198949001083L&limit=10&offset=0&sort=timestamp:desc

# /api/blocks?limit=10&offset=0&generatorPublicKey=ec111c8ad482445cfe83d811a7edd1f1d2765079c99d7d958cca1354740b7614&sort=timestamp%3Aasc

def get_dpos_api_info_lisk(node_url, address, api_info):

    if api_info == "balance" or api_info == "publicKey":
        request_url = node_url + '/api/accounts?address=' + address
    elif api_info == "delegates":
        request_url = node_url + '/api/delegates?address=' + address
    elif api_info == "forgingdelegates":
        request_url = node_url + '/api/delegates?offset=0&limit=101&sort=rank%3Aasc'
    elif api_info == "transactions":
        request_url = node_url + '/api/transactions?recipientId=' + address + '&limit=10&offset=0&sort=timestamp:desc'
    elif api_info == "epoch":
        request_url = node_url + '/api/getBlockStatus'
    elif api_info == "blocks":
        request_url = node_url + '/api/blocks?limit=10&offset=0&generatorPublicKey=' + address + '&sort=timestamp:desc'
    elif api_info == "voters":
        request_url = node_url + '/api/voters?address=' + address
    elif api_info == "votes":
        request_url = node_url + '/api/votes?address=' + address + '&offset=0&limit=101&sort=username%3Aasc'
    else:
        return ""

    try:
        response = requests.get(request_url)
        if response.status_code == 200:
            response_json = response.json()

            if api_info == "epoch":
                return response_json[api_info]
            elif response_json["data"]:
                if api_info == "publicKey":
                    return response_json["data"][0]["publicKey"]
                if api_info == "balance":
                    return response_json["data"][0][api_info]
                elif api_info == "voters":
                    return int(response_json["data"]["votes"])
                elif api_info == "votes":
                    return response_json["data"]["votes"]
                elif api_info == "blocks":
                    return response_json["data"][0]["timestamp"]
                elif api_info == "forgingdelegates":
                    return response_json["data"]
                elif api_info == "delegates" or api_info == "transactions":
                    return response_json["data"][0]
                else:
                    if api_info == "balance" or api_info == "voters":
                        return 0
                    return ""
            else:
                if api_info == "balance" or api_info == "voters":
                    return 0
                return ""
        else:
            print("Error (not 200): " + str(response.status_code) + ' URL: '
                  + request_url + ', response: ' + response.text)
            if api_info == "balance" or api_info == "voters":
                return 0
            return ""
    except:
        print("Error: url is probably not correct: " + request_url)
        # known case: with parameter 'delegates' and if there are no votes returned from API, this exception occurs
        if api_info == "balance" or api_info == "voters":
            return 0
        else:
            return ""


##############################################################################3
# get_dpos_api_info
# specific for Dpos nodes and their API
# node_url: is the base of the API without the /, which is stripped earlier
# address: can be several identifications: the public address; the publickey
# api_info : indicates which part of the API we use (see the elif statement)

def get_dpos_api_info(node_url, address, api_info):
    if api_info == "publicKey":
        request_url = node_url + '/api/accounts/getPublicKey?address=' + address
    elif api_info == "delegate":
        request_url = node_url + '/api/delegates/get?publicKey=' + address
    elif api_info == "accounts":
        request_url = node_url + '/api/delegates/voters?publicKey=' + address
    elif api_info == "blocks":
        request_url = node_url + '/api/blocks?generatorPublicKey=' + address
    elif api_info == "balance":
        request_url = node_url + '/api/accounts/getBalance?address=' + address
    elif api_info == "transactions":
        request_url = node_url + '/api/transactions?limit=1&recipientId=' + address + '&orderBy=timestamp:desc'
    elif api_info == "epoch":
        request_url = node_url + '/api/blocks/getEpoch'
    elif api_info == "delegates":
        if address == "":
            request_url = node_url + '/api/delegates'
        else:
            request_url = node_url + '/api/accounts/delegates?address=' + address
    else:
        return ""

    try:
        response = requests.get(request_url)
        if response.status_code == 200:
            response_json = response.json()
            if response_json['success']:
                return response_json[api_info]
            else:
                #                    print(request_url + ' ' + str(response.status_code) + ' Failed to get ' + api_info)
                if api_info == "balance":
                    return 0
                return ""
        else:
            print("Error (not 200): " + str(
                response.status_code) + ' URL: ' + request_url + ', response: ' + response.text)
            if api_info == "balance":
                return 0
            return ""
    except:
        print("Error: url is probably not correct: " + request_url)
        # known case: with parameter 'delegates' and if there are no votes returned from API, this exception occurs
        if api_info == "balance":
            return 0
        else:
            return ""


##############################################################################3
# get_dpos_private_vote_info
# specific for Dpos private addresses (if you mark your Delegate Address also a second time as private
# If you vote delegates, you want to keep track if they are still in forging position, besides the % they pay!
# This function checks the known DPoS systems in combination of the private DPoS Wallet address and its votes on Delegates
# load all the forging delegates
#
# function returns 2 values
#   1. the total number of votes a DPoS address in this ecosystem can cast
#   2. a list of names of delegates who are currently not forging (together with the current forging spot)
#
def get_dpos_private_vote_info(coin_nodeurl, address):
    amount_forging_delegates = len(get_dpos_api_info(coin_nodeurl, "", "delegates"))
    private_delegate_vote_info = get_dpos_api_info(coin_nodeurl, address, "delegates")

    # create a dict for the not forging names
    notforgingdelegates = {}

    for item in private_delegate_vote_info:
        if "rank" in item:
            rate = "rank"
        elif "rate" in item:
            rate = "rate"
        else:
            return len(private_delegate_vote_info), notforgingdelegates

        if item[rate] > amount_forging_delegates:
            notforgingdelegates[item["username"]] = item[rate]
    return len(private_delegate_vote_info), notforgingdelegates


def get_dpos_private_vote_info_lisk(coin_nodeurl, address):
    amount_forging_delegates = 101
    private_delegate_vote_info = get_dpos_api_info_lisk(coin_nodeurl, address, "votes")
    forging_delegates_info = get_dpos_api_info_lisk(coin_nodeurl, "", "forgingdelegates")

    # create a dict for the not forging names
    notforgingdelegates = {}
    forgingdelegatesnames = {}
    voteddelegates = {}

    for item in forging_delegates_info:
        forgingdelegatesnames.update({item["username"]: item["rank"]})

    for item in private_delegate_vote_info:
        if item["username"] not in forgingdelegatesnames:
            # get the rank of the not forgingdelegate
            delegate_info = get_dpos_api_info_lisk(coin_nodeurl, item["address"], "delegates")
            notforgingdelegates[item["username"]] = delegate_info["rank"]

    return len(private_delegate_vote_info), notforgingdelegates


def dashboard():
    from urllib.parse import urlsplit
    from datetime import datetime
    from operator import itemgetter
    import copy

    # read the json, this is the database of the dashbaord
    coininfo_output = loadLog()
    keep4history = 0

    # get current day in month (we don't need anything else)
    currentDay = datetime.now().day  # datetime's now is localized
    # get the day of the last run of the script from the "lasttimecalculated"
    if coininfo_output['lasttimecalculated'] > 0:
        timesampleday = datetime.fromtimestamp(coininfo_output['lasttimecalculated']).day

        # these are not the same anymore, this run will be the run at around 00:00 (if hourly scheduld) and will be marked
        # as a run to be archived if you want a daily archive with one day history samples
        if timesampleday != currentDay:
            keep4history = 1
    else:
        keep4history = 1


    # Update last time the cryptodashboard has run
    coininfo_output['lasttimecalculated'] = int(time.time())
    timestamp = coininfo_output['lasttimecalculated']

    timereceived = 0
    amountreceived = 0

    for item in conf["coins"]:
        coinitemexists = 0
        coin_explorerlink = ""
        share_perc = 0
        amountreceived = 0
        timereceived = 0
        share_perc = 0
        typeliskcoin = 0
        lastforgedblock_timestamp = 0

        if item in coininfo_output["coins"]:
            coinitemexists = 1

        # Section: dpos_delegate and dpos_private
        if conf["coins"][item]["cointype"] == "dpos_delegate" or conf["coins"][item]["cointype"] == "dpos_private":
            coin_nodeurl = get_node_url(conf["coins"][item]["node"])
            coin_explorerlink = copy.copy(conf["coins"][item].get("exploreraddress"))
            if coin_explorerlink == None:
                coin_explorerlink = copy.copy(coin_nodeurl.replace("wallet", "explorer"))

            if conf["coins"][item]["coin"].lower() == "lisk":
                typeliskcoin = 1
            if typeliskcoin == 1:
                # get the public key of this address
                coin_pubkey = get_dpos_api_info_lisk(coin_nodeurl, conf["coins"][item]["pubaddress"], "publicKey")
                if coin_pubkey == None:
                    coin_pubkey = ""

                balance = int(float(get_dpos_api_info_lisk(coin_nodeurl, conf["coins"][item]["pubaddress"], "balance"))) / 100000000

                # get all the delegate info
                coin_lisk_delegateinfo = get_dpos_api_info_lisk(coin_nodeurl, conf["coins"][item]["pubaddress"], "delegates")

                # get number of voters
                nrofvoters = int(get_dpos_api_info_lisk(coin_nodeurl, conf["coins"][item]["pubaddress"], "voters"))

                # get from a dpos address MaxNummerOfVotes you can cast and the names of the delegates who are currently not in the forging state with their forging position!
                nrofvotescasted, notforgingdelegates = get_dpos_private_vote_info_lisk(coin_nodeurl,
                                                                            conf["coins"][item]["pubaddress"])

                # get last transaction
                transactions = get_dpos_api_info_lisk(coin_nodeurl, conf["coins"][item]["pubaddress"], "transactions")
                if len(transactions) > 0:
                    amountreceived = int(transactions["amount"]) / 100000000

                    coin_epoch = get_dpos_api_info_lisk(coin_explorerlink, 0, "epoch")
                    # epoch "2016-05-24T17:00:00.000Z"
                    # convert the epoch time to a normal Unix time in sec datetime.strptime('1984-06-02T19:05:00.000Z', '%Y-%m-%dT%H:%M:%S.%fZ')
                    utc_dt = datetime.strptime(coin_epoch, '%Y-%m-%dT%H:%M:%S.%fZ')
                    # Convert UTC datetime to seconds since the Epoch and add the found transaction timestamp to get the correct Unix date/time in sec.
                    timereceived = (utc_dt - datetime(1970, 1, 1)).total_seconds() + transactions["timestamp"]

                # get the Date and Time of the last forged block of this delegate
                blocks_delegateinfo = get_dpos_api_info_lisk(coin_nodeurl, coin_pubkey, "blocks")
                if blocks_delegateinfo:
                    lastforgedblock_timestamp = (utc_dt - datetime(1970, 1, 1)).total_seconds() + blocks_delegateinfo

            else:
                # get the public key of this address
                coin_pubkey = get_dpos_api_info(coin_nodeurl, conf["coins"][item]["pubaddress"], "publicKey")
                if coin_pubkey == None:
                    coin_pubkey = ""

                # first check if url is working, if so, I assume other calls will also work ;-)
                # there are addresses (wallets) which don't have a pubkey; This address has never-ever sent earlier a transaction through the blockchain!

                # get the current balance of this address
                # todo : when wrong ip addres is filled-in in pubaddress ==> catch the error!
                balance = int(
                    float(get_dpos_api_info(coin_nodeurl, conf["coins"][item]["pubaddress"], "balance"))) / 100000000

                # get all the delegate info
                coin_delegateinfo = get_dpos_api_info(coin_nodeurl, coin_pubkey, "delegate")

                # get number of voters
                nrofvoters = len(get_dpos_api_info(coin_nodeurl, coin_pubkey, "accounts"))

                # get from a dpos address MaxNummerOfVotes you can cast and the names of the delegates who are currently not in the forging state with their forging position!
                nrofvotescasted, notforgingdelegates = get_dpos_private_vote_info(coin_nodeurl,
                                                                                  conf["coins"][item]["pubaddress"])

                # get last transaction
                transactions = get_dpos_api_info(coin_nodeurl, conf["coins"][item]["pubaddress"], "transactions")
                if len(transactions) > 0:
                    amountreceived = transactions[0]["amount"] / 100000000

                    coin_epoch = get_dpos_api_info(coin_nodeurl, 0, "epoch")
                    # convert the epoch time to a normal Unix time in sec datetime.strptime('1984-06-02T19:05:00.000Z', '%Y-%m-%dT%H:%M:%S.%fZ')
                    utc_dt = datetime.strptime(coin_epoch, '%Y-%m-%dT%H:%M:%S.%fZ')
                    # Convert UTC datetime to seconds since the Epoch and add the found transaction timestamp to get the correct Unix date/time in sec.
                    timereceived = (utc_dt - datetime(1970, 1, 1)).total_seconds() + transactions[0]["timestamp"]

                # get the Date and Time of the last forged block of this delegate
                blocks_delegateinfo = get_dpos_api_info(coin_nodeurl, coin_pubkey, "blocks")
                if blocks_delegateinfo:
                    lastforgedblock_timestamp = (utc_dt - datetime(1970, 1, 1)).total_seconds() + blocks_delegateinfo[0]["timestamp"]

            # todo get the next forger: not here, probably in a more faster updated cycle!
            # https://explorer.oxycoin.io/api/delegates/getNextForgers
            # https://wallet.oxycoin.io/api/delegates/getNextForgers?limit=201
            if conf["coins"][item]["cointype"] == "dpos_delegate":
                share_perc = conf["coins"][item].get("share_perc")

             # check if item/coin already exists? If not, add coin to the output list
            if coinitemexists != 1:
                coininfo_output["coins"][item] = {
                    "coin": conf["coins"][item]["coin"],
                    "cointype": conf["coins"][item]["cointype"],
                    "delegatename": "",
                    "explink": coin_explorerlink + "/address/" + conf["coins"][item]["pubaddress"],
                    "share_perc": share_perc,
                    "nrofvotescasted": 0,
                    "nrofnotforingdelegates": 0,
                    "notforgingdelegates": {},
                    "history": []
                }
            else:
                # these items can change now and then by the user...
                coininfo_output["coins"][item]["explink"] = coin_explorerlink + "/address/" + conf["coins"][item][
                    "pubaddress"]
                coininfo_output["coins"][item]["share_perc"] = share_perc

            # generic variable coin info
            coininfo_tocheck = {
                "timestamp": timestamp,
                "totalbalance": balance,
                "amountreceived": amountreceived,
                "timereceived": timereceived,
                "rank": 0,
                "approval": 0,
                "nrofvoters": 0,
                "producedblocks": 0,
                "missedblocks": 0,
                "lastforgedblock_timestamp": lastforgedblock_timestamp
            }

            # Specific delegate Dpos coin info
            if typeliskcoin == 1:
                if coin_lisk_delegateinfo != "":
                    coininfo_output["coins"][item]["delegatename"] = coin_lisk_delegateinfo["username"]
                    coininfo_tocheck["rank"] = coin_lisk_delegateinfo["rank"]
                    coininfo_tocheck["approval"] = coin_lisk_delegateinfo["approval"]
                    coininfo_tocheck["nrofvoters"] = nrofvoters
                    coininfo_tocheck["producedblocks"] = coin_lisk_delegateinfo["producedBlocks"]
                    coininfo_tocheck["missedblocks"] = coin_lisk_delegateinfo["missedBlocks"]
                    # todo                coininfo_tocheck["actual_share_perc"] = get_actual_share_perc(coin_delegateinfo["username"], conf["coins"][item]["coin"])

            elif coin_delegateinfo != "":
                coininfo_output["coins"][item]["delegatename"] = coin_delegateinfo["username"]
                coininfo_tocheck["rank"] = coin_delegateinfo["rate"]
                coininfo_tocheck["approval"] = coin_delegateinfo["approval"]
                coininfo_tocheck["nrofvoters"] = nrofvoters
                coininfo_tocheck["producedblocks"] = coin_delegateinfo["producedblocks"]
                coininfo_tocheck["missedblocks"] = coin_delegateinfo["missedblocks"]
#                coininfo_tocheck["actual_share_perc"] = get_actual_share_perc(coin_delegateinfo["username"], conf["coins"][item]["coin"])

            coininfo_output["coins"][item].update({"nrofvotescasted": nrofvotescasted})
            coininfo_output["coins"][item].update({"nrofnotforingdelegates": len(notforgingdelegates)})
            coininfo_output["coins"][item]["notforgingdelegates"] = notforgingdelegates

            # try to figure out the change of missedblocks between this sample and the previous
            # if missedblocksdelta24h > 0 we have an indication, delegate is missing blocks
            # previous sample:  coininfo_output["coins"][item]["missedblocks"]
            # current sample:   coininfo_tocheck["missedblocks"]
            # results:
            #   previous_sample > current_sample  ==> amount missed blocks is still increasing, Not good!
            #   previous sample <= current sample ==> amount missed blocks is the same or decreasing, Good!
            # color the output cell of this delegate! Red = increasing = 2; Green = steady or decreasing = 1; transparent = no blocks missing = 0
            setstatus = 0
            try:
                previous_sample = coininfo_output["coins"][item]["missedblocks"]
                current_sample = coininfo_tocheck["missedblocks"]
                sample = current_sample - previous_sample

                if coininfo_output["coins"][item]["missedblocksdelta24h"] > 0:
                    if sample > 0:
                        setstatus = 2
                    elif sample <= 0:
                        setstatus = 1
                else:
                    setstatus = 0
            except:
                pass
            coininfo_output["coins"][item].update({"missedblockstatus": setstatus})

            # archive the coin info:
            # 1. check if coin info is the same as earlier samples, in the history (timestamp may differ)
            # 2. for the overview add/overwrite the info to the current coin info.
            coininfo_alreadypresent = 0
            modified = {}
            for coininfohistory in coininfo_output["coins"][item]["history"]:
                added, removed, modified, same = dict_compare(coininfohistory, coininfo_tocheck)
                if len(modified) == 1 and "timestamp" in modified:
                    coininfo_alreadypresent = 1
                    break

            if keep4history == 1:
                coininfo_alreadypresent = 0

            if coininfo_alreadypresent == 0:
                coininfo_output["coins"][item]["history"].append(coininfo_tocheck)

            # try to figure out the 24h change of balance, rank and nrofvoters
            coininfo_output["coins"][item]["history"].sort(key=lambda x: x["timestamp"], reverse=True)
            for coininfohistory in coininfo_output["coins"][item]["history"]:
                timestamp24hpast = int(time.time()) - 23 * 60 * 59
                # coin_timestamp_readable = time.strftime("%Y-%m-%d %H:%M", time.localtime(int(coininfohistory["timestamp"])))
                # timestamp24hpast_readable = time.strftime("%Y-%m-%d %H:%M", time.localtime(timestamp24hpast))

                if coininfohistory["timestamp"] <= timestamp24hpast:
                    rankdelta24h = coininfohistory["rank"] - coininfo_tocheck["rank"]
                    coininfo_output["coins"][item]["rankdelta24h"] = rankdelta24h

                    votersdelta24h = coininfo_tocheck["nrofvoters"] - coininfohistory["nrofvoters"]
                    coininfo_output["coins"][item]["nrofvoters24h"] = votersdelta24h

                    totalbalancedelta24h = coininfo_tocheck["totalbalance"] - coininfohistory["totalbalance"]
                    coininfo_output["coins"][item]["totalbalancedelta24h"] = totalbalancedelta24h

                    try:
                        producedblocksdelta24h = coininfo_tocheck["producedblocks"] - coininfohistory["producedblocks"]
                        coininfo_output["coins"][item]["producedblocksdelta24h"] = producedblocksdelta24h

                        missedblocksdelta24h = coininfo_tocheck["missedblocks"] - coininfohistory["missedblocks"]
                        coininfo_output["coins"][item]["missedblocksdelta24h"] = missedblocksdelta24h
                    except:
                        break
                    break

            if len(modified) > 1 or coininfo_alreadypresent == 0:
                coininfo_output["coins"][item].update(coininfo_tocheck)

            print(coininfo_output["coins"][item])

        elif conf["coins"][item]["cointype"] == "masternode" or conf["coins"][item]["cointype"] == "pos_staking" or \
                conf["coins"][item]["cointype"] == "wallet":
            # Section: masternode, pos_staking and wallet
            # todo: clean this up if neccesary to split it in masternode, pos_staking and or wallet
            balance = get_walletbalance(conf["coins"][item]["exploreraddress"], conf["coins"][item]["pubaddress"])
            timereceived, amountreceived = get_walletlasttransaction(conf["coins"][item]["exploreraddress"],
                                                                     conf["coins"][item]["pubaddress"])

            # get the base_url of the url which is provided
            base_url = "{0.scheme}://{0.netloc}/".format(urlsplit(conf["coins"][item]["exploreraddress"]))

            coin_explorerlink = copy.copy(conf["coins"][item].get("exploreraddress"))
            if coin_explorerlink == None:
                coin_explorerlink = copy.copy(coin_nodeurl.replace("wallet", "explorer"))

            if coinitemexists != 1:
                coininfo_output["coins"][item] = {
                    "coin": conf["coins"][item]["coin"],
                    "cointype": conf["coins"][item]["cointype"],
                    "delegatename": "",
                    "timereceived": timereceived,
                    "explink": base_url + "address/" + conf["coins"][item]["pubaddress"],
                    "history": []
                }
# create temp coininfo block to check if the same values are already in the json, if so, I don't want those values
            coininfo_tocheck = {
                "timestamp": timestamp,
                "rank": "",
                "totalbalance": balance,
                "approval": "",
                "nrofvoters": "",
                "amountreceived": amountreceived,
                "timereceived": timereceived
            }

            modified = {}
            coininfo_alreadypresent = 0
            for coininfohistory in coininfo_output["coins"][item]["history"]:
                added, removed, modified, same = dict_compare(coininfohistory, coininfo_tocheck)
                if len(modified) == 1 and "timestamp" in modified:
                    coininfo_alreadypresent = 1
                    break

            if keep4history == 1:
                coininfo_alreadypresent = 0

            if coininfo_alreadypresent == 0:
                coininfo_output["coins"][item]["history"].append(coininfo_tocheck)

            coininfo_output["coins"][item]["history"].sort(key=lambda x: x["timestamp"], reverse=True)
            for coininfohistory in coininfo_output["coins"][item]["history"]:
                timestamp24hpast = int(time.time()) - 23 * 60 * 59
                coin_timestamp_readable = time.strftime("%Y-%m-%d %H:%M",
                                                        time.localtime(int(coininfohistory["timestamp"])))
                timestamp24hpast_readable = time.strftime("%Y-%m-%d %H:%M", time.localtime(timestamp24hpast))

                if coininfohistory["timestamp"] <= timestamp24hpast:
                    totalbalancedelta24h = coininfo_tocheck["totalbalance"] - coininfohistory["totalbalance"]
                    coininfo_output["coins"][item]["totalbalancedelta24h"] = totalbalancedelta24h
                    break

            if len(modified) > 1 or coininfo_alreadypresent == 0:
                coininfo_output["coins"][item].update(coininfo_tocheck)

            print(coininfo_output["coins"][item])
        else:
            print("Unknown cointype: " + conf["coins"][item][
                "cointype"] + ", please check your config.json. Valid cointypes are: dpos_delegate, dpos_private, masternode pos,_staking and wallet.")

    savelog(coininfo_output, LOGFILE)

def logcruncher():
    # read the json, this is the database of the dashbaord
    coininfo_crunched = coininfo_tocrunch = loadLog()

    # Hisotry crunching starts after 48 hour
    daytime = 24 * 60 * 60
    currenttime = int(time.time())

    today_timestamp_readable = time.strftime("%Y-%m-%d", time.localtime(int(currenttime)))
    yesterday_timestamp_readable = time.strftime("%Y-%m-%d", time.localtime(int(currenttime) - daytime))

    # for every coin, crunch the history
    for item in coininfo_tocrunch["coins"]:

        pasttime = currenttime
        coininfohistory = sorted(coininfo_tocrunch["coins"][item]["history"],
                                 key=lambda k: ("timestamp" not in k, k.get("timestamp", None)), reverse=True)
        coin_daytimestamparray_readable = []
        coinhisroytitem_temp = {
            "history": []
        }

        for coinhisroytitem in coininfohistory:
            # When history < 2 days (48 hours):  every hour needs 1 entry
            # after this 1 day is 1 entry in the log

            coin_timestamp_readable = time.strftime("%Y-%m-%d", time.localtime(int(coinhisroytitem["timestamp"])))

            # If coin_timestamp is from today; add them all
            if coin_timestamp_readable == today_timestamp_readable or coin_timestamp_readable == yesterday_timestamp_readable:
                coinhisroytitem_temp["history"].append(coinhisroytitem)


            # If coin timestamp is not from today or yesterday; add only the first of a certain date and skip the rest of dat date
            elif pasttime - 2 * daytime >= coinhisroytitem["timestamp"]:
                if coin_timestamp_readable not in coin_daytimestamparray_readable:
                    coinhisroytitem_temp["history"].append(coinhisroytitem)

                    # add this timestamp to the compare array -  we don't need another sample for this date!
                    coin_daytimestamparray_readable.append(
                        time.strftime("%Y-%m-%d", time.localtime(int(coinhisroytitem["timestamp"]))))

        coininfo_crunched["coins"][item]["history"] = coinhisroytitem_temp["history"].copy()
        savelog(coininfo_crunched, LOGFILE)


#########################################################
# Todo
# 1. implement in the HTML the periode to look back from a dropdown; looks like: https://plnkr.co/edit/mig31CiYgHX3iH9DI6Wc?p=preview



if __name__ == "__main__":
    dashboard()
    if conf["crunch_history"]:
        logcruncher()
