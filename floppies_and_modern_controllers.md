
## Reading M20 floppies with modern controllers

Version: 11 Jan 2023 (WIP)

<p align="center">
  <img src="article_media/floppy.jpg" alt="An original PCOS 2.0 floppy from 1983" width="700px"/>
</p>

Reading under Linux with standard pc controller (48 tracks per inch, sector size 256 bytes, 16 sectors per track, MFM encoding implicit):

    $ setfdprm /dev/fd1 tpi=48 ssize=256 sect=16 dd ds
    $ sdd -noerror try=5 iseek=4096 oseek=4096 if=/dev/fd1 of=floppy.img bs=256 count=1104 

Modern Options:

### Controller

* [Kryoflux](https://kryoflux.com/):

  * Can not write *.img files back to floppy directly (need to convert to raw flux files first with e.g. the [HxC Floppy Emulator](https://hxc2001.com/download/floppy_drive_emulator/)).
  * Mainly made for reading floppies, writing floppies is a "bonus" and not officially supported (e.g. if one needs help in the forums)

* [Greaseweazel](https://github.com/keirf/Greaseweazle/wiki):

  * Can [read and write](https://github.com/keirf/greaseweazle/wiki/Supported-Image-Types) *.img files
  * Can even read and write [mixed](https://github.com/keirf/greaseweazle/issues/143) FM/MFM floppies

#### Greaseweazel setup

Setup/ Create a `diskdefs.cfg` config for M20 floppies. Use with [development](https://github.com/keirf/greaseweazle/issues/261#issuecomment-1369036593) version of greaseweazel tools or with future version > 1.5:

    # Full M20 floppy definition
    disk olivetti.m20
        cyls = 35
        heads = 2
        tracks 0.0:ibm.fm
            secs = 16
            bps = 128
            rate = 125
        end
        tracks 0.1-34:ibm.mfm
            secs = 16
            bps = 256
            rate = 250
        end
    end

    # M20 floppy definition for FM. Only use this with "c=0:h=0"
    disk olivetti.m20.fm
        cyls = 35
        heads = 2
        tracks *:ibm.fm
            secs = 16
            bps = 128
            rate = 125
        end
    end

    # M20 floppy definition for MFM.
    disk olivetti.m20.mfm
        cyls = 35
        heads = 2
        tracks *:ibm.mfm
            secs = 16
            bps = 256
            rate = 250
        end
    end

#### Reading

Reading the entire disk in one go with the mixed `olivetti.m20` format did not work yet, so we will read the FM and MFM parts separately:

* Read FM Track0 (Cylinder 0, Head 0). This will read 2 kiB, since FM density is lower.
* Read the entire Floppy in MFM. This will attemp to re-read Track0 (and fail) but already creates a kiB offset for it on the output side. It also saves us an additional step to separately read Track1 (c=0:h=1).
* Transfer the 2 kiB FM track0 into the empty first 4 kiB of the output image. This effectively leaves another 2 kiB of zeros before track1 starts.

Example commands:

    gw read --tracks="c=0:h=0" --diskdefs diskdefs.cfg --format="olivetti.m20.fm" tmp_t0.img
    gw read --diskdefs diskdefs.cfg --format="olivetti.m20.mfm" floppy.img
    dd conv=notrunc if="tmp_t0.img" of="floppy.img" bs=2048 count=1
    
This basically follows the original approach of skipping the first 4 kiB (one MFM track) on both input and output side and having track1 start at a 4 kiB offset. This is however a convention, one needs to define when storing sector images in a consistent way.

One use case would be to load the images in [MAME](http://www.z80ne.com/m20/index.php?argument=sections/tech/mame_m20.inc), which also follows the convention that track1 starts with a 4 kiB offset in the sector image file. As a sidenote: Mame actually assumes [every one of the 16 sectors](https://github.com/mamedev/mame/blob/master/src/lib/formats/m20_dsk.cpp#L9) in the FM track to be padded with 128 Bytes, instead of padding the entire track with and additional 2 kiB (like we did here). This would make the reading process more complex, since we would need to slice track0 into 16 parts à 128 bytes and pad them individually. We can however skip this as a simplification, since only the [very first sector](https://forums.bannister.org/ubbthreads.php?ubb=showflat&Number=100146#Post100146) in the FM track seems to contain data anayways. One should probably keep this in mind when reading original M20 floppies and verify that this is always the case.

#### Writing

Writing back to floppy we have to do in three parts, again assuming a homogeneous 4 kiB/ track image file. Then we can write track0, track1, and the rest of the disk: 

    gw write --tracks="c=0:h=0" --diskdefs diskdefs.cfg --format="olivetti.m20.fm" floppy.img
    gw write --tracks="c=0:h=1" --diskdefs diskdefs.cfg --format="olivetti.m20.mfm" floppy.img
    gw write --tracks="c=1-34" --diskdefs diskdefs.cfg --format="olivetti.m20.mfm" floppy.img

### Drive

Should be a 360kB 40 track drive. 80 track drives might be able to read the M20 35 track floppies, but not write them well, due to the narrow track size.

* Teac FD-55BR: [vogons](https://vogonswiki.com/index.php/Teac_FD-55BR) or [retrocmp](https://retrocmp.de/fdd/teac/fd55_i.htm)
* Tandon TM100-2A: [retrocmp](https://retrocmp.de/fdd/tandon/tm100-2a.htm)

### Media

* Use 5+1⁄4-inch DD 360 kB floppies.
* Possible to use 720 kB QD?
* Possible to use 1.2M HD? See [this article](https://forum.vcfed.org/index.php?threads/1-2mb-floppy-in-360kb-drive.52905/).

## TODOs

- [ ] Can the original M20 boot a floppy with a replaced track0 from a random image?
- [ ] Can the original M20 boot images which do not work in mame? (cpm8k?)
- [ ] Provide Feedback [here](https://gist.github.com/jandelgado/88962932896127dcabbe251f996e790e), [here](https://github.com/keirf/greaseweazle/issues/143) and [here](https://github.com/keirf/greaseweazle/issues/261)
- [ ] Interesting read: https://www.smbaker.com/raspberry-pi-floppy-controller-board

