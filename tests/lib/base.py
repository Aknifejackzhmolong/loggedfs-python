# -*- coding: utf-8 -*-

"""

LoggedFS-python
Filesystem monitoring with Fuse and Python
https://github.com/pleiszenburg/loggedfs-python

	tests/lib/base.py: Base class for test infrastructure

	Copyright (C) 2017-2020 Sebastian M. Ernst <ernst@pleiszenburg.de>

<LICENSE_BLOCK>
The contents of this file are subject to the Apache License
Version 2 ("License"). You may not use this file except in
compliance with the License. You may obtain a copy of the License at
https://www.apache.org/licenses/LICENSE-2.0
https://github.com/pleiszenburg/loggedfs-python/blob/master/LICENSE

Software distributed under the License is distributed on an "AS IS" basis,
WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License for the
specific language governing rights and limitations under the License.
</LICENSE_BLOCK>

"""


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import os
import shutil
import time

from .const import (
	TEST_FS_EXT4,
	TEST_FS_LOGGEDFS,
	TEST_FSCK_FN,
	TEST_FSTEST_LOG_FN,
	TEST_IMAGE_FN,
	TEST_IMAGE_SIZE_MB,
	TEST_MOUNT_CHILD_PATH,
	TEST_MOUNT_PARENT_PATH,
	TEST_LOG_HEAD,
	TEST_LOG_PATH,
	TEST_ROOT_PATH,
	TEST_LOGGEDFS_CFG_FN,
	TEST_LOGGEDFS_ERR_FN,
	TEST_LOGGEDFS_LOG_FN,
	TEST_LOGGEDFS_OUT_FN,
	)
from .mount import (
	attach_loop_device,
	detach_loop_device,
	find_loop_devices,
	is_path_mountpoint,
	mount,
	mount_loggedfs_python,
	umount,
	umount_fuse,
	)
