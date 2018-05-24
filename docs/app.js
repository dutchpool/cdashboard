var app = angular.module('dashboardApp', []);

app.controller('indexCtrl', function($scope, $http) {
    $scope.accounts_dpos = [];
    $scope.accounts_masternode = [];
    $scope.accounts_wallet = [];
    $scope.CurrentDate = new Date();

    $scope.orderByField = 'totalbalancedelta24h';
    $scope.reverseSort = true;
    $scope.searchCoin   = '';     // set the default search/filter term

    $http.get ('cdashboard.json').then (function (res) {
		$scope.lastupdate = res.data.lasttimecalculated * 1000;

// currently there are 3 sections in the web front end;
//  - accounts_dpos; accounts_masternode and accounts_wallets
// dpos_delegate, dpos_private, masternode, pos_staking and wallet
// feel free to cluster/change the various cointypes between those.
// You can do this to move the case statement
// You can also add another section in the HTML and add accounts_xxxx here.

        for (addr in res.data.coins) {
            switch (res.data.coins[addr]["cointype"]) {
                case 'dpos_delegate':
                    var it = res.data.coins[addr];
                    it['address'] = addr;
                    $scope.accounts_dpos.push (it);
                    break;
                case 'dpos_private':
                case 'masternode':
                case 'pos_staking':
                    var it = res.data.coins[addr];
                    it['address'] = addr;
                    $scope.accounts_masternode.push (it);
                    break;
                case 'wallet':
                    var it = res.data.coins[addr];
                    it['address'] = addr;
                    $scope.accounts_wallet.push (it);
                    break;
                default:
                    var it = res.data.coins[addr];
                    it['address'] = addr;
                    $scope.accounts_wallet.push (it);
                    break;
            }
        }
    });
});