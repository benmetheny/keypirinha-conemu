import os
path_dirs = [
            os.path.expandvars(p.strip())
                for p in os.getenv("PATH", "").split(";") if p.strip() ]

for path_dir in path_dirs:
    exe_file = os.path.join(path_dir, "ConEmuC.exe")
    if os.path.exists(exe_file):
        #self.info("ConEmu plugin located base directory at: " + path_dir)
        print(path_dir)