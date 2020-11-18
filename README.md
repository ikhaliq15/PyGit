# PyGit
A Python implementation of the version control software [Git](https://en.wikipedia.org/wiki/Git).

## Commands Implemented

| Command | Usage | Description |
| :---: | :---: | :---: |
| init | `python3 main.py init` | Creates a new Gitlet version-control system in the current directory. |
| add | `python3 main.py add [file name]` | Adds a copy of the file as it currently exists to the staging area. |
| commit | `python3 main.py commit [message]` | Saves a snapshot of certain files in the current commit and staging area so they can be restored at a later time, creating a new commit. |
| rm | `python3 main.py rm [file name]` | Unstage the file if it is currently staged for addition. If the file is tracked in the current commit, stage it for removal and remove the file from the working directory if the user has not already done so. |
| log | `python3 main.py log` | Starting at the current head commit, display information about each commit backwards along the commit tree until the initial commit. |
| global-log | `python3 main.py global-log` | Like log, except displays information about all commits ever made. No particular order is guranteed. |
| find | `python3 main.py find [commit message]` | Prints out the ids of all commits that have the given commit message, one per line |
| status | `python3 main.py status` | Displays what branches currently exist, and marks the current branch with a *. Also displays what files have been staged for addition or removal. |
| checkout | `python3 main.py checkout -- [file name]` | Takes the version of the file as it exists in the head commit, the front of the current branch, and puts it in the working directory, overwriting the version of the file that's already there if there is one. The new version of the file is not staged. |
| checkout | `python3 main.py checkout [commit id] -- [file name]` | Takes the version of the file as it exists in the commit with the given id, and puts it in the working directory, overwriting the version of the file that's already there if there is one. The new version of the file is not staged. |
| checkout | `python3 main.py checkout [branch name]` | Takes all files in the commit at the head of the given branch, and puts them in the working directory, overwriting the versions of the files that are already there if they exist. Also, at the end of this command, the given branch will now be considered the current branch. |
| branch | `python3 main.py branch [branch name]` | Creates a new branch with the given name. |
| rm-branch | `python3 main.py rm-branch [branch name]` | Deletes the branch with the given name. |
| reset | `python3 main.py reset [commit id]` | Checks out all the files tracked by the given commit. Removes tracked files that are not present in that commit. Also moves the current branch's head to that commit node |
| merge | `python3 main.py merge [branch name]` | Merges files from the given branch into the current branch. |

## Inspiration
Original project from the Spring 2020 Iteration of CS61B with Professor Hilfinger. Original project written in Java.
Refer to this site for further details on the project. https://inst.eecs.berkeley.edu/~cs61b/sp20/materials/proj/proj3/
