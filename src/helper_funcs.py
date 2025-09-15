import json
import newsdataapi as news
from dotenv import load_dotenv
import os

load_dotenv()
search_key = os.getenv("SEARCH_API_KEY")
cse_id = os.getenv("CSE_ID")
news_key = os.getenv("NEWS_KEY")

from googleapiclient.discovery import build
#google api setup
service = build("customsearch", "v1", developerKey=search_key)

#newsapi
newsapi = news.NewsDataApiClient(apikey=news_key)

# Function to save the list to a file
def save_to_file(file_name, data):
    with open(file_name, 'w') as file:
        json.dump(data, file)

# Function to load the list from a file
def load_from_file(file_name):
    try:
        with open(file_name, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []  # Return an empty list if the file does not exist
    except json.JSONDecodeError:
        print("Error decoding JSON. Returning an empty list.")
        return []
    

async def split_string(input_string):
# Check if the string length is greater than 1500
    if len(input_string) > 1500:
        # Split the string into chunks of 1500 characters
        chunks = [input_string[i:i + 1500] for i in range(0, len(input_string), 1500)]
        return chunks
    else:
        # Return the original string if it's 1500 characters or less
        return [input_string]
        

async def google_search(search_term, **kwargs):
    res = service.cse().list(q=search_term, cx=cse_id, num=3, filter=1, safe='medium', **kwargs).execute()
    results = res['items']
    answer = ""
    #for result in results:
        #answer += f"{result['title']}: [source](<{result['link']}>)\r\n"

    for index, result in enumerate(results):
        if index == 0:  # Check if it's the first iteration
            answer += f"**{result['title']}**: [source]({result['link']})\r\n"  # Change formatting for the first result
        else:
            answer += f"{result['title']}: [source](<{result['link']}>)\r\n"  # Normal formatting for 
    return answer
    
async def get_news(query, country):
    data = newsapi.latest_api(q=query, country=country, max_result=3)
    if data['status'] == 'success':
        articles = data['results']
        for article in articles:
            title = article['title']
            link = article['link']
            description = article['description']
            pub_date = article['pubDate']

            # Format the message
            message = f"**{title}**\n{description}\nPublished on: {pub_date}\n[Read more]({link})"
            return message