import socket
from socketserver import TCPServer, BaseRequestHandler
import sys
import os
# set the paths to find library
file_dir = os.path.dirname( __file__)
parent_dir = os.path.abspath(os.path.join(file_dir, ".."))
parent_parent_dir = os.path.abspath(os.path.join(parent_dir, ".."))
sys.path.append(file_dir)
sys.path.append(parent_dir)
sys.path.append(parent_parent_dir)
from ur_online_control.utilities import read_file_to_string, read_file_to_list


def list_str_to_list(str):
    str = str[(str.find("[") + 1):str.find("]")]
    return [float(x) for x in str.split(",")]


def is_available(ur_ip):
    system_call = "ping -r 1 -n 1 {}".format(ur_ip)
    response = os.system(system_call)
    if response == 0:
        return True
    else:
        return False


def send_script(ur_ip, script, port=30002):
    try:
        s = socket.create_connection((ur_ip, port), timeout=2)
        s.send(script)
        print("Script sent to %s on port %i" % (ur_ip, port))
        s.close()
    except socket.timeout:
        print("UR with ip %s not available on port %i" % (ur_ip, port))
        raise


class MyTCPHandler(BaseRequestHandler):
    def handle(self):
        # self.request is the TCP socket connected to the client
        pose = ""
        while pose.find("]") == -1:
            pose += self.request.recv(1024)
        self.server.rcv_msg = pose
        self.server.server_close() # this throws an exception


def generate_base_script(server_ip, server_port, tool_angle_axis, ur_ip):
    base_script = URCommandScript(server_ip, server_port, tool_angle_axis, ur_ip)
    base_script.start()
    return base_script


def generate_script_pick_and_place_block(base_script, move_commands=[], interlock=False):
    base_script.add_airpick_commands()
    for i, [x, y, z, dx, dy, dz, r, v] in zip(range(len(move_commands)), move_commands):
        base_script.add_move_linear(x, y, z, dx, dy, dz, r, v)
        if i == 1:
            base_script.airpick_on()
        elif i == 4 and not interlock:
            base_script.airpick_off()
        elif i == 5 and interlock:
            base_script.airpick_off()
        else:
            pass
    base_script.end()
    return base_script.dict_to_script()

def airpick_on(base_script):
    base_script.add_airpick_commands()
    base_script.airpick_on()
    base_script.end()
    return base_script.dict_to_script()

def airpick_off(base_script):
    base_script.add_airpick_commands()
    base_script.airpick_off()
    base_script.end()
    return base_script.dict_to_script()


class URCommandScript:
    def __init__(self, server_ip, server_port, tool_angle_axis, ur_ip):
        self.commands_dict = {}
        self.server_ip = server_ip
        self.server_port = server_port
        self.tool_angle_axis = tool_angle_axis
        self.ur_ip = ur_ip
        self.airpick_commands = False

    def dict_to_script(self):
        return '\n'.join(self.commands_dict.values())

    def start(self):
        self.commands_dict.update({
            0: "def program():",
            1: "\ttextmsg(\">> Entering program.\")",
            2: "\tSERVER_ADDRESS = \"{}\"".format(self.server_ip),
            3: "\tPORT = {}".format(self.server_port),
            4: "\ttextmsg(SERVER_ADDRESS)",
            5: "\ttextmsg(PORT)",
            6: "\tset_tcp(p{})".format(self.tool_angle_axis),
            7: "\tsocket_open(SERVER_ADDRESS, PORT)"
        })

    def end(self):
        i = len(self.commands_dict)
        self.commands_dict.update({
            i: "\tsocket_close()",
            i+1: "\ttextmsg(\"<< Exiting program.\")",
            i+2: "end",
            i+3: "program()\n\n\n"
        })

    def get_current_position_cartesian(self):
        i = len(self.commands_dict)
        self.commands_dict.update({
            i: "\tcurrent_pose = get_forward_kin()",
            i+1: "\ttextmsg(current_pose)",
            i+2: "\tMM2M = 1000.0",
            i+3: "\tsocket_send_string([current_pose[0] * MM2M, current_pose[1] * MM2M, current_pose[2] * MM2M, current_pose[3], current_pose[4], current_pose[5]])"
        })

    def add_move_linear(self, x, y, z, dx, dy, dz, v, r):
        i = len(self.commands_dict)
        self.commands_dict.update({
            i: "\tmovel(p[{}, {}, {}, {}, {}, {}], v={}, r={})".format(x, y, z, dx, dy, dz, v, r)
        })

    def airpick_on(self):
        i = len(self.commands_dict)
        self.commands_dict.update({
            i: "\trq_vacuum_grip(advanced_mode=True, maximum_vacuum=60, minimum_vacuum=10, timeout_ms=10, wait_for_object_detected=True, gripper_socket='1')"
        })
        self.airpick_commands = True

    def airpick_off(self):
        i = len(self.commands_dict)
        self.commands_dict.update({
            i: "\trq_vacuum_release(advanced_mode=True, shutoff_distance_cm=1, wait_for_object_released=False, gripper_socket='1')"
        })
        self.airpick_commands = True

    def add_airpick_commands(self):
        path = os.path.join(os.path.dirname(__file__), "scripts")
        program_file = os.path.join(path, "airpick_methods.script")
        program_str = read_file_to_string(program_file)
        i = len(self.commands_dict)
        self.commands_dict.update({
            i: program_str
        })

    def check_available(self):
        system_call = "ping -r 1 -n 1 {}".format(self.ur_ip)
        response = os.system(system_call)
        if response == 0:
            return True
        else:
            return False

    def send_script(self, port=30002):
        script = self.dict_to_script()
        if self.airpick_commands:
            script = self.add_airpick_commands(script)
        else:
            pass

        # start server
        server = TCPServer((self.server_ip, self.server_port), MyTCPHandler)

        try:
            s = socket.create_connection((self.ur_ip, port), timeout=2)
            s.send(script)
            print("Script sent to %s on port %i" % (self.ur_ip, port))
            s.close()
        except socket.timeout:
            print("UR with ip %s not available on port %i" % (self.ur_ip, port))
            raise

        # send file
        try:
            server.serve_forever()
        except:
            return list_str_to_list(server.rcv_msg)

if __name__ == "__main__":
    server_port = 30005
    server_ip = "192.168.10.11"
    ur_ip = "192.168.10.10"

    tool_angle_axis = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    movel_cmds = [
        [900.0, 45.0, 25.0, 2.0, -2.0, 0.0, 20.0, 0.0],
        [900.0, 45.0, 25.0, 2.0, -2.0, 0.0, 20.0, 0.0],
        [900.0, 45.0, 25.0, 2.0, -2.0, 0.0, 20.0, 0.0],
        [900.0, 45.0, 25.0, 2.0, -2.0, 0.0, 20.0, 0.0],
        [900.0, 45.0, 25.0, 2.0, -2.0, 0.0, 20.0, 0.0],
        [900.0, 45.0, 25.0, 2.0, -2.0, 0.0, 20.0, 0.0]
    ]
    base_script = generate_base_script(server_ip, server_port, tool_angle_axis, ur_ip)
    program = generate_script_pick_and_place_block(base_script, movel_cmds)

    print(program)