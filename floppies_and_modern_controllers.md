
## Reading M20 floppies with modern controllers

Version: 11 Jan 2023

<p align="center">
  <img src="article_media/floppy.jpg" alt="An original PCOS 2.0 floppy from 1983" width="700px"/>
</p>

* https://www.smbaker.com/raspberry-pi-floppy-controller-board

### Controller

Multiple options:

#### Kryoflux

Cons:

* Can not write *.img files back to floppy directly (need to convert to raw flux files first with HxC^[[https://hxc2001.com/download/floppy_drive_emulator/](https://hxc2001.com/download/floppy_drive_emulator/)]
* Mainly made for reading floppies

#### Greaseweazel

Pros:

* Can [read and write](https://github.com/keirf/greaseweazle/wiki/Supported-Image-Types) *.img files
* Can potentially even read and write [mixed](https://github.com/keirf/greaseweazle/issues/143) FM/MFM floppies

### Drive

Should be a 360kB 40 track drive. 80 track drives might be able to read the M20 35 track floppies, but not write them well, due to the narrow track size.

* Tandon TM100-2A: [retrocmp](https://retrocmp.de/fdd/tandon/tm100-2a.htm)
* Teac FD-55BR: [vogons](https://vogonswiki.com/index.php/Teac_FD-55BR) or [retrocmp](https://retrocmp.de/fdd/teac/fd55_i.htm)

### Media

* Possible to use 1.2M floppies? See [this article](https://forum.vcfed.org/index.php?threads/1-2mb-floppy-in-360kb-drive.52905/).

## TODOs

- [ ] Decide on a drive to buy
- [ ] Research: What are the differences in drives (e.g. 40 vs 80 tracks) and which is the best for M20 floppies?


