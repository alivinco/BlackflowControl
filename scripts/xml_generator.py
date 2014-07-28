__author__ = 'alivinco'

xml_str = '<cmd_exec_info>' \
          '<param_info json_path="command.properties.<$id>.value"  value_type="int"/>' \
          '<value_info command_class_id="112" command_class_name="COMMAND_CLASS_CONFIGURATION" command_class_version="1" value_genre="config" value_type="short" value_index="<$id>" value_unit="" value_label=""/>' \
          '</cmd_exec_info>'

f = open("result.xml","w")
for i in range(1,256):
    f.write(xml_str.replace("<$id>",str(i))+"\n")

f.close()