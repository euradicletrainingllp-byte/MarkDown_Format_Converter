import os
import tempfile
from flask import Flask, request, jsonify, render_template
from markitdown import MarkItDown

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
)
app.config["MAX_CONTENT_LENGTH"] = None  # No file size limit

md = MarkItDown()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/convert", methods=["POST"])
def convert():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": "No file selected"}), 400

    suffix = os.path.splitext(file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        file.save(tmp.name)
        tmp_path = tmp.name

    try:
        # keep_data_uris=True tells markitdown to embed images as base64
        # instead of writing placeholder filenames like Picture4.jpg
        result = md.convert(tmp_path, keep_data_uris=True)
        return jsonify({"markdown": result.text_content, "filename": file.filename})
    except Exception as e:
        import traceback
        return jsonify({"error": str(e), "detail": traceback.format_exc()}), 500
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


@app.route("/convert-url", methods=["POST"])
def convert_url():
    data = request.get_json()
    url = (data or {}).get("url", "").strip()
    if not url:
        return jsonify({"error": "No URL provided"}), 400
    try:
        result = md.convert(url)
        return jsonify({"markdown": result.text_content, "filename": url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("\n🚀  MarkItDown Web App running at http://localhost:5000\n")
    app.run(debug=True, port=5000)
