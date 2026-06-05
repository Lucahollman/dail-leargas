"""
Script to find all debate entires on the Oireactas site

Debate urls are contained within pages in the format:
https://www.oireachtas.ie/en/debates/debate/dail/YYYY-MM-DD/

We want to find all possible dates between a range, find the hyperlinks within,
and save them with some metadata to a csv.
"""

import datetime as dt
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


def main() -> None:

    base_url = "https://www.oireachtas.ie/en/debates/debate/dail"

    start_time = dt.datetime(2025, 1, 22).date()
    end_time = dt.datetime.today().date()

    # Create list of all possible dates for debates
    possible_dates = [
        start_time + i * dt.timedelta(days=1)
        for i in range((end_time - start_time).days)
    ]

    possible_urls = [t.strftime(f"{base_url}/%Y-%m-%d/") for t in possible_dates]

    queries = []
    for u in tqdm(possible_urls, desc=f"Finding Debates from {start_time} to {end_time}"):
        result = extract_links(u)

        if result["found"]:
            queries.append(result)

    debates = []
    for q in queries:
        for debate_dict in q["links"]:

            # Skip sublinks to headings
            if "#" in debate_dict["href"]:
                continue

            debates.append(
                {
                    "url": debate_dict["href"],
                    "title": debate_dict["text"],
                    "date": q["url"].split("/")[-2],
                }
            )

    # Create CSV
    output_file = "debates.csv"
    print(f"Writing to: {output_file}")
    pd.DataFrame(debates).to_csv(output_file)


def extract_links(url: str, div_class: str = "results") -> dict:
    """
    Fetch a URL, find the first <div class='results'>,
    and extract every href at every nesting level inside it.
    """
    result = {"url": url, "title": "", "found": False, "links": []}

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

    except requests.RequestException as e:
        return result

    soup = BeautifulSoup(response.text, "html.parser")

    container = soup.find("div", class_=div_class)

    if not container:
        # print(f"[NOT FOUND] {url} — no <div class='{div_class}'>")
        return result

    result["found"] = True

    # find_all() recurses into nested <ul>/<li> automatically
    links = [
        {
            "href": urljoin(url, tag["href"]),
            "text": tag.get_text(strip=True),
        }
        for tag in container.find_all("a", href=True)
    ]

    result["links"] = links
    # print(f"{url} — found {len(links)} link(s)")

    return result


if __name__ == "__main__":
    main()
