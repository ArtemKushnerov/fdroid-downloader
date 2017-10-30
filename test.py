import os
import subprocess


gradle_executable_path = 'c:\\Gradle\\gradle-2.14.1\\bin\\gradle'
package_path = 'anupam.acrylic'
os.chdir(package_path)
try:
    out = subprocess.check_output(f'{gradle_executable_path} assembleDebug', shell=True, stderr=subprocess.STDOUT, timeout=20*60)
    print(out.decode('utf-8'))
except subprocess.CalledProcessError as e:
    print(e.output.decode('utf-8'))
except subprocess.TimeoutExpired as e:
    print('Compilation took more that 5 sec')


