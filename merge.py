#!/usr/bin/env python2

import subprocess

def bash_command(cmd):
	subprocess.Popen(cmd, shell=True, executable='/bin/bash')

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
	unmerged = [i for i in open("unmerged.txt", "rb").read().split("\n") if i]
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

	s = " ".join(to_ours)
	buf += "for i in %s; do git checkout --ours $i; done; for i in %s; do git add $i; done; " % (s, s)
	s = " ".join(to_theirs)
	buf += "for i in %s; do git checkout --theirs $i; done; for i in %s; do git add $i; done; " % (s, s)
	if not unmerged:
		buf += "git commit --no-edit && "
	else:
		buf += "true && "

	s = "\n".join(unmerged)
	open("unmerged_new.txt", "w").write(s)
	buf += "mv unmerged_new.txt unmerged.txt"
	print(buf)
	if not unmerged:
		bash_command(buf)
	print(s)
	#buf += "echo %s"

if __name__ == "__main__":
	main()
