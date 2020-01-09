import os
import re
import signal
import subprocess

# -----------------------------------------------------------------------------------
# ---- U N I X - S H E L L ----------------------------------------------------------
# -----------------------------------------------------------------------------------

def find_process(process_name):
    """
    Looks for a running unix-process with the given name
    :param process_name
    :return: process-info line
    """
    ps = subprocess.Popen("ps | grep "+process_name, shell=True, stdout=subprocess.PIPE)
    output = ps.stdout.read()
    ps.stdout.close()
    ps.wait()

    return output


def is_process_running(process_name):
    """
    Wrapper for *find_process*
    :param process_name
    :return: true / false
    """
    return len(find_process(process_name)) > 0


def _execute_process(cmd):
    """
    Wrapper for performing a command in unix-shell
    :param cmd: unix-command
    :return: stdout / 1
    """
    try:
        return subprocess.run(cmd,
                              stdout=subprocess.PIPE,
                              universal_newlines=True).returncode

    except subprocess.CalledProcessError as e:
        print("Error on subprocess-execution", e.output)
        return 1


def restart_gphoto():
    if is_camera_present():
        kill_process(b'gvfsd-gphoto2')
        return True
    return False


def kill_process(process_name):
    p = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
    out, err = p.communicate()

    # Search for the process we want to kill
    for line in out.splitlines():
        if process_name in line:
            # Kill that process!
            pid = int(line.split(None, 1)[0])
            os.kill(pid, signal.SIGKILL)


#Bus 002 Device 014: ID 04a9:32cc Canon, Inc. EOS 200D
def is_camera_present():
    p1 = subprocess.Popen(["lsusb"], stdout=subprocess.PIPE)
    p2 = subprocess.Popen(["grep", "Canon"], stdin=p1.stdout, stdout=subprocess.PIPE)
    p1.stdout.close()  # Allow p1 to receive a SIGPIPE if p2 exits.

    return len(p2.communicate()[0]) > 0


# -----------------------------------------------------------------------------------
# ---- C A M E R A - A C T I O N S --------------------------------------------------
# -----------------------------------------------------------------------------------

def start_livestream():
    """
    Forwards camera-livestrem to */dev/video2*
    """
    if not is_process_running("ffmpeg"):
        try:
            subprocess.run("gphoto2 --stdout --capture-movie | ffmpeg -i - -vcodec rawvideo \
                            -pix_fmt yuv420p -threads 0 -f v4l2 /dev/video2",
                           shell=True, check=True)
        except: #TODO check for abrout
            restart_gphoto()
            pass


def stop_livestream():
    _execute_process(['gphoto2', '--set-config', "movie=0"])
    kill_process(b'ffmpeg')


def capture_preview(filename, iso, aperture):
    print("Capturing Preview...", filename, iso, aperture)

    return _execute_process(['gphoto2',
                             '--set-config', 'whitebalance=8',   # Manuell
                             '--set-config', 'aperture={}'.format(aperture),
                             '--set-config', 'iso={}'.format(iso),
                             '--filename', 'media/preview/{}'.format(filename),
                             '--force-overwrite',
                             '--capture-preview'
                             ])

# def capture_image(filename, capture_config):
#    return capture_image(filename, capture_config.iso, capture_config.aperture,
#                         capture_config.exposure, capture_config.image_format, capture_config.bulb_time)


def capture_image(path, filename, iso, aperture, exposure, image_format, bulb_time=0):

    imagepath = path[1:]+filename

    if str(bulb_time) != '0':
        return capture_image_bulb(imagepath, iso, aperture, bulb_time, image_format)

    print("Capturing Image...", imagepath, iso, aperture, exposure, image_format, bulb_time)

    return _execute_process(['gphoto2',
                             '--set-config', 'whitebalance=8',   # Manuell
                             '--set-config', 'imageformat={}'.format(image_format),
                             '--set-config', 'shutterspeed={}'.format(exposure),
                             '--set-config', 'aperture={}'.format(aperture),
                             '--set-config', 'iso={}'.format(iso),
                             '--filename', '{}'.format(imagepath),
                             '--force-overwrite',
                             '--capture-image-and-download'
                             ])


def capture_image_bulb(imagepath, iso, aperture, bulb_time, image_format):
    print("Capturing Bulb-Image...", imagepath, iso, aperture, bulb_time, image_format)

    return _execute_process(['gphoto2',
                             '--set-config', 'whitebalance=8',   # Manuell
                             '--set-config', 'imageformat={}'.format(image_format),
                             '--set-config', 'shutterspeed=bulb',
                             '--set-config', 'aperture={}'.format(aperture),
                             '--set-config', 'iso={}'.format(iso),
                             '--filename', '{}'.format(imagepath),
                             '--wait-event=1s',
                             '--set-config', 'eosremoterelease=5',
                             '--wait-event={}s'.format(bulb_time),
                             '--set-config', 'eosremoterelease=11',
                             '--wait-event-and-download=2s'
                             ])

# -----------------------------------------------------------------------------------
# ---- R E A D - C A M E R A - C O N F I G ------------------------------------------
# -----------------------------------------------------------------------------------

def get_certain_config(action):
    try:
        proc1 = subprocess.Popen(['gphoto2',
                                 '--get-config', action], stdout=subprocess.PIPE)

        proc2 = subprocess.Popen(['grep', 'Current:'], stdin=proc1.stdout,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        proc1.stdout.close()
        out, err = proc2.communicate()
        return True, str(out).split(' ')[1][:-3]
    except: #TODO
        return False, None


def get_available_shots():
    success, val = get_certain_config('/main/status/availableshots')
    if success:
        return val
    return 0


def get_battery_level(cam_is_present):
    if cam_is_present:
        success, val = get_certain_config('/main/status/batterylevel')
        if success:
            return val
    return 0


def get_iso(cam_is_present):
    if cam_is_present:
        success, val = get_certain_config('/main/imgsettings/iso')
        if success:
            return val
    return 200


def get_aperture(cam_is_present):
    if cam_is_present:
        success, val = get_certain_config('/main/capturesettings/aperture')
        if success:
            return val
    return 5.6


def get_exposure(cam_is_present):
    if cam_is_present:
        success, val = get_certain_config('/main/capturesettings/shutterspeed')
        if success:
            return val
    return 0.4


def get_image_format(cam_is_present):
    if cam_is_present:
        success, val = get_certain_config('/main/imgsettings/imageformatsd')
        if success:
            return val
    return 'Large Normal JPEG'


def get_auto_off():
    _, val = get_certain_config('/main/settings/autopoweroff')
    return val
