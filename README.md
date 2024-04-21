


# Master of Focus

## Overview
Master of Focus is a cutting-edge classroom engagement system designed to improve students' focus during remote learning sessions. This system employs facial recognition technology to assess students' attentiveness in real-time, providing valuable feedback to both students and educators.

## Key Features

- **Real-Time Engagement Tracking**: Continuously monitors and analyzes students' attentiveness during class.
- **Instructor Dashboard**: Enables instructors to view detailed reports on each student’s focus level, class participation, and overall performance.
- **Individual Performance Insights**: Students can access their own focus metrics and performance, helping them identify areas for improvement.
- **Alert System**: Notifies when a student’s attention deviates, allowing for immediate correction.
- **Comprehensive Reporting**: Generates detailed reports on class and individual performance for further analysis.

## System Architecture

The backend of the system uses `dlib` for precise face positioning combined with `Python` for processing the engagement metrics. Data is stored in `SQLite` and served via a `Flask` web framework. The frontend is developed using `HTML`, `CSS`, and `JavaScript` to stream video data to the database in real-time.

## Setup 
   Run the Flask server:
   ```
   python app.py
   ```

## Usage

After setting up the system, navigate to `localhost:5000` on your web browser to access the system dashboard.

- **For Students**: Log in with your student credentials to track your real-time attentiveness during classes.
- **For Teachers**: Use your instructor login to view and analyze attentiveness metrics across your classes.

## Demo
  


