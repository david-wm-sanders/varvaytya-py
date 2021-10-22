import itertools
import pathlib
import shutil
import subprocess
import xml.etree.ElementTree as XmlET

# this magic allows for Ctrl+C to PyCharm run console to be handled nicely
try:
    from console_thrift import KeyboardInterruptException as KeyboardInterrupt  # noqa
except ImportError:
    pass

SCRIPT_DIR = pathlib.Path(__file__).parent
PKG_CFG = SCRIPT_DIR / "package_config.xml"
AS_SCRIPT = SCRIPT_DIR / "start_enlistd_invasion_2.as"
RWR_ROOT = pathlib.Path(r"C:\Program Files (x86)\Steam\steamapps\common\RunningWithRifles")
RWR_SERV = RWR_ROOT / "rwr_server.exe"
PKGS_ROOT = RWR_ROOT / "media/packages"
TEST_PKG_DIR = PKGS_ROOT / "_enlistd_test_pkg"


def _consume_prompt(proc):
    # consume the prompt marker
    prompt_marker = proc.stdout.read(1)
    if prompt_marker != ">":
        raise Exception(f"prompt marker read got unexpected '{prompt_marker}' :/")


def wait_for_server_load(proc):
    _spinner_steps = itertools.cycle(["/", "-", "\\", "|"])
    while True:
        # read a line from rwr server stdout
        _output_line = proc.stdout.readline().lstrip(">")
        # strip the line for easier processing
        _stripped_line = _output_line.strip()
        # print(f"{stripped_line=!r}")
        if _stripped_line.startswith("Loading"):
            _s = next(_spinner_steps)
            print(f"{_s} Loading...", end="\r")
        elif _stripped_line == "Game loaded":
            # exit the while loop now
            break
        else:
            print(_stripped_line)
    return True


def send_command(proc, cmd: str):
    proc.stdin.write(f"{cmd}\n")
    proc.stdin.flush()


def setup_test_pkg():
    if not TEST_PKG_DIR.exists():
        TEST_PKG_DIR.mkdir()
    # copy in the latest package config
    shutil.copy(PKG_CFG, TEST_PKG_DIR)
    (TEST_PKG_DIR / "scripts").mkdir(exist_ok=True)
    # copy in the server starting script
    shutil.copy(AS_SCRIPT, (TEST_PKG_DIR / "scripts"))


if __name__ == '__main__':
    # set up the test env
    setup_test_pkg()
    # start an rwr server
    path_to_package = f"media/packages/{TEST_PKG_DIR.name}"
    print(f"Starting RWR server for '{path_to_package}' package...")
    rwr_serv_args = [f"{RWR_SERV}"]
    # rwr_serv_args = [f"{RWR_SERV}", "verbose"]
    # rwr_serv = subprocess.run(rwr_serv_args, cwd=RWR_ROOT.absolute(), encoding="utf-8")
    rwr_serv = subprocess.Popen(rwr_serv_args, cwd=RWR_ROOT.absolute(), encoding="utf-8",
                                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    try:
        # wait for the first prompt
        wait_for_server_load(rwr_serv)
        _consume_prompt(rwr_serv)
        start_server_command = f"start_script {AS_SCRIPT.name} {path_to_package}"
        print(f"Server loaded, sending '{start_server_command}'...")
        # write the start script command to rwr server stdin
        send_command(rwr_serv, start_server_command)
        # wait again as the server now loads from overlays set in the script
        wait_for_server_load(rwr_serv)
        print(f"Package script start completed!")
        # wait until Ctrl-C
        while True:
            # read a line from rwr server stdout
            output_line = rwr_serv.stdout.readline().lstrip(">")
            # strip the line for easier processing
            stripped_line = output_line.strip()
            print(stripped_line)
            # time.sleep(10)
            # todo: print status
    except KeyboardInterrupt:
        print("Ctrl-C detected, shutting down!")
        rwr_serv.kill()

