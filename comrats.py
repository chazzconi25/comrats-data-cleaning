import pandas
import numpy
import datetime

comratsValuesDict = { 2019 : 12.30, 2020 : 12.40, 2021 : 12.90, 2022 : 13.55, 2023 : 15.00}

# Function to change dates from MMDDYY to YYMMDD 
def fixDates(x):
    x = str(x)
    return x[4:6] + x[:4] + x[10:] + x[6:10]

# This even works in the edgecase that somone took over two years of continuous leave
def total(start, end):
    total = 0
    while start.year != end.year:
        delta = (datetime.datetime(start.year,12,31) - start).days + 1
        total += comratsValuesDict[int(start.year)]*delta
        start = datetime.datetime(start.year + 1,1,1)
    total += comratsValuesDict[int(start.year)]*((end - start).days +1)
    return total



# Read in input for csv filename
# csvFile = input("Please input the name of comrats csv file: ")

# Read in raw data csv to dataframe
df = pandas.read_csv("COMRATS.csv", dtype=str)

# Clean data by removing plebes and changing all last names to uppercase
df.rename(columns={df.columns[1]:'email', df.columns[2]:'last', df.columns[4]:'social'}, inplace = True)
df = df[df['email'].str[1:3] != '26']
df['last'] = df['last'].str.upper()
dfClean = df[['last']].copy()

# Add columns representing misssing dates and validity
missingInd = 1
validInd = 1
for columnName in df.columns:
    if columnName.find('Please enter the ') != -1:
        dfClean['missing'+str(missingInd)] = df[columnName]
        missingInd += 1
    if columnName.find('Were you properly signed') != -1:
        dfClean['valid'+str(validInd)] = df[columnName]
        validInd += 1

# The data set contains 17 missing date columns but only 16 vaild columns
# adding this column to keep the df balanced
dfClean['valid17'] = 'N/A'

# The last valid and missing columns are out of order in the csv, reoganizing them
# here
dfCleanTemp = df[['last']].copy()
for count in range(1,missingInd-1):
    dfCleanTemp['missing'+str(count)] = dfClean[['missing'+str(count)]]
    dfCleanTemp['valid'+str(count)] = dfClean[['valid'+str(count)]]
dfClean = dfCleanTemp

# Remove extra chars from dates and make dates into format YYMMDD 
dfClean = dfClean.replace({'/','-'},['']*2, regex=True)
dfClean.iloc[:,range(1,len(dfClean.columns),2)] = dfClean.iloc[:,range(1,len(dfClean.columns),2)].applymap(fixDates)

# Add SSNs to dfClean
dfClean.insert(loc=0,
          column='social',
          value=df['social'])
print(dfClean)
# Create a new dataframe to store all last names, formatted missing dates, and SSNs
allDates = pandas.DataFrame (columns=['last','date'])
# index though cleaned data and make dataframes for each mid with their missing dates and SSN
for index in range(len(dfClean.index)):
    last = [str(dfClean['last'].values[34])]*16
    social = [str(dfClean['social'].values[34])]*16
    # this needs to be cleaned up - sorry this is confusing to me, not sure why I did it like this
    missing = dfClean.iloc[34,range(2,len(dfClean.columns),2)].values
    valid = dfClean.iloc[34,range(3,len(dfClean.columns),2)].values
    oneMid = pandas.DataFrame ({'last':last, 'missing':missing, 'valid':valid, 'social':social})
    # remove all invalid leave periods 
    oneMid = oneMid[oneMid['valid'] == 'Yes']
    oneMid = oneMid[oneMid['missing'] != 'nan']

    oneMid['start'] = pandas.to_datetime(oneMid['missing'].str[:6], format="%y%m%d")
    oneMid['end'] = pandas.to_datetime(oneMid['missing'].str[6:], format="%y%m%d")
    oneMid['total'] = oneMid.apply(lambda x: total(x['start'], x['end']), axis=1)
    # add formatted date column
    
    oneMid['date'] = "4003" + oneMid['social'] + oneMid['last'].str[0:6] + oneMid['missing']
    # Add last name and dates of this mid to full list
    allDates = pandas.concat([allDates, oneMid[['last','date']]])


# Create two data frames for different last name sizes
shortLN = allDates[allDates['last'].str.len() < 5]
longLN = allDates[allDates['last'].str.len() >= 5]

# Create csv files with only dates from dataframes
#shortLN['date'].to_csv('shortLNCOMRATS.csv', header = False, index = False)
#longLN['date'].to_csv('longLNCOMRATS.csv', header = False, index = False)

# Print dataframes to console
#print(shortLN)
#print(longLN)

