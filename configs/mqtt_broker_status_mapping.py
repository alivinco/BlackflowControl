__author__ = 'aleksandrsl'
mqtt_broker_status_mapping = {
    "$SYS/broker/bytes/received":"The total number of bytes received since the broker started.",
    "$SYS/broker/bytes/sent":"The total number of bytes sent since the broker started.",
    "$SYS/broker/changeset":"The repository changeset (revision) associated with this build. Static.",
    "$SYS/broker/clients/active":"The number of currently connected clients",
    "$SYS/broker/clients/expired":"The number of disconnected persistent clients that have been expired and removed through the persistent_client_expiration option.",
    "$SYS/broker/clients/inactive":"The total number of persistent clients (with clean session disabled) that are registered at the broker but are currently disconnected.",
    "$SYS/broker/clients/maximum":"The maximum number of active clients that have been connected to the broker. This is only calculated when the $SYS topic tree is updated, so short lived client connections may not be counted.",
    "$SYS/broker/clients/total":"The total number of active and inactive clients currently connected and registered on the broker.",
    "$SYS/broker/connection/":"When bridges are configured to/from the broker, common practice is to provide a status topic that indicates the state of the connection. This is provided within $SYS/broker/connection/ by default. If the value of the topic is 1 the connection is active, if 0 then it is not active. See the Bridges section below for more information on bridges.",
    "$SYS/broker/heap/current":"The current size of the heap memory in use by mosquitto. Note that this topic may be unavailable depending on compile time options.",
    "$SYS/broker/heap/maximum":"The largest amount of heap memory used by mosquitto. Note that this topic may be unavailable depending on compile time options.",
    "$SYS/broker/load/connections/":"The moving average of the number of CONNECT packets received by the broker over different time intervals. The final + of the hierarchy can be 1min, 5min or 15min. The value returned represents the number of connections received in 1 minute, averaged over 1, 5 or 15 minutes.",
    "$SYS/broker/load/bytes/received/":"The moving average of the number of bytes received by the broker over different time intervals. The final + of the hierarchy can be 1min, 5min or 15min. The value returned represents the number of bytes received in 1 minute, averaged over 1, 5 or 15 minutes.",
    "$SYS/broker/load/bytes/sent/":"The moving average of the number of bytes sent by the broker over different time intervals. The final + of the hierarchy can be 1min, 5min or 15min. The value returned represents the number of bytes sent in 1 minute, averaged over 1, 5 or 15 minutes.",
    "$SYS/broker/load/messages/received/":"The moving average of the number of all types of MQTT messages received by the broker over different time intervals. The final + of the hierarchy can be 1min, 5min or 15min. The value returned represents the number of messages received in 1 minute, averaged over 1, 5 or 15 minutes.",
    "$SYS/broker/load/messages/sent/":"The moving average of the number of all types of MQTT messages sent by the broker over different time intervals. The final + of the hierarchy can be 1min, 5min or 15min. The value returned represents the number of messages send in 1 minute, averaged over 1, 5 or 15 minutes.",
    "$SYS/broker/load/publish/dropped/":"The moving average of the number of publish messages dropped by the broker over different time intervals. This shows the rate at which durable clients that are disconnected are losing messages. The final + of the hierarchy can be 1min, 5min or 15min. The value returned represents the number of messages dropped in 1 minute, averaged over 1, 5 or 15 minutes.",
    "$SYS/broker/load/publish/received/":"The moving average of the number of publish messages received by the broker over different time intervals. The final + of the hierarchy can be 1min, 5min or 15min. The value returned represents the number of publish messages received in 1 minute, averaged over 1, 5 or 15 minutes.",
    "$SYS/broker/load/publish/sent/":"The moving average of the number of publish messages sent by the broker over different time intervals. The final + of the hierarchy can be 1min, 5min or 15min. The value returned represents the number of publish messages sent in 1 minute, averaged over 1, 5 or 15 minutes.",
    "$SYS/broker/load/sockets/":"The moving average of the number of socket connections opened to the broker over different time intervals. The final + of the hierarchy can be 1min, 5min or 15min. The value returned represents the number of socket connections in 1 minute, averaged over 1, 5 or 15 minutes.",
    "$SYS/broker/messages/inflight":"The number of messages with QoS>0 that are awaiting acknowledgments.",
    "$SYS/broker/messages/received":"The total number of messages of any type received since the broker started.",
    "$SYS/broker/messages/sent":"The total number of messages of any type sent since the broker started.",
    "$SYS/broker/messages/stored":"The number of messages currently held in the message store. This includes retained messages and messages queued for durable clients.",
    "$SYS/broker/publish/messages/dropped":"The total number of publish messages that have been dropped due to inflight/queuing limits. See the max_inflight_messages and max_queued_messages options in mosquitto.conf(5) for more information.",
    "$SYS/broker/publish/messages/received":"The total number of PUBLISH messages received since the broker started.",
    "$SYS/broker/publish/messages/sent":"The total number of PUBLISH messages sent since the broker started.",
    "$SYS/broker/retained messages/count":"The total number of retained messages active on the broker.",
    "$SYS/broker/subscriptions/count":"The total number of subscriptions active on the broker.",
    "$SYS/broker/timestamp":"The timestamp at which this particular build of the broker was made. Static.",
    "$SYS/broker/uptime":"The amount of time in seconds the broker has been online.",
    "$SYS/broker/version":"The version of the broker. Static."
}

def get_mqtt_broker_status_description(topic):
    for k,v in mqtt_broker_status_mapping.items():
        if k in topic :
            return v