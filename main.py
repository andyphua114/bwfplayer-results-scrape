from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd

# "76115/loh-kean-yew"
# "83822/yeo-jia-min"
select_player = "83822/yeo-jia-min"
years = ["2025", "2024", "2023", "2022", "2021", "2020", "2019", "2018"]

for year in years:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(
            "https://bwfworldtour.bwfbadminton.com/player/"
            + select_player
            + "/tournament-results?year="
            + year
        )
        # print(page.title())
        html_content = page.content()

        soup = BeautifulSoup(html_content, "html.parser")

        # time.sleep(5)
        browser.close()

    current_year = year

    # print(soup.prettify())

    # with open("soup_content.html", "w", encoding="utf-8") as file:
    #     file.write(soup.prettify())  # Use prettify() for nicely formatted HTML

    # with open("soup_content.html", "r", encoding="utf-8") as file:
    #     saved_content = file.read()

    # Parse the saved HTML content with BeautifulSoup
    # soup = BeautifulSoup(saved_content, "html.parser")

    div_tournament = soup.find_all("div", "info")
    # exclude the element with class="info right"
    tournament = [div for div in div_tournament if "right" not in div.get("class", [])]

    tournament_name = []
    tournament_date = []

    # print(len(tournament))

    for t in tournament:
        # get tournament name
        tournament_name.append(t.find("h2").find("a").get_text(strip=True))
        # get tournamet date
        tournament_date.append(t.find("h4").get_text(strip=True))

    # print(tournament_name)
    # print(tournament_date)

    div_matches = soup.find_all("div", "tournament-matches")

    formatted_div_matches = []
    idx = 0
    while idx < len(div_matches):
        matches = div_matches[idx].find_all("div", "tournament-matches-row")
        for m in matches:
            result_round = m.find("div", "player-result-round").get_text(strip=True)
            if "qual" in result_round.lower():
                if idx + 1 < len(div_matches):
                    combined_html = str(div_matches[idx]) + str(div_matches[idx + 1])
                else:
                    combined_html = str(div_matches[idx])
                formatted_div_matches.append(
                    BeautifulSoup(combined_html, "html.parser")
                )
                idx += 2
                break
        else:
            formatted_div_matches.append(div_matches[idx])
            idx += 1

    # for each tournament
    for idx, d in enumerate(formatted_div_matches):
        matches = d.find_all("div", "tournament-matches-row")

        name = [tournament_name[idx]] * len(matches)
        date = [tournament_date[idx]] * len(matches)
        tournament_year = [current_year] * len(matches)

        # for each match
        round = []
        player1 = []
        player2 = []
        result = []
        scores = []
        duration = []
        for m in matches:
            round.append(m.find("div", "player-result-round").get_text(strip=True))
            player1.append(
                m.find("div", "player-result-name-1")
                .find("div", "name")
                .get_text(strip=True)
            )
            player2.append(
                m.find("div", "player-result-name-2")
                .find("div", "name")
                .get_text(strip=True)
            )
            result.append(
                m.find("div", "player-result-win").find("strong").get_text(strip=True)
            )
            scores.append(
                m.find("div", "player-result-win").find("span").get_text(strip=True)
            )
            duration.append(
                m.find("div", "player-result-duration")
                .find("div", "timer")
                .get_text(strip=True)
            )
        temp_df = pd.DataFrame(
            {
                "tournament_year": tournament_year,
                "tournament_name": name,
                "tournament_date": date,
                "round": round,
                "player1": player1,
                "player2": player2,
                "result": result,
                "scores": scores,
                "duration": duration,
            }
        )

        if idx == 0:
            df = temp_df
        else:
            df = pd.concat([df, temp_df])

    if current_year == years[0]:
        final_df = df
    else:
        final_df = pd.concat([final_df, df])

final_df.to_csv("data/{}.csv".format(select_player.split("/")[1]), index=False)
