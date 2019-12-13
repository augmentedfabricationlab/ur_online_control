import sys, os, socket

# set the paths to find library
file_dir = os.path.dirname( __file__)
parent_dir = os.path.abspath(os.path.join(file_dir, ".."))
parent_parent_dir = os.path.abspath(os.path.join(parent_dir, ".."))
sys.path.append(file_dir)
sys.path.append(parent_dir)
sys.path.append(parent_parent_dir)

from ur_online_control.utilities import read_file_to_string, read_file_to_list
from ur_online_control.ur_direct.utilities import send_script, is_available

UR_SERVER_PORT = 30002

def generate_script_pick_block(pick_up_plane):
    pass

def generate_script_place_block():
    pass

def generate_script_pick_and_place_block(tool_angle_axis, movel_cmds=[]):

    
    script_lines = []

    # move to pick up plane safe level
    x, y, z, ax, ay, az, speed, radius = movel_cmds[0]
    script_lines.append("movel(p%s, v=%f, r=%f)" % (str([x/1000., y/1000., z/1000, ax, ay, az]), speed/1000., radius/1000.))

    # move to pick up plane
    x, y, z, ax, ay, az, speed, radius = movel_cmds[1]
    script_lines.append("movel(p%s, v=%f, r=%f)" % (str([x/1000., y/1000., z/1000, ax, ay, az]), speed/1000., radius/1000.))

    # turn vacuum on
    script_lines.append('rq_vacuum_grip(advanced_mode=True, maximum_vacuum=60, minimum_vacuum=10, timeout_ms=10, wait_for_object_detected=True, gripper_socket="1")')
    #script_lines.append("sleep(1)")

    # move to pick up plane safe level
    x, y, z, ax, ay, az, speed, radius = movel_cmds[2]
    script_lines.append("movel(p%s, v=%f, r=%f)" % (str([x/1000., y/1000., z/1000, ax, ay, az]), speed/1000., radius/1000.))

    # move to current plane safe level
    x, y, z, ax, ay, az, speed, radius = movel_cmds[3]
    script_lines.append("movel(p%s, v=%f, r=%f)" % (str([x/1000., y/1000., z/1000, ax, ay, az]), speed/1000., radius/1000.))

    # move to current plane
    x, y, z, ax, ay, az, speed, radius = movel_cmds[4]
    script_lines.append("movel(p%s, v=%f, r=%f)" % (str([x/1000., y/1000., z/1000, ax, ay, az]), speed/1000., radius/1000.))

     # turn vacuum off
    script_lines.append('rq_vacuum_release(advanced_mode=True, shutoff_distance_cm=1, wait_for_object_released=False, gripper_socket="1")')
    #script_lines.append("sleep(0.3)")

    # move to current plane safe level
    x, y, z, ax, ay, az, speed, radius = movel_cmds[5]
    script_lines.append("movel(p%s, v=%f, r=%f)" % (str([x/1000., y/1000., z/1000, ax, ay, az]), speed/1000., radius/1000.))


    script = "\n"
    script += "\ttextmsg(\">> program start\")\n"

    x, y, z, ax, ay, az = tool_angle_axis
    script += "\tset_tcp(p%s)\n" % str([x/1000., y/1000., z/1000, ax, ay, az]) # set tool tcp
    
    script += "".join(["\t%s\n" % line for line in script_lines])
    script += "\ttextmsg(\"<< program end\")\n"

    path = os.path.join(os.path.dirname(__file__), "scripts")
    program_file = os.path.join(path, "airpick_program.script")
    program_str = read_file_to_string(program_file)


    program_str = program_str.replace("{AIRPICK_PROGRAM}", script)
    return program_str

    #pick_and_place with approach plane
