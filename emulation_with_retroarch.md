
# Emulating the M20 with RetroArch

Version: 11 Jan 2023

This guide highlights the particularities of running the M20 MAME driver on RetroArch with the examples of setting it up on Android and Retropie. For a general overview of running the M20 with MAME itself refer to the [M20 emulation with MAME article](http://www.z80ne.com/m20/index.php?argument=sections/tech/mame_m20.inc).

<p align="center">
  <img src="article_media/retropad.jpg" alt="Mauerschießen running on Android RetroArch" width="700px"/>
</p>

Above is the iconic game "Mauerschießen", a pong clone from the German demo floppy running on Android RetroArch, playable entirely by gamepad. The necessary keys have been mapped to the controller.

Running the M20 on Retroarch can be useful for a number of reasons: Retroach is being built for a vast number of platforms (like Android, the Nintendo Switch, and even Win95) for which there is no pre-compiled Mame option. RetroArch also offers some additional features, like snapshots, effectively introducing a "save game" function. While RetroArch is just the frame, it contains MAME as a "core".

The goal of this article is to get M20 emulation running on RetroArch, and map some keys of simple 1D and 2D games to the RetroArch virtual gamepad "RetroPad", so they can be played without a keyboard. Data provided with this article:

| Description | File | Size | CRC |
|:--|:--|--:|--:|
|Olivetti M20 - games, thumbnails, MAME hash table | m20_games.zip | 7217045 | 5633ad79 |
|Retropad controller mapping configs | [m20_retropad_mapping.zip](article_media/m20_retropad_mapping.zip) | 336860 | 05c142fd |

#### Loading floppy images in a non-keyboard environment

On a PC one can call MAME with a number of custom arguments from a console. In RetroArch, we need to supply a single argument to the emulator, in form of a file that the user can tap on. Therefore floppies/ images can be loaded by MAME in two additional ways, that only require a single argument when calling the emulator:

* Loading a known (softlisted) image by just specifying its name. MAME will load this image automatically from a defined input folder and tell MAME that it is a floppy. Softlisted images must be zipped, and named exactly in the way they are listed.
* Specifying the image location and floppy-type manually in a *.cmd file, which is then passed as an argument itself to MAME instead of the image itself. This also allows one to pass additional options by adding them to the *.cmd file.

#### The M20 softlist in MAME

In order to use the softlist loading method, add entries to the [hash table](https://github.com/mamedev/mame/blob/master/hash/m20.xml)/ softlist. The listed images can be started directly from the app, without having to create a *.cmd file. A few notes about the xml:

* "software  name" is the name of the zipped image
* "rom  name" is the name of the image file inside the zip
* size and checksums can be wrong, mame will throw an error into the log, but should still start the image

#### Structure of CMD files

CMD files need to contain at least the following information:

- Driver: `mame m20`
- Location of the M20 bios: `-rompath <location>`
- Image (type) to be loaded: `-flop1 <image.zip>`

Additional MAME [commandline-arguments](https://docs.mamedev.org/commandline/commandline-all.html):

- M20 Bios version: e.g. `-bios 1`
- Second floppy drive: `-flop2 <image>`
- System config directory: `-cfg_directory <location>`
- Controller- config/ directory: `-ctrlrpath <location> -ctrlr <config-name>`
- Execute after launch: `-autoboot_delay 15 -autoboot_command "<cmd>"`
- Emulation speed: `-speed <factor>`

An example could look like this:

    mame m20 -speed 1.1 -ctrlrpath /storage/emulated/0/RetroArch/roms/m20/cfg/ -ctrlr othello -rompath /storage/emulated/0/RetroArch/roms/m20 -flop1 /storage/emulated/0/RetroArch/roms/m20/othello.zip

#### Mapping M20 keys to the RetroPad

Using the retropad (on-screen) gamepad instead of a keyboard (e.g. on a phone) is a bit more difficult, but possible. In order to make this work one needs to map some of retropad buttons to the M20 keyboard. Since every game has different input, we create a dedicated _controller config_ on a per image basis, by adding the `-ctrlrpath` and `-ctrlr` arguments to the _*.cmd_ launch file. Custom configs will be placed inside a "cfg" directory with the M20 roms, e.g.:

	"-ctrlrpath <RetroArch>/roms/m20/cfg/ -ctrlr <game>"

This will make mame expect a "\<game>.cfg" file inside the given cfg-directory. Let's make a [simple mapping](https://docs.mamedev.org/advanced/ctrlr_config.html#overriding-defaults-by-input-type) for the space key, hereby keeping the keyboard-key intact:

    <input>
		<keyboard tag=":kbd:m20" enabled="1" />
		<port tag=":kbd:m20:LINE6" type="KEYBOARD" mask="1" defvalue="0">
		<newseq type="standard">KEYCODE_SPACE OR JOYCODE_1_BUTTON2</newseq></port>
    </input>

Similar key mappings can be defined for other keys. Taking e.g. the pong clone "Mauerschießen" as an example, we need the keys "0", "2" (down, up), and "space" (start), and "j" (restart), which is the minimum requirement. Examples for some games are provided in `m20_retropad_mapping.zip` and have been created with this [script](https://github.com/eberhab/m20/blob/master/scripts/create_retropad_mapping.py). For a complete overview of M20 key names in MAME scroll to the bottom of this file.

When modifying the keys in-game through the MAME menu, the mapping will be saved in a _system config_ file called `m20.cfg`. If one wants to keep those settings on a per game basis, instead of the ctrlrpath and ctrlr arguments, one can supply the cfg_directory argument, to have the system-config stored in a separate location e.g.:

	"-cfg_directory <RetroArch>/roms/m20/cfg/<game>/"

The syntax of the m20.cfg system config file inside this folder is identical to the controller config and can be edited both in-game or with a text editor.

# RetroArch on Android 

This guide is based on RetroArch v1.14. The "Multi (MESS - Current)" core is based on MAME v0.251 and available from the online core downloader. 

The RetroArch directory on the Android device is assumed to be under: "/storage/emulated/0/RetroArch"
After setup, the basic structure inside the RetroArch folder should look like this[^1]:

    ./roms/m20/m20.zip  (bios)
    ./roms/m20/<game>.zip  (rom)
    ./roms/m20/cfg/<game>/m20.cfg  (sys-cfg)
    ./roms/m20/cfg/<game>.cfg  (ctrlr-cfg)
    ./system/mame/hash/m20.xml  (softlist)
    ./thumbnails/m20/[Named_Boxarts, Named_Snaps, Named_Titles]/<game>.png
    ./playlists/m20.lpl
    ./saves/mame/cfg/m20.cfg  (default-sys-cfg)
    ./download/mamemess_libretro_android.so
    ./logs

### Setup

1) Start by installing [Retroarch](https://www.retroarch.com/?page=platform) 64 bit for Android.
   
2) Download the "Multi (MESS - Current)" via the core downloader either directly or by downloading from [buildbot](https://buildbot.libretro.com/nightly/android/latest/arm64-v8a/mamemess_libretro_android.so.zip) into the RetroArch/download folder.

3) Create a subfolder "roms/m20" and put (zipped) floppy images and M20 bios/ rom inside. Make sure the images have a working/ non-empty track0.

4) Make sure the roms are softlisted in hash/m20.xml or alternatively create a _*.cmd_ launch file pointing at the zip file, and also place into "roms/m20" folder:

       mame m20 -rompath /storage/emulated/0/RetroArch/roms/m20 -flop1 /storage/emulated/0/RetroArch/roms/m20/maus.zip 
   
5) Now it is time to start up the RetroArch app and change a few settings:
   - Activate file logging into "logs" directory, so that we know why things fail/ crash if they do:
      Settings -> Logging -> Log to File & Timestamp Log Files

6) Choose input device. There are two options:

