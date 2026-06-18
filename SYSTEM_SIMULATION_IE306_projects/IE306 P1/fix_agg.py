with open('generate_q2_excel.py', 'r', encoding='utf-8') as f:
    text2 = f.read()

target = 'cell_o.font = Font(size=9, color="595959")'
agg_logic = '''
    sim_end = max(sim_end, trt_end)
    sum_sys_times += sys_time
    if doctor == "D1":
        d1_busy += trt_dur
        d1_count += 1
    else:
        d2_busy += trt_dur
        d2_count += 1
'''

if target in text2:
    if "sim_end = max(sim_end, trt_end)" not in text2:
        text2 = text2.replace(target, target + "\n" + agg_logic)
        print("Found and replaced target logic!")
    else:
        print("Logic already exists.")
else:
    print("Target not found.")

with open('generate_q2_excel.py', 'w', encoding='utf-8') as f:
    f.write(text2)
