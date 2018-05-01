# Dpos-crypto-dashboard
[![MIT License](http://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/dutchpool/cdashboard/blob/master/LICENSE)
[![docs](https://img.shields.io/badge/doc-online-blue.svg)](https://github.com/dutchpool/cdashboard/wiki)


Dashboard for Dpos delegate information, Masternodes status, staking info and crypto Wallets

An overview of all your important Dpos delegate information (rank, amount of coins, approval, votes), Masternodes status, staking info or even just crypto Wallets!
Crypto Dashboard is made to sort those things out and present you all your important information in one handy overview.


_If you like this dashboard, please consider to vote for all the Dutch Pool delegates: "dutch_pool", "st3v3n", "kippers", "fnoufnou" and "thamar" and receive the high sharing percentage of 90% per delegate!

If you are curious and want to see a working demo of the Dpos-crypto-dashboard, please visit: http://cdashboarddemo.thamar.net/

More info about Dutchpool, our mission, our other tools and contributions to the Dpos ecosystem, please visit http://dutchpool.io_


## Installing it

First clone the crypto dashboard repository, install python and requests:

```git clone https://github.com/dutchpool/cdashboard```

```cd cdashboard```

```apt-get install python3-pip```

```pip3 install requests```


## Configure it

To configure the Dashboard we need to open the config.json. With this install you get an example config.json ("config_example.json") which you need to copy and change with your own parameters and coin basic information.

```cp config_example.json config.json```

Note: Never fill in your private keys, the crypto dashboard doesn't need those, we only work with public addresses!!!

The parameters:
- cryptodashboard_file_version: internal check if version is correct for updates
- crunch_history: true or false; currently not functioning yet!
- logfile: the file where all coin info is stored and added; default "cdashboard.json"; you can change the logfile name the way you like (handy for setting up multiple config files with multiple log files, using one python script)
- coins: section where the coin info is represented
   - identifier: coin identifier,
      - coin: coin name
      - node: Dpos coin node web address (if coin not a Dpos coin, fill the exploreraddress)
      - pubaddress: the public address of the coin
      - cointype: options are: dpos_delegate, dpos_private, masternode, pos_staking and wallet
         - currently, dpos_delegate is the first section of the dashboard; and dpos_private, masternode, pos_staking and wallet, are the second section of the dashboard. If you want to change this, you can do this in the case-statement in the app.js.
      - exploreraddress: coin explorer web address (for cointype: masternode, pos_staking and wallet)



Example config.json:
```
{
  "cryptodashboard_file_version": 0.6,
  "crunch_history": false,
  "logfile": "cdashboard.json",
  "coins": {
    "OXY Dutch Pool Mainnet": {
      "coin": "OXY",
      "node": "https://wallet.oxycoin.io",
      "pubaddress": "15957132064002739627X",
      "cointype": "dpos_delegate"
    },
    "LWF Thamar mainnet": {
      "coin": "LWF",
      "node": "https://wallet.lwf.io",
      "pubaddress": "567015584193522108LWF",
      "cointype": "dpos_delegate"
    },
  }
}
```



## Start it:

```python3 cryptodashboard.py```

or if you want to use another config file:

```python3 cryptodashboard.py -c config2.json```

It produces a file (if default) "cdashboard.json" with all the crypto dashboard information which can be presented with the included HTML setup.


We advise to run the cryptodashboard script every hour to collect it's data. The cronjob to configure this (use crontab -e):

`00 * * * * cd ~/cdashboard && python3 ~/cdashboard/cryptodashboard.py`

When the script is ready and configured; you can setup the web environment, see the setup file "cdashboard_site_setup.md".


## Command line usage

```
usage: cryptodashboard.py [-h] [-c config.json] [-y]

Crypto dashboard script

optional arguments:
  -h, --help            show this help message and exit
  -c config.json        set a config file (default: config.json)

```


## Supported/tested chains / explorers

At the moment CryptDashboard supports and is tested on the following chains / explorers:
- Dpos:  OXY, LWF, ONZ, LISK, ARK, SHIFT, RISE
- all clones of Iquidus Explorer

Known issues:
- a lot of explorer chains are not supported yet; working on it!
- chainz.cryptoid.info - basic info is working, no last TX and date-received

## Changelog

### 0.6
- Initial release
	- basic support for coin explorers (e.g. BTC and ETC); more needs to be done!


## To Do
We are planning to integrate other cool features:
- in the HTML overview, select the history period with a dropdown, now it is 24h and 48h;
- add a live indication in the Dpos main dashboard, the time until a node will forge
- strip/crunch the history of the log (default: cdashboard.json), e.g. after 48h only 1 entry a day or week
- add euro / dollar for amount of coins
- create a web interface to maintain the config.json




## Donations

Besides voting voor de Dutch Pool delegates, if you like this Dpos crypto dashboard and it helps you to get organized, we would greatly appreciate if you would consider to show some support by donating to one of the below mentioned addresses.

- OXY: 		902564290011692795X
- LWF: 		2526916071607963001LWF
- ONZ: 		ONZfxHuBy5e39nipSZuSgcKhYURE6QkWsK2j
- Shift: 	18040765904662116201S
- Lisk: 	8890122000260193860L
- BTC: 		1NrA8k8wNRwEZj2ooKQEf2fFnF6KqTE32T


## Credits

@st3v3n, @kippers, @fnoufnou


## License

```
Copyright (c) 2018 Thamar proud member of Dutch Pool

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NON INFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
```
