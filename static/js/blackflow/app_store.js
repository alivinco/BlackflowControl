/**
 * Created by alivinco on 26/07/15.
 */
var app = angular.module('AppStore', []);

app.config(['$interpolateProvider', function($interpolateProvider) {
  $interpolateProvider.startSymbol('{[');
  $interpolateProvider.endSymbol(']}');
}]);


app.controller("AppStoreController",["$scope","$http","$filter",function($scope,$http,$filter){

    $scope.loadData = function () {
        $http.get(app_store_api+'/apps').
        then(function (response) {
            $scope.asData = response.data
        }, function (response) {
            // called asynchronously if an error occurs
            // or server returns response with an error status.
        });
    }
    $scope.saveApp = function () {
        $http.post(app_store_api+'/apps',data=$scope.selected_app).
        then(function (response) {
            $('#app_extended_info_modal').modal("hide")
            $scope.loadData()
        }, function (response) {
            // called asynchronously if an error occurs
            // or server returns response with an error status.
        });
    }
    $scope.loadData()
    $scope.openAppExtendedInfoModal = function(index){
        //$scope.selected_app = $filter('filter',$scope.asData,{"id":app_id})
        $scope.selected_app = $scope.asData[index]
        console.dir($scope.selected_app)
        $('#app_extended_info_modal').modal("show")
    }

    $scope.deleteApp = function(){
        $http.delete(app_store_api+'/apps/'+$scope.selected_app.id).
        then(function (response) {
            $('#app_extended_info_modal').modal("hide")
            $scope.loadData()
        }, function (response) {
            // called asynchronously if an error occurs
            // or server returns response with an error status.
            alert("Error")
        });
    }
    $scope.installApp = function (){
        packet = getMessagePacket("command","app_store","download_app")
        packet.command.default.value = $scope.selected_app.id
        packet.command.properties = {app_store_url:app_store_api,sec_token:""}
        $http.post(root_uri+"/api/blackflow/"+bf_inst_name+"/proxy",{"req_type":"sync_response","req_payload":packet,"corr_type":"COR_ID"}).
        then(function(response) {
            console.dir(response.data)
            if(response.data.event.default.value == 200){
              alert("App was installed successfully.")
              $('#app_extended_info_modal').modal("hide")
            } else {
              alert("Something went wrong")
            }
          }, function(response) {
             alert("Error")
          });
    }

}])

