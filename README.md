# Clash Royale Win Rate Analysis

A Python data analysis project exploring how card usage, deck composition, and play time relate to match outcomes in Clash Royale.

## Overview

This project analyzes real Clash Royale battle data to identify patterns in card usage and player performance.

I built a data pipeline that retrieves battle information through the Clash Royale API, stores the data in a SQLite database, and analyzes it using Python.

Rather than relying on a prebuilt dataset, I worked through the full process of collecting, structuring, querying, and interpreting gameplay data.

## Research Questions

The project was built around a few main questions:

* Which cards appeared most frequently in my matches?
* Which cards were associated with higher win rates?
* How did different deck strategies perform?
* Did the time of day have any relationship with match outcomes?
* What patterns could be found by combining battle data with card usage data?

## Data Pipeline

The project follows this general workflow:

**Clash Royale API → Python → SQLite → pandas → Analysis → Visualization**

Battle data is retrieved through the Clash Royale API and stored locally in SQLite tables.

Python scripts then process the stored data to calculate statistics such as card usage frequency, win rates, and performance across different times of day.

## Key Findings

Some patterns that appeared in the collected dataset included:

* **Mortar** had a 75% win rate across 8 recorded matches.
* **Hog Rider** appeared in 61 matches with an approximately 51% win rate.
* **Golem** appeared in 13 matches with an approximately 39% win rate.
* Matches played late at night produced the highest overall win rate in the analyzed dataset.
* Frequently used cards included Firecracker, The Log, Mighty Miner, Hog Rider, and Tesla.

These findings are based on the collected sample and should not be interpreted as global Clash Royale statistics.

## Technologies Used

* Python
* Clash Royale API
* SQLite
* pandas
* matplotlib
* requests
* REST APIs
* Data analysis
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
├── clash_project.db
└── requirements.txt
```

## Running the Project

Install the required Python libraries:

```bash
pip install -r requirements.txt
```

The project includes scripts for collecting data, storing it in SQLite, analyzing battle performance, and visualizing results.

To collect Clash Royale data, a valid Clash Royale API key and player tag are required.

Example:

```bash
python clash_data.py --mode cards
```

To retrieve battle data:

```bash
python clash_data.py --mode battles --player_tag YOUR_PLAYER_TAG
```

To run the analysis:

```bash
python analyze_data.py
```

## What I Learned

This project gave me experience working with an end to end data workflow rather than simply analyzing an existing dataset.

I learned how to retrieve information from an external API, structure relational data using SQLite, query and transform data with Python, and convert raw gameplay records into interpretable statistics.

One of the biggest lessons was understanding how much the quality of an analysis depends on the way the data is collected and structured.

For example, a card having a high win rate does not automatically mean that the card is stronger. Sample size, deck composition, player behavior, and the context of each match can all influence the result.

This project helped me think more critically about the difference between identifying a pattern and drawing a conclusion from that pattern.

## Challenges

One challenge was combining multiple pieces of information from individual battles into a database structure that could be queried effectively.

Another was working with a limited number of recorded matches. Some cards produced high win rates but appeared in relatively few games, making sample size an important consideration when interpreting the results.

## Future Improvements

If I continued developing the project, I would:

* Collect a much larger battle dataset
* Analyze complete deck combinations rather than individual cards
* Compare deck archetypes and strategies
* Track changes in performance over time
* Incorporate trophy level and opponent information
* Compare personal results with broader Clash Royale meta trends
* Build an interactive dashboard for exploring the data
* Add clearer visualizations for card performance and usage
* Automate data collection over longer periods

## Author

**Jungwon Park**
