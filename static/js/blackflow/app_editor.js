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

function serializeDescriptor(orig_descriptor,sub_for,pub_to,configs)
{
    descr_new = {}
    sub_for_new  = []
    pub_to_new  = []
    configs_new  = []
    angular.copy(sub_for,sub_for_new)
    angular.copy(pub_to,pub_to_new)
    angular.copy(configs,configs_new)
    angular.copy(orig_descriptor,descr_new)
    descr_new.sub_for = convertKeyValueListToDict(sub_for_new)
    descr_new.pub_to = convertKeyValueListToDict(pub_to_new)
    descr_new.configs = convertKeyValueListToList(configs_new)
    return descr_new
}

function get_app_class_name(app_name)
{
    return String(app_name.match(/(?=_n)\w+(?=_v)/g)).replace("_n","");

}

app.controller("AppEditorController",["$scope","$http","$base64",function($scope,$http,$base64){
    packet = getMessagePacket("command","file","download")
    packet["command"]["default"]["value"] = app_name+"/"+get_app_class_name(app_name)+".py"
    $http.post(root_uri+'/api/proxy',{"req_type":"sync_response","req_payload":packet,"corr_type":"COR_ID","container_id":bf_inst_name}).
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
        app_class_name = get_app_class_name(app_name)
        packet = getMessagePacket("command","file","upload")
        packet.command.properties = {"name":app_name+"/"+app_class_name+".py","type":"python","bin_data":bin_data}
        $http.post(root_uri+"/api/proxy",{"req_type":"sync_response","req_payload":packet,"corr_type":"COR_ID","container_id":bf_inst_name}).
        then(function(response) {
            alert("Changes were saved")
          }, function(response) {
             alert("Error")
          });
    }
    $scope.reload = function (){
        packet = getMessagePacket("command","blackflow","reload_app")
        packet.command.default.value =app_name
        $http.post(root_uri+"/api/proxy",{"req_type":"sync_response","req_payload":packet,"corr_type":"COR_ID","container_id":bf_inst_name}).
        then(function(response) {
           if (response.data.event.default.value)
               alert("The app reloaded successfully")
           else
               alert(response.data.event.properties.error)
          }, function(response) {
             alert("Error")
          });
    }
    $scope.upload_to_app_store = function (){
        packet = getMessagePacket("command","app_store","upload_app")
        packet.command.default.value = app_name
        packet.command.properties = {app_store_url:app_store_api,id_token:id_token}
        $http.post(root_uri+"/api/proxy",{"req_type":"sync_response","req_payload":packet,"corr_type":"COR_ID","container_id":bf_inst_name}).
        then(function(response) {
            console.dir(response.data)
            if(response.data.event.default.value == 200){
              alert("App was uploaded successfully.")
            } else {
              alert("Something went wrong")
            }
          }, function(response) {
             alert("Error")
          });
    }

}])


app.controller("AppDescriptorController",["$scope","$http","$base64",function($scope,$http,$base64){
    packet = getMessagePacket("command","file","download")
    packet["command"]["default"]["value"] = app_name+"/manifest.json"
    $http.post(root_uri+'/api/proxy',{"req_type":"sync_response","req_payload":packet,"corr_type":"COR_ID","container_id":bf_inst_name}).
        then(function(response) {
            base64data = response.data.event.properties.bin_data
            decoded = $base64.decode(base64data);
            data = angular.fromJson(decoded)

            $scope.original_descriptor = data
            $scope.sub_for = convertDictToKeyValList(data.sub_for)
            $scope.pub_to = convertDictToKeyValList(data.pub_to)
            $scope.configs = convertListToKeyValueList(data.configs)
          }, function(response) {
            // called asynchronously if an error occurs
            // or server returns response with an error status.
          });
    $scope.save_descriptor = function() {
        descr = serializeDescriptor($scope.original_descriptor,$scope.sub_for,$scope.pub_to,$scope.configs)
        bin_data =  $base64.encode(angular.toJson(descr));
        packet = getMessagePacket("command","file","upload")
        packet.command.properties = {"name":app_name+"/manifest.json","type":"python","post_save_action":"reload_manifest","bin_data":bin_data}
        $http.post(root_uri+"/api/proxy",{"req_type":"one_way","req_payload":packet,"container_id":bf_inst_name}).
        then(function(response) {
            alert("Changes were saved")
          }, function(response) {
             alert("Error")
          });
        //console.dir(descr)
    }
    $scope.add_sub = function() {
        $scope.sub_for.push({"key": "", "value": {"adapter": "mqtt", "msg_type": "", "dev_type": "", "descr": ""}})
    }
    $scope.del_sub = function(index){
        $scope.sub_for.splice(index,1)
    }
    $scope.add_pub = function() {
        $scope.pub_to.push({"key": "", "value": {"adapter": "mqtt", "msg_type": "", "dev_type": "", "descr": ""}})
    }
    $scope.del_pub = function(index){
        $scope.pub_to.splice(index,1)
    }
    $scope.add_conf = function(){
        $scope.configs.push({"value":""})
    }
    $scope.del_conf = function(index){
        $scope.configs.splice(index,1)
    }
}])
