/**
 * Created by alivinco on 31/10/15.
 */


var app = angular.module('AppsList', []);

app.config(['$interpolateProvider', function($interpolateProvider) {
  $interpolateProvider.startSymbol('{[');
  $interpolateProvider.endSymbol(']}');
}]);

app.controller("AppsListController",["$scope","$http",function($scope,$http){
    $scope.open_new_app_modal = function(){
        $scope.app_developer = app_developer
        $scope.app_version = 1
        $('#create_new_app_modal').modal("show")
    }
    $scope.init_new_app = function (container_id){
        packet = getMessagePacket("command","blackflow","init_new_app")
        packet.command.default.value = $scope.app_name
        packet.command.properties = {"version":$scope.app_version,"developer":$scope.app_developer}
        $http.post(root_uri+"/api/proxy",{"req_type":"sync_response","corr_type":"COR_ID","req_payload":packet,"container_id":$scope.app_container_id}).
        then(function(response) {
            if(response.data.event.default.value == 200) {
                alert("New app was added")
                location.reload()
            }else {
                alert(response.data.event.properties.text)
            }
          }, function(response) {
             alert("Error")
          });
    }
    $scope.delete_app = function (app_full_name,container_id){
        packet = getMessagePacket("command","blackflow","delete_app")
        packet.command.default.value = app_full_name
        $http.post(root_uri+"/api/proxy",{"req_type":"sync_response","corr_type":"COR_ID","req_payload":packet,"container_id":container_id}).
        then(function(response) {
            if(response.data.event.default.value == 200) {
                alert("App was deleted")
                location.reload()
            }else {
                alert(response.data.event.properties.text)
            }
          }, function(response) {
             alert("Error")
          });
    }
    $scope.reload = function (full_app_name,container_id){
        packet = getMessagePacket("command","blackflow","reload_app")
        packet.command.default.value =full_app_name
        $http.post(root_uri+"/api/proxy",{"req_type":"sync_response","req_payload":packet,"corr_type":"COR_ID","container_id":container_id}).
        then(function(response) {
           if (response.data.event.default.value)
               alert("The app was reloaded successfully")
           else
               alert(response.data.event.properties.error)
          }, function(response) {
             alert("Error")
          });
    }
}])


