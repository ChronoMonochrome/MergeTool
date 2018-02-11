#!/usr/bin/env python2

import os, sys
import subprocess

DRYRUN = {"--dry-run": "-d"}
QUIET = {"--quiet": "-q"}

valid_flags = [DRYRUN, QUIET]

def bash_command(cmd):
	subprocess.Popen(cmd, shell=True, executable='/bin/bash')

def nano(files):
	for f in files:
		subprocess.call(['nano', f])
	#subprocess.Popen(cmd, shell=True, executable='/bin/nano')

def startswith_any(s, l):
	if not s:
		return ""

	for i in l:
		if not i:
			continue
		if s.startswith(i):
			return s
	return ""

def main(flags = []):
	ours_list = [i for i in open("ours.txt", "rb").read().split("\n") if i]
	theirs_list = [i for i in open("theirs.txt", "rb").read().split("\n") if i]
	unmerged = [i for i in subprocess.check_output("git diff --name-only --diff-filter=U".split(" ")).split("\n") if i]

	_flag_quiet = QUIET in flags
	_flag_dryrun = DRYRUN in flags

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
		buf += "echo %s | xargs -L 1 git checkout --ours; echo %s | xargs -L 1 git add; " % (s, s)

	if to_theirs:
		s = " ".join(to_theirs)
		buf += "echo %s | xargs -L 1 git checkout --theirs; echo %s | xargs -L 1 git add; " % (s, s)

	if not unmerged:
		buf += "git commit --no-edit"

	s = "\n\t" + "\n\t".join(unmerged)

	if not _flag_dryrun:
		bash_command(buf)
	elif not _flag_quiet:
		print(buf)


	if not (_flag_dryrun or _flag_quiet) and unmerged:
		print("The following files needs merging: \n%s\n" % s)
		try:
			_start_nano = raw_input("Do you want to open these files in nano? [y]/n\n")
			if _start_nano != "n":
				nano(unmerged)
		except KeyboardInterrupt:
			pass

if __name__ == "__main__":
	flags = []
	_args = sys.argv

	for flag in valid_flags:
		alias, key = list(flag.items())[0]
		if alias in _args or key in _args:
			flags.append(flag)

	main(flags)
