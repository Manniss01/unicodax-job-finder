import base64
import gradio as gr
import requests
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image
import pandas as pd

BASE_URL = "https://jsearch.p.rapidapi.com/search"

def fetch_jobs(api_key_encoded, query, location, num_pages=3):
    empty_df = pd.DataFrame()

    try:
        api_key = base64.b64decode(api_key_encoded).decode("utf-8")
    except Exception:
        return empty_df, "Invalid API Key encoding. Please check and try again.", None, empty_df, False

    if not api_key.strip():
        return empty_df, "API Key is required.", None, empty_df, False
    if not query.strip():
        return empty_df, "Job title is required.", None, empty_df, False
    if not location.strip():
        return empty_df, "Location is required.", None, empty_df, False

    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }

    one_week_ago = datetime.now() - timedelta(days=7)
    jobs_all = []

    for page in range(1, num_pages + 1):
        params = {
            "query": query,
            "location": location,
            "page": page,
            "num_pages": 10
        }
        response = requests.get(BASE_URL, headers=headers, params=params)
        if response.status_code != 200:
            return empty_df, f"API error: {response.status_code}. Check your API key or parameters.", None, empty_df, False

        jobs = response.json().get("data", [])
        for job in jobs:
            date_str = job.get("job_posted_at")
            try:
                post_date = datetime.strptime(date_str, "%Y-%m-%d")
                if post_date >= one_week_ago:
                    jobs_all.append(job)
            except:
                jobs_all.append(job)

    if not jobs_all:
        return empty_df, "No recent jobs found.", None, empty_df, False

    rows = []
    salary_ranges = {"<50k": 0, "50k-100k": 0, ">100k": 0, "Unknown": 0}

    for job in jobs_all:
        title = job.get("job_title", "N/A")
        company = job.get("employer_name", "N/A")
        location_str = job.get("job_city", "N/A")
        remote = "Remote" if job.get("job_is_remote") else "On-site"
        date = job.get("job_posted_at", "N/A")
        desc = job.get("job_description", "N/A")[:200].replace("\n", " ") + "..."
        link = job.get("job_apply_link") or job.get("job_google_link") or ""

        salary = job.get("job_salary", "Unknown")

        rows.append({
            "Title": title,
            "Company": company,
            "Location": location_str,
            "Type": remote,
            "Posted": date,
            "Salary": salary,
            "Apply Link": link,
            "Description": desc
        })

        sal = salary.lower() if salary else "unknown"
        try:
            nums = [int(s.replace("k", "")) for s in sal.split() if "k" in s]
            avg_salary = sum(nums) / len(nums) if nums else None
            if avg_salary is None:
                salary_ranges["Unknown"] += 1
            elif avg_salary < 50:
                salary_ranges["<50k"] += 1
            elif avg_salary <= 100:
                salary_ranges["50k-100k"] += 1
            else:
                salary_ranges[">100k"] += 1
        except:
            salary_ranges["Unknown"] += 1

    location_counts = {}
    for job in jobs_all:
        loc = job.get("job_city")
        if not loc:
            loc = "Unknown"
        location_counts[loc] = location_counts.get(loc, 0) + 1

    if not location_counts:
        bar_chart = None
    else:
        labels = list(location_counts.keys())
        counts = list(location_counts.values())
        plt.figure(figsize=(20, 15))
        plt.bar(labels, counts, color='skyblue')
        plt.xlabel("Location")
        plt.ylabel("Number of Jobs")
        plt.title("Job Count by Location")
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        buf = BytesIO()
        plt.savefig(buf, format='PNG')
        plt.close()
        buf.seek(0)
        bar_chart = Image.open(buf)

    df = pd.DataFrame(rows)

    return df, f"Found {len(jobs_all)} recent jobs.", bar_chart, df, True


def encode_api_key(api_key):
    if not api_key:
        return ""
    return base64.b64encode(api_key.encode("utf-8")).decode("utf-8")


def export_csv(df):
    if df is None or df.empty:
        return None
    filepath = "jobs.csv"
    df.to_csv(filepath, index=False)
    return filepath


with gr.Blocks(title="Unicodax Professional Job Finder") as unicodax_app:
    gr.Markdown(
        """
        <div style="text-align:center;">
            <h1>Unicodax Professional Job Finder</h1>
            <p>Enter your RapidAPI key, search for recent software & tech jobs, and see job distribution by location.</p>
        </div>
        """
    )

    with gr.Row():
        api_key_input = gr.Textbox(
            label="Your RapidAPI Key (will be base64 encoded)",
            type="password",
            placeholder="Paste your RapidAPI key here",
            lines=1,
        )
        encoded_key = gr.Textbox(
            label="Encoded API Key (auto-generated)",
            interactive=False,
            lines=1
        )

    with gr.Row():
        job_input = gr.Textbox(label="Job Title", placeholder="e.g., Software Engineer", lines=1)
        loc_input = gr.Textbox(label="Location", placeholder="e.g., London", lines=1)

    search_btn = gr.Button("Search Jobs")
    export_btn = gr.Button("Export Results as CSV", visible=False)
    results_table = gr.DataFrame(
        headers=["Title", "Company", "Location", "Type", "Posted", "Salary", "Apply Link", "Description"],
        interactive=False
    )
    status = gr.Markdown()
    location_bar = gr.Image(label="Job Distribution by Location")
    csv_data_state = gr.State([])

    api_key_input.change(
        lambda key: encode_api_key(key) if key else "",
        inputs=api_key_input,
        outputs=encoded_key,
        show_progress=False
    )

    def search_jobs_and_enable_export(api_key_enc, job, loc):
        df, status_msg, bar_img, csv_data, enable_export = fetch_jobs(api_key_enc, job, loc)
        return df, status_msg, bar_img, csv_data, gr.update(visible=enable_export)

    search_btn.click(
        search_jobs_and_enable_export,
        inputs=[encoded_key, job_input, loc_input],
        outputs=[results_table, status, location_bar, csv_data_state, export_btn],
        show_progress=True,
    )

    export_btn.click(
        export_csv,
        inputs=csv_data_state,
        outputs=gr.File(label="Download Jobs CSV"),
        show_progress=False
    )

if __name__ == "__main__":
    unicodax_app.launch()
