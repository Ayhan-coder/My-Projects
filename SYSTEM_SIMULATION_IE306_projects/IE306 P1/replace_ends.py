import re

with open('generate_q1_excel.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace("ws['B47'] = 11", "ws['B47'] = 18")
text = text.replace("ws['B48'] = 11 / 10", "ws['B48'] = 18 / 10")
text = text.replace("ws['B51'] = 140", "ws['B51'] = 33")

with open('generate_q1_excel.py', 'w', encoding='utf-8') as f:
    f.write(text)
print('Q1 end substituted.')


with open('generate_q2_excel.py', 'r', encoding='utf-8') as f:
    text2 = f.read()

# Add accumulators right before loop
loop_start = "for i, (rn_r, rn_a, rn_t) in enumerate(patient_inputs):"
accums = '''sim_end = 0
sum_sys_times = 0
d1_busy = 0
d2_busy = 0
d1_count = 0
d2_count = 0
'''
text2 = text2.replace(loop_start, accums + loop_start)

# Add accumulator logic right after loop content
cell_o_start = r"cell_o.font = Font(size=9, color=""595959"")"
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
text2 = text2.replace(cell_o_start, cell_o_start + "\n" + agg_logic)

# Since sim starts with Patient 0, D1 was busy for Patient 0
# Patient 0 trt_dur was 14.97 (10 + 10 * 0.497). Let's just adjust d1_busy later.

# Replace formulas
text2 = text2.replace('ws[\'B47\'] = f"=MAX(L{FIRST}:L{LAST})"', 'ws[\'B47\'] = sim_end')
text2 = text2.replace('ws[\'D47\'] = f"=MAX(L{FIRST}:L{LAST})"', 'ws[\'D47\'] = ""')
text2 = text2.replace('ws[\'B49\'] = f"=SUM(M{FIRST}:M{LAST})/10"', 'ws[\'B49\'] = sum_sys_times / 10')
text2 = text2.replace('ws[\'D49\'] = f"=SUM(M{FIRST}:M{LAST}) / 10   (sum of system times divided by 10 patients)"', 'ws[\'D49\'] = "sum of system times divided by 10 patients"')

text2 = text2.replace('ws[\'B50\'] = f"=D12+SUMIF(G{FIRST}:G{LAST},\\"D1\\",I{FIRST}:I{LAST})"', 'ws[\'B50\'] = 14.97 + d1_busy')
text2 = text2.replace('ws[\'D50\'] = "=D12 (Patient 0 trt) + SUMIF(Doctor,\\"D1\\",TrtDur)"', 'ws[\'D50\'] = "Patient 0 trt + SUMIF D1 TrtDur"')

text2 = text2.replace('ws[\'B51\'] = f"=SUMIF(G{FIRST}:G{LAST},\\"D2\\",I{FIRST}:I{LAST})"', 'ws[\'B51\'] = d2_busy')
text2 = text2.replace('ws[\'D51\'] = "=SUMIF(Doctor,\\"D2\\",TrtDur)"', 'ws[\'D51\'] = "SUMIF D2 TrtDur"')

text2 = text2.replace('ws[\'B52\'] = "=B50/B47"', 'ws[\'B52\'] = (14.97+d1_busy)/sim_end')
text2 = text2.replace('ws[\'D52\'] = "=D1 Busy / Sim End"', 'ws[\'D52\'] = "D1 Busy / Sim End"')

text2 = text2.replace('ws[\'B53\'] = "=B51/B47"', 'ws[\'B53\'] = d2_busy/sim_end')
text2 = text2.replace('ws[\'D53\'] = "=D2 Busy / Sim End"', 'ws[\'D53\'] = "D2 Busy / Sim End"')

text2 = text2.replace('ws[\'B56\'] = f"=SUM(M{FIRST}:M{LAST})"', 'ws[\'B56\'] = sum_sys_times')
text2 = text2.replace('ws[\'B57\'] = f\'=COUNTIF(G{FIRST}:G{LAST},"D1")\'', 'ws[\'B57\'] = d1_count')
text2 = text2.replace('ws[\'B58\'] = f\'=COUNTIF(G{FIRST}:G{LAST},"D2")\'', 'ws[\'B58\'] = d2_count')

with open('generate_q2_excel.py', 'w', encoding='utf-8') as f:
    f.write(text2)

print('Q2 end substituted.')
