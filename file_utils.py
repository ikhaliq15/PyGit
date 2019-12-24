import os
import sys
from shutil import copyfile, copy
import pickle

from commits import *
from time_utils import *
from hash_utils import *
from res_strs import *

def create_directory(directory):
	if not dir_exists(directory):
		os.mkdir(directory)

def dir_exists(dir_name):
	return os.path.exists(dir_name) and os.path.isdir(dir_name)

def file_exists(file_name):
	return os.path.exists(file_name)

def exists_branch(branch_name):
	branch_loc = os.path.join(get_heads_dir(), branch_name)
	return os.path.exists(branch_loc) and not os.path.isdir(branch_loc)

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
	create_directory(get_heads_dir())
	initial_commit = Commit("initial commit", time=get_begin_unix_time())
	write_commit(initial_commit)
	write_branch("master", hash_commit(initial_commit))
	write_head("master")
	pickle.dump([], open(get_remove_file(), 'wb'))

def write_blob(filename):
	with open(filename, mode='r') as file:
		contents = file.read()
	write_object(hash_file(filename), contents)
	file.close()
	return hash_file(filename)

def write_commit(commit):
	write_object(hash_commit(commit), commit)

def write_branch(branch_name, head):
	branch_head = open(os.path.join(get_heads_dir(), branch_name), 'wb')
	pickle.dump(head, branch_head)

def add_commit_to_head(commit):
	head_file = open(get_head_file(), 'rb')
	branch = pickle.load(head_file)
	branch_head_file = open(os.path.join(get_heads_dir(), branch), 'wb')
	pickle.dump(hash_commit(commit), branch_head_file)

def write_head(branch):
	head_file = open(get_head_file(), 'wb')
	pickle.dump(branch, head_file)

def get_current_branch():
	head_file = open(get_head_file(), 'rb')
	branch = pickle.load(head_file)
	head_file.close()
	return branch

def get_branch_names():
	return os.listdir(get_heads_dir())

def get_head_for_branch(branch_name):
	branch_head = open(os.path.join(get_heads_dir(), branch_name), 'rb')
	return pickle.load(branch_head)

def read_head_file():
	head_file = open(get_head_file(), 'rb')
	branch = str(pickle.load(head_file))
	branch_head_file = open(os.path.join(get_heads_dir(), branch), 'rb')
	return str(pickle.load(branch_head_file))

def remove_branch(branch_name):
	branch_head_loc = os.path.join(get_heads_dir(), branch_name)
	if file_exists(branch_head_loc):
		os.remove(branch_head_loc)

def find_commit(commit_id):
	hash_id = commit_id[:2]
	hash_file = commit_id[2:]

	buckets = []
	for folder in os.listdir(get_objects_dir()):
		if os.path.isdir(os.path.join(get_objects_dir(), folder)) and folder.startswith(hash_id):
			buckets.append(folder)

	if not buckets:
		print(ErrorMessages.no_commit_found)
		sys.exit(0)
	elif len(buckets) > 1:
		print(ErrorMessages.ambiguous_commit_id)
		sys.exit(0)

	bucket = buckets[0]

	chosen_files = []
	for file in os.listdir(os.path.join(get_objects_dir(), bucket)):
		if not os.path.isdir(file) and file.startswith(hash_file):
			chosen_files.append(file)

	if not chosen_files:
		print(ErrorMessages.no_commit_found)
		sys.exit(0)
	elif len(chosen_files) > 1:
		print(ErrorMessages.ambiguous_commit_id)
		sys.exit(0)

	return bucket + chosen_files[0]

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

def find_all_commits():
	commits = []
	for folder in os.listdir(get_objects_dir()):
		current_bucket = os.path.join(get_objects_dir(), folder)
		if os.path.isdir(current_bucket):
			for file in os.listdir(current_bucket):
				obj = read_object(folder + file)
				if type(obj) == Commit:
					commits.append(obj)
	return commits



def get_head_file():
	return os.path.join(get_git_directory(), "HEAD")

def get_remove_file():
	return os.path.join(get_git_directory(), "REMOVE")

def get_staging_dir():
	return os.path.join(get_git_directory(), "staging")

def get_objects_dir():
	return os.path.join(get_git_directory(), "objects")

def get_heads_dir():
	return os.path.join(get_git_directory(), "heads")

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