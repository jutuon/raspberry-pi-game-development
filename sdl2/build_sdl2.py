#!/usr/bin/python3

import os
import subprocess
import sys
import shutil
import glob

# Download links

SDL2_LINK = "https://www.libsdl.org/release/SDL2-2.0.5.tar.gz"
SDL2_IMAGE_LINK = "https://www.libsdl.org/projects/SDL_image/release/SDL2_image-2.0.1.tar.gz"
SDL2_TTF_LINK = "https://www.libsdl.org/projects/SDL_ttf/release/SDL2_ttf-2.0.14.tar.gz"
SDL2_MIXER_LINK = "https://www.libsdl.org/projects/SDL_mixer/release/SDL2_mixer-2.0.1.tar.gz"

def get_last_part_from_url(url):
    url_parts = url.split('/')
    return url_parts.pop()

def remove_file_extension(file_name, file_extension):
    return file_name.partition(file_extension)[0]

# File names with file extension

SDL2_TAR = get_last_part_from_url(SDL2_LINK)
SDL2_IMAGE_TAR = get_last_part_from_url(SDL2_IMAGE_LINK)
SDL2_TTF_TAR = get_last_part_from_url(SDL2_TTF_LINK)
SDL2_MIXER_TAR = get_last_part_from_url(SDL2_MIXER_LINK)

# Set directory names

FILE_EXTENSION = ".tar.gz"

BUILD_DIR = "sdl2-build-directory"
SDL2_DIR = remove_file_extension(SDL2_TAR, FILE_EXTENSION)
SDL2_IMAGE_DIR = remove_file_extension(SDL2_IMAGE_TAR, FILE_EXTENSION)
SDL2_TTF_DIR = remove_file_extension(SDL2_TTF_TAR, FILE_EXTENSION)
SDL2_MIXER_DIR = remove_file_extension(SDL2_MIXER_TAR, FILE_EXTENSION)

SDL2_ALL = {
    "url": SDL2_LINK,
    "tar_archive_name": SDL2_TAR,
    "directory_name": SDL2_DIR,
    "configure_argument_list": [],
}
SDL2_MIXER_ALL = {
    "url":SDL2_MIXER_LINK,
    "tar_archive_name": SDL2_MIXER_TAR,
    "directory_name": SDL2_MIXER_DIR,
    "configure_argument_list": [],
}
SDL2_TTF_ALL = {
    "url":SDL2_TTF_LINK,
    "tar_archive_name": SDL2_TTF_TAR,
    "directory_name": SDL2_TTF_DIR,
    "configure_argument_list": [],
}
SDL2_IMAGE_ALL = {
    "url":SDL2_IMAGE_LINK,
    "tar_archive_name": SDL2_IMAGE_TAR,
    "directory_name": SDL2_IMAGE_DIR,
    "configure_argument_list": [],
}


INCLUDE_DIR = "include"
LIBRARY_DIR = "lib"

BUILDING_OK_FILE_NAME = "building-info.txt"

def download_if_not_exists(url_to_file, file_name_for_download):
    if os.path.exists(file_name_for_download):
        print("file '" + file_name_for_download + "' already exist")
    else:
        run_program(["wget", url_to_file])

def run_program_and_return_output(list_of_arguments):
    try:
        return subprocess.check_output(list_of_arguments, stderr=sys.stderr)
    except subprocess.CalledProcessError:
        print("error when running program '" + list_of_arguments[0] + "' with arguments " + str(list_of_arguments[1:]))
        exit(-1)

def run_program(list_of_arguments):
    try:
        subprocess.check_call(list_of_arguments, stdout=sys.stdout, stderr=sys.stderr)
    except subprocess.CalledProcessError:
        print("error when running program '" + list_of_arguments[0] + "' with arguments " + str(list_of_arguments[1:]))
        exit(-1)

def extract_if_not_exists(archive_name, dir_name):
    if os.path.exists(dir_name):
        print("archive '"+ archive_name +"' is already extracted to '" + dir_name + "'")
    else:
        run_program(["tar", "--extract", "--file", archive_name])

