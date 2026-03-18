import os
import subprocess
import sys

num_tests = round(len(os.listdir("example_tests"))/2)
num_success = 0

for i in range(num_tests):
    inpf = open("example_tests/example_input_" + str(i+1), "r")
    inp = inpf.read().strip()
    inpf.close()
    outf = open("example_tests/example_output_" + str(i+1), "r")
    out = outf.read().strip()
    outf.close()
    try:
        # try python3 instead of python, if it does not work
        res = subprocess.run([sys.executable, "Main.py"], input=inp, capture_output=True, text=True, timeout=10)
        st_out = res.stdout.strip()
        if res.stderr:
            print("Test %d failed with the following error:" % (i+1))
            print(res.stderr)
        elif not st_out == out:
            print("Test %d failed with invalid output:" % (i+1))
            print("The input:\n"+inp)
            print("Your output:\n"+st_out)
            print("Correct output:\n"+out)
        else:
            print("Test %d was a success!" % (i+1))
            print("The input:\n"+inp)
            print("Your output:\n"+st_out)
            print("Correct output:\n"+out)
            num_success += 1
    except subprocess.TimeoutExpired:
        print("Test %d took too long to execute. (>10 seconds)" % (i+1))
    print("-" * 50)
print("%d out of %d tests were successful." % (num_success, num_tests))