import os

def create_directory(directory):
	if not os.path.exists(directory):
		os.mkdir(directory)

def get_git_directory():
	cwd = os.getcwd()
	git_dir = os.path.join(cwd, ".pygit")
	return git_dir

def is_initialized():
	return os.path.exists(get_git_directory())

def initialize_git():
	create_directory(get_git_directory())