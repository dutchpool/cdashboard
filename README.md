# DPoS-Crypto-Dashboard
[![MIT License](http://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/dutchpool/cdashboard/blob/master/LICENSE)
[![docs](https://img.shields.io/badge/doc-online-blue.svg)](https://github.com/dutchpool/cdashboard/wiki)


Dashboard for DPoS delegate information, DPoS private addresses, Masternodes status, staking info and crypto Wallets.

An overview of all your important DPoS delegate information e.g. Rank, Amount of coins, Approval, Number of Votes and the difference of the last 24h. 
Also Masternode information, like when you receive the last amount of coins in your MN wallet. The same for Staking coins, last but not least, just crypto Wallets, like Bitcoin and Ethereum!
Crypto Dashboard is made to sort those things out and present you all your important information in one handy overview.


DPoS Dashboard Features, for active delegates but also for private wallets:
- Monitor your delegate(s) Rank, Balance, Approval, Votes received, Forged blocks, Missed blocks, Votes casted, Votes casted on not forging delegates
- Monitor your delegate(s)performance over the last 24 hours
- See quickly if your node is missing blocks or is recovered
- When blocks are missing now and then, this is an indicator that something could be wrong with the server, pro-active maintenance can be initiated!
- <B>No secrets!!! No Pass phrases!!!</B> needed in de config.json! All this is done with the public addresses of the wallets/delegate(s)and the API's available in the several DPoS platforms
- No need to run this script on a delegate's node/server! Every server/VPS with python will do
- By actively inspecting your "Votes casted" on "(not) forging delegates", you can quickly re-vote and monetise your voting weight more wisely


If you want to see a working demo of the Dpos-crypto-dashboard, please visit: http://cdashboarddemo.thamar.net/
If you like this dashboard created by delegate Thamar, please consider to vote for all the Dutch Pool delegates: "dutch_pool", "st3v3n", "kippers", "fnoufnou" and off course "thamar"! A small donation is also appreciated (see for more donation info below)

_More info about Dutch Pool, our mission, our other tools and contributions to the DPoS ecosystem, please visit http://dutchpool.io_


## Installing it

First clone the crypto dashboard repository, install python and requests:

```git clone https://github.com/dutchpool/cdashboard```

```cd cdashboard```

```apt-get install python3-pip```

```pip3 install requests```


## Configure it

To configure the Dashboard we need to fill in the configuration file. With this install you get an example json config_example.json with a lot of examples and a file "config_template.json" which you can use as the config.json and change with your own parameters and coin basic information. To prepare this: 

```cp config_emptytemplate.json config.json```

Note: Never fill in your private keys, the crypto dashboard doesnt need those, we only work with public addresses!!!

The parameters:
- cryptodashboard_file_version: internal check if version is correct for updates
- crunch_history: true or false; this will crunch the log file after 48 hours to only one sample a day
- logfile: the file where all gathered coin info is stored; default "cdashboard.json"; you can change the logfile name the way you like (handy for setting up multiple config files with multiple log files, using one python script)
- coins: section where the coin info is represented
   - identifier: coin identifier, can be any random name, can hold white spaces, but I suggest to keep it short
      - coin: coin name; 
         - Note: For a Lisk entry you have to fill in LSK or LISK as coin name (case insensitive)!
      - node: DPoS coin node web address (only for the DPoS coins)
      - pubaddress: the public address of the coins wallet (never add your private address/seeds!!!)
      - cointype: options are: dpos_delegate, dpos_private, masternode, pos_staking and wallet
         - currently, dpos_delegate is the first section of the dashboard; second section: dpos_private, masternode, pos_staking; third section: crypto wallets like BTC, ETC etc.. If you want to change this, you can do this in the case-statement in the app.js.
      - exploreraddress: coin explorer web address (for all the cointypes, if the format of the DPoS coin for the explorer address is wallet.something_coin.xx; wallet will be replaced internally with explorer and you don't have to fill in the explorer parameter)


Example config.json:
```
{
  "cryptodashboard_file_version": 0.97,
  "crunch_history": true,
  "logfile": "cdashboard.json",
  "coins": {
      "lisk dutch_pool donation": {
      "coin": "Lisk",
      "node": "https://wallet.mylisk.com",
      "pubaddress": "8890122000260193860L",
      "exploreraddress": "https://explorer.mylisk.com",
      "cointype": "dpos_private"
    },
    "LWF Thamar mainnet": {
      "coin": "LWF",
      "node": "https://wallet.lwf.io",
      "pubaddress": "567015584193522108LWF",
      "cointype": "dpos_delegate"
    },
     "onzdutchpoolmainnet": {
      "coin": "ONZ",
      "node": "https://node10.onzcoin.com",
      "pubaddress": "ONZkL6Jm1MKGWnVzMzkJ8jwTxbQ8Cudqh1Hw",
      "exploreraddress": "https://explorer.onzcoin.com",
      "cointype": "dpos_delegate"
    }
 }
}
```
Above is an indication of how the config.json must look like. We have included a config_example.json which includes an entry for most DPoS systems from which you can copy and fill-in your specific information per DPoS coin, also an almost empty json (config_template.json ) which you can copy to the standard config.json and use this as your starting point to fill all your coin info.


## Start it:

```python3 cryptodashboard.py```

or if you want to use another config file:

```python3 cryptodashboard.py -c config2.json```

It produces a file (if default) "cdashboard.json" with all the crypto dashboard information which can be presented with the included HTML setup. Note: the 24h information will not show immediately.

You have to copy (use crontab) the "cdashboard.json" file to the /docs folder to let the website have access to the gathered coin information. 

We advise to run the cryptodashboard python script every hour to collect it's data. The crontab to configure this (use crontab -e):

```
00 * * * * cd ~/cdashboard && python3 ~/cdashboard/cryptodashboard.py
10 * * * * cd ~/cdashboard && cp cdashboard.json docs/cdashboard.json
```

You can also create a bash script with the above information if you prefer.
When the cdashboard script is ready and configured; you can setup the web environment to show the dashboard, see the setup file "cdashboard_site_setup.md".

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
- DPoS (mainnet and testnet):  LWF, ONZ, LISK 1.0, ARK, SHIFT, RISE, RipaEx, Qredit, Sauco, Skelpy, Adamant, Blockpool 
- Crypto wallets: all clones of Iquidus Explorer

Known issues for Masternodes and staking chains:
- a lot of explorer chains are not supported yet; working on it!
- chainz.cryptoid.info - basic info is working, no last TX and date-received

## Changelog

###### Release 0.97
- New feature Added: tooltip when hovering over the Missed Blks(24h) colon which indicates the time of the last forged block 

###### Release 0.96
- New feature Added: With the new Number of forged blocks and missed blocks, we can indicate if a node is not forging
    - Missed Blks(24h) = cell = red ==> node is missing blocks! You need to fix it!
    - Missed Blks(24h) = cell = green ==> node is not missing blocks anymore! It did, and this will show green, 24h!
    - Missed Blks(24h) = cell = normal ==> node is forging, no problem's in the last 24h 


###### Release 0.95
New feature:
- Added: Number of forged blocks and missed blocks of Delegate node
- Removed: Sharing percentages information; In current state not informative enough
- Fixed bug for Lisk support (dashboard is now integrated with Lisk API 1.0) - last transaction info
- Fixed bug: the history and 24h update functionality is now working (with running the monitor every hour)
- known issue: the pop-up only should show info from the coin which was selected; currently it shows all the coins.

###### Release 0.93
New feature:
- Added Lisk support (dashboard is now integrated with Lisk API 1.0)
- removed OXY references, since it is no DPoS anymore
- known issue: the pop-up only should show info from the coin which was selected; currently it shows all the coins.
- known issue: the history and 24 update functionality is still not working as expected.

###### Release 0.9/0.91
New feature:
- check your DPoS (private) addresses, if all your voted delegates are still forging!
- fixed some bugs for addresses which are brand new with no transactions jet.
- known issue: the pop-up only should show info from the coin which was selected; currently it shows all the coins.

###### Release 0.8
- Bugfix and feature release
	- Log cruncher is working!
	- Better suport for BTC and ETC;
	- integration between Dutch Pool verifier for overview of sharing %
	- a lot off small bugs
###### Release 0.6
- Initial release
	- basic support for coin explorers (e.g. BTC and ETC); more needs to be done!


## To Do
We are planning to integrate other cool features:
- create a script that for one delegate name, creates the config.json for all the known dpos-systems
- make it possible to remove info/history from a removed wallet/delegate address
- show the voted delegates of one wallet with their percentages that they are paying in the pop-up 
- in the HTML overview, select the history period with a dropdown, now it is 24h and 48h
- add a live indication in the DPoS main dashboard, the time until a node will forge
- add euro / dollar for amount of coins - If already possible! Not main focus currently
- create a web interface to maintain the config.json for adding, removing, adjusting coin info
- create an HTML with main focus Masternodes instead of DPoS

## Donations

Besides voting for de Dutch Pool delegates, if you like this DPoS Crypto Dashboard and it helps you to get organized, or even monitize your voting weight better, we would greatly appreciate if you would consider to show some support by donating to one of the below mentioned addresses.

- LWF: 		2526916071607963001LWF
- ETH (or OXY ;-) 0x7E1B5CAf074e0AB5B8aA8d7373e2756Ca105e707
- ONZ: 		ONZfxHuBy5e39nipSZuSgcKhYURE6QkWsK2j
- Shift: 	18040765904662116201S
- Lisk: 	8890122000260193860L
- BTC: 		1NrA8k8wNRwEZj2ooKQEf2fFnF6KqTE32T


## Cr3dits

Thanks @st3v3n, @kippers, @fnoufnou for your help creating and testing this project! @dakk for the inspiration for the architecture of the project.


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
