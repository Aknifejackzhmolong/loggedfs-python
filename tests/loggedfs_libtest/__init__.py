# -*- coding: utf-8 -*-

"""

LoggedFS-python
Filesystem monitoring with Fuse and Python
https://github.com/pleiszenburg/loggedfs-python

	tests/loggedfs_libtest/__init__.py: Test library module init

	Copyright (C) 2017 Sebastian M. Ernst <ernst@pleiszenburg.de>

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
from pprint import pprint as pp
import shutil
import subprocess

from yaml import load, dump
try:
	from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
	from yaml import Loader, Dumper


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CONST
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

TEST_ROOT_PATH = 'tests'

TEST_FSTEST_PATH = 'fstest'
TEST_FSTEST_CONF_SUBPATH = 'tests/conf'
TEST_FSTEST_MAKE_SUBPATH = 'Makefile'
TEST_MOUNT_PATH = 'loggedfs_mount'

TEST_CFG_FN = 'test_loggedfs_cfg.xml' # TODO unused
TEST_LOG_FN = 'test_loggedfs.log'
TEST_RESULTS_FN = 'test_fstest_results.log'
TEST_ERRORS_FN = 'test_fstest_errors.log'


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES: FSTEST
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def install_fstest():

	install_path = os.path.join(TEST_ROOT_PATH, TEST_FSTEST_PATH)
	if os.path.isdir(install_path):
		shutil.rmtree(install_path, ignore_errors = True)
	__run_command__(['git', 'clone', 'https://github.com/zfsonlinux/fstest.git', install_path])
	__build_fstest__(install_path)


def run_fstest():

	os.chdir(TEST_ROOT_PATH) # tests usually run from project root

	test_root_abs_path = os.path.abspath(os.getcwd())
	test_mount_abs_path = os.path.join(test_root_abs_path, TEST_MOUNT_PATH)

	__pre_test_cleanup_mountpoint__(test_mount_abs_path)
	__pre_test_cleanup_logfiles__(test_root_abs_path)
	os.mkdir(test_mount_abs_path)

	loggedfs_status = __mount_loggedfs_python__(test_mount_abs_path, os.path.join(test_root_abs_path, TEST_LOG_FN))
	assert loggedfs_status
	assert __is_path_mountpoint__(test_mount_abs_path)

	prove_status, prove_out, prove_err = __run_fstest__(
		os.path.join(test_root_abs_path, TEST_FSTEST_PATH), test_mount_abs_path
		)
	__write_file__(os.path.join(test_root_abs_path, TEST_RESULTS_FN), prove_out)
	__write_file__(os.path.join(test_root_abs_path, TEST_ERRORS_FN), prove_err)

	umount_fuse_status = __umount_fuse__(test_mount_abs_path)
	assert umount_fuse_status
	assert not __is_path_mountpoint__(test_mount_abs_path)

	os.chdir('..') # return to project root


def __build_fstest__(abs_in_path, filesystem = 'ext3'):

	old_path = os.getcwd()
	os.chdir(abs_in_path)

	fstest_conf = __read_file__(TEST_FSTEST_CONF_SUBPATH).split('\n')
	for index, line in enumerate(fstest_conf):
		if line.startswith('fs='):
			fstest_conf[index] = 'fs="%s"' % filesystem
			break
	__write_file__(TEST_FSTEST_CONF_SUBPATH, '\n'.join(fstest_conf))

	# ftest_make = __read_file__(TEST_FSTEST_MAKE_SUBPATH)
	# __write_file__(TEST_FSTEST_MAKE_SUBPATH, ftest_make.replace('#CFLAGS', 'CFLAGS'))

	__run_command__(['make', 'clean'])
	build_status, out, err = __run_command__(['make', 'fstest'], return_output = True)
	print(build_status, out, err)
	assert build_status

	os.chdir(old_path)


def __is_path_mountpoint__(in_abs_path):

	return __run_command__(['mountpoint', '-q', in_abs_path])


def __mount_loggedfs_python__(in_abs_path, logfile):

	return __run_command__(['loggedfs', '-l', logfile, in_abs_path])


def __pre_test_cleanup_logfiles__(in_abs_path):

	for filename in [TEST_LOG_FN, TEST_RESULTS_FN, TEST_ERRORS_FN]:
		try:
			os.remove(os.path.join(in_abs_path, filename))
		except FileNotFoundError:
			pass


def __pre_test_cleanup_mountpoint__(in_abs_path):

	if __is_path_mountpoint__(in_abs_path):
		umount_status = __umount__(in_abs_path, sudo = True, force = True)
		assert umount_status

	if os.path.isdir(in_abs_path):
		shutil.rmtree(in_abs_path, ignore_errors = True)
	assert not os.path.isdir(in_abs_path)


def __run_command__(cmd_list, return_output = False):

	proc = subprocess.Popen(
		cmd_list, stdout = subprocess.PIPE, stderr = subprocess.PIPE
		)
	outs, errs = proc.communicate()

	if return_output:
		return (not bool(proc.returncode), outs.decode('utf-8'), errs.decode('utf-8'))
	return not bool(proc.returncode)


def __run_fstest__(abs_test_path, abs_mountpoint_path):

	old_cwd = os.getcwd()
	os.chdir(abs_mountpoint_path)

	ret_tuple = __run_command__(
		['prove', '-v', '-r', abs_test_path], return_output = True
		)

	os.chdir(old_cwd)
	return ret_tuple


def __umount__(in_abs_path, sudo = False, force = False):

	cmd_list = []
	if sudo:
		cmd_list.append('sudo')
	cmd_list.append('umount')
	if force:
		cmd_list.append('-f')
	cmd_list.append(in_abs_path)

	return __run_command__(cmd_list)


def __umount_fuse__(in_abs_path):

	return __run_command__(['fusermount', '-u', in_abs_path])


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES: FSTEST ANALYSIS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def compare_results(old_results, new_results):

	old_results_keys = set(old_results.keys())
	new_results_keys = set(new_results.keys())
	common_keys = old_results_keys & new_results_keys

	dropped_keys = old_results_keys - common_keys
	new_keys = new_results_keys - common_keys

	ch_to_fail = {}
	ch_to_pass = {}
	for key in common_keys:
		if old_results[key] == new_results[key]:
			continue
		if new_results[key]:
			ch_to_pass.add(key)
		else:
			ch_to_fail.add(key)

	return {
		'ch_to_fail_set': ch_to_pass,
		'ch_to_pass_set': ch_to_fail,
		'dropped_dict': {key: old_results_keys[val] for key in dropped_keys},
		'new_dict': {key: old_results_keys[val] for key in new_keys}
		}


def compile_stats(in_dict):

	tests_total = 0
	tests_failed = 0

	for item_key in in_dict.keys():
		tests_total += 1
		if not in_dict[item_key]:
			tests_failed += 1

	return {
		'int_tests': tests_total,
		'int_failed': tests_failed
		}


def get_results():

	test_results_raw_log = __read_file__(os.path.join(TEST_ROOT_PATH, TEST_RESULTS_FN))
	return __process_raw_results__(test_results_raw_log)


def __process_raw_results__(in_str):

	lines = in_str.split('\n')
	ret_dict = {}

	for line in lines:

		line = line.strip()
		if line == '':
			break

		if line.startswith('Failed') or line == 'ok':
			continue

		if line.startswith('/'):
			current_path = line.split('fstest/tests/')[1].split(' ')[0]
			continue

		if '..' in line:
			index = 1
			continue

		if line.startswith('ok '):
			res = True
		elif line.startswith('not ok '):
			res = False
		else:
			print(current_path, index, line)
			raise

		if not line.endswith(str(index)):
			raise

		ret_dict.update({'%s:%d' % (current_path, index): res})
		index += 1

	return ret_dict


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES: I/O
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def dump_yaml(filename, data):

	f = open(filename, 'w+')
	dump(data, f, Dumper = Dumper, default_flow_style = False)
	f.close()


def load_yaml(filename):

	f = open(filename, 'r')
	data = load(f)
	f.close()
	return data


def __read_file__(filename):

	f = open(filename, 'r')
	data = f.read()
	f.close()
	return data


def __write_file__(filename, data):

	f = open(filename, 'w+')
	f.write(data)
	f.close()