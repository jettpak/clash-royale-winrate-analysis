# Clash Royale Win Rate Analysis

A data analysis project exploring how card selection, deck composition, and play time influence match outcomes in Clash Royale.

## Overview

This project uses real Clash Royale battle data to investigate patterns in player performance and card usage. I built a data pipeline that collects battle information through the Clash Royale API, stores the data in a SQLite database, and analyzes it using Python.

The goal was to explore questions such as:

* Which cards appeared most frequently in my matches?
* Which cards were associated with the highest win rates?
* How did different deck strategies perform?
* Did the time of day have any relationship with match outcomes?

## Key Findings

Some of the patterns identified in the dataset included:

* Mortar had a 75% win rate across the recorded matches in which it appeared.
* Hog Rider appeared in 61 matches with an approximately 51% win rate.
* Golem appeared in 13 matches with an approximately 39% win rate.
* Matches played late at night produced the highest overall win rate in the analyzed dataset.
* Frequently used cards included Firecracker, The Log, Mighty Miner, Hog Rider, and Tesla.

These results reflect the collected sample and are not intended to represent global Clash Royale statistics.

## How It Works

The project follows a simple data pipeline:

**Clash Royale API → Python → SQLite → pandas → Data Analysis → Visualization**

Battle data is collected from the Clash Royale API and stored locally using SQLite. Python scripts then query and transform the stored data to calculate card usage, win rates, and other gameplay patterns.

## Technologies

* Python
* Clash Royale API
* SQLite
* pandas
* matplotlib
* REST APIs
* Data visualization

## Project Structure

```text
clash-royale-winrate-analysis/
├── analyze_data.py
├── check_db_counts.py
├── clash_data.py
├── database_setup.py
├── timeapi_data.py
├── visualize_data.py
├── clash_data.db
└── analysis_output.txt
```

## What I Learned

This project gave me experience working with an end to end data workflow rather than analyzing a prebuilt dataset.

I learned how to retrieve information from an external API, design a relational database for storing battle data, query and transform that information with Python, and turn raw gameplay records into meaningful statistics.

One of the biggest lessons was that data analysis depends heavily on how data is collected and structured. Even seemingly simple questions such as whether a certain card has a high win rate require careful consideration of sample size, context, and how the metric is calculated.

## Future Improvements

If I continued developing the project, I would:

* Collect a substantially larger dataset
* Compare performance across different deck archetypes
* Analyze card combinations rather than individual cards
* Build an interactive dashboard for exploring results
* Incorporate additional player and trophy information
* Compare personal statistics with broader Clash Royale meta trends

## Author

Jungwon Park
