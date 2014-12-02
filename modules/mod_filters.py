__author__ = 'alivinco'
import os ,json

class FiltersManager:

    def __init__(self):
        self.app_root_path = os.getcwd()
        self.filters_file_path = os.path.join(self.app_root_path, "configs", "filters.json")
        self.load_filters()

    def load_filters(self):
        self.filters = json.load(file(self.filters_file_path))

    def get_filters(self,filters_type):
        return self.filters[filters_type]

    def upsert_filter(self,filters_type,id,name,filter):
        if id :
           filter = filter( (lambda item : item["id"]==id) ,self.filters[filters_type])[0]
           filter["name"]=name
           filter["filter"]=filter
        else :
           if len(self.filters[filters_type])>0:
               new_id = max(self.filters[filters_type],key=lambda item:item["id"])["id"]+1
           else : new_id = 1
           self.filters[filters_type].append({"id":new_id,"name":name,"filter":filter})

        self.serialize_filters()

    def delete_filter(self,filters_type,id):
        f = filter((lambda item : item["id"]==id) ,self.filters[filters_type])[0]
        self.filters[filters_type].remove(f)

        self.serialize_filters()

    def serialize_filters(self):
        # log.info("Serializing address mapping to file " + self.address_mapping_file_path)
        f = open(self.filters_file_path, "w")
        f.write(json.dumps(self.filters, indent=True))
        f.close()

if __name__ == "__main__":
    t = FiltersManager()
    # print json.dumps(t.get_dashboard_map(),indent=True)
    print json.dumps(t.get_filters("inter_console"),indent=True)
    # t.upsert_filter("inter_console",None,"Test filter","sen_power")
    t.delete_filter("inter_console",2)
