var app = angular.module('dashboardApp', []);

app.controller('indexCtrl', function($scope, $http) {
    $scope.accounts = [];
    $scope.accounts2 = [];
    $scope.CurrentDate = new Date();

    $scope.orderByField = 'address';
    $scope.reverseSort = false;
    $scope.searchCoin   = '';     // set the default search/filter term

    $http.get ('cdashboard.json').then (function (res) {
		$scope.lastupdate = res.data.lasttimecalculated * 1000;

// dpos_delegate, dpos_private, masternode, pos_staking and wallet
// currently there are 2 sections in the web front end; accounts and accounts2
// feel free to cluster/change the various cointypes between those two.
// You can do this to move the case statement
// You can also add another section in the HTML and add accounts3 here.

        for (addr in res.data.coins) {
            switch (res.data.coins[addr]["cointype"]) {
                case 'dpos_delegate':
                    var it = res.data.coins[addr];
                    it['address'] = addr;
                    $scope.accounts.push (it);
                    break;
                case 'dpos_private':
                case 'masternode':
                case 'pos_staking':
                case 'wallet':
                    var it = res.data.coins[addr];
                    it['address'] = addr;
                    $scope.accounts2.push (it);
                    break;
                default:
                    var it = res.data.coins[addr];
                    it['address'] = addr;
                    $scope.accounts2.push (it);
                    break;
            }
        }
    });
});