* Connect a keyboard to the Android device e.g. use an Android tablet with a bluetooth keyboard.
* Use the RetroPad (either on-screen, or via a real gamepad):
	* Adding a custom key-config directory to the *.cmd file: 
		`-cfg_directory /storage/emulated/0/RetroArch/roms/m20/cfg/<game>`
	* Edit the file `roms/m20/cfg/<game>/m20.cfg` and add all the mappings for the game
	* One can let Mame create the file on first run, but the folder needs to be created first
	* The mapping between a physical gamepad and RetroPad can be configured via Settings -> Input -> Port 1 Controls

7) Launch the emulation by:
   - Load content -> (select the *.cmd launch file)
   - When prompted, select "Arcade (MAME - Current)" core

### Optional steps

* A few more helpful RetroArch settings:
   - Activate "game focus" mode, to deactivate RetroArch hotkeys and pass keyboard inputs directly to the core:
     - Settings -> Input -> Auto enable Game Focus (disables all hotkeys but Game Focus Toggle) 
     - Settings -> Input -> Hotkeys -> Game Focus (Toggle)
   - Activate slow motion mode (if the game is too fast)
     - Define speed factor under: Settings -> Frame Throttle -> Slow-Motion Rate 
     - Assign to hotkey: Settings -> Input -> Hotkeys -> Slow-Motion (Toggle) - 

