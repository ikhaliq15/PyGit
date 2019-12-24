import sys
import os

import file_utils
from commits import *
from res_strs import *
from hash_utils import *

class Command:

	command_map = {
					"init": lambda: InitCommand,
					"add": lambda: AddCommand,
					"commit": lambda: CommitCommand,
					"rm": lambda: RemoveCommand,
					"log": lambda: LogCommand,
					"global-log": lambda: GlobalLogCommand,
					"find": lambda: FindCommand,
					"status": lambda: StatusCommand,
					"checkout": lambda: CheckoutSpliiterCommand,
					"branch": lambda: BranchCommand,
					"rm-branch": lambda: RemoveBranchCommand,
					"reset": lambda: ResetCommand,
					"merge": lambda: MergeCommand,
				}

	def get_command(command):
		return Command.command_map[command]()

	def check_args_count(self, args):
		if self.arg_count != len(args):
			print(ErrorMessages.invalid_parameters)
			sys.exit(0)

	def require_initialized(self):
		if not file_utils.is_initialized():
			print(ErrorMessages.non_initialized_dir)
			sys.exit(0)

class InitCommand(Command):
	arg_count = 0

	def run(self, args):
		self.check_args_count(args)

		if file_utils.is_initialized():
			print(ErrorMessages.already_initialized_dir)
			sys.exit(0)

		file_utils.initialize_git_dir()

class AddCommand(Command):
	arg_count = 1

	def run(self, args):
		self.check_args_count(args)
		self.require_initialized()

		file = args[0]

		if not file_utils.file_exists(file):
			print(ErrorMessages.add_file_not_found)
			sys.exit(0)

		current_commit = file_utils.read_object(file_utils.read_head_file())
		if file in current_commit.blobs and current_commit.blobs[file] == hash_file(file):
			file_utils.unstage_file(file)
		else:
			file_utils.stage_file(file)

		if file in file_utils.get_marked_for_remove():
			file_utils.unmark_for_remove(file)

class CommitCommand(Command):
	arg_count = 1

	def run(self, args):
		self.check_args_count(args)
		self.require_initialized()

		commit_message = args[0]
		if commit_message == "":
			print(ErrorMessages.invalid_commit_message)
			sys.exit(0)

		current_commit = file_utils.read_object(file_utils.read_head_file())
		new_commit = Commit(msg=args[0], parent=file_utils.read_head_file())
		marked_rm_files = file_utils.get_marked_for_remove()

		for blob in current_commit.blobs:
			new_commit.blobs[blob] = current_commit.blobs[blob]

		for file in os.listdir(file_utils.get_staging_dir()):
			filename = os.fsdecode(file)
			new_commit.add_file(filename)

		for file in marked_rm_files:
			if file in new_commit.blobs:
				del new_commit.blobs[file]

		if current_commit.blobs == new_commit.blobs:
			print(ErrorMessages.no_new_changes)
			sys.exit(0)

		file_utils.clear_stage_dir()
		file_utils.clear_marked_for_remove()
		file_utils.write_commit(new_commit)
		file_utils.add_commit_to_head(new_commit)

class RemoveCommand(Command):
	arg_count = 1

	def run(self, args):
		self.check_args_count(args)
		self.require_initialized()

		filename = args[0]

		is_staged = file_utils.is_staged(filename)
		file_utils.unstage_file(filename)

		current_commit = file_utils.read_object(file_utils.read_head_file())
		is_tracked = filename in current_commit.blobs

		if is_tracked:
			file_utils.mark_for_remove(filename)
			os.remove(filename)

		if not (is_tracked or is_staged):
			print(ErrorMessages.no_reason_to_remove)
			sys.exit(0)

class LogCommand(Command):
	arg_count = 0

	def run(self, args):
		self.check_args_count(args)
		self.require_initialized()

		current_commit = file_utils.read_object(file_utils.read_head_file())

		while current_commit is not Commit.empty:
			print("===")
			print(current_commit.clean_str(), end="\n")
			print("")
			current_commit = file_utils.read_object(current_commit.parent)

class GlobalLogCommand(Command):
	arg_count = 0

	def run(self, args):
		self.check_args_count(args)
		self.require_initialized()

		printed_commits = []

		commits = file_utils.find_all_commits()

		for commit in commits:
			print("===")
			print(commit.clean_str(), end="\n")
			print("")


