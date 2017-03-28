import holidays

for year in range(2016,1880,-1):
   for date, name in holidays.Canada(state='ON', years=year).items():
      if name == 'Victoria Day':
          print(date, name)


for date, name in holidays.Canada(state='ON', years=2016, observed=False).items():
    print(date, name)
