# Hotel Benchmarking Tool — Local Setup Guide
## (Backup if the hosted Render link is unavailable)

---

## What You Need
- A computer running Windows, Mac, or Linux
- Internet connection
- About 10 minutes

---

## Step 1 — Install Python

1. Go to: https://www.python.org/downloads/
2. Download **Python 3.11** or newer
3. Run the installer
   - ✅ On Windows: **tick "Add Python to PATH"** before clicking Install
4. Verify: open a terminal/command prompt and type:
   ```
   python --version
   ```
   You should see something like `Python 3.11.x`

---

## Step 2 — Download the App Files

You should have received a ZIP file or folder called `hotel-benchmarking`.
Extract / copy it to a location you can find easily, e.g.:
- Windows: `C:\Users\YourName\hotel-benchmarking\`
- Mac/Linux: `~/hotel-benchmarking/`

---

## Step 3 — Open a Terminal in the App Folder

**Windows:**
1. Open File Explorer → navigate to `hotel-benchmarking` folder
2. Click the address bar, type `cmd`, press Enter

**Mac:**
1. Open Terminal
2. Type `cd ~/hotel-benchmarking` and press Enter

---

## Step 4 — Install Dependencies

In the terminal, run these two commands one at a time:

```bash
pip install -r requirements.txt
```

```bash
playwright install chromium
```

This downloads the automated browser. It may take a few minutes.

---

## Step 5 — Run the App

```bash
python app.py
```

You should see:
```
 * Running on http://0.0.0.0:5000
```

---

## Step 6 — Open in Your Browser

Open any browser and go to:
```
http://localhost:5000
```

The benchmarking tool will open. 🎉

---

## Using the Tool

1. **Step 1 — Add Hotels**
   - Your property is the first card (pre-filled)
   - Add competitors using **+ Add Hotel**
   - Paste the exact Booking.com and/or Expedia URL for each hotel
   - Set **Location Score** (1–5) manually — based on proximity to highway/crossroads
   - Set **Brand Tier** from the dropdown (Economy → Luxury)

2. **Step 2 — Run Benchmarking**
   - Click **Run Benchmarking**
   - The tool opens the hotel pages automatically in the background
   - Progress shows which hotel is being scraped

3. **Step 3 — Review & Download**
   - Review the Scoring Matrix and Amenities Checklist
   - Click any **score** or **reason** to edit it manually
   - Click **⬇ Amenities CSV** and **⬇ Scoring CSV** to download both files

---

## Scoring Criteria Reference

| Factor | How Scored |
|---|---|
| Location | Manual entry (1–5) |
| Amenities | Auto-checked — 1 point per 2 amenities found (max 5) |
| Restaurant | On-site=5, Buffet=3, Vending/Coffee=1.5, Both=3.5 |
| Meeting Space | Business Centre=1, Meeting Room=3, Multiple=4, +BC=5, Banquet=5 |
| Brand | Economy=1.5, MidScale=2.5, UpperMidScale=3, UpperScale=3.5, UpperUpscale=4, Luxury=5 |
| Parking | Lorry/bus=5, EV=4, Free on-site=3, Charged=2, Street=1 |
| Ratings | Average of BDC + Expedia ratings (auto-scraped, converted to /5) |
| Swimming Pool | None=0, Closed=1, Seasonal=2, Seasonal Heated=2.5, Outdoor=3, Heated/2=3.5, Indoor=4, Indoor Heated/2=5 |

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `pip` not found | Use `pip3` instead of `pip` |
| `playwright install` fails | Run: `pip install playwright` first |
| Site blocked/CAPTCHA | Try running with a real browser session or try again later |
| Port 5000 in use | Edit `app.py` last line, change `5000` to `5001` |

---

## Stopping the App

Press `Ctrl + C` in the terminal window.

---

*Built for competitive hotel benchmarking. Scores based on Booking.com + Expedia data.*
