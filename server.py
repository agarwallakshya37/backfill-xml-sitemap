from flask import Flask, request, jsonify
import script
from datetime import datetime

app = Flask(__name__)

@app.route("/parse_sitemap", methods=["POST"])
def parse_sitemap():
    """API to process a sitemap and extract URLs."""
    data = request.json
    sitemap_url = data.get("sitemap_url")
    start_date = data.get("start_date")
    end_date = data.get("end_date")
    content_filter = data.get("content_filter")

    if not sitemap_url:
        return jsonify({"error": "Missing required parameter: sitemap_url"}), 400

    try:
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
        if start_date > end_date:
            return jsonify({"error": "Start date cannot be later than end date!"}), 400
    except ValueError:
        return jsonify({"error": "Invalid date format. Please use YYYY-MM-DD."}), 400

    try:
        sitemaps, urls = script.main(sitemap_url, start_date, end_date, content_filter)
        return jsonify({"sitemaps": sitemaps, "urls": urls})
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except ValueError as e:
        return jsonify({"error": str(e)}), 422
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
