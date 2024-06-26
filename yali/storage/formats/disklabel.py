#!/usr/bin/python
# -*- coding: utf-8 -*-

try:
    from PyQt6.QtCore import QCoreApplication
    _ = QCoreApplication.translate
except:
    _ = lambda x,y: y

import os
import copy
import parted
import _ped

import yali.baseudev
import yali.util
from yali.storage.formats import Format, FormatError, register_device_format

class DiskLabelError(FormatError):
    pass

class InvalidDiskLabelError(DiskLabelError):
    pass

class DiskLabelCommitError(DiskLabelError):
    pass

class DiskLabel(Format):
    """ Disklabel """
    _type = "disklabel"
    _name = _("General", "partition table")
    _formattable = True                # can be formatted
    _supported = False                 # is supported

    def __init__(self, *args, **kwargs):
        """ Create a DiskLabel instance.

            Keyword Arguments:

                device -- path to the underlying device
                exists -- indicates whether this is an existing format

        """
        Format.__init__(self, *args, **kwargs)

        self._size = None

        self._partedDevice = None
        self._partedDisk = None
        self._origPartedDisk = None
        self._alignment = None
        self._endAlignment = None

        if self.partedDevice:
            # set up the parted objects and raise exception on failure
            self._origPartedDisk = self.partedDisk.duplicate()

    def __deepcopy__(self, memo):
        """ Create a deep copy of a Disklabel instance.

            We can't do copy.deepcopy on parted objects, which is okay.
            For these parted objects, we just do a shallow copy.
        """
        new = self.__class__.__new__(self.__class__)
        memo[id(self)] = new
        shallow_copy_attrs = ('_partedDevice', '_partedDisk', '_origPartedDisk')
        for (attr, value) in self.__dict__.items():
            if attr in shallow_copy_attrs:
                setattr(new, attr, copy.copy(value))
            else:
                setattr(new, attr, copy.deepcopy(value, memo))

        return new

    def __str__(self):
        s = Format.__str__(self)
        s += ("  type = %(type)s  partition count = %(count)s"
              "  sectorSize = %(sectorSize)s\n"
              "  align_offset = %(offset)s  align_grain = %(grain)s\n"
              "  partedDisk = %(disk)r\n"
              "  origPartedDisk = %(orig_disk)r\n"
              "  partedDevice = %(dev)r\n" %
              {"type": self.labelType, "count": len(self.partitions),
               "sectorSize": self.partedDevice.sectorSize,
               "offset": self.alignment.offset,
               "grain": self.alignment.grainSize,
               "disk": self.partedDisk, "orig_disk": self._origPartedDisk,
               "dev": self.partedDevice})
        return s

    def resetPartedDisk(self):
        """ Set this instance's partedDisk to reflect the disk's contents. """
        self._partedDisk = self._origPartedDisk

    def freshPartedDisk(self):
        """ Return a new, empty parted.Disk instance for this device. """
        if yali.util.isEfi():
            labelType = "gpt"
        else:
            labelType = "msdos"

        return parted.freshDisk(device=self.partedDevice, ty=labelType)

    @property
    def partedDisk(self):
        if not self._partedDisk:
            if self.exists:
                try:
                    self._partedDisk = parted.Disk(device=self.partedDevice)
                except (_ped.DiskLabelException, _ped.IOException,
                        NotImplementedError) as e:
                    raise InvalidDiskLabelError()

                if self._partedDisk.type == "loop":
                    # When the device has no partition table but it has a FS,
                    # it will be created with label type loop.  Treat the
                    # same as if the device had no label (cause it really
                    # doesn't).
                    raise InvalidDiskLabelError()
            else:
                self._partedDisk = self.freshPartedDisk()

            # turn off cylinder alignment
            if self._partedDisk.isFlagAvailable(parted.DISK_CYLINDER_ALIGNMENT):
                self._partedDisk.unsetFlag(parted.DISK_CYLINDER_ALIGNMENT)

        return self._partedDisk

    @property
    def partedDevice(self):
        if not self._partedDevice and self.device and \
           os.path.exists(self.device):
            # We aren't guaranteed to be able to get a device.  In
            # particular, built-in USB flash readers show up as devices but
            # do not always have any media present, so parted won't be able
            # to find a device.
            try:
                 self._partedDevice = parted.Device(path=self.device)
            except (_ped.IOException, _ped.DeviceException):
                 pass

        return self._partedDevice

    @property
    def labelType(self):
        """ The disklabel type (eg: 'gpt', 'msdos') """
        return self.partedDisk.type

    @property
    def name(self):
        return "%s (%s)" % (self._name, self.labelType.upper())

    @property
    def size(self):
        size = self._size
        if not size:
            try:
                size = self.partedDevice.getSize(unit="MB")
            except Exception:
                size = 0

        return size

    @property
    def status(self):
        """ Device status. """
        return False

    def setup(self, *args, **kwargs):
        """ Open, or set up, a device. """
        if not self.exists:
            raise DiskLabelError("format has not been created", self.device)

        if self.status:
            return

        Format.setup(self, *args, **kwargs)

    def teardown(self, *args, **kwargs):
        """ Close, or tear down, a device. """
        if not self.exists:
            raise DiskLabelError("format has not been created", self.device)

    def create(self, *args, **kwargs):
        """ Create the device. """
        if self.exists:
            raise DiskLabelError("format already exists", self.device)

        if self.status:
            raise DiskLabelError("device exists and is active", self.device)

        Format.create(self, *args, **kwargs)

        # We're relying on someone having called resetPartedDisk -- we
        # could ensure a fresh disklabel by setting self._partedDisk to
        # None right before calling self.commit(), but that might hide
        # other problems.
        self.commit()
        self.exists = True

    def destroy(self, *args, **kwargs):
        """ Wipe the disklabel from the device. """
        if not self.exists:
            raise DiskLabelError("format does not exist", self.device)

        if not os.access(self.device, os.W_OK):
            raise DiskLabelError("device path does not exist", self.device)

        self.partedDevice.clobber()
        self.exists = False

    def commit(self):
        """ Commit the current partition table to disk and notify the OS. """
        try:
            self.partedDisk.commit()
        except parted.DiskException as msg:
            raise DiskLabelCommitError(msg)
        else:
            yali.baseudev.udev_settle()

    def commitToDisk(self):
        """ Commit the current partition table to disk. """
        try:
            self.partedDisk.commitToDevice()
        except parted.DiskException as msg:
            raise DiskLabelCommitError(msg)

    def addPartition(self, *args, **kwargs):
        partition = kwargs.get("partition", None)
        if not partition:
            partition = args[0]
        geometry = partition.geometry
        constraint = kwargs.get("constraint", None)
        if not constraint and len(args) > 1:
            constraint = args[1]
        elif not constraint:
            constraint = parted.Constraint(exactGeom=geometry)

        new_partition = parted.Partition(disk=self.partedDisk,
                                         type=partition.type,
                                         geometry=geometry)
        self.partedDisk.addPartition(partition=new_partition,
                                     constraint=constraint)

    def removePartition(self, partition):
        self.partedDisk.removePartition(partition)

    @property
    def extendedPartition(self):
        try:
            extended = self.partedDisk.getExtendedPartition()
        except Exception:
            extended = None
        return extended

    @property
    def logicalPartitions(self):
        try:
            logicals = self.partedDisk.getLogicalPartitions()
        except Exception:
            logicals = []
        return logicals

    @property
    def freePartitions(self):
        try:
            freeSpaces = self.partedDisk.getFreeSpacePartitions()
        except Exception:
            freeSpaces = []
        return freeSpaces

    @property
    def firstPartition(self):
        try:
            part = self.partedDisk.getFirstPartition()
        except Exception:
            part = None
        return part

    @property
    def partitions(self):
        try:
            parts = self.partedDisk.partitions
        except Exception:
            parts = []
        return parts

    @property
    def alignment(self):
        """ Alignment requirements for this device. """
        if not self._alignment:
            try:
                disklabel_alignment = self.partedDisk.partitionAlignment
            except _ped.CreateException:
                disklabel_alignment = parted.Alignment(offset=0, grainSize=1)

            try:
                optimum_device_alignment = self.partedDevice.optimumAlignment
            except _ped.CreateException:
                optimum_device_alignment = None

            try:
                minimum_device_alignment = self.partedDevice.minimumAlignment
            except _ped.CreateException:
                minimum_device_alignment = None

            try:
                a = optimum_device_alignment.intersect(disklabel_alignment)
            except (ArithmeticError, AttributeError):
                try:
                    a = minimum_device_alignment.intersect(disklabel_alignment)
                except (ArithmeticError, AttributeError):
                    a = disklabel_alignment

            self._alignment = a

        return self._alignment

    @property
    def endAlignment(self):
        if not self._endAlignment:
            self._endAlignment = parted.Alignment(
                                        offset = self.alignment.offset - 1,
                                        grainSize = self.alignment.grainSize)

        return self._endAlignment

register_device_format(DiskLabel)

