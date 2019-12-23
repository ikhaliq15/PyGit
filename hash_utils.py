import hashlib

def get_sha1(s):
	return hashlib.sha1(s.encode('utf-8')).hexdigest()

def hash_commit(commit):
	return get_sha1(str(commit))

def hash_file(filename):
	with open(filename, mode='r') as file:
		contents = file.read()
	file.close()
	return get_sha1(str(contents))