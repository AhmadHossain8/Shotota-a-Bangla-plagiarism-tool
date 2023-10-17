import requests
from bs4 import BeautifulSoup
from googlesearch import search

# This function gives us the most similar results link.
def get_google_results(query, num_results=10):
    search_results = []

    try:
        for result in search(query, num_results=num_results):  # Use num_results parameter
            search_results.append(result)
    except Exception as e:
        print("An error occurred:", str(e))

    return search_results

# This function gives us the most similar sentences.
def get_search_results(query, num_results=10):
    user_agent = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"

    try:
        response = requests.get(search_url, headers=user_agent)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")
        search_results = []

        count = 0
        for result in soup.select("div.BNeawe.s3v9rd.AP7Wnd"):
            search_results.append(result.get_text())
            count += 1
            if count >= num_results:
                break

        return search_results
    except Exception as e:
        print("An error occurred:", str(e))
        return []

def main():
    sentence = input("Enter a sentence to search on Google: ")

    # Using the googlesearch library
    search_results_googlesearch = get_google_results(sentence, num_results=10)  # Use num_results parameter
    print("\nUsing googlesearch library:")
    for i, result in enumerate(search_results_googlesearch, start=1):
        print(f"{i}. {result}")

    # Using requests and BeautifulSoup for parsing
    search_results_bs4 = get_search_results(sentence, num_results=10)   # This will give us the most similar sentences.
    print("\nUsing BeautifulSoup and requests:")
    for i, result in enumerate(search_results_bs4, start=1):
        print(f"{i}. {result}")

if __name__ == "__main__":
    main()
