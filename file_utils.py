import os
from shutil import copyfile, copy
import pickle

from commits import *
from time_utils import *
from hash_utils import *

def create_directory(directory):
	if not dir_exists(directory):
		os.mkdir(directory)

def dir_exists(dir_name):
	return os.path.exists(dir_name) and os.path.isdir(dir_name)

def file_exists(file_name):
	return os.path.exists(file_name)

def get_git_directory():
	cwd = os.getcwd()
	git_dir = os.path.join(cwd, ".pygit")
	return git_dir

def is_initialized():
	return os.path.exists(get_git_directory())

def initialize_git_dir():
	create_directory(get_git_directory())
	create_directory(get_objects_dir())
	create_directory(get_staging_dir())
	initial_commit = Commit("initial commit", time=get_begin_unix_time())
	write_commit(initial_commit)
	write_head(initial_commit)
	pickle.dump([], open(get_remove_file(), 'wb'))

def write_blob(filename):
	with open(filename, mode='r') as file:
		contents = file.read()
	write_object(hash_file(filename), contents)
	file.close()
	return hash_file(filename)

def write_commit(commit):
	write_object(hash_commit(commit), commit)

def write_head(commit):
	head_file = open(get_head_file(), 'wb')
	pickle.dump(hash_commit(commit), head_file)

def read_head_file():
	head_file = open(get_head_file(), 'rb')
	return str(pickle.load(head_file))

def write_object(filename, content):
	hash_id = filename[:2]
	hash_file = filename[2:]
	object_dir = os.path.join(get_objects_dir(), hash_id)
	create_directory(object_dir)
	object_file = open(os.path.join(object_dir, hash_file), 'wb')
	pickle.dump(content, object_file)
	object_file.close()

def read_object(filename):
	obj_map = {Commit.empty: Commit.empty}
	if filename not in obj_map:
		hash_id = filename[:2]
		hash_file = filename[2:]
		object_dir = os.path.join(get_objects_dir(), hash_id)
		object_file = open(os.path.join(object_dir, hash_file), 'rb')
		obj_map[filename] = pickle.load(object_file)
		object_file.close()
	return obj_map[filename]

def get_head_file():
	return os.path.join(get_git_directory(), "HEAD")

def get_remove_file():
	return os.path.join(get_git_directory(), "REMOVE")

def get_staging_dir():
	return os.path.join(get_git_directory(), "staging")

def get_objects_dir():
	return os.path.join(get_git_directory(), "objects")

def copy_file(current_loc, new_loc):
	copyfile(current_loc, new_loc)

def stage_file(file_name):
	copy(file_name, get_staging_dir())

def unstage_file(file_name):
	if file_exists(os.path.join(get_staging_dir(), file_name)):
		os.remove(os.path.join(get_staging_dir(), file_name))

def clear_stage_dir():
	for file in os.listdir(file_utils.get_staging_dir()):
		os.remove(os.path.join(get_staging_dir(), file))

def is_staged(file_name):
	return file_exists(os.path.join(get_staging_dir(), file_name))

def mark_for_remove(file_name):
	objects_to_remove = pickle.load(open(get_remove_file(), 'rb'))
	if file_name not in objects_to_remove:
		objects_to_remove.append(file_name)
	pickle.dump(objects_to_remove, open(get_remove_file(), 'wb'))

def unmark_for_remove(file_name):
	objects_to_remove = pickle.load(open(get_remove_file(), 'rb'))
	if file_name in objects_to_remove:
		objects_to_remove.remove(file_name)
	pickle.dump(objects_to_remove, open(get_remove_file(), 'wb'))

def get_marked_for_remove():
	return pickle.load(open(get_remove_file(), 'rb'))

def clear_marked_for_remove():
	objects_to_remove = []
	pickle.dump(objects_to_remove, open(get_remove_file(), 'wb'))