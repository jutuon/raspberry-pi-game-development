# SDL2 Library and Raspberry Pi


## General

[SDL2 Homepage](https://www.libsdl.org/)

[SDL2 Wiki](https://wiki.libsdl.org/FrontPage)

## Installation

### Raspberry Pi 2 and 3

1. Enable experimental OpenGL support from `raspi-config`.

2. Download SDL2 packages from package repositories.

### Raspberry Pi 1 and Zero

**Note**, use the following SDL2 rpi video driver only with game controllers. Currently all local keyboard keystrokes will be
sent also to the console or X server, so you can possibly execute some dangerous commands.

The [new driver](https://github.com/anholt/mesa/wiki/VC4) for Raspberry Pi's GPU can't be yet enabled
in `raspi-config` for Raspberry Pi 1 and Zero. Instead, SDL2 has built in support for Broadcom's binary GPU driver.
However that support is not compiled to the SDL2 package in the Raspbian package repository, so you will have
to compile SDL2 with that support enabled. Note that this rpi video driver in SDL2 has keystroke leak problem described above.

[Readme file for SDL2 rpi video driver](https://hg.libsdl.org/SDL/file/default/docs/README-raspberrypi.md)

#### Build script

I made a build script in Python 3 to simplify the building process. It will download
source archives, extract the archives, build libraries, copy required files for compiling and linking
to two directories and optionally add two environment variables pointing to those two directories to your `~/.profile` file.

The script also has a workaround for SDL2 2.0.5 and Raspbian 9 Stretch. The files like "libEGL.so" in `/opt/vc/lib` which
name don't contain "brcm" text got removed in Raspbian 9 Stretch, so script will modify 'SDL_egl.c' source file's library paths
to point correct files.

1. Install dependencies

```
sudo apt-get install libudev-dev libasound2-dev libdbus-1-dev
```

You might want to install other optional dependencies for example SDL2_mixer's ogg file format support.
Easiest way to do that is to get all building dependencies from package repository's source package. For SDL2_mixer that is

```
sudo apt-get build-dep libsdl2-mixer-2.0-0
```

2. Clone this repository

```
git clone https://github.com/jutuon/raspberry-pi-game-development
```

3. Change directory
```
cd raspberry-pi-game-development/sdl2
```

4. Run the script

If you can't run the script, run `chmod u+x build_sdl2.py` to add execute permissions to
to the script or run the script like this: `python3 build_sdl2.py`.

Run `./build_sdl2.py` to print script's available options and help texts to the command line.

To build all SDL2 libraries the script supports and add environment variables to `~/.profile`, run script with these options.

```
./build_script.py --build-all --add-profile-variables
```

5. Logout and login back to your computer, so the modifications to your `~/.profile` will take effect.

6. Export some environment variables for compiler and linker.

You may not have to set `CPATH` environment variable if you are using some other programming language than C/C++ with SDL2.

```
export CPATH=$SDL2_INCLUDE
```
```
export LIBRARY_PATH=$SDL2_LIBRARY
```
```
export LD_LIBRARY_PATH=$SDL2_LIBRARY
```


#### Building Manually

Build process for SDL2 and its add-on libraries goes something like this:

1. Download source tar and extract it.
2. `cd source-folder`
3. `mkdir build && cd build`
4. `../configure && make`
5. .so and .a files are in the build folder and .h files might be in the source and/or build folder.

Note that you have to set `SDL2_CONFIG`, `CPPFLAGS`, `LDFLAGS` and `LD_LIBRARY_PATH` environment variables
before building the add-on libraries like SDL2_mixer.

Note also that you might want to use `make install` to install the libraries.