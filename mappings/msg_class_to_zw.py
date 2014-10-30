__author__ = 'alivinco'


ZW_TO_MSG_CLASS = [
    {"dev_type":"bin_switch","capability":"COMMAND_CLASS_BASIC","msg_class":["binary.switch"],"event_msg_class":[]},
    {"dev_type":"sen_temp","capability":"COMMAND_CLASS_SENSOR_MULTILEVEL","msg_class":[],"event_msg_class":[]},
    {"dev_type":"met_power","capability":"COMMAND_CLASS_METER","msg_class":[],"event_msg_class":[]},
    {"dev_type":"bin_temper","capability":"COMMAND_CLASS_ALARM","msg_class":[],"event_msg_class":[]},
    {"dev_type":"lvl_thermostat","capability":"COMMAND_CLASS_THERMOSTAT_SETPOINT","msg_class":["level.thermostat"],"event_msg_class":[]},
    {"dev_type":"lvl_dimmer","capability":"COMMAND_CLASS_SWITCH_MULTILEVEL","msg_class":["level.dimmer"],"event_msg_class":[]},
    {"dev_type":"bin_switch","capability":"COMMAND_CLASS_SWITCH_BINARY","msg_class":["binary.switch"],"event_msg_class":[]},
    {"dev_type":"dev_sys","capability":"COMMAND_CLASS_MANUFACTURER_SPECIFIC","msg_class":[],"event_msg_class":[]},
    {"dev_type":"dev_sys","capability":"COMMAND_CLASS_CONFIGURATION","msg_class":["config.set","config.get"],"event_msg_class":["config.report"]},
    {"dev_type":"dev_sys","capability":"COMMAND_CLASS_ASSOCIATION","msg_class":["association.set","association.get"],"event_msg_class":["association.report"]}
]

def get_msg_class_by_capabilities(dev_type,capability):
    return filter(lambda item:item["dev_type"]==dev_type and item["capability"]==capability,ZW_TO_MSG_CLASS)[0]