class FindCommand(Command):
	arg_count = 1

	def run(self, args):
		self.check_args_count(args)
		self.require_initialized()

		search_query = args[0]

		searched_commits = []
		commits = file_utils.find_all_commits()

		found = False
		for commit in commits:
			if commit.message == search_query:
				found = True
				print(hash_commit(commit))

		if not found:
			print(ErrorMessages.found_no_commits)
			sys.exit(0)

class StatusCommand(Command):
	arg_count = 0

	def run(self, args):
		self.check_args_count(args)
		self.require_initialized()

		staged = os.listdir(file_utils.get_staging_dir())
		removed = file_utils.get_marked_for_remove()
		current_branch_name = file_utils.get_current_branch()
		branches = file_utils.get_branch_names()
		sorted_branch_names = branches.sort()
		current_commit = file_utils.read_object(file_utils.read_head_file())

		print("=== Branches ===")
		for branch in branches:
			if branch == current_branch_name:
				print("*", end="")
			print(branch)
		print("\n=== Staged Files ===")
		for file in staged:
			print(file)
		print("\n=== Removed Files ===")
		for file in removed:
			print(file)
		print("\n=== Modifications Not Staged For Commit ===")
		for file in current_commit.blobs:
			if not os.path.exists(file) and not os.path.isdir(file) and file not in removed:
				print(file, "(deleted)")
			elif file in staged and hash_file(file) != hash_file(os.path.join(file_utils.get_staging_dir(), file)):
				print(file, "(modified)")
			elif file not in staged and file not in removed and hash_file(file) != current_commit.blobs[file]:
				print(file, "(modified)")
		print("\n=== Untracked Files ===")
		for file in os.listdir(os.getcwd()):
			if not os.path.isdir(file) and file not in staged and file not in current_commit.blobs:
				print(file)

class CheckoutSpliiterCommand(Command):
	arg_count = 0 # will be handled in splitter

	def run(self, args):
		self.require_initialized()

		if len(args) == 1:
			CheckoutBranchCommand().run(args)
		elif len(args) == 2 and args[0] == "--":
			LastCommitCheckoutCommand().run(args)
		elif len(args) == 3 and args[1] == "--":
			AnyCommitCheckoutCommand().run(args)
		else:
			print(ErrorMessages.invalid_parameters)
			sys.exit(0)

class LastCommitCheckoutCommand(Command):
	arg_count = 2

	def run(self, args):
		self.check_args_count(args)
		self.require_initialized()

		filename = args[1]
		current_commit = file_utils.read_object(file_utils.read_head_file())

		if filename not in current_commit.blobs:
			print(ErrorMessages.checkout_no_file)
			sys.exit(0)

		file = open(filename, "w")
		file.write(file_utils.read_object(current_commit.blobs[filename]))
		file.close()

class AnyCommitCheckoutCommand(Command):
	arg_count = 3

	def run(self, args):
		self.check_args_count(args)
		self.require_initialized()

		filename = args[2]
		commit_id = args[0]
		current_commit = file_utils.read_object(file_utils.find_commit(commit_id))

		if filename not in current_commit.blobs:
			print(ErrorMessages.checkout_no_file)
			sys.exit(0)

		file = open(filename, "w")
		file.write(file_utils.read_object(current_commit.blobs[filename]))
		file.close()

class CheckoutBranchCommand(Command):
	arg_count = 1

	def run(self, args):
		self.check_args_count(args)
		self.require_initialized()

		branch_name = args[0]

		if not file_utils.exists_branch(branch_name):
			print(ErrorMessages.branch_not_found)
			sys.exit(0)

		old_commit = file_utils.read_object(file_utils.read_head_file())
		new_commit = file_utils.read_object(file_utils.get_head_for_branch(branch_name))

		current_branch_name = file_utils.get_current_branch()

		if branch_name == current_branch_name:
			print(ErrorMessages.already_in_branch)
			sys.exit(0)

		removed = file_utils.get_marked_for_remove()

		for filename in new_commit.blobs:
			if file_utils.file_exists(filename) and not (file_utils.is_staged(filename) or filename in removed or filename in old_commit.blobs):
				print(ErrorMessages.checkout_warning)
				sys.exit(0)

		for filename in new_commit.blobs:
			file = open(filename, "w")
			file.write(file_utils.read_object(new_commit.blobs[filename]))
			file.close()

		for blob in old_commit.blobs:
			if blob not in new_commit.blobs:
				if file_utils.file_exists(blob):
					os.remove(blob)

		file_utils.write_head(branch_name)

		file_utils.clear_stage_dir()
		file_utils.clear_marked_for_remove()


