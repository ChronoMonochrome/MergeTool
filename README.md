<h1> MergeTool: a simple git merge tool. </h1>

<h2><b>
Usage:
</b></h2>
<pre>
 ./merge.py [flags]
</pre>

<h2><b>
Flags:
</b></h2>
<pre>
 -d, --dry-run    - don't actually do anything, just display what would happen
 -h, --help       - show this help message
 -n, --no-prompts - don't prompt for conflicts resolution
 -q, --quiet      - run quietly
 -v, --verbose    - verbose output.
</pre>

The tool will do `git checkout --ours` (`git checkout --theirs`)
for any unmerged files/directories specified in ours.txt (theirs.txt).

Note that flags passing like "-dv" is not supported, use "-d -v" instead.
