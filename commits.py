import os
import file_utils
from time_utils import *
from hash_utils import *

class Commit:

	empty = ()

	def __init__(self, msg="", parent=empty, time=None):
		self.message = msg
		if time:
			self.time_stamp = time
		else:
			self.time_stamp = get_current_time()
		self.parent = parent
		self.blobs = {}

	def add_file(self, filename):
		file = os.path.join(file_utils.get_staging_dir(), filename)
		blob_id = file_utils.write_blob(file)
		self.blobs[filename] = blob_id

	def clean_str(self):
		return "commit: " + hash_commit(self) + "\n" + "Date: " + get_time_stamp(self.time_stamp) + "\n" + self.message + "\n" + str(self.blobs)

	def __str__(self):
		return "Date: " + get_time_stamp(self.time_stamp) + "\n\n\t" + self.message + "\n" + str(self.blobs)