def generate_script_pick_and_place_interlock(tool_angle_axis, movel_cmds=[]):

    
    script_lines = []

    # move to pick up plane safe level
    x, y, z, ax, ay, az, speed, radius = movel_cmds[0]
    script_lines.append("movel(p%s, v=%f, r=%f)" % (str([x/1000., y/1000., z/1000, ax, ay, az]), speed/1000., radius/1000.))

    # move to pick up plane
    x, y, z, ax, ay, az, speed, radius = movel_cmds[1]
    script_lines.append("movel(p%s, v=%f, r=%f)" % (str([x/1000., y/1000., z/1000, ax, ay, az]), speed/1000., radius/1000.))

    # turn vacuum on
    script_lines.append('rq_vacuum_grip(advanced_mode=True, maximum_vacuum=60, minimum_vacuum=10, timeout_ms=10, wait_for_object_detected=True, gripper_socket="1")')
    #script_lines.append("sleep(1)")

    # move to pick up plane safe level
    x, y, z, ax, ay, az, speed, radius = movel_cmds[2]
    script_lines.append("movel(p%s, v=%f, r=%f)" % (str([x/1000., y/1000., z/1000, ax, ay, az]), speed/1000., radius/1000.))

    # move to current approch plane safe level
    x, y, z, ax, ay, az, speed, radius = movel_cmds[3]
    script_lines.append("movel(p%s, v=%f, r=%f)" % (str([x/1000., y/1000., z/1000, ax, ay, az]), speed/1000., radius/1000.))

    # move to current approch plane
    x, y, z, ax, ay, az, speed, radius = movel_cmds[4]
    script_lines.append("movel(p%s, v=%f, r=%f)" % (str([x/1000., y/1000., z/1000, ax, ay, az]), speed/1000., radius/1000.))

    # move to current plane
    x, y, z, ax, ay, az, speed, radius = movel_cmds[5]
    script_lines.append("movel(p%s, v=%f, r=%f)" % (str([x/1000., y/1000., z/1000, ax, ay, az]), speed/1000., radius/1000.))

     # turn vacuum off
    script_lines.append('rq_vacuum_release(advanced_mode=True, shutoff_distance_cm=1, wait_for_object_released=False, gripper_socket="1")')
    #script_lines.append("sleep(0.3)")

    # move to current plane safe level
    x, y, z, ax, ay, az, speed, radius = movel_cmds[6]
    script_lines.append("movel(p%s, v=%f, r=%f)" % (str([x/1000., y/1000., z/1000, ax, ay, az]), speed/1000., radius/1000.))


    script = "\n"
    script += "\ttextmsg(\">> program start\")\n"

    x, y, z, ax, ay, az = tool_angle_axis
    script += "\tset_tcp(p%s)\n" % str([x/1000., y/1000., z/1000, ax, ay, az]) # set tool tcp
    
    script += "".join(["\t%s\n" % line for line in script_lines])
    script += "\ttextmsg(\"<< program end\")\n"

    path = os.path.join(os.path.dirname(__file__), "scripts")
    program_file = os.path.join(path, "airpick_program.script")
    program_str = read_file_to_string(program_file)


    program_str = program_str.replace("{AIRPICK_PROGRAM}", script)
    return program_str


    #path = os.path.join(os.path.dirname(__file__), "scripts")
    #methods_file = os.path.join(path, "airpick_methods.script") 
    #methods_str = read_file_to_string(methods_file)
    #program_str = methods_str + "\n" + script
    #return program_str    

def generate_script_airpick_on():

    path = os.path.join(os.path.dirname(__file__), "scripts")
    program_file = os.path.join(path, "airpick_program.script")
    program_str = read_file_to_string(program_file)

    vacuum_on_file = os.path.join(path, "airpick_vacuum_on.script")
    #vacuum_on_str = read_file_to_string(vacuum_on_file)

    vacuum_on_list = read_file_to_list(vacuum_on_file)
    vacuum_on_str = "\t".join(vacuum_on_list)

    program_str = program_str.replace("{AIRPICK_PROGRAM}", vacuum_on_str)
    return program_str


def generate_script_airpick_off():

    path = os.path.join(os.path.dirname(__file__), "scripts")
    program_file = os.path.join(path, "airpick_program.script")
    program_str = read_file_to_string(program_file)

    vacuum_off_file = os.path.join(path, "airpick_vacuum_off.script")
    #vacuum_on_str = read_file_to_string(vacuum_on_file)

    vacuum_off_list = read_file_to_list(vacuum_off_file)
    vacuum_off_str = "\t".join(vacuum_off_list)

    program_str = program_str.replace("{AIRPICK_PROGRAM}", vacuum_off_str)
    return program_str

def get_test_script():
    path = os.path.join(os.path.dirname(__file__), "scripts")
    program_file = os.path.join(path, "test.script")
    program_str = read_file_to_string(program_file)
    return program_str

def get_airpick_on_script():
    path = os.path.join(os.path.dirname(__file__), "scripts")
    program_file = os.path.join(path, "airpick_vacuum_off_full.script")
    #program_file = os.path.join(path, "test.script")
    program_str = read_file_to_string(program_file)
    return program_str

def get_airpick_off_script():
    path = os.path.join(os.path.dirname(__file__), "scripts")
    program_file = os.path.join(path, "airpick_vacuum_off_full.script")
    program_str = read_file_to_string(program_file)
    return program_str

if __name__ == "__main__":
    
    ur_ip = "192.168.10.10"
    #program = generate_script_airpick_on()

    tool_angle_axis = [0.0, -2.8878212124549687e-11, 158.28878352076936, 0.0, 0.0, 0.0]
    movel_cmds = [[932.16352622584691, 45.665029053475799, 24.999999999999982, 2.2214414690791831, -2.2214414690791831, 0.0, 20.0, 0.0], [932.16352622584691, 45.665029053475799, 24.999999999999982, 2.2214414690791831, -2.2214414690791831, 0.0, 20.0, 0.0], [932.16352622584691, 45.665029053475799, 24.999999999999982, 2.2214414690791831, -2.2214414690791831, 0.0, 20.0, 20.0], [932.16352622584691, 45.665029053475799, 24.999999999999982, 2.2214414690791831, -2.2214414690791831, 0.0, 20.0, 20.0], [932.16352622584691, 45.665029053475799, 24.999999999999982, 2.2214414690791831, -2.2214414690791831, 0.0, 20.0, 0.0], [932.16352622584691, 45.665029053475799, 24.999999999999982, 2.2214414690791831, -2.2214414690791831, 0.0, 20.0, 0.0]]
    program = generate_script_pick_and_place_block(tool_angle_axis, movel_cmds)

    #program_on = get_airpick_on_script()
    #program_off = get_airpick_off_script()

    #program = generate_script_airpick_off()

    #program = get_airpick_off_script()
    program = get_test_script()
    print(program)

    send_script(ur_ip, program,  port=UR_SERVER_PORT)