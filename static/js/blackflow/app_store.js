/**
 * Created by alivinco on 26/07/15.
 */
var app = angular.module('AppStore', []);

app.config(['$interpolateProvider', function($interpolateProvider) {
  $interpolateProvider.startSymbol('{[');
  $interpolateProvider.endSymbol(']}');
}]);


app.controller("AppStoreController",["$scope","$http",function($scope,$http){

    $scope.loadData = function () {
        $http.get('http://localhost:8080/bfhub/api/apps').
        then(function (response) {
            $scope.asData = response.data
        }, function (response) {
            // called asynchronously if an error occurs
            // or server returns response with an error status.
        });
    }
     $scope.loadData()


}])

