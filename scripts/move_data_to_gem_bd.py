import subprocess
p = subprocess.Popen(["scp", "my_file.txt", "username@server:path"])
sts = os.waitpid(p.pid, 0)