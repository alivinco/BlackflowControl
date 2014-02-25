__author__ = 'aleksandrsl'
import os

# msg_list = {"events": ["file_name"], "commands": ["file_name"]}
msg_list = [{"file_name":"inclusion.json","type":"event"}]


class MessageManager:
    def __init__(self):
        self.root = "C:\ALWorks\SG\BlackflyTestSuite\messages"

    def list_files(self):
        events_dir = os.path.join(self.root, "events")
        commands_dir = os.path.join(self.root, "commands")
        msg_list = []
        for file in os.listdir(events_dir):
            msg_list.append({"file_name":file,"type":"event"})
        for file in os.listdir(commands_dir):
            msg_list.append({"file_name":file,"type":"command"})

        return msg_list


if __name__ == "__main__":
    m = MessageManager()
    print m.list_files()