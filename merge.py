#!/usr/bin/env python2

import os, sys
import subprocess

class bcolors:
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	ERROR = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'

error_fmt = lambda s: "%s%s%s" % (bcolors.ERROR, s, bcolors.ENDC)

DRYRUN = {"--dry-run": "-d"}
VERBOSE = {"--verbose": "-v"}
NOPROMPTS = {"--no-prompts": "-n"}
QUIET = {"--quiet": "-q"}
HELP = {"--help": "-h"}

valid_flags = [DRYRUN, VERBOSE, QUIET, HELP, NOPROMPTS]

def bash_command(cmd):
	subprocess.Popen(cmd, shell=True, executable='/bin/bash')

def nano(files):
	for f in files:
		subprocess.call(['nano', f])

def startswith_any(s, l):
	if not s:
		return ""

	for i in l:
		if not i:
			continue
		if s.startswith(i):
			return s
	return ""

def usage(err_msg = ""):
	buf = \
'''MergeTool: a simple git merge tool.

Usage:


 ./merge.py [flags]


Flags:


 -d, --dry-run    - don't actually do anything, just display what would happen
 -h, --help       - show this help message
 -n, --no-prompts - don't prompt for conflicts resolution
 -q, --quiet      - run quietly
 -v, --verbose    - verbose output.


The tool will do `git checkout --ours' (`git checkout --theirs')
for any files/directories specified in ours.txt (theirs.txt).

Note that flags passing like "-dv" is not supported, use "-d -v" instead.%s'''

	if err_msg:
		buf %= ("\n\n" + err_msg)

	print(buf)

	exit()

def main(flags = []):
	ours_list = [i for i in open("ours.txt", "rb").read().split("\n") if i]
	theirs_list = [i for i in open("theirs.txt", "rb").read().split("\n") if i]
	unmerged = [i for i in subprocess.check_output("git diff --name-only --diff-filter=U".split(" ")).split("\n") if i]

	_flag_quiet = QUIET in flags
	_flag_verbose = VERBOSE in flags
	_flag_dryrun = DRYRUN in flags
	_flag_help = HELP in flags
	_flag_noprompts = NOPROMPTS in flags

	if _flag_help:
		usage()

	if not unmerged:
		if not _flag_quiet:
			print("No files needs merging.")
		exit()

	to_ours, to_theirs = [], []
	for f in unmerged:
		if startswith_any(f, ours_list):
			to_ours.append(f)

	for i in to_ours:
		if i in unmerged:
			del unmerged[unmerged.index(i)]

	#print(unmerged)

	for f in unmerged:
		if startswith_any(f, theirs_list):
			to_theirs.append(f)

	for i in to_theirs:
		if i in unmerged:
			del unmerged[unmerged.index(i)]
	buf = ""

	if to_ours:
		s = " ".join(to_ours)
		buf += "echo %s | xargs -L 1 git checkout --ours 2>/dev/null; echo %s | xargs -L 1 git add; " % (s, s)
		if not _flag_quiet:
			s = "\n\t" + "\n\t".join(to_ours)
			print("Resetting the following files to ours:\n%s\n" % s)

	if to_theirs:
		s = " ".join(to_theirs)
		buf += "echo %s | xargs -L 1 git checkout --theirs 2>/dev/null; echo %s | xargs -L 1 git add; " % (s, s)
		if not _flag_quiet:
			s = "\n\t" + "\n\t".join(to_theirs)
			print("Resetting the following files to theirs:\n%s\n" % s)

	if not unmerged:
		buf += "git commit --no-edit"


	if not _flag_dryrun:
		bash_command(buf)

	if _flag_verbose:
		print(buf)

	s = "\n\t" + "\n\t".join(unmerged)

	if not (_flag_dryrun or _flag_quiet) and unmerged:
		print("The following files needs merging: \n%s\n" % s)
		try:
			_start_nano = "y"

			if not _flag_noprompts:
				_start_nano = raw_input("Do you want to open these files in nano? [y]/n\n")

			if _start_nano != "n":
				nano(unmerged)
		except KeyboardInterrupt:
			pass

if __name__ == "__main__":
	flags = []
	_args = sys.argv[1:]

	for arg in _args:
		arg_valid = False
		for flag in valid_flags:
			alias, key = list(flag.items())[0]
			if arg in [alias, key]:
				arg_valid = True
				flags.append(flag)
				break

		if not arg_valid:
			usage(error_fmt("Error: Unknown flag: %s" % arg))

	main(flags)