class BranchCommand(Command):
	arg_count = 1

	def run(self, args):
		self.check_args_count(args)
		self.require_initialized()

		branch_name = args[0]

		if file_utils.exists_branch(branch_name):
			print(ErrorMessages.branch_already_exists)
			sys.exit(0)

		current_commit = file_utils.read_head_file()
		file_utils.write_branch(branch_name, current_commit)

class RemoveBranchCommand(Command):
	arg_count = 1

	def run(self, args):
		self.check_args_count(args)
		self.require_initialized()

		branch_name = args[0]
		current_branch_name = file_utils.get_current_branch()

		if branch_name == current_branch_name:
			print(ErrorMessages.removing_current_branch)
			sys.exit(0)

		if not file_utils.exists_branch(branch_name):
			print(ErrorMessages.branch_not_found_rm)
			sys.exit(0)
			
		file_utils.remove_branch(branch_name)

class ResetCommand(Command):
	arg_count = 1

	def run(self, args):
		self.check_args_count(args)
		self.require_initialized()

		commit_id = args[0]
		old_commit = file_utils.read_object(file_utils.read_head_file())
		new_commit = file_utils.read_object(file_utils.find_commit(commit_id))

		removed = file_utils.get_marked_for_remove()

		for filename in new_commit.blobs:
			if file_utils.file_exists(filename) and not (file_utils.is_staged(filename) or filename in removed or filename in old_commit.blobs):
				print(ErrorMessages.checkout_warning)
				sys.exit(0)

		for filename in new_commit.blobs:
			file = open(filename, "w")
			file.write(file_utils.read_object(new_commit.blobs[filename]))
			file.close()

		for blob in old_commit.blobs:
			if blob not in new_commit.blobs:
				if file_utils.file_exists(blob):
					os.remove(blob)

		file_utils.add_commit_to_head(new_commit)
		file_utils.clear_stage_dir()
		file_utils.clear_marked_for_remove()

