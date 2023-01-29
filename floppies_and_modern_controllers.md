
## Reading M20 floppies with modern controllers

Version: 22 Jan 2023 (WIP). Text based on Greaseweazel 1.5.dev2, a Teac FD-55BR drive and Mame v.251, all running on Ubuntu 22.10.

<p align="center">
  <img src="article_media/floppy.jpg" alt="An original PCOS 2.0 floppy from 1983" width="700px"/>
</p>

When reading M20 floppies under Linux with a standard pc controller (48 tracks per inch, sector size 256 bytes, 16 sectors per track, MFM) one likely has to skip the first 4 kiB/ track0, as many PC controllers cannot read the FM track:

    $ setfdprm /dev/fd1 tpi=48 ssize=256 sect=16 dd ds
    $ sdd -noerror try=5 iseek=4096 oseek=4096 if=/dev/fd1 of=floppy.img bs=256 count=1104 

The first 4 kiB of this image will be zero. More information about setfdprm/ fdutils and the `sdd` tool can be found [here](http://www.z80ne.com/m20/index.php?argument=sections/transfer/imagereadwrite/imagereadwrite.inc). The main reason to use `sdd` over `dd` was the additional seek parameter on the input side.

Other options, using modern USB-floppy-controllers, are also able to read the FM track:

#### Controller options

* [Kryoflux](https://kryoflux.com/):

  * Can not write *.img files back to floppy directly (need to convert to raw flux files first with e.g. the [HxC Floppy Emulator](https://hxc2001.com/download/floppy_drive_emulator/)).
  * Mainly made for reading floppies, writing floppies is possible, but considered a "bonus" and is not officially supported (e.g. if one needs help in the support forums)
  * Reading M20 floppies works and is described e.g. [here](https://jandelgado.github.io/blog/posts/olivetti-m20-disk-preservation/).

* [Greaseweazel v4](https://github.com/keirf/Greaseweazle/wiki):

  * Can [read and write](https://github.com/keirf/greaseweazle/wiki/Supported-Image-Types) *.img files
  * Can even read and write [mixed](https://github.com/keirf/greaseweazle/issues/143) FM/MFM floppies
  * Discussion about support FM track padding [in progress](https://github.com/keirf/greaseweazle/issues/275).

### Greaseweazel setup

Get all necessarzy parts and set up the Greaseweazel v4 according to the [documentation](https://github.com/keirf/greaseweazle/wiki/V4-Setup). Then create a `diskdefs.cfg` config for M20 floppies - available since v1.6 of the greaseweazel tools:

    # Greaseweazel v1.6 diskdefs.cfg for Olivetti M20 360 kB DD floppies
    disk olivetti.m20
        cyls = 35
        heads = 2
        tracks 0.0 ibm.fm
            secs = 16
            bps = 128
            rate = 125
        end
        tracks * ibm.mfm
            secs = 16
            bps = 256
            rate = 250
        end
    end

#### Reading

Now one has to issue only a single read command to the `gw`-tool and it will take care of handling the mixed format all by itself:

    gw read --diskdefs diskdefs.cfg --format="olivetti.m20" floppy.img
    
This produces an image with the size of 278 kiB. One has to keep in mind that the FM track is only 2 kiB in size, while the MFM tracks are 4 kiB. So this method produces an image file of a different size, than the original method, which skipped track0 in "MFM mode", hence resulting in a size of 280 kiB. 

One use-case would be to load the images in [MAME](http://www.z80ne.com/m20/index.php?argument=sections/tech/mame_m20.inc), which also follows the convention that track1 starts with a 4 kiB offset in the sector image file. In order to convert the image to the homogeneous the 4 kiB / track sizing, one needs to add an additional 2 kiB of zeros to pad the first track:

    dd if=floppy.img of=floppy_mame.img bs=2048 count=1
    dd if=floppy.img of=floppy_mame.img bs=2048 skip=1 seek=2

As a sidenote: Mame actually assumes [every one of the 16 sectors](https://github.com/mamedev/mame/blob/master/src/lib/formats/m20_dsk.cpp#L9) in the FM track to be padded with 128 Bytes, instead of padding the entire track0 with an additional 2 kiB (like done here). Reproducing this during imaging would make the conversion process more complex, since one would need to slice track0 into 16 parts à 128 bytes and pad them individually. We can however stick to the simplification, since only the [very first sector](https://forums.bannister.org/ubbthreads.php?ubb=showflat&Number=100146#Post100146) in the FM track seems to contain data anayways. Due to this, the difference between track and sector padding vanishes. This is indeed the case for all known images, but one should probably keep this in mind when imaging floppies which haven't been looked at yet.

When trying to create authentic copies which can be validated by checksum (crc/ sha) one also has to keep in mind the additional data used for padding the sectors first track. While we use 0s for the padding, MAME seems to use 1s to pad the offset to the second track. Hence an image converted by MAME would result in a different checksum, allthough the user data is fully identical.

#### Writing

For writing back to floppy, again one has to take into account the padding in the original image. If it has 280 kiB/ has been used in Mame, one needs to remove the extra 2 kiB of data from track0:

    dd if=floppy_mame.img of=floppy.img bs=2048 count=1
    dd if=floppy_mame.img of=floppy.img bs=2048 skip=2 seek=1

The the image can be written with a single command, based on the mixed floppy composition defined in the config:
    
    gw write --diskdefs $diskdefs --format="olivetti.m20" $FN
    
Another MAME sidenote: Likewise, when writing, one has to keep in mind the convention used for padding the FM track data in the sector image file. If the image has previously been created/ converted in MAME, then it is possible that the padding was actually done per sector rather than per track. And since MAME uses non-zero data for the padding, in this case, it actually _does_ make a difference. One can investigate the image e.g. with dd and hexdump, by increasing the skip parameter to odd numbers:

    dd if=floppy.img bs=128 skip=1 count=1 |hexdump -v -C

When writing back the first 2 kiB of such an image file, in the way describe here, one would write some of the non-zero sector-padding data back to the disk, which does not technically belong there. One option would again be to slice the image data up into chunks of 128 bytes and remove the padding before writing back to disk. Alternatively, assuming again that only the first sector contains data, the conversion can also be done by only copying the first sector to the image and skipping the rest of the first track:

    dd if=floppy_mame.img of=floppy.img bs=128 count=1
    dd if=floppy_mame.img of=floppy.img bs=2048 skip=2 seek=1
    
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

