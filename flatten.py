import csv
import glob
import inflect
import json
import logging
import os
import pandas as pd
import zipfile

from bs4 import BeautifulSoup

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ]
)

p = inflect.engine()

# Parse the HTML file
def read_html(file_content):
    try:
        soup = BeautifulSoup(file_content, 'html.parser')
    except:
        logging.error("Failed to parse HTML page for representative")
        raise

    return soup

# Extract the name of the representative
def get_name(soup):
    name = {}

    div = soup.find_all('div', class_='mp-name')[0]
    name["Name"] = div.get_text(strip=True)

    return name

# Extract basic information about the representative
def get_basic_info(soup):
    basicInfo = {}

    div = soup.find_all('div', class_='mp-basic-info')[0]
    for child_div in div:
        try:
            text = child_div.get_text(strip=True)
            key, value = text.split(':',  1)
            basicInfo[key.lstrip().rstrip()] = value.lstrip().rstrip()
        except:
            continue

    return basicInfo

# Extract personal profile of the representative
def get_personal_profile(soup):
    personalProfile = {}

    div = soup.find_all('div', class_='personal_profile_parent')[1]
    for child_div in div:
        try:
            text = child_div.get_text(strip=True)
            key, value = text.split(':',  1)
            personalProfile[key.lstrip().rstrip()] = value.lstrip().rstrip()
        except:
            continue

    return personalProfile

# Extract details about the representative
def get_representative(soup):
    representative = {}

    try:
        representative.update(get_name(soup))
        representative.update(get_basic_info(soup))
        representative.update(get_personal_profile(soup))
    except:
        logging.error("failed to extract information about the representative")
        raise

    return representative

# Parse the HTML table and return a DataFrame with table contents
def parse_table(table):
    try:
        headers = [th.text.strip() for th in table.find_all('th')]
        rows = table.find_all('tr')
        data = []
        for row in rows[1:]:  # skip the header row
            cols = row.find_all('td')
            data_dict = {headers[i]: cols[i].text.strip() for i in range(len(headers))}
            if row.find('a'):
                try:
                    data_dict["link"] = row.find('a').get('href')
                except:
                    logging.warn("No link found for row")
                    pass
            data.append(data_dict)
        return pd.DataFrame(data)
    except:
        logging.warn("could not parse table from html page for representative")
        raise

# Initialize list of table details in multiple dataFrame elements
def init_dataframes(soup):
    try:
        tables = soup.find_all('table', class_='views-table')
        dataFrames = []
        for table in tables:
            df = parse_table(table)
            if not df.empty:
                dataFrames.append(df)
        return dataFrames
    except:
        logging.error("Could not create dataframe for representative")
        raise

# Get legislative activity details from dataFrames and return a dictionary containing the details
def get_legislative_activity(dataFrames):
    try:
        details = {}
        dataFrameTypes = ["Attendance", "Debates", "Questions", "Bills"]
        for dataFrameType in dataFrameTypes:
            details[dataFrameType] = pd.DataFrame()
        for dataFrame in dataFrames:
            if "Attendance" in dataFrame.columns:
                details["Attendance"] = dataFrame
            if "Debate Type" in dataFrame.columns:
                details["Debates"] = dataFrame
            if "Ministry or Category" in dataFrame.columns:
                details["Questions"] = dataFrame
            if "Bill title" in dataFrame.columns:
                details["Bills"] = dataFrame
        return details
    except:
        logging.error("Failed to get representative details")
        raise

# Initialize a JSON for the representative
def init_json(representative, legislativeActivity):
    json = {}

    json["Name"] = representative["Name"]
    json["Constituency"] = representative["Constituency"]

    try:
        attendance_average = (legislativeActivity["Attendance"]["Attendance"].str.rstrip('%').astype(float) /  100).mean()
        json["Attendance"] = f"{attendance_average *  100:.2f}%"
    except:
        json["Attendance"] = ""
    json["Debates"] = len(legislativeActivity["Debates"])
    json["Questions"] = len(legislativeActivity["Questions"])
    json["Bills"] = len(legislativeActivity["Bills"])

    representative["State"] = representative["State"][:representative["State"].rfind("(") - 1]
    representative["Party"] = representative["Party"][:representative["Party"].rfind("(") - 1]
    json.update(representative)

    json["Activity"] = {}
    json["Activity"]["Attendance"] = (legislativeActivity["Attendance"].to_dict(orient='records'))
    json["Activity"]["Debates"] = (legislativeActivity["Debates"].to_dict(orient='records'))
    json["Activity"]["Questions"] = (legislativeActivity["Questions"].to_dict(orient='records'))
    json["Activity"]["Bills"] = (legislativeActivity["Bills"].to_dict(orient='records'))

    return json

