# Automated CSV → Table for Game Time Couture

## All Company and personl information has been removed


Convert Square or Shoppify CSV exports into clean, formatted table with subtotals and grand totals for sharing as an **Excel** report.

This lightweight **ETL** workflow powers GTC's day-to-day reporting by:
1) **Extracting** a CSV export,  
2) **Transforming** it (cleaning, rounding, pivoting, inserting **Sub Totals** +  **Grand Totals**), and  
3) **Loading** the result to **Excel** (`.xlsx`).

---

## Features

- **One-click run** from a raw CSV export
- **Automaticaly determin datasource**
- **Log processes with timestamps**
- **Data cleaning**
  - Drop unnecessary columns
  - Numeric rounding to 2 decimals (when applocatble)
  - Format appropriate data type 
- **Pivoted report**
- **Automatic SubTotals** per item (inserts a `SubTotal` row)
- **Automatic Grand Totals**
- **Export**
  - `to_excel(...)`
- **Idempotent**: safe to re-run on the same day’s file

---

## Input Expectations

**One or multiple CSV files from either Square or Shoppify following their export format**

> If your sources are different or uses different headers, the script will not function as intended.

---

## How it works

1. **Load CSV**

2. **Clean data to usable dataframe**

3. **Build Multi-index pivot table**

4. **Insert SubTotals**

5. **Insert Grand Total**

6. **Export**


## Example

Input (CSV rows):
```
Item Name,Item Modifiers,Item Variation,Order Name,Item Quantity,Item Price
Denim Hoodie,Custom Patch,Medium,Order-001,2,79.00
Denim Hoodie,Custom Patch,Medium,Order-002,1,79.00
Denim Hoodie,Glitter Patch,Large,Order-003,1,85.00
```

Output (Excel):
- **Mutli-index pivot table**
- Grouped by item/modifier/variation, with each order shown and a
- **SubTotal** row for each group.
- **Grand Total** at the bottom.

---

## License

MIT (or choose your preferred license).

---

## Acknowledgments

Built for **Game Time Couture** 
