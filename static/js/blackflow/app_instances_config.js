/**
 * Created by alivinco on 26/07/15.
 */
var app = angular.module('blackflow', []);

app.config(['$interpolateProvider', function($interpolateProvider) {
  $interpolateProvider.startSymbol('{[');
  $interpolateProvider.endSymbol(']}');
}]);

app.filter('range', function() {
  return function(input, total) {
    total = parseInt(total);

    for (var i=0; i<total; i++) {
      input.push(i);
    }

    return input;
  };
});

function getInstConfigRequest(inst_config_orig,sub_for,pub_to,configs)
{
    inst_config = {}
    sub_for_new  = []
    pub_to_new  = []
    configs_new  = []
    angular.copy(sub_for,sub_for_new)
    angular.copy(pub_to,pub_to_new)
    angular.copy(configs,configs_new)
    angular.copy(inst_config_orig,inst_config)
    inst_config.sub_for = convertKeyValueListToDict(sub_for_new)
    inst_config.pub_to = convertKeyValueListToDict(pub_to_new)
    inst_config.configs = convertKeyValueListToDict(configs_new)
    inst_config.comments = inst_config_orig.comments
    //inst_config.schedules = inst_config_orig.schedules
    // cleaning up unneeded fields
    for (i in inst_config.sub_for)
    {
        delete inst_config.sub_for[i].app_def
    }
    for (i in inst_config.pub_to)
    {
        delete inst_config.pub_to[i].app_def
    }
    return inst_config
}

app.controller("AppConfigController",function($scope,$http){

    $http.get(root_uri+'/api/app_instance_config',{params:{"id":inst_id,"app_name":app_name,"container_id":bf_inst_name}}).success(function(data) {

        $scope.inst_config = data;
        $scope.sub_for = convertDictToKeyValList(data.sub_for)
        $scope.pub_to = convertDictToKeyValList(data.pub_to)
        $scope.configs = convertDictToKeyValList(data.configs)
        if (!data.schedules)
           data.schedules = []
        $scope.schedules = data.schedules

    });
    $scope.update = function (){
        packet = getMessagePacket("command","blackflow","configure_app_instance")
        req = getInstConfigRequest($scope.inst_config,$scope.sub_for,$scope.pub_to,$scope.configs)
        packet.command.properties = req
        $http.post(root_uri+"/api/proxy",{"req_type":"sync_response","corr_type":"COR_ID","req_payload":packet,"container_id":bf_inst_name}).
        then(function(response) {
            //window.location = "/ui/blackflow/app_instances"
            if(!inst_id){
               inst_id = parseInt(response.data.event.properties.text)
               $scope.inst_config.id = inst_id
               alert("New instance id = "+inst_id)
            }
          }, function(response) {
            // called asynchronously if an error occurs
            // or server returns response with an error status.
          });

    }
    $scope.reload_app_instance = function (id){
        packet = getMessagePacket("command","blackflow","configure_app_instance")
        packet.default.value = id
        $http.post(root_uri+"/api/proxy",{"req_type":"one_way","req_payload":packet,"container_id":bf_inst_name})
    }
    $scope.add_sub = function(){
        $scope.sub_for.push({"key":"","value":{"topic":""}})
    }
    $scope.del_sub = function(index){
        $scope.sub_for.splice(index,1)
    }
    //
    $scope.add_pub = function(){
        $scope.pub_to.push({"key":"","value":{"topic":""}})
    }
    $scope.del_pub = function(index){
        $scope.pub_to.splice(index,1)
    }
    //
    $scope.add_conf = function(){
        $scope.configs.push({"key":"","value":""})
    }
    $scope.del_conf = function(index){
        $scope.configs.splice(index,1)
    }
    $scope.add_schedule = function(trigger_type)
    {
        tz = moment.tz.guess();
        console.log(tz)
        $scope.schedules.push({trigger_type:trigger_type,timezone:tz})
    }
    $scope.del_schedule = function(index)
    {
        console.log(index)
        $scope.schedules.splice(index,1)
    }
    $scope.restart = function (){
        packet = getMessagePacket("command","blackflow","reload_app_instance")
        packet.command.default.value = $scope.inst_config.id
        $http.post(root_uri+"/api/proxy",{"req_type":"sync_response","req_payload":packet,"corr_type":"COR_ID","container_id":bf_inst_name}).
        then(function(response) {
           if (response.data.event.default.value)
               alert("The app instance restarted successfully")
           else
               alert(response.data.event.properties.error)
          }, function(response) {
             alert("Error")
          });
    }
})