def build_library(dir_name, config_flags_list, no_skip):
    os.chdir(dir_name)

    if not os.path.exists("build"):
        os.mkdir("build")

    os.chdir("build")

    if os.path.exists(BUILDING_OK_FILE_NAME) and not no_skip:
        print("library at directory " + dir_name + " is already been built")
    else:
        run_program(["../configure"] + config_flags_list)
        run_program(["make"])

        file = open(BUILDING_OK_FILE_NAME, mode='w')
        file.write("building finished without errors\n\n")
        file.close()


    os.chdir(os.pardir)
    os.chdir(os.pardir)

def show_configure_options(dir_name):
    os.chdir(dir_name)
    run_program(["./configure", "--help"])
    os.chdir(os.pardir)

def copy_building_result(dir_name):

    # Create directories where files will be copied.
    if not os.path.exists(LIBRARY_DIR):
        os.mkdir(LIBRARY_DIR)

    if not os.path.exists(INCLUDE_DIR):
        os.mkdir(INCLUDE_DIR)

    os.chdir(INCLUDE_DIR)

    if not os.path.exists("SDL2"):
        os.mkdir("SDL2")

    os.chdir(os.pardir)

    # Copy files.

    os.chdir(dir_name)

    if os.path.exists("include"):
        for path in glob.iglob("include/*.h"):
            shutil.copy(path, "../" + INCLUDE_DIR + "/SDL2")
    else:
        for path in glob.iglob("SDL*.h"):
            shutil.copy(path, "../" + INCLUDE_DIR + "/SDL2")

    os.chdir("build")

    if os.path.exists("build/.libs"):
        for path in glob.iglob("build/.libs/libSDL2*.a"):
            shutil.copy(path, "../../" + LIBRARY_DIR)

        for path in glob.iglob("build/.libs/libSDL2*.so*"):
            try:
                shutil.copy(path, "../../" + LIBRARY_DIR, follow_symlinks=False)
            except FileExistsError:
                continue

    elif os.path.exists(".libs"):
        for path in glob.iglob(".libs/libSDL2*.a"):
            shutil.copy(path, "../../" + LIBRARY_DIR)

        for path in glob.iglob(".libs/libSDL2*.so*"):
            try:
                shutil.copy(path, "../../" + LIBRARY_DIR, follow_symlinks=False)
            except FileExistsError:
                continue

    if os.path.exists("include/SDL_config.h"):
        shutil.copy("include/SDL_config.h", "../../" + INCLUDE_DIR + "/SDL2")


    os.chdir(os.pardir)
    os.chdir(os.pardir)

def change_to_build_directory():
    if os.path.split(os.getcwd())[1] == BUILD_DIR:
        return

    if not os.path.exists(BUILD_DIR):
        os.mkdir(BUILD_DIR)

    os.chdir(BUILD_DIR)

def exit_if_running_as_root():
    if os.getuid() == 0:
        print("Run this script only with normal user privileges, not as root")
        exit(-1)

def download_and_extract_all(list_of_libraries):
    print("\n------- Downloading SDL libraries -------\n")
    for library in list_of_libraries:
        download_if_not_exists(library["url"], library["tar_archive_name"])

    print("\n------- Extracting library source archives -------\n")
    for library in list_of_libraries:
        extract_if_not_exists(library["tar_archive_name"], library["directory_name"])

def show_configure_options_for_all_libraries(list_of_libraries):
    for library in list_of_libraries:
        print("\n------- Configure options for '" + library["directory_name"] + "' -------\n")
        show_configure_options(library["directory_name"])

