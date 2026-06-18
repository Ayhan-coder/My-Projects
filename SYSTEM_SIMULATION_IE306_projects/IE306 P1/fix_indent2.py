with open('generate_q2_excel.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "ws['D55'] =" in line:
        lines[i] = "ws['D55'] = '16.51 min (time with exactly 1 in queue) / 128.56 min (sim end)  tracked from event table'\n"

with open('generate_q2_excel.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