class MergeCommand(Command):
	arg_count = 1

	def run(self, args):
		self.check_args_count(args)
		self.require_initialized()

		other_branch_name = args[0]
		current_branch_name = file_utils.get_current_branch()

		staged, removed = os.listdir(file_utils.get_staging_dir()), file_utils.get_marked_for_remove()

		if len(staged) != 0 or len(removed) != 0:
			print(ErrorMessages.uncommitted_changes)
			sys.exit(0)

		if not file_utils.exists_branch(other_branch_name):
			print(ErrorMessages.branch_not_found_rm)
			sys.exit(0)

		if current_branch_name == other_branch_name:
			print(ErrorMessages.merge_with_self)
			sys.exit(0)

		current_branch_head = file_utils.read_object(file_utils.get_head_for_branch(current_branch_name))
		given_branch_head = file_utils.read_object(file_utils.get_head_for_branch(other_branch_name))

		ancestors_of_current = []
		while current_branch_head is not Commit.empty:
			ancestors_of_current.append(hash_commit(current_branch_head))
			current_branch_head = file_utils.read_object(current_branch_head.parent)

		ancestors_of_given = []
		while given_branch_head is not Commit.empty:
			ancestors_of_given.append(hash_commit(given_branch_head))
			given_branch_head = file_utils.read_object(given_branch_head.parent)

		split_point = ""
		for commit in ancestors_of_given:
			if commit in ancestors_of_current:
				split_point = commit
				break

		current_branch_head = file_utils.read_object(file_utils.get_head_for_branch(current_branch_name))
		given_branch_head = file_utils.read_object(file_utils.get_head_for_branch(other_branch_name))
		split_point_commit = file_utils.read_object(split_point)

		untracked_files = []
		for untracked_file in os.listdir(os.getcwd()):
			if not os.path.isdir(untracked_file) and untracked_file not in current_branch_head.blobs:
				untracked_files.append(untracked_file)

		for file in split_point_commit.blobs:
			if file not in untracked_files:
				continue
			current_ver_modified = file not in current_branch_head.blobs or split_point_commit.blobs[file] != current_branch_head.blobs[file]
			given_ver_modified = file not in given_branch_head.blobs or split_point_commit.blobs[file] != given_branch_head.blobs[file]

			if given_ver_modified and not current_ver_modified:
				if file in given_branch_head.blobs:
					print(ErrorMessages.checkout_warning)
					sys.exit(0)
				else:
					print(ErrorMessages.checkout_warning)
					sys.exit(0)
			elif given_ver_modified and current_ver_modified:
				if (file not in current_branch_head.blobs and file not in given_branch_head.blobs) or (given_branch_head.blobs[file] == current_branch_head.blobs[file]):
					continue
				else:
					print(ErrorMessages.checkout_warning)
					sys.exit(0)

		for file in given_branch_head.blobs:
			if file not in untracked_files:
				continue
			if file not in split_point_commit.blobs and file not in current_branch_head.blobs:
				print(ErrorMessages.checkout_warning)
				sys.exit(0)

		if split_point == hash_commit(given_branch_head):
			print("Given branch is an ancestor of the current branch.")
			sys.exit(0)

		if split_point == hash_commit(current_branch_head):
			file_utils.write_head(other_branch_name)
			print("Current branch fast-forwarded.")
			sys.exit(0)

		was_merge_conflict = False

		for file in split_point_commit.blobs:
			current_ver_modified = file not in current_branch_head.blobs or split_point_commit.blobs[file] != current_branch_head.blobs[file]
			given_ver_modified = file not in given_branch_head.blobs or split_point_commit.blobs[file] != given_branch_head.blobs[file]

			if given_ver_modified and not current_ver_modified:
				if file in given_branch_head.blobs:
					f = open(file, "w")
					f.write(file_utils.read_object(given_branch_head.blobs[file]))
					f.close()
					file_utils.stage_file(file)
					continue
				else:
					os.remove(file)
					file_utils.mark_for_remove(file)
			elif not given_ver_modified and current_ver_modified:
				continue
			elif given_ver_modified and current_ver_modified:
				if file not in current_branch_head.blobs and file in given_branch_head.blobs:
					current_file_content = "" if file not in current_branch_head.blobs else file_utils.read_object(current_branch_head.blobs[file])
					given_file_content = "" if file not in given_branch_head.blobs else file_utils.read_object(given_branch_head.blobs[file])
					f = open(file, "w")
					f.write("<<<<<<< HEAD\n" + current_file_content + "=======\n" + given_file_content + ">>>>>>>\n")
					f.close()
					file_utils.stage_file(file)
					was_merge_conflict = True
				elif file not in given_branch_head.blobs and file in current_branch_head.blobs:
					current_file_content = "" if file not in current_branch_head.blobs else file_utils.read_object(current_branch_head.blobs[file])
					given_file_content = "" if file not in given_branch_head.blobs else file_utils.read_object(given_branch_head.blobs[file])
					f = open(file, "w")
					f.write("<<<<<<< HEAD\n" + current_file_content + "=======\n" + given_file_content + ">>>>>>>\n")
					f.close()
					file_utils.stage_file(file)
					was_merge_conflict = True
				elif (file in current_branch_head.blobs != file in given_branch_head.blobs) or (given_branch_head.blobs[file] != current_branch_head.blobs[file]):
					current_file_content = "" if file not in current_branch_head.blobs else file_utils.read_object(current_branch_head.blobs[file])
					given_file_content = "" if file not in given_branch_head.blobs else file_utils.read_object(given_branch_head.blobs[file])
					f = open(file, "w")
					f.write("<<<<<<< HEAD\n" + current_file_content + "=======\n" + given_file_content + ">>>>>>>\n")
					f.close()
					file_utils.stage_file(file)
					was_merge_conflict = True

		for file in given_branch_head.blobs:
			if file not in split_point_commit.blobs and file not in current_branch_head.blobs:
				f = open(file, "w")
				f.write(file_utils.read_object(given_branch_head.blobs[file]))
				f.close()
				file_utils.stage_file(file)
				continue

		CommitCommand().run(["Merged " + other_branch_name + " into " + current_branch_name + "."])

		if was_merge_conflict:
			print("Encountered a merge conflict.")