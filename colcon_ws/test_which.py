import shutil
import time
t = time.time()
shutil.which('xacro')
print(f"Time: {time.time() - t}")
