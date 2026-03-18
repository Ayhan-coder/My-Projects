temperatures = list(map(int, input().split()))
# DO_NOT_EDIT_ANYTHING_ABOVE_THIS_LINE
fahrtemp = 0
daynum = 0
for temp in temperatures:
    fahrtemp = (9/5) * temp + 32
    daynum += 1
    if fahrtemp > 80:print("It's hot on day", daynum)

    elif fahrtemp < 60:print("It's cold on day", daynum)
    elif 80 >= fahrtemp >= 60:
        print("It's warm on day", daynum)
    else:
        continue
# DO_NOT_EDIT_ANYTHING_BELOW_THIS_LINE
