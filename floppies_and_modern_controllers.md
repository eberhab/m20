
## Reading M20 floppies with modern controllers

Version: 22 Jan 2023 (WIP). Text based on Greaseweazel 1.5.dev2, a Teac FD-55BR drive and Mame v.251, all running on Ubuntu 22.10.

<p align="center">
  <img src="article_media/floppy.jpg" alt="An original PCOS 2.0 floppy from 1983" width="700px"/>
</p>

When reading M20 floppies under Linux with a standard pc controller (48 tracks per inch, sector size 256 bytes, 16 sectors per track, MFM) one likely has to skip the first 4 kiB/ track0, as many PC controllers cannot read the FM track:

    $ setfdprm /dev/fd1 tpi=48 ssize=256 sect=16 dd ds
    $ sdd -noerror try=5 iseek=4096 oseek=4096 if=/dev/fd1 of=floppy.img bs=256 count=1104 

More information about setfdprm/ fdutils and the `sdd` tool can be found [here](http://www.z80ne.com/m20/index.php?argument=sections/transfer/imagereadwrite/imagereadwrite.inc). The main reason to use `sdd` over `dd` was the additional seek parameters. Nowadays, one could try to use standard `dd` directly, which seems to support iseek/ oseek by now (tbc).

Other options, using modern USB-floppy-controllers, are also able to read the FM track:

#### Controller options

* [Kryoflux](https://kryoflux.com/):

  * Can not write *.img files back to floppy directly (need to convert to raw flux files first with e.g. the [HxC Floppy Emulator](https://hxc2001.com/download/floppy_drive_emulator/)).
  * Mainly made for reading floppies, writing floppies is possible, but considered a "bonus" and is not officially supported (e.g. if one needs help in the support forums)
  * Reading M20 floppies works and is described e.g. [here](https://jandelgado.github.io/blog/posts/olivetti-m20-disk-preservation/).

* [Greaseweazel v4](https://github.com/keirf/Greaseweazle/wiki):

  * Can [read and write](https://github.com/keirf/greaseweazle/wiki/Supported-Image-Types) *.img files
  * Can even read and write [mixed](https://github.com/keirf/greaseweazle/issues/143) FM/MFM floppies

### Greaseweazel setup

Get all necessarzy parts and set up the Greaseweazel v4 according to the [documentation](https://github.com/keirf/greaseweazle/wiki/V4-Setup). Then create a `diskdefs.cfg` config for M20 floppies - available with the [development](https://github.com/keirf/greaseweazle/issues/261#issuecomment-1369036593) version of greaseweazel tools or with future version > 1.5:

    # Greaseweazel v1.5.dev2 diskdefs.cfg for Olivetti M20 360 kB DD floppies (WIP)
    
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

    # M20 floppy definition for FM. Only use this with "c=0:h=0".
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
* Read the entire Floppy in MFM. This will attemp to re-read Track0 (and fail) but already creates a 4 kiB offset for it on the output side. It also saves us an additional step to separately read Track1 (c=0:h=1).
* Transfer the 2 kiB FM track0 into the empty first 4 kiB of the output image. This effectively leaves another 2 kiB of zeros before track1 starts, which is what we want.

Example commands:

    gw read --tracks="c=0:h=0" --diskdefs diskdefs.cfg --format="olivetti.m20.fm" tmp_t0.img
    gw read --diskdefs diskdefs.cfg --format="olivetti.m20.mfm" floppy.img
    dd conv=notrunc if="tmp_t0.img" of="floppy.img" bs=2048 count=1
    
This basically follows the original approach of skipping the first 4 kiB (one MFM track) on both input and output side and having track1 start at a 4 kiB offset (instead of 2 kiB). This is however a convention, one needs to define when storing sector images in a consistent way.

One use-case would be to load the images in [MAME](http://www.z80ne.com/m20/index.php?argument=sections/tech/mame_m20.inc), which also follows the convention that track1 starts with a 4 kiB offset in the sector image file. As a sidenote: Mame actually assumes [every one of the 16 sectors](https://github.com/mamedev/mame/blob/master/src/lib/formats/m20_dsk.cpp#L9) in the FM track to be padded with 128 Bytes, instead of padding the entire 2 kiB track with and additional 2 kiB (like we did here). Reproducing this during imaging would make the reading process more complex, since we would need to slice track0 into 16 parts à 128 bytes and pad them individually. We can however stick to the simplification, since only the [very first sector](https://forums.bannister.org/ubbthreads.php?ubb=showflat&Number=100146#Post100146) in the FM track seems to contain data anayways. This is indeed the case for all known images, but one should probably keep this in mind when imaging floppies which haven't been looked at yet.

When trying to create authentic copies which can be validated by checksum (crc/ sha) one also has to keep in mind the additional data used for padding the sectors first track. While we use 0s for the padding, MAME seems to use 1s to pad the offset to the second track. Hence an image converted by MAME would result in a different checksum, allthough the user data is fully identical.

#### Writing

Writing back to floppy we have to do in three parts, again assuming a homogeneous 4 kiB/ track image file. Then we can write track0, track1, and the rest of the disk: 

    gw write --tracks="c=0:h=0" --diskdefs diskdefs.cfg --format="olivetti.m20.fm" floppy.img
    gw write --tracks="c=0:h=1" --diskdefs diskdefs.cfg --format="olivetti.m20.mfm" floppy.img
    gw write --tracks="c=1-34" --diskdefs diskdefs.cfg --format="olivetti.m20.mfm" floppy.img
    
Likewise, when writing, one has to keep in mind the convention used for padding the FM track data in the sector image file. If the image has previously been created/ converted in MAME, then it is possible that the padding was actually done per sector rather than per track. And since MAME uses non-zero data for the padding, in this case, it actually _does_ make a difference. One can investigate the image e.g. with dd and hexdump, by increasing the skip parameter to odd numbers:

    dd if=floppy.img bs=128 skip=1 count=1 |hexdump -v -C

When writing back the first 2 kiB of such an image file in the way describe here, one would write some of the padding data back to the disk, which does not technically belong there. One option would again be to slice the image data up into chunks of 128 bytes and remove the padding before writing back to disk, or, if we assume that only the first sector contains data, we can construct a new header by first filling it with 2 kiB of 0s and then adding the first sector's data:

    dd if=/dev/null of=tmp_t0.img bs=2048 count=1
    dd conv=notrunc if="floppy.img" of="tmp_t0.img" bs=128 count=1
    gw write --tracks="c=0:h=0" --diskdefs diskdefs.cfg --format="olivetti.m20.fm" tmp_t0.img
    
None of the known (non-dos) images contain any data other than in the first sector/ first 128 bytes, so the method should be safe to use, but better double check.

### Drive

Should be a 360kB 40 track drive:

* Teac FD-55BR: [vogons](https://vogonswiki.com/index.php/Teac_FD-55BR) or [retrocmp](https://retrocmp.de/fdd/teac/fd55_i.htm)
* Tandon TM100-2A: [retrocmp](https://retrocmp.de/fdd/tandon/tm100-2a.htm)

The newer 1.2 MB, 80 track drives might be able to read the M20 35 track floppies, but not write them well, due to the narrow track size. When reading with such a drive, one might need to pass an [additional `step=2` parameter](https://github.com/keirf/greaseweazle/wiki/Getting-Started) to the imaging software.

### Media

* Use 5+1⁄4-inch DD 360 kB floppies.
* Possible to use 720 kB QD? They are supported by the M20 natively, but I have never seen such a floppy.
* Possible to use 1.2M HD? According to [this article](https://forum.vcfed.org/index.php?threads/1-2mb-floppy-in-360kb-drive.52905/) it might be possible to re-format this media for DD for use in the M20.

## TODOs

- [ ] Check the inner workings of RDM20/ teledisk/ imagedisk and how they do the FM track padding (per sector/ track?). Do we have access to the source code? TD and IMD should be available via MAME source.
- [ ] Can the original M20 boot a floppy with a replaced track0 from a random image?
- [ ] Can the original M20 boot images which do not work in mame? (cpm8k?)
- [ ] Provide Feedback [here](https://gist.github.com/jandelgado/88962932896127dcabbe251f996e790e), [here](https://github.com/keirf/greaseweazle/issues/143) and [here](https://github.com/keirf/greaseweazle/issues/261)
- [ ] Interesting read: https://www.smbaker.com/raspberry-pi-floppy-controller-board

