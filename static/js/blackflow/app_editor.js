/**
 * Created by alivinco on 26/07/15.
 */
var app = angular.module('blackflow', ['base64']);
var editor = ace.edit("editor");
editor.setTheme("ace/theme/monokai");
editor.getSession().setMode("ace/mode/python");

app.config(['$interpolateProvider', function($interpolateProvider) {
  $interpolateProvider.startSymbol('{[');
  $interpolateProvider.endSymbol(']}');
}]);


app.controller("AppEditorController",["$scope","$http","$base64",function($scope,$http,$base64){
    packet = getMessagePacket("command","file","download")
    packet["command"]["default"]["value"] = app_name
    $http.post('/api/blackflow/proxy',{"req_type":"sync_response","req_payload":packet,"corr_type":"COR_ID"}).
        then(function(response) {
            // this callback will be called asynchronously
            // when the response is available

            base64data = response.data.event.properties.bin_data
            decoded = $base64.decode(base64data);
            editor.setValue(decoded)

          }, function(response) {
            // called asynchronously if an error occurs
            // or server returns response with an error status.
          });

    $scope.save = function (){
        packet = getMessagePacket("command","file","upload")
        packet.command.properties = {"name":""}
        $http.post("/api/blackflow/proxy",{"req_type":"one_way","req_payload":packet}).
        then(function(response) {
            // this callback will be called asynchronously
            // when the response is available
            window.location = "/ui/blackflow/app_instances"
          }, function(response) {
            // called asynchronously if an error occurs
            // or server returns response with an error status.
          });
        //console.dir(req)


    }

}])