from .procio import (
	ck_filesystem,
	create_zero_file,
	mk_filesystem,
	run_command,
	write_file,
	)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASS: (1/3) PRE
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class fstest_base_class():


	with_sudo = True
	fs_type = TEST_FS_LOGGEDFS
	travis = False


	def init_a_members(self, fs_type = TEST_FS_LOGGEDFS):

		self.fs_type = fs_type

		self.prj_abs_path = os.getcwd()
		self.root_abs_path = os.path.abspath(os.path.join(self.prj_abs_path, TEST_ROOT_PATH))
		assert os.path.isdir(self.root_abs_path)

		self.logs_abs_path = os.path.join(self.root_abs_path, TEST_LOG_PATH)

		self.image_abs_path = os.path.join('/dev/shm', TEST_IMAGE_FN)

		self.mount_parent_abs_path = os.path.join(self.root_abs_path, TEST_MOUNT_PARENT_PATH)
		self.mount_child_abs_path = os.path.join(self.mount_parent_abs_path, TEST_MOUNT_CHILD_PATH)

		self.loggedfs_log_abs_path = os.path.join(self.logs_abs_path, TEST_LOGGEDFS_LOG_FN)
		self.loggedfs_cfg_abs_path = os.path.join(self.root_abs_path, TEST_LOGGEDFS_CFG_FN)

		if 'TRAVIS' in os.environ.keys():
			self.travis = os.environ['TRAVIS'] == 'true'

		self.fstest_log_abs_path = os.path.join(self.logs_abs_path, TEST_FSTEST_LOG_FN)


	def init_b_cleanup(self):

		if self.travis:
			return

		self.__cleanup_logfiles__() # rm -r log_dir
		self.__cleanup_mountpoint__(self.mount_child_abs_path) # umount & rmdir
		self.__cleanup_mountpoint__(self.mount_parent_abs_path) # umount & rmdir
		self.__cleanup_loop_devices__() # losetup -d /dev/loopX
		self.__cleanup_image__() # rm file


	def init_c_parentfs(self):

		if not self.travis:
			create_zero_file(self.image_abs_path, TEST_IMAGE_SIZE_MB)
			self.__attach_loop_device__()
			mk_filesystem(self.loop_device_path, file_system = TEST_FS_EXT4)
		self.__mk_dir__(self.mount_parent_abs_path)
		if not self.travis:
			self.__mount_parent_fs__()
		self.__mk_dir__(self.logs_abs_path, allow_preexisting = True)


	def init_d_childfs(self):

		open(self.loggedfs_log_abs_path, 'a').close() # HACK create empty loggedfs log file
		self.__mk_dir__(self.mount_child_abs_path, in_fs_root = True)
		if self.fs_type == TEST_FS_LOGGEDFS:
			self.__mount_child_fs__()
		open(self.fstest_log_abs_path, 'a').close() # HACK create empty fstest log file


	def assert_childfs_mountpoint(self):

		assert is_path_mountpoint(self.mount_child_abs_path)


	def assert_parentfs_mountpoint(self):

		if self.travis:
			return

		assert is_path_mountpoint(self.mount_parent_abs_path)


	def destroy_a_childfs(self):

		if not self.fs_type == TEST_FS_LOGGEDFS:
			return

		if is_path_mountpoint(self.mount_child_abs_path):
			umount_child_status = umount_fuse(self.mount_child_abs_path, sudo = self.with_sudo)
			assert umount_child_status
			assert not is_path_mountpoint(self.mount_child_abs_path)

		self.__rm_tree__(self.mount_child_abs_path, in_fs_root = True)

		time.sleep(0.1) # HACK ... otherwise parent will be busy


	def destroy_b_parentfs(self):

		if not self.travis:
			umount_parent_status = umount(self.mount_parent_abs_path, sudo = True)
			assert umount_parent_status
			assert not is_path_mountpoint(self.mount_parent_abs_path)

		self.__rm_tree__(self.mount_parent_abs_path)

		if self.travis:
			return

		loop_device_list = find_loop_devices(self.image_abs_path)
		assert isinstance(loop_device_list, list)
		assert len(loop_device_list) == 1
		loop_device_path = loop_device_list[0]

		ck_status_code, ck_out, ck_err = ck_filesystem(loop_device_path)
		write_file(
			os.path.join(self.logs_abs_path, TEST_FSCK_FN),
			''.join([
				TEST_LOG_HEAD % 'EXIT STATUS',
				'%d\n' % ck_status_code,
				TEST_LOG_HEAD % 'OUT',
				ck_out,
				TEST_LOG_HEAD % 'ERR',
				ck_err
				])
			)

		detach_status = detach_loop_device(loop_device_path)
		assert detach_status

		assert not bool(ck_status_code) # not 0 for just about any type of error! Therefore asserting at the very end.

		os.remove(self.image_abs_path)
		assert not os.path.exists(self.image_abs_path)


	def __attach_loop_device__(self):

		loop_status = attach_loop_device(self.image_abs_path)
		assert loop_status
		loop_device_list = find_loop_devices(self.image_abs_path)
		assert isinstance(loop_device_list, list)
		assert len(loop_device_list) == 1

		self.loop_device_path = loop_device_list[0]


	def __cleanup_image__(self):

		if os.path.isfile(self.image_abs_path):
			os.remove(self.image_abs_path)
		assert not os.path.isfile(self.image_abs_path)


	def __cleanup_mountpoint__(self, in_path):

		if is_path_mountpoint(in_path):
			umount_status = umount(in_path, sudo = True, force = True)
			if not umount_status:
				fumount_status = umount_fuse(in_path, sudo = True)
			assert not is_path_mountpoint(in_path)

		if os.path.isdir(in_path):
			assert in_path != '/'
			run_command(['rmdir', in_path], sudo = self.with_sudo)
		assert not os.path.isdir(in_path)


	def __cleanup_logfiles__(self):

		if os.path.isdir(self.logs_abs_path):
			assert self.logs_abs_path != '/'
			run_command(['rm', '-r', self.logs_abs_path], sudo = self.with_sudo)


	def __cleanup_loop_devices__(self):

		if not os.path.isfile(self.image_abs_path):
			assert find_loop_devices(self.image_abs_path) == []
			return

		loop_dev_list = find_loop_devices(self.image_abs_path)
		assert loop_dev_list is not None

		for loop_dev in loop_dev_list:
			detach_status = detach_loop_device(loop_dev)
			assert detach_status

		assert find_loop_devices(self.image_abs_path) == []


	def __mk_dir__(self, in_path, in_fs_root = False, allow_preexisting = False):

		if allow_preexisting:
			if os.path.isdir(in_path):
				return

		if not in_fs_root:
			os.mkdir(in_path)
		else:
			mkdir_status = run_command(['mkdir', in_path], sudo = True)
			assert mkdir_status
			chown_status = run_command(['chown', '%d:%d' % (os.getuid(), os.getgid()), in_path], sudo = True)
			assert chown_status

		assert os.path.isdir(in_path)


	def __mount_child_fs__(self):

		assert not is_path_mountpoint(self.mount_child_abs_path)

		loggedfs_status, loggedfs_out, loggedfs_err = mount_loggedfs_python(
			self.mount_child_abs_path,
			self.loggedfs_log_abs_path,
			self.loggedfs_cfg_abs_path,
			sudo = self.with_sudo
			)

		write_file(os.path.join(self.root_abs_path, TEST_LOG_PATH, TEST_LOGGEDFS_OUT_FN), loggedfs_out)
		write_file(os.path.join(self.root_abs_path, TEST_LOG_PATH, TEST_LOGGEDFS_ERR_FN), loggedfs_err)

		assert loggedfs_status
		assert is_path_mountpoint(self.mount_child_abs_path)


	def __mount_parent_fs__(self):

		assert not is_path_mountpoint(self.mount_parent_abs_path)
		mount_status = mount(self.mount_parent_abs_path, self.loop_device_path)
		assert mount_status
		assert is_path_mountpoint(self.mount_parent_abs_path)


	def __rm_tree__(self, in_path, in_fs_root = False):

		if not in_fs_root:
			shutil.rmtree(in_path)
		else:
			rmdir_status = run_command(['rm', '-r', in_path], sudo = True)
			assert rmdir_status

		assert not os.path.exists(in_path)
