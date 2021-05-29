# Introduction

Usually news-sites stress(ed) _today's_ Covid Statistics. Yet the data gathering process is determined by social behaviour (e.g. not wanting to work on Sundays). Thus the daily data follows a weekly pattern. Consequently we should look at weekly statistics and only use daily statistics as a fall back. A week with e.g. a public holiday can skew statistics dramatically.

Therefore this project tries to look at past developments based on _weekly_ summary statistics. In addition we look into the future by doing some simple calculations.

# Getting Started

## Prerequisites

You need

- Python>=3.6. I used 3.8
- [pip](https://pypi.org/project/pip/)
- The tabulator.scss file from this [repo](https://github.com/olifolkerd/tabulator/tree/master/src/scss). Download it and then move it to `plot_output/static`

## Installing

Load the dependent packages using

```
pip install requirements.txt
```

In addition you need to create a folder called `download_cache`. I use this folder to cache the first API call I make each day.

# Usage

## Running the code

From the base directory: `python main.py <country_code>` e.g. `python main.py fr` for France.

## Interpretation

# Contribute

## Overview of code execution

1. `country_settings.py`: Retrieve the coountry specific settings
2. `extract_data` : Download the data and create an ordered data structure
3. `transform_enrich` : Enrich the data with aggregations and simulations in preparation for plots/tables
4. `visuals_plotly`: Create tables/plots etc.
5. `visuals_tabulator`: Create tables with tabulator.js

Note that if you have any use for the deprecated code snippets, you can just run them at the end of code execution.

## Adding a new country

1. Find your country's data ressource
2. Manipulate `country_settings.py`. Write your own `data_prepation`-method
3. Add your country name and choose some theme colors in `country_settings.py`
4. Run (with fingers crossed)
