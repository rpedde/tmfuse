#!/usr/bin/env python -u

import os
import sys
import errno
import fuse

sys.stdout = sys.stderr

class TMFuse(fuse.Fuse):
    def __init__(self, root, xlated, *args, **kwargs):
        fuse.Fuse.__init__(self, *args, **kwargs)

        real_root = os.path.join(root, 'Backups.backupdb')
        if not os.path.exists(real_root):
            print 'Cannot find Backups.backupdb'
            sys.exit(1)

        self.root = real_root
        self.dirdata = None

        rootlist = os.listdir(root)
        for item in rootlist:
            if item.startswith('.HFS+ Private Directory Data'):
                self.dirdata = os.path.join(root, item)

        if self.dirdata is None or not os.path.exists(self.dirdata):
            print "Cannot find private directory data"
            sys.exit(1)

        print 'Real root: %s' % self.root
        print 'Dir data: %s' % self.dirdata

    def _path_parts(self, relative):
        relparts = relative.split('/')
        if relparts[0] == '':
            relparts.pop(0)

        if relparts[-1] == '':
            relparts.pop(-1)

        return relparts


    def _full_path(self, relative):
        relparts = self._path_parts(relative)

        full_path = self.root
        while len(relparts) > 0:
            full_path = os.path.join(full_path, relparts[0])
            relparts.pop(0)
            temp_path = self._get_indirected_path(full_path)
            if full_path is None:
                return None
            full_path = temp_path

        return full_path

    def _dirdata_path(self, dir_number):
        return os.path.join(self.dirdata, 'dir_%s' % dir_number)

    def _get_indirected_path(self, full_path):
        if not os.path.lexists(full_path):
            return None

        st = os.lstat(full_path)

        if st.st_size == 0:
            if os.path.exists(self._dirdata_path(st.st_nlink)):
                return self._dirdata_path(st.st_nlink)

        return full_path
        
    def _is_indirected_directory(self, full_path):
        if self._get_indirected_path(full_path) is None:
            return False

        return True

    def access(self, path, mode):
        full_path = self._full_path(path)
        if full_path is None:
            return -errno.ENOENT

        if not os.access(full_path, mode):
            return -errno.EACCESS

    def getattr(self, path):
        full_path = self._full_path(path)
        if full_path is None:
            return -errno.ENOENT

        st = os.lstat(full_path)
        return st

    def open(self, path, flags):
        full_path = self._full_path(path)
        result = os.open(full_path, flags)
        return str(result)

    def read(self, path, length, offset, fh):
        fh = int(fh)

        os.lseek(fh, offset, os.SEEK_SET)
        return os.read(fh, length)

    def readdir(self, path, offset):
        full_path = self._full_path(path)

        dirents = ['.', '..']
        if os.path.isdir(full_path):
            dirents.extend(os.listdir(full_path))
        for d in dirents:
            yield fuse.Direntry(d)

    def readlink(self, path):
        full_path = self._full_path(path)
        if full_path is None:
            return -errno.ENOENT

        pathname = os.readlink(full_path)
        if pathname.startswith("/"):
            # Path name is absolute, but should be absolute
            # wrt disk...
            base = path.split('/')
            relpath = '/%s%s' % ('/'.join(base[1:4]), pathname)
            return relpath
        else:
            return pathname
        
    def release(self, path, flags, fh):
        return close(int(fh))

    def statfs(self):
        return os.statvfs(self.root)


if __name__ == '__main__':
    fuse.fuse_python_api = (0, 2)

    fs = TMFuse(sys.argv[1], sys.argv[2])
    fs.flags = 0
    fs.multithreaded = 0
    fs.parse(errex=1)
    fs.main()



    
