/**
 * Created by alivinco on 26/07/15.
 */
var app = angular.module('AppEditor', ['base64']);
var editor = ace.edit("editor");
editor.setTheme("ace/theme/monokai");
editor.getSession().setMode("ace/mode/python");

app.config(['$interpolateProvider', function($interpolateProvider) {
  $interpolateProvider.startSymbol('{[');
  $interpolateProvider.endSymbol(']}');
}]);


app.controller("AppEditorController",["$scope","$http","$base64",function($scope,$http,$base64){
    packet = getMessagePacket("command","file","download")
    packet["command"]["default"]["value"] = app_name+"/"+app_name+".py"
    $http.post('/api/blackflow/'+bf_inst_name+'/proxy',{"req_type":"sync_response","req_payload":packet,"corr_type":"COR_ID"}).
        then(function(response) {
            base64data = response.data.event.properties.bin_data
            decoded = $base64.decode(base64data);
            editor.setValue(decoded)
          }, function(response) {
            // called asynchronously if an error occurs
            // or server returns response with an error status.
          });

    $scope.save = function (){
        src = editor.getValue()
        bin_data =  $base64.encode(src);
        packet = getMessagePacket("command","file","upload")
        packet.command.properties = {"name":app_name+"/"+app_name+".py","type":"python","bin_data":bin_data}
        $http.post("/api/blackflow/"+bf_inst_name+"/proxy",{"req_type":"one_way","req_payload":packet}).
        then(function(response) {
            alert("Changes were saved")
          }, function(response) {
             alert("Error")
          });
    }
    $scope.reload = function (){
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


app.controller("AppDescriptorController",["$scope","$http","$base64",function($scope,$http,$base64){
    packet = getMessagePacket("command","file","download")
    packet["command"]["default"]["value"] = app_name+"/"+app_name+".json"
    $http.post('/api/blackflow/'+bf_inst_name+'/proxy',{"req_type":"sync_response","req_payload":packet,"corr_type":"COR_ID"}).
        then(function(response) {
            base64data = response.data.event.properties.bin_data
            decoded = $base64.decode(base64data);
            data = angular.fromJson(decoded)
            console.dir(data)
            $scope.sub_for = convertDictToKeyValList(data.sub_for)
            $scope.pub_to = convertDictToKeyValList(data.pub_to)
            $scope.configs = data.configs
          }, function(response) {
            // called asynchronously if an error occurs
            // or server returns response with an error status.
          });
    $scope.add_sub = function(){
        $scope.sub_for.push({"key":"","value":{"topic":""}})
    }
}])
