import pandas as pd

df = pd.read_html("https://fightingirish.com/sports/wbball/roster/")[0]

df.info()

cleaned_df = df[['Name', 'POSITION', 'Height', 'Class']].copy()


cleaned_df.info()

cleaned_df['feet'] = cleaned_df['Height'].apply(lambda x: x[0])

cleaned_df['inches'] = cleaned_df['Height'].apply(lambda x: x[2])



cols = ['feet', 'inches']

for col in cols:
    cleaned_df[col] = cleaned_df[col].astype(int)


cleaned_df.info()


cleaned_df['height'] = (cleaned_df['feet'] * 12) + cleaned_df['inches']

cleaned_df

cleaned_df.drop(['feet', 'inches'], axis = 1, inplace = True)

cleaned_df.to_csv('w_basketball1.csv', index=False)