def build_all_libraries_and_copy_library_files(list_of_libraries, no_skip):
    # Build SDL2 first, because add-on libraries requires it.
    print("\n------- Building '" + SDL2_ALL["directory_name"] + "' -------\n")
    print(" Configure options: " + str(SDL2_ALL["configure_argument_list"]) + "\n")
    build_library(SDL2_ALL["directory_name"], SDL2_ALL["configure_argument_list"], no_skip)

    print("\n------- Copying library files for '" + SDL2_ALL["directory_name"] + "' -------\n")
    copy_building_result(SDL2_ALL["directory_name"])

    os.environ["SDL2_CONFIG"] = os.path.join(os.getcwd(), SDL2_DIR, "build", "sdl2-config")
    os.environ["CPPFLAGS"] = "-I" + os.path.join(os.getcwd(), INCLUDE_DIR, "SDL2")
    os.environ["LDFLAGS"] = "-L" + os.path.join(os.getcwd(), LIBRARY_DIR)

    for library in list_of_libraries:
        if library == SDL2_ALL:
            continue

        print("\n------- Building '" + library["directory_name"] + "' -------\n")
        print(" Configure options: " + str(library["configure_argument_list"]) + "\n")

        build_library(library["directory_name"], library["configure_argument_list"], no_skip)

    for library in list_of_libraries:
        if library == SDL2_ALL:
            continue

        print("\n------- Copying built library files for '" + library["directory_name"] + "' -------\n")
        copy_building_result(library["directory_name"])


SCRIPT_OPTIONS = {
    "--show-configure-sdl2": {
        "help_option_text": "--show-configure-sdl2",
        "help_text": "Show SDL2 configure script's available options.",
        "libraries": [SDL2_ALL],
        "action": "show_configure",
    },
    "--show-configure-mixer": {
        "help_option_text": "--show-configure-mixer",
        "help_text": "Show SDL2_mixer configure script's available options.",
        "libraries": [SDL2_MIXER_ALL],
        "action": "show_configure",
    },
    "--show-configure-ttf": {
        "help_option_text": "--show-configure-ttf",
        "help_text": "Show SDL2_ttf configure script's available options.",
        "libraries": [SDL2_TTF_ALL],
        "action": "show_configure",
    },
    "--show-configure-image": {
        "help_option_text": "--show-configure-image",
        "help_text": "Show SDL2_image configure script's available options.",
        "libraries": [SDL2_IMAGE_ALL],
        "action": "show_configure",
    },
    "--build-sdl2": {
        "help_option_text": "--build-sdl2 [CONFIGURE_OPTIONS]",
        "help_text": "Build SDL2.",
        "libraries": [SDL2_ALL],
        "action": "build",
    },
    "--build-mixer": {
        "help_option_text": "--build-mixer [CONFIGURE_OPTIONS]",
        "help_text": "Build SDL2_mixer.",
        "libraries": [SDL2_MIXER_ALL],
        "action": "build",
    },
    "--build-ttf": {
        "help_option_text": "--build-ttf [CONFIGURE_OPTIONS]",
        "help_text": "Build SDL2_ttf.",
        "libraries": [SDL2_TTF_ALL],
        "action": "build",
    },
    "--build-image": {
        "help_option_text": "--build-image [CONFIGURE_OPTIONS]",
        "help_text": "Build SDL2_image.",
        "libraries": [SDL2_IMAGE_ALL],
        "action": "build",
    },
    "--build-all": {
        "help_option_text": "--build-all",
        "help_text": "Build all libraries with default configure options.",
        "libraries": [SDL2_ALL, SDL2_TTF_ALL, SDL2_MIXER_ALL, SDL2_IMAGE_ALL],
        "action": "build",
    },
    "--help": {
        "help_option_text": "--help",
        "help_text": "Show this text.",
        "libraries": [],
        "action": "show_help",
    },
    "-h": {
        "help_option_text": "-h",
        "help_text": "Show this text.",
        "libraries": [],
        "action": "show_help",
    },
    "--add-profile-variables": {
        "help_option_text": "--add-profile-variables",
        "help_text": "Add header and library files location variables to your ~/.profile",
        "libraries": [],
        "action": "modify_profile_file",
    },
    "--no-skip": {
        "help_option_text": "--no-skip",
        "help_text": "Don't skip building if library is built before.",
        "libraries": [],
        "action": "no_skip",
    },
    "--no-configure-options": {
        "help_option_text": "--no-configure-options",
        "help_text": "Build with no default or user selected configure options.",
        "libraries": [],
        "action": "no_configure_options",
    },
    "--no-raspberry-pi-support": {
        "help_option_text": "--no-raspberry-pi-support",
        "help_text": "Disables adding '--host=...' configure option with target triple containing text '-raspberry-linux'.",
        "libraries": [],
        "action": "no_raspberry_pi_support",
    },
}

