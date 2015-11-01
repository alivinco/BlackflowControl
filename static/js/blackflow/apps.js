/**
 * Created by alivinco on 31/10/15.
 */


var app = angular.module('AppsList', []);

app.config(['$interpolateProvider', function($interpolateProvider) {
  $interpolateProvider.startSymbol('{[');
  $interpolateProvider.endSymbol(']}');
}]);

app.controller("AppsListController",["$scope","$http",function($scope,$http){
    $scope.init_new_app = function (){
        packet = getMessagePacket("command","blackflow","init_new_app")
        packet.command.default.value = $scope.app_name
        packet.command.properties = {"version":$scope.app_version}
        $http.post("/api/blackflow/"+bf_inst_name+"/proxy",{"req_type":"sync_response","corr_type":"COR_ID","req_payload":packet}).
        then(function(response) {
            if(response.data.event.default.value == 200) {
                alert("New app was added")
            }else {
                alert(response.data.event.properties.text)
            }
          }, function(response) {
             alert("Error")
          });
    }
}])


