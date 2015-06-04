__author__ = 'alivinco'

import subprocess
import os
import platform


class Tools():
    def start_service(self, service_name):
        sp = subprocess.check_output(
            "nohup service " + service_name + " start > /tmp/nohup_" + service_name + ".log 2>&1 &", shell=True)
        return sp

    def stop_service(self, service_name):
        sp = subprocess.check_output(
            "nohup service " + service_name + " stop > /tmp/nohup_" + service_name + ".log 2>&1 &", shell=True)
        return sp

    def run_update_procedure(self, distro_server_uri, platform):
        if platform == "sg":
            script = ["curl -o /tmp/bf_install.sh " + distro_server_uri + "/install.sh"]
            script.append("chmod a+x /tmp/bf_install.sh")
            script.append("nohup /tmp/bf_install.sh  > /var/log/bla/blackfly_upgrade.log 2>&1 &")
        elif platform == "debian":
            script = ["curl -o /tmp/bf_install.sh " + distro_server_uri + "/install_debian.sh"]
            script.append("chmod a+x /tmp/bf_install.sh")
            script.append("nohup /tmp/bf_install.sh  > /var/log/blackfly/blackfly_upgrade.log 2>&1 &")
        for cmd in script:
            sp = subprocess.check_output(cmd, shell=True)
        return sp

    @staticmethod
    def open_port_in_firewall():
        try:
            if platform.system() == "Linux":
                sp = subprocess.check_output("iptables -L INPUT", shell=True)
                status = "iptables already has rule for port 5000"
                if not ("tcp dpt:5000" in sp):
                    status = "Adding rule for port 5000"
                    sp = subprocess.check_output("iptables -I INPUT -p tcp --dport 5000 -j ACCEPT", shell=True)
            else:
                status = "Your platform doesn't have iptables"
        except:
            status = "Firewall can be opened "

        return status

        # iptables -I INPUT -p tcp --dport 5000 -j ACCEPT

    def process_status(self, process_name):
        """

       :param process_name:
       :return:
       return parsed ps out
       result[0] - uname
       result[1] - pid
       result[2] - ppid
       """
        sp = subprocess.check_output("ps -ef|grep " + process_name, shell=True)
        result = []
        for line in sp.splitlines():
            ps_line = line.split(None)
            is_grep = False
            is_process_name = False
            for item in ps_line:
                if item in "grep": is_grep = True
                if item in process_name: is_process_name = True

            if not (is_grep) and not (is_process_name):
                result.append(ps_line)

        return result

    def kill_process(self, process_name):
        output = []
        ps = self.process_status(process_name)
        for proc in ps:
            pid = proc[1]
            sp = subprocess.check_output("kill -9 " + pid, shell=True)
            output.append(sp)

        return ps

    def tail_log(self, log_file, n_lines, search_str):
        if search_str:
            cmd_str = "tail -" + str(n_lines) + " " + log_file + "|grep " + search_str
        else:
            cmd_str = "tail -" + str(n_lines) + " " + log_file

        return subprocess.check_output(cmd_str, shell=True)

    def get_logfiles(self):
        """
        The function return list of log files

        :return:
        """
        log_dir = "/var/log/"
        # paths = [os.path.join(path,fn) for fn in next(os.walk(path))[2]]
        file_paths = []  # List which will store all of the full filepaths.

        # Walk the tree.
        for root, directories, files in os.walk(log_dir):
            for filename in files:
                # Join the two strings in order to form the full filepath.
                filepath = os.path.join(root, filename)
                file_paths.append(filepath)  # Add it to the list.

        return file_paths

    def get_services(self):
        """
        The function returns list of services

        :return:
        """
        path = "/etc/init.d/"
        paths = os.listdir(path)
        return paths


if __name__ == "__main__":
    t = Tools()
    # q = t.process_status("python")
    # r = t.tail_log("/var/log/system.log",100,"")
    r = t.get_logfiles()
    r = t.get_services()
    print r
