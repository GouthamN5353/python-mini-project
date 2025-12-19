# PES Campus Navigator

PES Campus Navigator is a simple web application built to help students and visitors find their way around the PES University RR Campus. It provides clear, step-by-step walking directions between important campus locations, along with optional audio instructions for convenience and accessibility.

---

## About the Project

Finding directions inside a large campus can be confusing, especially for first-year students or visitors. This project aims to make campus navigation easier by offering a clean interface where users can select a starting point and a destination and instantly receive easy-to-follow directions.

The application focuses on clarity and real-world usability rather than complex map visuals, making it lightweight and easy to use.

---

## Features

- Select starting point and destination from major campus locations  
- Step-by-step text-based directions  
- Optional audio navigation using text-to-speech  
- Simple and responsive user interface  
- Fast backend powered by Flask  
- Audio playback runs independently without blocking the app  

---

## Locations Covered

- Main Gate  
- GJB  
- GJB Canteen  
- OAT  
- BE Block  
- F Block  
- Admission Office  
- GJB Library  
- Boys Hostel  
- SKM Bakery and MealStation  

---

## How It Works

The campus is represented internally as a graph where each location is connected to nearby locations.  
When a user selects a start and destination, the backend verifies that a valid route exists and then returns carefully written directions based on real campus paths.  
If audio is enabled, the same directions are spoken using a text-to-speech engine.

---

## Tech Stack

- **Frontend:** HTML, CSS, JavaScript  
- **Backend:** Python (Flask)  
- **Audio:** pyttsx3 (Text-to-Speech)  
- **Templating:** Jinja2  
- **Concurrency:** Python threading  

