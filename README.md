# Spotify Analytics ETL + Power BI Dashboard

A Python-based ETL pipeline that extracts personal Spotify listening data using the Spotify Web API, transforms it into analytics-ready datasets, and visualizes insights through an interactive Power BI dashboard.

---

## Features

- Spotify API Integration
- ETL Pipeline (Extract → Transform → Load)
- Data Cleaning using Pandas
- Automatic Sample Dataset Generation
- Interactive Power BI Dashboard
- Personalized Analytics

---

## Tech Stack

- Python
- Spotipy
- Pandas
- Power BI
- Spotify Web API

---

## Project Structure

```text
Spotify-Analytics/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── sample/
│
├── docs/
│
├── PowerBI Dashboard/
│   └── Spotify Dashboard.pbix
│
├── src/
│
├── README.md
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## Installation

Clone the repository

```bash
git clone <repository-url>
```

Install dependencies

```bash
pip install -r requirements.txt
```

Create a `.env` file from `.env.example`.

Add your Spotify credentials.

Run

```bash
python src/main.py
```

---

## Dashboard

The Power BI dashboard provides insights into:

- Top Tracks
- Top Artists
- Recently Played Songs
- Playlist Analysis
- Listening Trends
- Track Popularity

---

## Sample Dataset

The repository includes a small sample dataset inside `data/sample` so the dashboard can be explored without connecting to Spotify.

To generate your own data:

```bash
python src/main.py
```

---

## Future Improvements

- Genre Analytics
- Audio Feature Analysis
- Monthly Listening Reports
- Recommendation Engine
- Web Dashboard using FastAPI

---

## Author

Sherlynn Vaz