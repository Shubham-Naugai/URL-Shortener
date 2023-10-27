from flask import Flask, request, jsonify, render_template, redirect, url_for
from bs4 import BeautifulSoup
import hashlib
import requests

app = Flask(__name__)
shortned_urls = {}

# generate code for url
def generate_short_code(url):
    string = str(url)
    hash_code = int(hashlib.sha256(string.encode('utf-8')).hexdigest(), 16) % 10**8
    return str(hash_code)


# short url function
def shorten_url(long_url):
    short_code = generate_short_code(long_url)
    if short_code in shortned_urls:
        return None
    short_url = f'http://127.0.0.1:5000/{short_code}'
    shortned_urls[short_code] = {'url': long_url, 'short_url':short_url, 'hits': 0}
    return short_url


# endpoint for url shortning
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        long_url = request.form['long_url']
        short_url = shorten_url(long_url)
        if short_url == None:
            return "URL already shorted"
        # shortned_urls[short_url] = long_url
        return f"Your shortned URL: {short_url}"
    return render_template("index.html")


#  store metadata about short url, total number of hits
@app.route("/<short_code>")
def redirect_url(short_code):
    if short_code in shortned_urls:
        long_url = shortned_urls[short_code]['url']
        shortned_urls[short_code]['hits'] += 1
        return redirect(long_url)
    else:
        return "URL not found", 404

# endpoint for metadata about a short URL
@app.route('/metadata/<short_code>', methods=['GET'])
def get_metadata(short_code):
    if short_code in shortned_urls:
        url_data = shortned_urls[short_code]
        return jsonify({'url': url_data['url'], 'hits': url_data['hits']})
    else:
        return "URL not found", 404


#search endpoint
@app.route('/search', methods=['GET'])
def search():
    term = request.args.get('term')
    if not term:
        return render_template('search.html', matching_urls=[])
    
    matching_urls = []
    for short_code, url_data in shortned_urls.items():
        long_url = shortned_urls[short_code]['url']
        title = get_title(long_url)
        if term.lower() in title.lower():
            matching_urls.append({
                'title': title,
                'url': f'http://127.0.0.1:5000/{short_code}',
                'hits': shortned_urls[short_code]['hits']
            })
    return matching_urls


# helper function for search
def get_title(long_url):
    try:
        response = requests.get(long_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string
            return title.strip() if title else "No Title Found"
        else:
            return "No Title Found"
    except Exception as e:
        return "No Title Found"


if __name__ == '__main__':
    app.run(debug=True)
