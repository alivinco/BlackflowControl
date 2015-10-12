/**
 * Created by alivinco on 26/07/15.
 */
var app = angular.module('AppInstances', []);

app.config(['$interpolateProvider', function($interpolateProvider) {
  $interpolateProvider.startSymbol('{[');
  $interpolateProvider.endSymbol(']}');
}]);


app.controller("AppInstancesController",["$scope","$http",function($scope,$http){

    $scope.deleteAppInstance = function (inst_id){
        packet = getMessagePacket("command","blackflow","delete_app_instance")
        packet.command.default.value = inst_id
        $http.post("/api/blackflow/"+bf_inst_name+"/proxy",{"req_type":"one_way","req_payload":packet}).
        then(function(response) {
            alert("App instance was deleted")
            location.reload()
          }, function(response) {
             alert("Error")
          });
    }
    $scope.controlAppInstance = function (inst_id,action){
        packet = getMessagePacket("command","blackflow","control_app_instance")
        packet.command.default.value = inst_id
        packet.command.properties = {"action":action}
        $http.post("/api/blackflow/"+bf_inst_name+"/proxy",{"req_type":"one_way","req_payload":packet}).
        then(function(response) {
           location.reload()
          }, function(response) {
             alert("Error")
          });
    }

}])

