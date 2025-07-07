# 🚀 Unicodax Professional Job Finder

A **Gradio-based job search web app** that fetches recent software & tech job listings using the **JSearch API via RapidAPI**, then visualizes job distribution and allows CSV export.

---

## 🔧 Features

- 🔐 API key encoded via Base64
- 🧑‍💻 Search by job title and location
- 📆 Filters jobs posted in the **last 7 days**
- 📊 Bar chart showing job count by location
- 📁 Export job listings as CSV

---

## 🔑 Get Your RapidAPI Key

1. Go to [https://rapidapi.com/letscrape-6bRBa3Qgu/api/jsearch/](https://rapidapi.com/letscrape-6bRBa3Qgu/api/jsearch/)
2. Sign up or log in to **RapidAPI**
3. Subscribe to the **Free Plan** for the JSearch API
4. Copy your **X-RapidAPI-Key** from the "Endpoints" tab
5. Paste it into the app where prompted — it will be **base64 encoded automatically**

---

## 🖥️ How to Run Locally

### 1. Clone the Repository

```bash
git clone https://github.com/Manniss01/unicodax-job-finder.git
cd unicodax-job-finder

## How to Run Locally

```bash
pip install -r requirements.txt
python app.py
