from flask import Flask, request, jsonify, render_template
from script import main
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def index():
    """Render the frontend page."""
    return render_template("index.html")

@app.route("/crawl", methods=["POST"])
def crawl_sitemap():
    """API endpoint to process a sitemap and return URLs."""
    try:
        data = request.json
        sitemap_url = data.get("sitemap_url")
        start_date_str = data.get("start_date")
        end_date_str = data.get("end_date")
        content_filter = data.get("content_filter", "")

        if not sitemap_url:
            return jsonify({"error": "Sitemap URL is required"}), 400
        if not start_date_str or not end_date_str:
            return jsonify({"error": "Start and End dates are required"}), 400

        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
        except ValueError:
            return jsonify({"error": "Invalid date format, expected YYYY-MM-DD"}), 400

        sitemaps, all_urls = main(sitemap_url, start_date, end_date, content_filter)

        if not all_urls:
            return jsonify({"message": "No URLs found in the given date range."}), 200

        return jsonify({
            "sitemaps": sitemaps,
            "urls": all_urls
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
