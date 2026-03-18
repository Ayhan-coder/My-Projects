# System Calls Table Entries

http://ftp.tr.debian.org/debian/pool/main/l/linux/linux-headers-6.12.57+deb13-arm64_6.12.57-1_arm64.deb
http://ftp.tr.debian.org/debian/pool/main/l/linux/linux-headers-6.12.57+deb13-amd64_6.12.57-1_amd64.deb

Depending on your CPU's architecture download the correct deb file (Debian package). For Intel-AMD chipsets download amd64, for ARM chipsets download arm64.

After downloading, to extract the deb package, use this command:

dpkg -x <deb_package> <target_directory>

This will extract the package and place the contents to the target directory.

After extracting, check out those paths:

For ARM users:
<target_directory>/usr/src/linux-headers-6.12.57+deb13-arm64/arch/arm64/include/generated/asm/syscall_table_64.h

For INTEL-AMD users:
<target_directory>/usr/src/linux-headers-6.12.57+deb13-amd64/arch/x86/include/generated/asm/syscalls_64.h

Check out these files to match correct system calls to their numbers. Answers will change according to your CPU's architecture.

To go further, download the source code of the Linux, and check out the system call tables. This is optional.


# Sudoers File and Root Privileges

After installing a fresh OS, the user you created in installation may not have the permission of using 'sudo' command. Check it out by writing

sudo -s

If you see privilege messages, just switch the user to root. The command you should use is 'su'.

su
<asks_your_root_password>

Then write down this:

nano /etc/sudoers

This will open up the sudoers file, which determines whether a user or group can use the sudo features. Find the section under the comment "# User privilege specification", and add the line
<your_username> ALL=(ALL) NOPASSWD:ALL

After saving and exiting you can use the sudo command without any password requirements.

IMPORTANT:
Use this only in your personal computer in order to prevent security. It is your responsibility to save your personal data and protect root access. After adding yourself to the sudoers file with no password flag anyone can reach your user credentials can also reach root access without even knowing the root password. Again, it is your responsibility.


# For Q4

It will be better to explain what to do in this question.

Firstly, start the question by reading strace dump of the mentioned executables. Check out the differences between the empty and syscall_capture executables.  Then compare them and find out the additional system call entries of syscall_capture, and enter their system call numbers one by one, not their names. Find the numbers.


# Report Section

Submitting the project report is compulsory. Put your report in your project.
