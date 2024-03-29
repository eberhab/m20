

## Emulating the M20 with MAME

--> Working copy of [M20-Mame on z80ne/m20](http://www.z80ne.com/m20/index.php?argument=sections/emulation/mame_m20.inc) <--

Since a while, the Multiple Arcade Machine Emulator [MAME](https://www.mamedev.org/) has a [driver](https://github.com/mamedev/mame/blob/master/src/mame/olivetti/m20.cpp) for the Olivetti L1 M20, enabling MAME to run M20 floppy images, boot PCOS and execute programs, almost like on the original machine [^1]. This article is based on MAME v0.252 on Linux Mint 21 (Feb 2023).

<p align="center">
  <img src="article_media/clock.png" alt="M20 clock from the German demo floppy" width="700px"/>
</p>

Data provided with this article:

| Description | File | Size | CRC |
|:--|:--|--:|--:|
|Olivetti M20 - MAME Floppy-set | [m20_roms.zip](sections/emulation/m20_roms.zip) | 5471765 | 9e3520df |
|Olivetti M20 - Source code of all BAS games | [m20_code.zip](sections/emulation/m20_code.zip) | 216192 | d19ddad2 |

### Running M20 floppy images

After installing MAME, one needs to separately download the M20's ROM contents, e.g. [_m20.zip_](https://wowroms.com/en/roms/mame/olivetti-l1-m20/89051.html). For legal reasons, most ROMs are [not included](https://wiki.mamedev.org/index.php/FAQ:ROMs) in MAME.

Secondly, one needs a floppy to boot from. Floppy disk images of different types can be loaded. Those can be: dd/ sdd/ rdm20 *.img (M20 floppy-sector-dumps), Teledisk *.td0, or ImageDisk *.imd files, as found in the [disk images section](http://www.z80ne.com/m20/index.php?argument=sections/download/wrm20/wrm20.inc). Single images will only work if they have bootable content (e.g. Olivetti's M20 operating system PCOS). A good entry point is _pcos102.img_. Images can also be loaded in zipped format. Multiple images belonging to a package can be in one zip file an are specified by number, e.g. "pascal.zip:1".

To get started right away, download ROM data and floppy images into a local directory and from within, run:

    $ mame m20 -rompath . -flop1 <image1> [-flop2 <image2>] [-bios m20-20d] [-ramsize 512k] [-window] [-nomouse]

This puts the floppy image into the virtual M20s right floppy drive (drive 0). Non-PCOS images can additionally be added to the left floppy drive (drive 1) via the "-flop2" argument.

Depending on the ROM file, the following M20 bios versions are supported:
* 1.0  (`-bios m20`) (default)
* 2.0d (`-bios m20-20d`)
* 2.0f (`-bios m20-20f`)

Note that some images might need more RAM to work and thus need the additional `ramsize` argument, while others (e.g. PCOS1) prefer the default setting of 160 k. M20 specific command line arguments can be explored [here](https://arcade.vastheman.com/minimaws/machine/m20), while a complete list of general MAME related arguments can be found [here](https://docs.mamedev.org/commandline/commandline-all.html).

Not all images are running with MAME right away. Some are missing another kind of boot information, which was stored in track0 of the original floppy, but was lost during the [imaging process](http://www.z80ne.com/m20/index.php?argument=sections/transfer/imagereadwrite/imagereadwrite.inc). This is actually the case with most _rdm20/ *.img_ disk images in the disc images section. Unless fixed, these floppies will usually not boot (or boot only partially in MAME), nor work in the second drive.

### The floppy track0 problem

To find out if an image is affected, use e.g. _hexdump_ to see if track0 has been skipped during imaging. Skipping has usually been done on the reading and writing side, so the first bytes of the file would have been filled with zeros. A working image would display bytes different from zero:

    $ hexdump spiele+uhr.img |head -n 1 
    0000000 0000 0000 0000 0000 0000 0000 0000 0000
    $ hexdump pcos102.img |head -n 1
    0000000 0401 2300 1002 0001 0a00 c400 8600 001e

When only dealing with image files in MAME, there is an easy solution. The missing part of track0 does not seem to contain any user data, but information which is written only once while formatting the floppy. It is possible to transfer this track/ information from one image to another. This makes the affected image directly usable with MAME. The file [_pcos102.img_](http://www.z80ne.com/m20/sections/download/wrm20/pcos102.img.bz2) for example has track0 data which can be used. Transferring it to another image using dd:

    $ dd conv=notrunc if=pcos102.img of=spiele+uhr.img bs=4096 count=1

We have successfully fixed _spiele+uhr.img_, which will now boot into PCOS and launch a menu of 19 games and demos!

### Make floppy images writable

MAME supports reading multiple floppy image formats: mfi (MAME floppy image), img (M20 floppy sector dumps, we will also call this format "M20"), imd (Image Disk), td0 (Teledisk). Only some of these images are writable:

| mfi | m20 | imd | td0 |
|:---:|:------------:|:---:|:---:|
| yes | [since v0.212](https://github.com/mamedev/mame/pull/5445) | [no](https://github.com/mamedev/mame/blob/mame0251/src/lib/formats/imd_dsk.cpp#L644) | [no](https://github.com/mamedev/mame/blob/mame0251/src/lib/formats/td0_dsk.cpp#L1028) |

MAME supplies a [tool](https://docs.mamedev.org/tools/floptool.html) for converting between these different formats, with the same limitations for write support. The following will convert an ImageDisk floppy image into a writable M20 sector image:

    $ floptool flopconvert imd m20 floppy1.imd floppy1.img
 
Alternatively, for a bit of PCOS practice, load the image to be converted and an existing image in the target format into the emulator. The method is limited to that the image to be converted needs to be a bootable PCOS image containing the _vformat_ and _vcopy_ tools (see [M20 PCOS and BASIC command reference](http://www.z80ne.com/m20/index.php?argument=sections/manuals/manuals.inc)[^2]). This method will also take care of fixing a missing track0 in the target image. Boot PCOS format, and copy the source image over to the target image:

On linux:

    $ mame m20 -rompath . -flop1 pcos30e.imd -flop2 copy_of_pcos102.img

On PCOS, format flop2 (1:) and copy flop1 (0:) over flop2:

    # system
    > vf 1:
    > vc 0: 1:

Instead of loading an existing image into flop2, it is also possible to create a completely new image from the MAME in-game menu. However at the time of this writing, it seems to only still be possible to create new _*.mfi_ images.

### Reading and writing BASIC files from images

Files contained in a regular M20-img file can be accessed with [m20floppy](http://www.z80ne.com/m20/index.php?argument=sections/transfer/imagehandle/imagehandle.inc).  Note that BASIC files are usually saved in a compressed/ tokenized binary format. An [interesting](https://github.com/gfis/basdetok) project to learn about the M20-Basic and convert the tokenized version to ASCII is the [M20 Basic Detokenizer](https://github.com/gfis/basdetok/blob/master/src/main/java/org/teherba/basdetok/M20Detokenizer.java)[^3]. Alternatively, one can save files as ASCII via MAME under PCOS BASIC with the "A" option, then extract with m20floppy:

    # SAVE "0:<filename>",A
    $ m20 <image.img> get <filename>

When writing BASIC code in ASCII back to the img, one has to make sure, that the newline delimiter is a single "CR". Linux' "LF" and Windows' "CRLF" would need to be replaced with e.g. _sed_ or _tr_.

### The anatomy of M20 floppies and MAME images

The original M20 stored data on the physical floppy in two different encodings. Part of the first track has data encoded in FM, while the rest of the floppy was encoded in MFM. PC floppy controllers usually do not understand the FM encoding, so reading of this section was often skipped during imaging.

Even if the whole floppy track can be read, one has to deal with an additional difficulty: FM tracks are 16 sectors * 128 Bytes (= 2048 Bytes) in size, while MFM encoded track size is 16 sectors * 256 Bytes (= 4096 Bytes). To simplify handling of the image file, MAME on the other hand assumes _all_ sectors to be of [equal 256 Byte size](https://github.com/mamedev/mame/blob/mame0251/src/lib/formats/m20_dsk.cpp#L11). 

When reading the original floppy in MFM mode and skipping the first track, this automatically results in the correct 4 KiB offset in the image file. When imaging a real floppy including the FM track, however, one has to pad every single FM sector with another 128 Bytes. Table adapted from[^4]:

|Cylinder.Side| Physical floppy format | Floppy image
|:---|---:|---:|
|00.0 |FM, 16 Sectors * 128 Bytes| 16 * 256 Bytes|
|00.1 |MFM, 16 Sectors * 256 Bytes | 16 * 256 Bytes|
|01-34.0-1| MFM, 16 Sectors * 256 Bytes | 16 * 256 Bytes|
|(Sum)|278 kiB|280 kiB|

Instead of extracting from floppy, another option to create a new first track, with PCOS on MAME itself. Booting with a PCOS image in drive0, then create and format a new floppy in drive1:

* Create a new floppy in drive1 via MAME menu:
   File Manager -> flop2 -> [create] -> new.mfi -> Create -> MAME floppy image
* Format the new floppy under PCOS with the command: > vf 1:
* Exit MAME and convert the image from _mfi_ to _m20_ _img_ format using _floptool_
* Investigate the _img_ file using _dd_ and _hexdump_

The resulting image in this example was produced using pcos41a and the first bytes differ slightly from the ones previously obtained from the pcos102 image:

      $ floptool flopconvert mfi m20 new.mfi new.img
      $ dd if=new.img bs=128 skip=0 count=1 |hexdump -v -C |head -n 3
      00000000  04 01 00 23 02 10 01 00  00 10 00 38 00 88 1e 00  |...#.......8....|
      00000010  ff ff 00 00 00 00 00 00  00 01 00 22 00 00 00 22  |..........."..."|
      00000020  ff ff ff ff ff ff ff ff  00 00 00 10 50 43 4f 53  |............PCOS|

Track0 does not contain any user data (see Page 10.2 of the Italian PCOS 1.0 manual) but its content seems to depend on the PCOS version it was created with. For the purpose of using images in MAME, the track does however seem to be completely interchangeable between images. Digging further into the created image, one can notice:

* Mame uses [0xff](https://github.com/mamedev/mame/blob/mame0251/src/tools/image_handler.cpp#L311) instead of 0x00 to pad the 128 byte FM sectors. This also happens during conversion using floptool. One has to keep this in mind when attempting to write images back to floppy, or when comparing checksums! You can observe the padding type by increasing the skip parameter in the _dd_-command above (skip uneven sectors).
* Only the first 128 bytes of the image (FM sector 1 of 16) does seem to contain any non-zero information. All other sectors are empty (skip even sectors with _dd_)
* So basically in chunks of 128 Byte, the track would have one section of data (D) then alternating zeros (0) and byte padding (0 or 1).

Two examples showing different padding types, broken down into 16 pairs of 128 bytes, representing the 4 kiB track0 in a MAME compatible sector image:

    D0 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  - pcos20f.img
    D1 01 01 01 01 01 01 01 01 01 01 01 01 01 01 01  - pcos20h.img (Converted by MAME from *.imd)

Bios 1 seems to be more forgiving concerning booting different FM tracks than Bios versions 2. When writing the images back to floppy to be used in a real machine with fixed Bios, one has to be more careful. Ideally the original FM track should be used, if it is not available one should try to use one from a matching PCOS version. (E.g. the german games/ demo disk does not boot on the original machine with the restored FM track from pcos102, but it does so with an FM track from another pcos20h from e.g. one of the oliword images).

### Compiling MAME from source and running older versions

The latest version of MAME is the github [master branch](https://github.com/mamedev/mame). On Linux just type "make" in the checked out tree. To compile floptool etc. as well, add the "tools" argument. Compiling only the M20 driver is significantly faster and can be done by adding the "subtarget" and "sources" arguments:

    $ git clone https://github.com/mamedev/mame.git && cd mame
    $ make -j8 TOOLS=1 SUBTARGET=m20 SOURCES=olivetti/m20.cpp

In order to compile a specific MAME (e.g. v0.212) version we might need to use a different python/ compiler version, e.g.:

    $ git clone -b mame0212 --depth 1 https://github.com/mamedev/mame.git mame0212 && cd mame0212
    $ sed -i 's/\$1\$(_args)/\$1 \$(_args)/g' 3rdparty/genie/src/host/scripts.c # Only for v<.220
    $ PYTHON_EXECUTABLE=python3.8 OVERRIDE_CC=gcc-9 OVERRIDE_CXX=g++-9 NOWERROR=1 \
      make -j8 SUBTARGET=m20 SOURCES=src/mame/drivers/m20.cpp 

Some versions < .220 might need this [bug](https://github.com/mamedev/mame/issues/6248) fixed. More compile options can be found [here](https://docs.mamedev.org/initialsetup/compilingmame.html). In case it all does not work, another method to run previous MAME versions is to use [pre-built binaries](https://www.mamedev.org/oldrel.html). They only exist for Windows, but they do run well with `wine` on Linux.

### Run MSDOS and CP/M on the M20

On a real M20, with the 8086 addon board, you can boot an Olivetti-[MS-Dos 2.0](https://en.wikipedia.org/wiki/MS-DOS#MS-DOS_2.x). This also works with MAME, by selecting bios >=1 and the _msdos.img_ floppy image from the disk images section.

    $ mame m20 -bios <1, 2> -rp . -flop1 msdos.img [-flop2 adm5.imd]

When asked if you want to boot the alternative CPU (8086), press "y" ("z") to boot into Dos. The keyboard layout can then be changed with the _setlang_ command, e.g.: `A> setlang german`
Keep in mind, that _msdos.img_ as well as the _adm5*.img_ are MSDOS images of MAME image type "pc". So e.g. _adm5.imd_ can be converted to a writable sector image using:

    $ floptool flopconvert imd pc adm5.imd adm5.img
    
In order to boot [CP/M](https://en.wikipedia.org/wiki/CP/M) on the M20, I had to adjust the ramsize, otherwise CP/M boots into a black screen:

    $ mame m20 -rp . -ramsize 512k -flop1 cpm8k.img

### Connecting to the M20 serial interface

Run mame with the follwing extra arguments:

    $ mame m20 -rs232 null_modem -bitb socket.127.0.0.1:4321

In PCOS (also see [FAQ](http://www.z80ne.com/m20/index.php?argument=sections/faq/faq.inc), [forum](https://forums.bannister.org/ubbthreads.php?ubb=showflat&Number=101847#Post101847)):

    0> sc com:,9600,,1,8,,on,4096
    0> rs232
    0> +Scom:, +Dcom:

Then connect to the socket with e.g. telnet

    $ telnet 127.0.0.1 4321

We can now type into PCOS from telnet, but PCOS output is not shown in the telnet terminal. I am not sure why. 

### Keyboard and layouts in PCOS and MAME

The keyboard layout depends on the language of the loaded PCOS. The language on PCOS >= 2.0 can be changed with the _sl_-command (see [FAQ](http://www.z80ne.com/m20/index.php?argument=sections/faq/faq.inc)). I could not figure out how to change the language under PCOS1. M20 special keys are usually:

* reset: esc
* hard reset: strg + esc
* yellow/ command: tab 
* blue/ ctrl: left_ctrl
* S1: (German keyboard: #, US keyboard: backslash)
* S2: backspace

Re-defining input keys can be done through the MAME in game menu. The menu can be accessed by first enabling hotkeys, by pressing the "ui_toggle" key and then "tab" to open the menu. The "ui_toggle" is usually set to "ScrollLock" or to "ForwardDelete" on keyboards which lack the former. If you cannot figure out how to toggle hotkeys, you can launch MAME with "-ui_active" and re-define the key: [tab] -> Configure Options -> General Inputs -> User Interface -> UI Toggle. It might makes sense to specify a consistent config directory to save the key mappings, as MAME seems to otherwise use the local working directory:

    $ mame m20 [-ui_active] [-cfg_directory ~/.mame/cfg] [-window]

While you are in the in-game menu, look into other useful options, like recording screenshots (F12) and recording video (LSHIFT + F12).

This little BASIC program can be used to compare different key combinations with the key code tables in the command reference manual:

    0 REM return decimal and hexadecimal values of pressed keys
    10 CLEAR
    20 G$=INKEY$: IF G$="" THEN GOTO 20
    30 PRINT ASC(G$) HEX$(ASC(G$))
    40 GOTO 20

MAME offers an additionally feature to automatically type specified text into the emulated machine with a specified delay after boot. This is useful to e.g. automatically execute programs after start. One has to keep in mind, that _autoboot_ always uses the original "natural" keyboard that the M20 MAME driver was built on, which is the Italian layout. So one has to use an italian pcos (e.g. pcos102.img) or change a pcos >=2.0 to Italian with _slang_ (> sl 0) and save the change to the floppy with _psave_ (> ps). Then the autoboot string will be interpreted correctly. 

The following will boot pcos, switch to BASIC mode and draw a circle:

    $ mame m20 -flop1 pcos102.img -autoboot_delay 15 -autoboot_command 'ba\ncircle(155,123),109\n' -rp . -nomouse -seconds_to_run 60 -skip_gameinfo -window -resolution0 800x600

To work with any given system language one would need access to the emulated keyboard. This is not currently possible via _autoboot_ and seems to be a current limitation of MAME.

### Notes, known issues, open questions

* Open questions:
    * How to change the language/ keyboard under pcos1? 
    * Input from telnet to the M20 works, terminal output from the M20 to telnet did not work. Wrong options?

* Issues/ questions at the time of writing (possibly MAME related):
    * Creating an new M20 floppy through the MAME menu causes MAME to crash
    * Is printer support possible?
    * What is missing for the "Command+S" boottime easteregg?

* Issues at the time of writing (possibly data related):
    * pcos11d.img/ pcos13.img: "Error 53 in files [font.all, kb.all]". The files can be replaced from e.g. pcos-1.3.img. An old (2012) e-mail conversation mentions these disks to be bootable on the original M20, this would need to be checked and hence could still be a MAME issue.
    * adm51.imd: It seems that this DOS image has been imaged by accidentally skipping track0. Broken.
    * startrek_de.img: Based on Italian pcos102, German characters not displayed correctly. Moving the game to a German pcos20 disk solves this, but results in graphics errors and misalignment between text and graphics. Possibly the emulated machine needs a German [keyboard](https://github.com/mamedev/mame/blob/master/src/mame/olivetti/m20_kbd.cpp)?

- [ ] Find out how to switch keyboard language in PCOS1 (multiplan_de contains an init.bas for this, but the file is not readable).
- [ ] Images on z80ne: add pcos20h.img, oliword_de.img.bz2 is actually English not German
- [ ] Create "official" m20 images (en/it) for "Two Days to Race", possible?
- [ ] Remove tech/mfi_images/pcos20_german.zip and games_german.zip MFIs from previous article version

### TODOs

[^1]: https://forums.bannister.org/ubbthreads.php?ubb=showflat&Number=78739
[^2]: http://www.z80ne.com/m20/sections/manuals/m20qreff.pdf
[^3]: https://github.com/gfis/basdetok
[^4]: https://jandelgado.github.io/blog/posts/olivetti-m20-disk-preservation/


