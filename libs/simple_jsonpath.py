__author__ = 'alivinco'


class SimpleJsonPath:
    def __init__(self):
        self.cache = {}

    def _get_path_list(self, path):
        # "$.event.default.value"
        # path_list["$.event.default.value.[1]"] = ['$','event','default','value',1]
        try:
            path_list = self.cache[path]
        except:
            path_list = path.split(".")
            for i in xrange(len(path_list)):
                v = path_list[i]
                if "[" in v:
                    path_list[i] = int(v.replace("[", "").replace("]", ""))
            self.cache[path] = path_list
        return path_list


    def get(self, obj, path):
        # path list looks like that  ['$','event','default','value',1]
        try:
            path_list = self._get_path_list(path)
            for item in path_list[1:]:
                obj = obj[item]
        except:
            obj = ""
        return obj

