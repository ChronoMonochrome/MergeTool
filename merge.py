#!/usr/bin/env python2

import os, sys
import subprocess

class bcolors:
	HEADER = '\033[35m'
	OKBLUE = '\033[34m'
	OKGREEN = '\033[32m'
	WARNING = '\033[33m'
	ERROR = '\033[31m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'

info_fmt = lambda s: "%s%s%s" % (bcolors.OKGREEN, s, bcolors.ENDC)
verbose_fmt = lambda s: s
warning_fmt = lambda s: "%s%s%s" % (bcolors.WARNING, s, bcolors.ENDC)
#info_fmt = warning_fmt = lambda s: s
error_fmt = lambda s: "%s%s%s" % (bcolors.ERROR, s, bcolors.ENDC)

EDITOR = "nano"
OURS_FILE = "ours.txt"
THEIRS_FILE = "theirs.txt"

DRYRUN = {"--dry-run": "-d"}
VERBOSE = {"--verbose": "-v"}
NOPROMPTS = {"--no-prompts": "-n"}
QUIET = {"--quiet": "-q"}
HELP = {"--help": "-h"}

valid_flags = [DRYRUN, VERBOSE, QUIET, HELP, NOPROMPTS]

def catch():
	__func__ = sys._getframe().f_back.f_code.co_name
	exc_type, exc_obj, exc_tb = sys.exc_info()
	print(error_fmt(u"%s: %s on line %d: %s" %(__func__, exc_type, exc_tb.tb_lineno, exc_obj)))

def bash_command(cmd):
	try:
		subprocess.Popen(cmd, shell = True, executable = '/bin/bash')
	except (subprocess.CalledProcessError, OSError) as e:
		catch()
		print(error_fmt("Can't execute requested command, exiting now"))
		exit()

def editor(files):
	try:
		for f in files:
			subprocess.call([EDITOR, f])
	except (subprocess.CalledProcessError, OSError) as e:
		catch()
		print(error_fmt("Can't start editor, exiting now"))
		exit()

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


The tool will do `git checkout --ours` (`git checkout --theirs`)
for any unmerged files/directories specified in ours.txt (theirs.txt).

Note that flags passing like "-dv" is not supported, use "-d -v" instead.'''

	if err_msg:
		buf += "\n\n" + err_msg

	print(buf)

	exit()

def main(flags = []):
	ours_list = []
	theirs_list = []

	if os.path.isfile(OURS_FILE):
		ours_list = [i for i in open(OURS_FILE, "r").read().split("\n") if i]
	else:
		print(warning_fmt("Warning: no ours file (%s) found" % OURS_FILE))

	if os.path.isfile(THEIRS_FILE):
		theirs_list = [i for i in open(THEIRS_FILE, "r").read().split("\n") if i]
	else:
		print(warning_fmt("Warning: no theirs file (%s) found" % THEIRS_FILE))

	try:
		unmerged = [i for i in subprocess.check_output("git diff --name-only --diff-filter=U".split(" ")).split("\n") if i]
	except (subprocess.CalledProcessError, OSError) as e:
		catch()
		exit()

	_flag_quiet = QUIET in flags
	_flag_verbose = VERBOSE in flags
	_flag_dryrun = DRYRUN in flags
	_flag_help = HELP in flags
	_flag_noprompts = NOPROMPTS in flags

	if _flag_help:
		usage()

	if not unmerged:
		if not _flag_quiet:
			print(warning_fmt("No files needs merging."))
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

	if not _flag_quiet:
		s = "\n\t" + "\n\t".join(to_ours)
		print(info_fmt("Resetting the following files to ours:") + "\n%s\n" % s)

	if to_ours:
		s = " ".join(to_ours)
		buf += "echo %s | xargs -L 1 git checkout --ours 2>/dev/null; echo %s | xargs -L 1 git add; " % (s, s)

	if not _flag_quiet:
		s = "\n\t" + "\n\t".join(to_theirs)
		print(info_fmt("Resetting the following files to theirs:") + "\n%s\n" % s)

	if to_theirs:
		s = " ".join(to_theirs)
		buf += "echo %s | xargs -L 1 git checkout --theirs 2>/dev/null; echo %s | xargs -L 1 git add; " % (s, s)

	if not unmerged:
		buf += "git commit --no-edit"


	if not _flag_dryrun:
		bash_command(buf)

	if _flag_verbose:
		print(verbose_fmt(buf))

	s = "\n\t" + "\n\t".join(unmerged)

	if not (_flag_dryrun or _flag_quiet) and unmerged:
		print(info_fmt("The following files needs merging:") + " \n%s\n" % s)
		try:
			_start_editor = "y"

			if not _flag_noprompts:
				_start_editor = raw_input(warning_fmt("Do you want to open these files in editor? [y]/n\n"))

			if _start_editor != "n":
				editor(unmerged)
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
