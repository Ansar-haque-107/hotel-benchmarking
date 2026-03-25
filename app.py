from flask import Flask, render_template, request, jsonify, send_file
import json
import csv
import io
import os
import threading
import uuid
import traceback

app = Flask(__name__)

# In-memory job store (resets on server restart — fine for this use case)
scraping_jobs = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/scrape', methods=['POST'])
def start_scrape():
    data = request.json
    hotels = data.get('hotels', [])
    if not hotels:
        return jsonify({'error': 'No hotels provided'}), 400

    job_id = str(uuid.uuid4())[:8]
    scraping_jobs[job_id] = {
        'status': 'running',
        'current': 0,
        'total': len(hotels),
        'current_hotel': '',
        'results': [],
        'error': None
    }

    def run_job():
        try:
            from scraper import scrape_hotel_data
            from scorer import process_hotel_data
            results = []
            for i, hotel in enumerate(hotels):
                scraping_jobs[job_id]['current'] = i
                scraping_jobs[job_id]['current_hotel'] = hotel.get('name', f'Hotel {i+1}')
                scraped = scrape_hotel_data(hotel)
                scored = process_hotel_data(hotel, scraped)
                results.append(scored)
                scraping_jobs[job_id]['results'] = results
            scraping_jobs[job_id]['current'] = len(hotels)
            scraping_jobs[job_id]['status'] = 'complete'
        except Exception as e:
            scraping_jobs[job_id]['status'] = 'error'
            scraping_jobs[job_id]['error'] = str(e) + '\n' + traceback.format_exc()

    thread = threading.Thread(target=run_job, daemon=True)
    thread.start()
    return jsonify({'job_id': job_id})

@app.route('/api/status/<job_id>')
def get_status(job_id):
    if job_id not in scraping_jobs:
        return jsonify({'error': 'Job not found'}), 404
    job = scraping_jobs[job_id]
    return jsonify({
        'status': job['status'],
        'current': job['current'],
        'total': job['total'],
        'current_hotel': job['current_hotel'],
        'error': job['error'],
        'has_results': len(job['results']) > 0
    })

@app.route('/api/results/<job_id>')
def get_results(job_id):
    if job_id not in scraping_jobs:
        return jsonify({'error': 'Job not found'}), 404
    return jsonify(scraping_jobs[job_id]['results'])

@app.route('/api/download/<job_id>/<csv_type>', methods=['POST'])
def download_csv(job_id, csv_type):
    data = request.json or {}
    results = data.get('results') or scraping_jobs.get(job_id, {}).get('results', [])
    if not results:
        return jsonify({'error': 'No results found'}), 400

    from scorer import generate_amenities_csv, generate_scoring_csv
    if csv_type == 'amenities':
        rows = generate_amenities_csv(results)
        filename = 'amenities_benchmarking.csv'
    else:
        rows = generate_scoring_csv(results)
        filename = 'scoring_benchmarking.csv'

    output = io.StringIO()
    writer = csv.writer(output)
    for row in rows:
        writer.writerow(row)
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
