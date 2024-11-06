import requests
from bs4 import BeautifulSoup
import random
import time

def get_random_user_agent():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36",
        "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Mobile Safari/537.36",
    ]
    return random.choice(user_agents)

def scrape_jobs(target_url):
    job_list = []

    headers = {
        "User-Agent": get_random_user_agent(),
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Connection": "keep-alive",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.indeed.com/",
        "DNT": "1",
        "TE": "Trailers",
    }

    try:
        response = requests.get(target_url, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses

        soup = BeautifulSoup(response.text, 'html.parser')
        job_cards = soup.find("div", {"class": "mosaic-provider-jobcards"})
        job_listings = job_cards.find_all("li", {"class": "eu4oa1w0"})

        for job_card in job_listings:
            job_info = {}

            job_info["name-of-the-job"] = job_card.find("a").find("span").text if job_card.find("a") else None
            job_info["name-of-the-company"] = job_card.find("span", {"data-testid": "company-name"}).text if job_card.find("span", {"data-testid": "company-name"}) else None
            job_info["job-location"] = job_card.find("div", {"data-testid": "text-location"}).text if job_card.find("div", {"data-testid": "text-location"}) else None
            job_info["job-details"] = job_card.find("div", {"class": "jobMetaDataGroup"}).text if job_card.find("div", {"class": "jobMetaDataGroup"}) else None
            
            job_list.append(job_info)

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")

    return job_list

if __name__ == "__main__":
    target_url = "https://www.indeed.com/jobs?q=python&l=New+York%2C+NY&vjk=8bf2e735050604df"

    # Retry logic
    for _ in range(2):
        job_data = scrape_jobs(target_url)
        if job_data:
            print(job_data)
            break
        else:
            time.sleep(random.randint(5, 10))  # Wait between 5 to 10 seconds before retrying