def build_option_help_text():
    text = "Options:\n"
    white_space_count = 35

    options_list = list(SCRIPT_OPTIONS.items())
    options_list.sort(key= lambda item: str.lower(item[0]))

    # TODO: change str concatenating to something more efficient.
    for key_and_value in options_list:
        first_text = key_and_value[1]["help_option_text"]
        text += "  " + first_text + " "*max(0, white_space_count - len(first_text)) + key_and_value[1]["help_text"] + "\n"

    return text

def library_to_text(library):
     text = "\n  URL: " + library["url"] + "\n  Configure options: "
     text += str(library["configure_argument_list"]) + "\n"
     return text

def default_settings_as_text():
    # TODO: change str concatenating to something more efficient.
    text = ""
    text += "SDL2" + library_to_text(SDL2_ALL) + "\n"
    text += "SDL2_image" + library_to_text(SDL2_IMAGE_ALL) + "\n"
    text += "SDL2_mixer" + library_to_text(SDL2_MIXER_ALL) + "\n"
    text += "SDL2_ttf" + library_to_text(SDL2_TTF_ALL) + "\n"
    return text


INCLUDE_ENVIRONMENT_VARIABLE = "SDL2_INCLUDE"
LIBRARY_ENVIRONMENT_VARIABLE = "SDL2_LIBRARY"

HELP_TEXT = """
SDL2 libraries building script.

Usage: ./build_sdl2.py [OPTIONS]

""" + build_option_help_text() + """\

Examples:
  ./build_sdl2.py --build-sdl2 "enable-video-opengl enable-video-opengles"

------- Default download URLs and configure options -------

""" + default_settings_as_text() + """\
------- Profile environment variables -------

If you run this script with option --add-profile-variables, the
script will add two environment variables to your ~/.profile file.

""" + INCLUDE_ENVIRONMENT_VARIABLE + " is path to directory where script copies all .h files." +  """
""" + LIBRARY_ENVIRONMENT_VARIABLE + " is path to directory where script copies all .so and .a files" + """"

With these environment variables you can easily set some other environment variables to point to the correct path.

Note that these changes to .profile file don't take effect until you logout and login again to your computer.

"""



def add_profile_variables():
    print("\n------- Adding profile environment variables -------\n")

    absolute_path_to_include_dir = os.path.abspath(INCLUDE_DIR)
    absolute_path_to_library_dir = os.path.abspath(LIBRARY_DIR)

    lines = [
        "# SDL2 build script environment variables\n",
        "if [ -d \""+ absolute_path_to_include_dir +"\" ] ; then\n",
        "    export " + INCLUDE_ENVIRONMENT_VARIABLE + "=\"" + absolute_path_to_include_dir + "\"\n",
        "fi\n",
        "\n",
        "if [ -d \""+ absolute_path_to_library_dir +"\" ] ; then\n",
        "    export " + LIBRARY_ENVIRONMENT_VARIABLE + "=\"" + absolute_path_to_library_dir + "\"\n",
        "fi\n",
        "\n",
    ]

    path = os.path.expanduser("~/.profile")

    if os.path.exists(path):
        file = open(path)
        line = file.readline()
        while line != "":
            if INCLUDE_ENVIRONMENT_VARIABLE in line:
                print("Profile variables are already been added.")
                file.close()
                return
            line = file.readline()
        file.close()

        file = open(path, 'a')
        file.writelines(lines)
        file.close()

    else:
        print("error: ~/.profile was not found")
        exit(-1)