* Create a playlist to automatically associate *.zip and *.cmd files in the m20 roms folder with the mame-current core via Playlists -> Import Content -> Manual Scan:
	* Content directory: roms/m20
	* System name: "Content directory" or "Custom -> m20"
	* Default core: "Multi (MESS - Current)"
	* File extensions: "zip cmd"

* Add artwork under the "thumbnails" folder:
	* Create a subfolder with the name "m20" or, if it differs, with the name of the created playlist
	* Inside, place the thumbnails into subfolders: Named_Boxarts, Named_Snaps, and/ or Named_Titles
	* Name thumbnails by game (image file-) name

* Place a modified [hash table](https://github.com/mamedev/mame/blob/master/hash/m20.xml) under "system/mame/hash/m20.xml" to load zipped images directly.

* Use autoboot to perform actions automatically (e.g. start a game on a multi-game floppy). While this is possible, it is quite fiddly and depends on a few things:
	* The floppy needs to autoboot into an Italian PCOS (for more details, see the main [MAME article](http://www.z80ne.com/m20/index.php?argument=sections/tech/mame_m20.inc))
	* For me, the autoboot_command string needed to be in double quotes itself, single quotes did not work. This makes it difficult if the command one wants to pass also contains double quotes. Escaping and triple quotes as suggested in some forums also did not work. Eventually I was using different (unicode) types of double quotes: 
		* U+0022 : quotation mark (as the outer quotes)
		* U+201C : left double quotation mark (as inner double quotes)

### Related work

* Create [Android64 MESS core](https://github.com/libretro/mame/pull/342) and related [info file](https://github.com/libretro/libretro-super/pull/1706)
* Add a more complete [gamelist](https://github.com/mamedev/mame/pull/10832) to MAME

# RetroArch on RetroPie

RetroPie is more versatile than pure RetroArch, so setup is also a bit more complex, with the advantage, that an up to date MAME core is readily available, as well as stand alone MAME.

This guide is based on 32bit RetroPie 4.8, RetroArch v1.12, incl. MAME v0.251 running on a Raspberry Pi 4B (8GB). At the time of writing, there is no pre-built 64bit SD card image available. While RetroPie 64bit can be installed manually on Raspberry Pi OS, it is no guaranteed that things will behave identical to what is described here.  

The RetroPie directory structure should eventually look like this:

    /home/pi/RetroPie/BIOS/mame/m20.zip
    /home/pi/RetroPie/roms/m20/<game>.zip
    /home/pi/RetroPie/roms/m20/cfg/<game>/
    /home/pi/RetroPie/BIOS/mame/hash/m20.xml
    /opt/retropie/configs/m20/emulators.cfg
    /opt/retropie/configs/m20/retroarch.cfg
    /opt/retropie/configs/all/emulationstation/es_systems.cfg
    /etc/emulationstation/themes/carbon/m20/*
    /home/pi/.emulationstation/gamelists/m20/gamelist.xml
    /home/pi/.emulationstation/downloaded_images/m20/<rom-artwork>

This guide will explain roughly which files needed to modify and provide a general idea of how it can be done. For more detail and discussion also refer to the [RetroPie forum](https://retropie.org.uk/forum/topic/33636/running-a-custom-rom-with-lr-mame).

### Setup

1) Boot a 32bit RetroPie 4.8 on a Raspberry Pi 4

2)  Install M20 support on Retropie:  

    * Install  `mame`  and  `lr-mess`  from  `RetroPie-Setup`  (experimental packages).  

3) Configure new emulator types in  `/opt/retropie/configs/m20/emulators.cfg`. Emulators are rule-sets for command line parameter to the emulator core. Use the mame/ lr-mess emulator configs as a reference. Some examples:

	* lr-mess-cmd: Use to launch cmd files
	* lr-mess-m20-manual: Launch non-softlisted roms by passing image and floppy type to mame
	* lr-mess-m20-cfg: Launch non-softlisted roms with a custom keyboard config
	* lr-mess-m20-softlist: Launch softlisted roms directly
	* mame-m20: Run the image with standalone mame (not via RetroaArch)

	The emulators.cfg should look roughly like this:

	   lr-mess-cmd = "/opt/retropie/emulators/retroarch/bin/retroarch -c /opt/retropie/configs/m20/retroarch.cfg -v -L /opt/retropie/libretrocores/lr-mess/mamemess_libretro.so %ROM%"
	   lr-mess-m20-manual = "/opt/retropie/emulators/retroarch/bin/retroarch -c /opt/retropie/configs/m20/retroarch.cfg -v -L /opt/retropie/libretrocores/lr-mess/mamemess_libretro.so 'm20 -cfg_directory /opt/retropie/configs/m20/lr-mess -rompath /home/pi/RetroPie/BIOS/mame;/home/pi/RetroPie/roms/m20 -flop1 %ROM%'"
	   lr-mess-m20-cfg = "/opt/retropie/emulators/retroarch/bin/retroarch -c /opt/retropie/configs/m20/retroarch.cfg -v -L /opt/retropie/libretrocores/lr-mess/mamemess_libretro.so 'm20 -cfg_directory /home/pi/RetroPie/roms/m20/cfg/%BASENAME%/ -rompath /home/pi/RetroPie/BIOS/mame;/home/pi/RetroPie/roms/m20 -flop1 %ROM%'"
	   lr-mess-m20-softlist = "/opt/retropie/emulators/retroarch/bin/retroarch --config /opt/retropie/configs/m20/retroarch.cfg -v -L /opt/retropie/libretrocores/lr-mess/mamemess_libretro.so 'mame m20 -cfg_directory /opt/retropie/configs/m20/lr-mess -rompath /home/pi/RetroPie/BIOS/mame;/home/pi/RetroPie/roms/m20/ '%BASENAME%''"
	   mame-m20 = "/opt/retropie/emulators/mame/mame -rompath /home/pi/RetroPie/BIOS/mame\;/home/pi/RetroPie/roms/m20 -v -c -ui_active -statename m20/%BASENAME% m20  -flop1 %ROM%"
	
	Note that the softlist launcher only needs the basename of the image, without location and file suffix. The referenced `retroarch.cfg` can be adapted from `/opt/retropie/configs/mess`.

4) Add the M20 machine type to Emulationstation via  `es_systems.cfg`:

      * Take the `mame` system as an example, duplicate it, make sure to replace all instances of mame into m20, except for the artwork.
      * Adapt the dedicated roms folder and supported rom suffixes (zip, img, imd, td0, cmd)
      * Additionally, one can place M20 related artwork into `/etc/emulationstation/themes/<theme>/m20/` by again taking the `mame` machine as a reference. Then one has to also specify m20 as the theme in es_systems.

5) Add floppy images/ roms/ bios:
    * Place (zipped) m20 floppy images into  `roms/m20/`.  Make sure the images have a working/ non-empty track0. 
    * Place bios file _m20.zip_ into  `BIOS/mame/`  

6) Choose input device. There are two options:

	* Connect a keyboard to the Pi and set it up under Emulationstation.
	* Use the RetroPad/ gamepad. Under RetroPie one has multiple options:
		* Use the pre-defined `lr-mess-m20-cfg` emulator, or
		* Adding a custom key-config directory to the *.cmd file and launch via `lr-mess-cmd`: 
		  `-cfg_directory /home/pi/RetroPie/roms/m20/cfg/<game>`
		* In both cases, edit the file `roms/m20/cfg/<game>/m20.cfg` and add all the necessary mappings for the game
		* One can let RetroArch/ Mame create the config on first run, but the folders needs to be created first manually 

  8) When launching emulationstation a new M20 machine type should show up. When launching, select the right emulator for the task. In case of error consult `/dev/shm/runcommand.log`

###  Optional steps

* Create _*.cmd_ launch files for command line arguments not covered by the defined emulators. Also place them into "roms/m20" folder, e.g.:

       mame m20 -rompath /home/pi/RetroPie/BIOS/mame;/home/pi/RetroPie/roms/m20/ -flop1 /storage/emulated/0/RetroArch/roms/m20/spiele+uhr.zip   

*   Place a modified [hash table](https://github.com/mamedev/mame/blob/master/hash/m20.xml) under "~/RetroPie/BIOS/mame/hash/m20.xml" to load zipped images via the pre-defined softlist emulator.

* Add game/ image specific artwork to `/home/pi/.emulationstation/downloaded_images/m20/` and link the images in the gameslist file: `/home/pi/.emulationstation/gamelists/m20/gamelist.xml`. This could probably be automated through a scraper?

* EmulationStation theme (optional)  
    * [Cygnus Blue Flames](https://github.com/DTEAM-1/cygnus-blue-flames)  theme has art support for the M20.
    * Place your own machine art files into `/etc/emulationstation/themes/carbon/m20/`. Take the ./carbon/mame machine as a reference.

# The M20 keyboard in MAME and RetroArch

### Retropad Numbering

Issues: L2 and R2 naming is not very intuitive. Maybe an oddity with the mapping between RetroArch an Mame or with v0.226? Mapping works nonetheless.

    Prefix: JOYCODE_1_*
	BUTTON1: A      |     RZAXIS_NEG_SWITCH: L2          |    HAT1UP           : UP
	BUTTON2: B      |     ZAXIS_NEG_SWITCH : R2          |    HAT1LEFT         : LEFT 
	BUTTON3: X      |     SELECT           : Select      |    HAT1RIGHT        : RIGHT 
	BUTTON4: Y      |     START            : Start       |    HAT1DOWN         : DOWN
	BUTTON5: L1     |     BUTTON9          : L3          |    YAXIS_UP_SWITCH  : Analog UP switch
	BUTTON6: R1     |     BUTTON10         : R3          |    XAXIS_LEFT_SWITCH: Analog LEFT switch

### Mame M20 key mapping

Issues: KEYCODE_STOP buttons not found/ gets deleted from cfg. Maybe a bug in v0.226 that STOP cannot be used?
The period/ stop key also does not work when attaching a physical keyboard.

	Key IT M20 - KEYCODE_*   - Port           - Mask   - Comment
	RESET      - ESC         - :kbd:m20:LINE0 - 1
	<  >       - LALT        - :kbd:m20:LINE0 - 2
	a  A       - A           - :kbd:m20:LINE0 - 4
	b  B       - B           - :kbd:m20:LINE0 - 8
	c  C       - C           - :kbd:m20:LINE0 - 16
	d  D       - D           - :kbd:m20:LINE0 - 32
	e  E       - E           - :kbd:m20:LINE0 - 64
	f  F       - F           - :kbd:m20:LINE0 - 128
	g  G       - G           - :kbd:m20:LINE1 - 1
	h  H       - H           - :kbd:m20:LINE1 - 2
	i  I       - I           - :kbd:m20:LINE1 - 4
	j  J       - J           - :kbd:m20:LINE1 - 8
	k  K       - K           - :kbd:m20:LINE1 - 16
	l  L       - L           - :kbd:m20:LINE1 - 32
	,  ?       - M           - :kbd:m20:LINE1 - 64
	n  N       - N           - :kbd:m20:LINE1 - 128
	o  O       - O           - :kbd:m20:LINE2 - 1
	p  P       - P           - :kbd:m20:LINE2 - 2
	q  Q       - Q           - :kbd:m20:LINE2 - 4
	r  R       - R           - :kbd:m20:LINE2 - 8
	s  S       - S           - :kbd:m20:LINE2 - 16
	t  T       - T           - :kbd:m20:LINE2 - 32
	u  U       - U           - :kbd:m20:LINE2 - 64
	v  V       - V           - :kbd:m20:LINE2 - 128
	z  Z       - W           - :kbd:m20:LINE3 - 1
	x  X       - X           - :kbd:m20:LINE3 - 2
	y  Y       - Y           - :kbd:m20:LINE3 - 4
	w  W       - Z           - :kbd:m20:LINE3 - 8
	à 0        - 0           - :kbd:m20:LINE3 - 16
	£ 1        - 1           - :kbd:m20:LINE3 - 32
	é 2        - 2           - :kbd:m20:LINE3 - 64
	"  3       - 3           - :kbd:m20:LINE3 - 128
	'  4       - 4           - :kbd:m20:LINE4 - 1
	(  5       - 5           - :kbd:m20:LINE4 - 2
	_  6       - 6           - :kbd:m20:LINE4 - 4
	è 7        - 7           - :kbd:m20:LINE4 - 8
	^  8       - 8           - :kbd:m20:LINE4 - 16
	ç 9        - 9           - :kbd:m20:LINE4 - 32
	)  °       - MINUS       - :kbd:m20:LINE4 - 64
	-  +       - EQUALS      - :kbd:m20:LINE4 - 128
	ì =        - OPENBRACE   - :kbd:m20:LINE5 - 1
	$  &       - CLOSEBRACE  - :kbd:m20:LINE5 - 2
	m  M       - COLON       - :kbd:m20:LINE5 - 4
	ù %        - QUOTE       - :kbd:m20:LINE5 - 8
	*  §       - TILDE       - :kbd:m20:LINE5 - 16
	;  .       - COMMA       - :kbd:m20:LINE5 - 32
	:  /       - STOP        - :kbd:m20:LINE5 - 64
	ò !        - SLASH       - :kbd:m20:LINE5 - 128
	Space      - SPACE       - :kbd:m20:LINE6 - 1
	Enter      - ENTER       - :kbd:m20:LINE6 - 2
	S1         - BACKSLASH   - :kbd:m20:LINE6 - 4
	S2         - BACKSPACE   - :kbd:m20:LINE6 - 8
	Keypad .   - DEL_PAD     - :kbd:m20:LINE6 - 16
	Keypad 0   - 0_PAD       - :kbd:m20:LINE6 - 32 
	Keypad 00  - ENTER_PAD   - :kbd:m20:LINE6 - 64
	Keypad 1   - 1_PAD       - :kbd:m20:LINE6 - 128
	Keypad 2   - 2_PAD       - :kbd:m20:LINE7 - 1      - (DOWN)
	Keypad 3   - 3_PAD       - :kbd:m20:LINE7 - 2
	Keypad 4   - 4_PAD       - :kbd:m20:LINE7 - 4      - (LEFT)
	Keypad 5   - 5_PAD       - :kbd:m20:LINE7 - 8
	Keypad 6   - 6_PAD       - :kbd:m20:LINE7 - 16     - (RIGHT)
	Keypad 7   - 7_PAD       - :kbd:m20:LINE7 - 32
	Keypad 8   - 8_PAD       - :kbd:m20:LINE7 - 64     - (UP)
	Keypad 9   - 9_PAD       - :kbd:m20:LINE7 - 128
	Keypad +   - PLUS_PAD    - :kbd:m20:LINE8 - 1
	Keypad -   - MINUS_PAD   - :kbd:m20:LINE8 - 2
	Keypad *   - ASTERISK    - :kbd:m20:LINE8 - 4
	Keypad /   - SLASH_PAD   - :kbd:m20:LINE8 - 8
	COMMAND    - TAB         - :kbd:m20:MODIFIERS - 1
	CTRL       - LCONTROL    - :kbd:m20:MODIFIERS - 2
	R SHIFT    - RSHIFT      - :kbd:m20:MODIFIERS - 4
	L SHIFT    - LSHIFT      - :kbd:m20:MODIFIERS - 8 

## Issues - TODOs
 
- [ ] Finish [Pacman](https://github.com/eberhab/m20/blob/master/scripts/pacman.bas) BAS game
- [ ] Add some more games from m20graph?
- [ ] [Compile](https://github.com/eberhab/m20/blob/master/scripts/Dockerfile.libnx) Mame-Mess core for Switch
- [X] [Compile](https://github.com/eberhab/m20/blob/master/scripts/Dockerfile.android) Mame-Mess core for Android

[^1]: https://forums.libretro.com/t/guide-play-non-arcade-systems-with-mame-or-mess/17728