# Build the JSON containing information on all the representatives in the Lok Sabha
def build_json(lok_sabha):

    zip_file_path = "raw/{}.zip".format(lok_sabha)
    dataFrame = pd.DataFrame()
    lokSabhaJson = []

    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        for file_name in zip_ref.namelist():
            if "index.html" in file_name:
                file_content = zip_ref.read(file_name)

                try:
                    # Read the file as HTML
                    soup = read_html(file_content)
                    # Get representative details from the HTML
                    representative = get_representative(soup)
                    # Initialize dataFrames with legislative activity information from HTML tables
                    dataFrames = init_dataframes(soup)
                    # Get legislativeActivity details from the dataFrames
                    legislativeActivity = get_legislative_activity(dataFrames)
                    # Initialize the JSON using the representative and legislativeActivity details
                    json = init_json(representative, legislativeActivity)
                    # Append the JSON to the combined list
                    lokSabhaJson.append(json)
                except:
                    logging.info("Skipping {}".format(file_name))

    # Add the Lok Sabha number to the JSON of every representative
    lokSabhaJson = [{**d, "Lok Sabha": p.ordinal(lok_sabha.split("/")[1])} for d in lokSabhaJson]

    return lokSabhaJson

# Flatten the raw HTMLs into a JSON file
def flatten_lok_sabhas():
    for lok_sabha in range(15, 18):
        try:
            lokSabhaJson = build_json("Lok Sabha/{}".format(lok_sabha))
            os.makedirs("json/Lok Sabha", exist_ok=True)
            lokSabhaJsonString = json.dumps(lokSabhaJson, separators=(',', ':'))
            with open("json/Lok Sabha/{}.json".format(p.ordinal(lok_sabha)), 'w') as file:
                file.write(lokSabhaJsonString)
        except:
            logging.info("Failed to flatten for Lok Sabha {}".format(lok_sabha))

# Add columns related to debate and question categories in the CSV
def add_categories_csv(data):
    for representative in data:
        category = {}

        for debate in representative["Activity"]["Debates"]:
            key = "Debates ({})".format(debate["Debate Type"]).title()
            if key in category:
                category[key] +=  1
            else:
                category[key] =  1
        for question in representative["Activity"]["Questions"]:
            key = "Questions ({})".format(question["Ministry or Category"]).title()
            if key in category:
                category[key] +=  1
            else:
                category[key] =  1

        for categoryName, count in category.items():
            representative[categoryName] = count

        del representative["Activity"]

    return data

def dump_csv():
    directory_path = './json'
    json_files = glob.glob(os.path.join(directory_path, '**/*.json'), recursive=True)
    
    for json_file in json_files:
        with open(json_file, 'r') as file:
            data = json.load(file)
        
        data = add_categories_csv(data)

        df = pd.DataFrame(data)
        pattern = r'Debate|Question'
        df.fillna(0, inplace=True)
        df.loc[:, df.columns.str.contains(pattern)] = df.loc[:, df.columns.str.contains(pattern)].astype(int)

        csv_file_path = json_file.replace('json', 'csv')
        df.to_csv(csv_file_path, index=False, sep=";", quoting=csv.QUOTE_ALL)

def merge_csvs_in_directory(directory):
    directory_path = './csv/{}'.format(directory)
    csv_files = glob.glob(os.path.join(directory_path, '**/*.csv'), recursive=True)

    dataframes = []
    for csv_file in csv_files:
        df = pd.read_csv(csv_file, sep=";", quoting=csv.QUOTE_ALL)
        dataframes.append(df)
    merged_dataframe = pd.concat(dataframes, ignore_index=True)

    pattern = r'Debate|Question'
    merged_dataframe.fillna(0, inplace=True)
    merged_dataframe.loc[:, merged_dataframe.columns.str.contains(pattern)] = merged_dataframe.loc[:, merged_dataframe.columns.str.contains(pattern)].astype(int)

    merged_dataframe.to_csv("{}.csv".format(directory_path), index=False, sep=";", quoting=csv.QUOTE_ALL)

def merge_csvs():
    merge_csvs_in_directory("Lok Sabha")

def flatten():
    flatten_lok_sabhas()
    dump_csv()
    merge_csvs()

if __name__ == "__main__":
    flatten()
