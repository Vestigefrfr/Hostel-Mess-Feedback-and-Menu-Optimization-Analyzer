# Hostel Mess Feedback and Menu Optimization Analyzer

A public repository for our university project (Computational Thinking and Programming, Bennett University).

Mess committees usually don't have proper data on what students think of the food, so unpopular dishes keep coming back and food gets wasted. This is a small command-line program where students rate their meals and the program turns those ratings into suggestions for the next weekly menu.

## What it does

- Students rate breakfast, lunch or dinner from 1 to 5 and can leave a short review
- Everything is saved in CSV files
- It works out weekly (last 7 days) and monthly (last 30 days) average ratings per dish
- It shows the highest and lowest rated dishes
- It recommends what to do with each dish:
  - **DROP**: average below 2.5
  - **MODIFY**: average from 2.5 to 3.5, with tips picked up from review words like "salty", "oily" or "cold"
  - **KEEP**: average 3.5 or above (marked "vary" if the dish is served more than twice a week)
  - **NOT ENOUGH DATA**: fewer than 3 ratings
- The report is also saved as `report.txt`

## How to run

You only need Python 3. There are no extra libraries to install.

```
python mess_analyzer.py
```

Then pick an option from the menu:

1. Submit feedback
2. View weekly menu
3. Generate analysis report
4. Exit

## Files

| File | What it is |
|---|---|
| `mess_analyzer.py` | The program |
| `menu.csv` | The weekly menu (day, meal, dish, category) |
| `feedback.csv` | Student ratings (date, student_id, meal, dish, rating, review) |
| `report.txt` | Created when you generate a report |

## Good to know

- The 7 and 30 day windows are counted back from the newest date in `feedback.csv`, not from today.
- Dates can be written as `YYYY-MM-DD` or `DD-MM-YYYY`. Blank or broken rows are skipped.
- The feedback in this repo is sample data from 17 to 25 October 2026.

## Team

- Aza Naiyer
- Ayush
- Lakshay Gupta
- Shivansh Singh
