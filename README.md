## tmfuse ##

So I find myself with a Airbook reformatted for Debian.  This is fine
and all, but then I realize that all my old data is on a time machine
backup.  I didn't figure it to be a problem, as I know I have HFS+
drivers in linux.  Alas, the time machine backups have some strange
directory indirection.  So here is a python FUSE module for reading
Mac Time Machine backups on linux.

I've only ever used this on Debian Wheezy.  YMMV, etc.  Patches for other systems welcome.

Requires `python-fuse`


~~~~

$ sudo mkdir -p /mnt/{orig,translated}
$ sudo mount /dev/sdc2 /mnt/orig
$ python tmfuse.py /mnt/orig /mnt/translated

~~~~

You'll probably need to be root to view the translated directory.

