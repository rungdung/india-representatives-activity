import pandas as pd
from pandas import json_normalize
import os


parent_dir = "./json/Lok Sabha"
# Read all json in the directory
for file in os.listdir(parent_dir):
    name = file
    file = pd.read_json(parent_dir + "/" + file)

    # Explode activity
    # link to Name, constituency, state, party, start of term
    # loop over the each member

    debates_df = pd.DataFrame()
    questions_df = pd.DataFrame()
    bills_df = pd.DataFrame()

    for index, member in file.iterrows():
        activity_data = member["Activity"]

        # Debates
        debates_data = json_normalize(activity_data["Debates"])
        debates_df = pd.concat([debates_df, debates_data], ignore_index=True)

        # questions
        questions_data = json_normalize(activity_data["Questions"])
        questions_df = pd.concat([questions_df, questions_data], ignore_index=True)

        # bills
        bills_data = json_normalize(activity_data["Bills"])
        bills_df = pd.concat([bills_df, bills_data], ignore_index=True)

        # Meta data
        # Copy the same into multiple dfs
        debates_df["Name"] = questions_df["Name"] = bills_df["Name"] = member["Name"]
        debates_df["Constituency"] = questions_df["Constituency"] = bills_df[
            "Constituency"
        ] = member["Constituency"]
        debates_df["State"] = questions_df["State"] = bills_df["State"] = member[
            "State"
        ]
        debates_df["Party"] = questions_df["Party"] = bills_df["Party"] = member[
            "Party"
        ]

    # Write
    debates_df.to_json(f'{parent_dir}/{name.split(".")[0]}_Debates.json', index=False)
    bills_df.to_json(f'{parent_dir}/{name.split(".")[0]}_Bills.json', index=False)
    questions_df.to_json(
        f'{parent_dir}/{name.split(".")[0]}_Questions.json', index=False
    )
