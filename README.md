# india-representatives-activity

Dataset of legislative activity by Indian parliamentary representatives. Sourced from [PRS India](https://prsindia.org/).

Browse the minified dataset for the current Lok Sabha here: <https://flatgithub.com/Vonter/india-representatives-activity?filename=csv/Lok%20Sabha/17th.csv&stickyColumnName=Name>.

## Dataset

The complete dataset is available as JSON files under the [json/](json) folder in this repository. The JSON files include details on Attendance, Debates, Questions and Bills. Each Lok Sabha is available as a separate JSON file:

- [17th Lok Sabha (Current)](json/Lok%20Sabha/17th.json?raw=1)
- [16th Lok Sabha](json/Lok%20Sabha/16th.json?raw=1)
- [15th Lok Sabha](json/Lok%20Sabha/15th.json?raw=1)

### Activites

Member's activites are available as separate JSONs, split into Debates, Questions and Bills for each Lok Sabha

- [Bills in the 17th Lok Sabha](json/Lok%20Sabha/17th_Bills.json)
- [Bills in the 16th Lok Sabha](json/Lok%20Sabha/16th_Bills.json)
- [Bills in the 15th Lok Sabha](json/Lok%20Sabha/15th_Bills.json)

- [Questions in the 17th Lok Sabha](json/Lok%20Sabha/17th_Questions.json)
- [Questions in the 16th Lok Sabha](json/Lok%20Sabha/16th_Questions.json)
- [Questions in the 15th Lok Sabha](json/Lok%20Sabha/15th_Questions.json)

- [Debates in the 17th Lok Sabha](json/Lok%20Sabha/17th_Debates.json)
- [Debates in the 16th Lok Sabha](json/Lok%20Sabha/16th_Debates.json)
- [Debates in the 15th Lok Sabha](json/Lok%20Sabha/15th_Debates.json)

Minified datasets, containing a subset of the data available in the above JSONs, can be found as CSV files under the [csv/](csv) folder:

- [17th Lok Sabha (Current)](csv/Lok%20Sabha/17th.csv?raw=1)
- [16th Lok Sabha](csv/Lok%20Sabha/16th.csv?raw=1)
- [15th Lok Sabha](csv/Lok%20Sabha/15th.csv?raw=1)

The minified dataset combined across each Lok Sabha can be explored here: <https://flatgithub.com/Vonter/india-representatives-activity?filename=csv/Lok%20Sabha.csv&stickyColumnName=Name>

## Scripts

- [fetch.sh](fetch.sh): Fetches the raw HTML pages from [PRS India](https://prsindia.org/)
- [flatten.py](flatten.py): Parses the raw HTML pages, and generates the JSON and CSV datasets
- [fetchActivityRecords.py](fetchActivityRecords.py): Denests the parent JSON records and joins with Member details

## License

This india-representatives-activity dataset is made available under the Open Database License: http://opendatacommons.org/licenses/odbl/1.0/.
Users of this data should attribute PRS India: https://prsindia.org

You are free:

- **To share**: To copy, distribute and use the database.
- **To create**: To produce works from the database.
- **To adapt**: To modify, transform and build upon the database.

As long as you:

- **Attribute**: You must attribute any public use of the database, or works produced from the database, in the manner specified in the ODbL. For any use or redistribution of the database, or works produced from it, you must make clear to others the license of the database and keep intact any notices on the original database.
- **Share-Alike**: If you publicly use any adapted version of this database, or works produced from an adapted database, you must also offer that adapted database under the ODbL.
- **Keep open**: If you redistribute the database, or an adapted version of it, then you may use technological measures that restrict the work (such as DRM) as long as you also redistribute a version without such measures.

## Generating

Ensure you have `bash`, `curl` and `python` installed

```
# Fetch the data
bash fetch.sh

# Generate the CSV
python flatten.py
```

The fetch script sources data from PRS India (https://prsindia.org/)

## TODO

- State Legislatures
- Rajya Sabha

## Credits

- [PRS India](https://prsindia.org/)
- [Vonter's efforts](https://github.com/Vonter/india-representatives-activity)

## Related

- [india-election-affidavits](https://github.com/Vonter/india-election-affidavits)
