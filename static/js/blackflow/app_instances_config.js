/**
 * Created by alivinco on 26/07/15.
 */
var app = angular.module('blackflow', []);

app.config(['$interpolateProvider', function($interpolateProvider) {
  $interpolateProvider.startSymbol('{[');
  $interpolateProvider.endSymbol(']}');
}]);

function convertDictToKeyValList(dict)
{
    result = []
    for (k in dict)
    {result.push({"key":k,"value":dict[k]})}
    return result
}
function convertKeyValueListToDict(list)
{
    result = {}
    for(item in list)
    {
        result[list[item].key] = list[item].value
    }
    return result
}


app.controller("AppConfigController",function($scope,$http){

    $http.get('/api/blackflow/app_instance_config',{params:{"id":inst_id,"app_name":app_name}}).success(function(data) {

        $scope.inst_config = data;
        $scope.sub_for = convertDictToKeyValList(data.sub_for)
        $scope.pub_to = convertDictToKeyValList(data.pub_to)
        $scope.configs = convertDictToKeyValList(data.configs)

    });
    $scope.update = function (){
        $scope.inst_config.sub_for = convertKeyValueListToDict($scope.sub_for)
        console.dir(inst_config)
    }
    $scope.add_sub = function(){
        $scope.sub_for.push({"key":"","value":""})
    }
    $scope.del_sub = function(index){
        $scope.sub_for.splice(index,1)
    }
    //
    $scope.add_pub = function(){
        $scope.pub_to.push({"key":"","value":""})
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
})

