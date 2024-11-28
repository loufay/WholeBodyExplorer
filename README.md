# Whole-Body Organ Explorer

This is a Streamlit-based application to explore organ data from MRI datasets. The app visualizes distributions and correlations of organ shape metrics (volume, diameter, surface area) across various factors such as age and gender.

## Features

- Home page with an overview of the dataset.
- Data Distribution Explorer.
- Data Correlation Explorer.

## Requirements

Install dependencies with:
```
pip install -r requirements.txt
```

## Run the Application

Run the Streamlit app:
```
streamlit run src/app.py
```
Open local URL in browser

```
http://localhost:8501
```

## Data Sources

- [NAKO Study](https://www.nako.de)
- [TotalSegmentator](https://github.com/wasserth/TotalSegmentator)



