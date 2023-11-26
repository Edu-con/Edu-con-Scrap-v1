from flask import Flask, render_template_string
import requests
from bs4 import BeautifulSoup
import datetime

app = Flask(__name__)

@app.route('/')
def run_scraper():
    courses = scrape_coursera()
    output = generate_html(courses)
    return output


def scrape_coursera():
    def get_soup(site):
        source = requests.get(site).text
        return BeautifulSoup(source, 'lxml')

    def get_title(soup):
        try:
            return soup.find('h1', class_='cds-119 cds-Typography-base css-1xy8ceb cds-121').text.strip()
        except:
            return None

    def get_rating_val(soup):
        try:
            return soup.find('div', class_='cds-119 cds-Typography-base css-h1jogs cds-121').text.strip()
        except:
            return None
        
    def get_review_count(soup):
        try:
            review_count = soup.find('p',class_='cds-119 cds-Typography-base css-dmxkm1 cds-121').text.strip()
            if any(char.isdigit() for char in review_count):  # Check if review_count contains numeric values
                return review_count
            else:
                return None
        except:
            return None
        


    source = requests.get('https://www.coursera.org/sitemap~www~courses.xml').text
    soup = BeautifulSoup(source, 'xml')  # Use XML parser

    courses = []

    for site in soup.find_all('loc'):
        site_soup = get_soup(site.text)
        title = get_title(site_soup)
        rating_val = get_rating_val(site_soup)
        review_count = get_review_count(site_soup)
        course_link = site.text

        if title and rating_val and review_count:
            courses.append((title, rating_val, review_count, course_link))

        if len(courses) >= 5:
            break

    # Sort courses by review count in descending order
    courses.sort(key=lambda x: int(''.join(filter(str.isdigit, x[2]))), reverse=True)

    return courses

def generate_html(courses):
    current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Edu-Con Coursera's Top 50 Courses</title>
        <style>
            h1{
                font-family: 'Product Sans', sans-serif;
            }

            p{
                font-family: 'Product Sans', sans-serif;
            }

            table {
                font-family: 'Product Sans', sans-serif;
                border-collapse: collapse;
                width: 100%;
            }

            th, td {
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }

            th {
                background-color: #f2f2f2;
            }

            a {
                text-decoration: none;
                color: #000;
            }
        </style>
    </head>
    <body>
        <h1><center>Top 50 Coursera Courses<center></h1>
        <p><small>Last Updated on {{ current_datetime }}</small></p>
        <table>
            <tr>
                <th>Course Title</th>
                <th>Rating</th>
                <th>Review Count</th>
            
            </tr>
            {% for title, rating, review_count, course_link in courses %}
                <tr>
                    <td><a href="{{ course_link }}">{{ title }}</a></td>
                    <td>{{ rating }}</td>
                    <td>{{ review_count }}</td>
                </tr>
            {% endfor %}
        </table>
    </body>
    </html>
    """
    return render_template_string(template, courses=courses, current_datetime=current_datetime)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
