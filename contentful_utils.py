import os
from contentful import Client
from requests.exceptions import ReadTimeout, ConnectionError
import requests
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

requests.Session().request = lambda *args, **kwargs: requests.Session().request(*args, **{**kwargs, 'timeout': 30})

client = Client(
    space_id=os.environ.get('CONTENTFUL_SPACE_ID'),
    access_token=os.environ.get('CONTENTFUL_ACCESS_TOKEN')
)

def get_top_stories(limit=10):
    try:
        logger.debug(f"Fetching top stories with limit: {limit}")
        entries = client.entries({
            'content_type': 'asset',
            'order': '-sys.createdAt',
            'limit': limit
        })
        logger.debug(f"Fetched entries: {entries}")
        stories = [{'title': entry.fields().get('title', 'Untitled')} for entry in entries]
        logger.debug(f"Processed stories: {stories}")
        return stories
    except (ReadTimeout, ConnectionError) as e:
        logger.error(f"Error connecting to Contentful: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error fetching stories from Contentful: {e}")
        return []