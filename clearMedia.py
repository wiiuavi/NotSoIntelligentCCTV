import shutil
import os

#run to clear all, warn on run


def clear_all_media1():

    script_dir = os.path.dirname(os.path.abspath(__file__))

    saved_path = os.path.join(script_dir, "saved")
    temp_path = os.path.join(script_dir, "temporary")
    e_path = os.path.join(script_dir, "events")
    e2_path = os.path.join(script_dir, "events2")

    if os.path.exists(saved_path):
        shutil.rmtree(saved_path)
        os.makedirs(saved_path)

    if os.path.exists(temp_path):
        shutil.rmtree(temp_path)
        os.makedirs(temp_path)

    if os.path.exists(e_path):
        shutil.rmtree(e_path)
        os.makedirs(e_path)

    if os.path.exists(e2_path):
        shutil.rmtree(e2_path)
        os.makedirs(e2_path)
