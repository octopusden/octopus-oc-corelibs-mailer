from setuptools import setup
import os
import glob

__version="1.0.0"

def list_recursive(app, directory, extension="*"):
    dir_to_walk = os.path.join(app, directory)

    found = [result for (cur_dir, subdirs, files) in os.walk(dir_to_walk)
             for result in glob.glob(os.path.join(cur_dir, '*.' + extension))]

    found_in_package = list(map(lambda x: x.replace(app + os.path.sep, "", 1), found))
    return found_in_package


spec = {
    "name": "oc_mailer",
    "version": __version,
    "license": "LGPLv2",
    "description": "SMTP mailer class for senging auto-notifications with pre-defined templates",
    "long_description": "",
    "long_description_content_type": "text/plain",
    "packages": ["oc_mailer"],
    "install_requires": [],
    "package_data": {"oc_mailer": list_recursive("oc_mailer", "resources")},
    "python_requires": ">=3.6",
}

setup(**spec)
