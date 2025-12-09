import pandas as pd

df = pd.read_html("https://fightingirish.com/sports/mhockey/roster/")[0]

df.info()


cleaned_df = df[['Name', 'POSITION', 'Height', 'Class', 'Weight']].copy()


cleaned_df.info()

cleaned_df['weight'] = cleaned_df['Weight'].apply(lambda x: x[:3])

cleaned_df['inches'] = cleaned_df['Height'].apply(lambda x: x[2])



cols = ['weight']

for col in cols:
    cleaned_df[col] = cleaned_df[col].astype(int)


cleaned_df.info()


cleaned_df['height'] = (cleaned_df['feet'] * 12) + cleaned_df['inches']

cleaned_df

cleaned_df.drop(['feet', 'Weight'], axis = 1, inplace = True)



hockey = pd.read_csv("m_hockey1.csv")

cleaned_df.to_csv('m_hockey1.csv', index=False)

hockey['weight'] = cleaned_df['weight']

hockey
hockey.to_csv('m_hockey1.csv', index=False)