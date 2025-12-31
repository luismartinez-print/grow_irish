import pandas as pd
import os
import googlemaps

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

API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY")



ORIGIN = "University of Notre Dame, South Bend, IN"
DESTINATION = 'NC State University, Raleigh, NC'

gmaps = googlemaps.Client(key = '#####') ### Add Keys

try:
    matrix_result = gmaps.distance_matrix(
        origins=[ORIGIN],
        destinations=[DESTINATION],
        mode='driving'
    )

        # 4. Extract the result
        # The result is a dictionary/JSON structure. We need to navigate to the 'rows' -> 'elements'
    element = matrix_result['rows'][0]['elements'][0]

    if element['status'] == 'OK':
        distance = element['distance']['text']
        duration = element['duration']['text']
            
        print(f"--- Distance Matrix Result (Driving) ---")
        print(f"Origin:      {ORIGIN}")
        print(f"Destination: {DESTINATION}")
        print(f"Distance:    **{distance}**")
        print(f"Duration:    **{duration}**")
        print("--------------------------------------")
    elif element['status'] == 'ZERO_RESULTS':
        print(f"Error: Could not find a route between {ORIGIN} and {DESTINATION}.")
    else:
        print(f"API Error: {element['status']}")

except Exception as e:
    print(f"An unexpected error occurred: {e}")


df = pd.read_csv("C:/Users/luism/Downloads/Games_data.csv")

df.rename(columns={"Season Type": "Season_Type"}, inplace= True)

df.rename(columns={"Home/Away": "home"}, inplace= True)

df['home'] = df['home'].apply(lambda x: 1 if x == 'Home' else 0)

df.to_csv("games.csv", index=False)