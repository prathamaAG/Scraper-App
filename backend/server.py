from first import first_scraper, name_of_city

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
# result = None

@app.route('/firstScraper', methods=['POST'])
def scraper1():
    data = request.json
    headers = data.get('headers')
    attractionCount = data.get('attractionCount')
    fetched_link = data.get('urls')
    result = first_scraper(headers, fetched_link, attractionCount)
    # return result
    csv_data = result.to_csv(index=False)
    
    # Set response headers to indicate CSV content
    headers = {
        "Content-Disposition": "attachment; filename=data.csv",
        "Content-Type": "text/csv",
    }
    
    # Return CSV data as a response
    return Response(csv_data, headers=headers)

@app.route('/secondScraper', methods=['POST'])
def scraper2():
    data = request.json
    headers = data.get('headers')
    attractionCount = data.get('attractionCount')
    base_url = data.get('urls')
    result = second_scraper(headers, base_url, attractionCount)
    # return result
    csv_data1 = result.to_csv(index=False)
    
    # Set response headers to indicate CSV content
    headers = {
        "Content-Disposition": "attachment; filename=data1.csv",
        "Content-Type": "text/csv",
    }
    
    # Return CSV data as a response
    return Response(csv_data1, headers=headers)
    
@app.route('/scraper1name', methods=['POST'])
def nameOfScraper():
    data = request.json
    headers = data.get('headers')
    fetched_link = data.get('urls')
    result = name_of_city(headers, fetched_link)
    return result

@app.route('/scraper2name', methods=['POST'])
def nameForScraper2():
    data = request.json
    headers = data.get('headers')
    base_url = data.get('urls')
    result1 = second_scraper_name(headers, base_url)
    return result1

if __name__ == '__main__':
    app.run(debug=True)