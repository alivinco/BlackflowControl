__author__ = 'alivinco'

import subprocess


class Tools():
    def start_service(self, service_name):
        sp = subprocess.check_output("service " + service_name + " start", shell=True)
        return sp

    def stop_service(self, service_name):
        sp = subprocess.check_output("service " + service_name + " stop", shell=True)
        return sp
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

    def tail_log(self, log_file,n_lines):
        return subprocess.check_output("tail -"+str(n_lines)+" "+log_file, shell=True)



if __name__ == "__main__":
    t = Tools()
    q = t.process_status("python")
    for i in q:
        print i