# UWCompass

A project that visualizes University of Waterloo course dependencies (e.g. prerequisite requirements) using graph-based layouts; offers course selection recommendations based on students' vision of their career paths. 

---

## Overview

This project automatically:

- Fetches official UW course pages using Selenium
- Extracts and parses prerequisite, antirequisite, and corequisite rules
- Converts structured relationships into JSON
- Uses elk.js for graph layout computation
- Plans to render interactive graphs using React Flow
- Focuses on clean JS/CSS/HTML user interaction

The goal is to help students visually understand course dependency chains and plan their degree progression more efficiently.

## Architecture

Selenium Scraper
        ↓
Raw HTML
        ↓
Parser (Prereq / Coreq / Antireq extraction)
        ↓
Structured JSON
        ↓
ELK.js Layout Engine
        ↓
React Flow Graph Renderer
        ↓
Interactive Frontend (JS/CSS/HTML)

## Tech Stack

Data Acquisition: 
- Python
- Selenium
- Headless Chrome

Parsing & Processing: 
- Custom prerequisite parser
- JSON schema normalization

Graph Layout (In Progress):
- elk.js - automatic graph layout computation

Frontend (In Progress): 
- React
- React Flow (graph rendering)
- Vanilla JS
- CSS
- HTML

## Technical Challenges Solved
1️⃣ Parsing Natural Language Requirements

UW prerequisites often contain:
- Nested AND/OR logic
- Program restrictions
- Level-based requirements
- Conditional statements

We built a structured parser that:
- Tokenizes logical operators
- Handles nested groupings
- Normalizes course codes
- Outputs graph-compatible JSON

2️⃣ Lack of Official Open API

UW does not provide a public API for course data.
To work around this, we:
- Used Selenium + ChromeDriver to fetch course pages dynamically
- Extracted course information directly from HTML
- Ensured rate-limiting and ethical scraping practices

## Next Steps

- Integrate React Flow for fully interactive graphs
- Add search & filter functionality
- Enable real-time graph expansion
- Improve UI/UX with custom CSS styling
- Optimize JSON loading performance

## Future Enhancements

- API backend instead of static JSON
- Caching & incremental updates
- Deploy the project to AWS EC2 for online access