def parse_configure_arguments(arg):
    if arg.startswith("--"):
        return []

    return list(map(lambda option: "--" + option, filter(lambda option: option.strip() != "", arg.split(" "))))

def add_if_not_on_the_list(list, item):
    found = False

    for list_item in list:
        if list_item == item:
            found = True
    if not found:
        list.append(item)

if __name__ == "__main__":
    exit_if_running_as_root()

    if len(sys.argv) == 1:
        print(HELP_TEXT)
        exit(0)

    # Parse args

    show_configure_options_list = []
    build_libraries_list = []

    configure_arg_parsing_mode = False
    library_to_set_configure_args = {}

    set_profile_variables = False
    no_skip_when_building_libraries = False
    no_configure_options = False
    no_raspberry_pi_support = False

    for arg in sys.argv[1:]:
        if configure_arg_parsing_mode:
            configure_arg_parsing_mode = False
            new_options = parse_configure_arguments(arg)
            if len(new_options) != 0:
                library_to_set_configure_args["configure_argument_list"] = new_options
                continue

        try:
            if SCRIPT_OPTIONS[arg]["action"] == "show_configure":
                for library in SCRIPT_OPTIONS[arg]["libraries"]:
                    add_if_not_on_the_list(show_configure_options_list,library)

            elif SCRIPT_OPTIONS[arg]["action"] == "build":
                for library in SCRIPT_OPTIONS[arg]["libraries"]:
                    add_if_not_on_the_list(build_libraries_list,library)

                if len(SCRIPT_OPTIONS[arg]["libraries"]) == 1:
                    configure_arg_parsing_mode = True
                    library_to_set_configure_args = SCRIPT_OPTIONS[arg]["libraries"][0]
            elif SCRIPT_OPTIONS[arg]["action"] == "show_help":
                print(HELP_TEXT)
                exit(0)
            elif SCRIPT_OPTIONS[arg]["action"] == "modify_profile_file":
                set_profile_variables = True
            elif SCRIPT_OPTIONS[arg]["action"] == "no_skip":
                no_skip_when_building_libraries = True
            elif SCRIPT_OPTIONS[arg]["action"] == "no_configure_options":
                no_configure_options = True
            elif SCRIPT_OPTIONS[arg]["action"] == "no_raspberry_pi_support":
                no_raspberry_pi_support = True

        except KeyError:
            unknown_argument = True
            print("Unknown argument '" + arg +"'")
            print(HELP_TEXT)
            exit(-1)

    change_to_build_directory()

    if no_configure_options:
        SDL2_ALL["configure_argument_list"] = []
        SDL2_MIXER_ALL["configure_argument_list"] = []
        SDL2_TTF_ALL["configure_argument_list"] = []
        SDL2_IMAGE_ALL["configure_argument_list"] = []

    if not no_raspberry_pi_support:
        target_triple = run_program_and_return_output(["gcc", "-dumpmachine"]).decode().strip()
        if not "-raspberry-linux" in target_triple:
            target_triple = target_triple.replace("-linux", "-raspberry-linux", 1)
        SDL2_ALL["configure_argument_list"].append("--host=" + target_triple)

    if len(show_configure_options_list) > 0:
        download_and_extract_all(show_configure_options_list)
        show_configure_options_for_all_libraries(show_configure_options_list)
        if not set_profile_variables:
            exit(0)

    if len(build_libraries_list) > 0:
        download_and_extract_all(build_libraries_list)
        build_all_libraries_and_copy_library_files(build_libraries_list, no_skip_when_building_libraries)
        print("Building libraries and copying files finished without errors.")
        print("Header files (.h) location:          '" + os.path.join(os.getcwd(), INCLUDE_DIR) + "'")
        print("Library files (.so and .a) location: '" + os.path.join(os.getcwd(), LIBRARY_DIR) + "'\n")
        if not set_profile_variables:
            exit(0)

    if set_profile_variables:
        add_profile_variables()