/**
 * Created by alivinco on 26/07/15.
 */
var app = angular.module('AppInstances', []);

app.config(['$interpolateProvider', function($interpolateProvider) {
  $interpolateProvider.startSymbol('{[');
  $interpolateProvider.endSymbol(']}');
}]);


app.controller("AppInstancesController",["$scope","$http",function($scope,$http){

    $scope.startInstance = function (inst_id){
        packet = getMessagePacket("command","blackflow","upload")
        packet.command.properties = {"name":app_name+"/"+app_name+".py","type":"python","bin_data":bin_data}
        $http.post("/api/blackflow/"+bf_inst_name+"/proxy",{"req_type":"one_way","req_payload":packet}).
        then(function(response) {
            alert("Changes were saved")
          }, function(response) {
             alert("Error")
          });
    }
    $scope.stopInstance = function (){
        packet = getMessagePacket("command","blackflow","reload_app")
        packet.command.default.value = app_name
        $http.post("/api/blackflow/"+bf_inst_name+"/proxy",{"req_type":"sync_response","req_payload":packet,"corr_type":"COR_ID"}).
        then(function(response) {
           if (response.data.event.default.value)
               alert("The app reloaded successfully")
           else
               alert(response.data.event.properties.error)
          }, function(response) {
             alert("Error")
          });
    }

}])

