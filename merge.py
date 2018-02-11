#!/usr/bin/env python2

import subprocess

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

def main():
	ours_list = [i for i in open("ours.txt", "rb").read().split("\n") if i]
	theirs_list = [i for i in open("theirs.txt", "rb").read().split("\n") if i]
	unmerged = subprocess.check_output("git diff --name-only --diff-filter=U".split(" ")).split("\n")

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

	s = "\n".join(unmerged)
	print(buf)
	bash_command(buf)

	if unmerged:
		nano(unmerged)

if __name__ == "__main__":
	main()
