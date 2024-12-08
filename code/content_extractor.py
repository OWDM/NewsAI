import requests
from langchain_community.chat_models import ChatOpenAI
from langsmith import traceable


from api_config import OPENAI_API_KEY, EXTRACTOR_API_KEY  # Import the API keys


# Check if the API keys are set
if not OPENAI_API_KEY or OPENAI_API_KEY == "your-openai-api-key":
    raise ValueError("Please set your OpenAI API Key in the api_config.py file.")
if not EXTRACTOR_API_KEY or EXTRACTOR_API_KEY == "your-extractor-api-key":
    raise ValueError("Please set your Extractor API Key in the api_config.py file.")

# Use the keys
llm = ChatOpenAI(model="gpt-4o-mini", openai_api_key=OPENAI_API_KEY)

def get_raw_content(url):
    extractor_url = f"https://extractorapi.com/api/v1/extractor/?apikey={EXTRACTOR_API_KEY}&url={url}"
    try:
        response = requests.get(extractor_url, timeout=10)
        response.raise_for_status()
        data = response.json()
        title = data.get("title", "")
        content = data.get("text", "")
        if not content:
            # Extraction failed; content is empty
            return False, "Failed to extract content from the URL."
        return True, (title, content)
    except requests.exceptions.Timeout:
        return False, "The request timed out while trying to fetch the content."
    except requests.exceptions.ConnectionError:
        return False, "Failed to connect to the content extraction service."
    except requests.exceptions.HTTPError as e:
        return False, f"HTTP error occurred: {e.response.status_code}."
    except requests.exceptions.RequestException:
        return False, "An error occurred while trying to fetch the content."
    except ValueError:
        return False, "Received an invalid response from the content extraction service."

# LLM function to clean the content
@traceable
def clean_content_with_llm(content):
    prompt = (
        "**Content** must:\n"
        "1. Exclude all hyperlinks, URLs, and references.\n"
        "2. Exclude any HTML tags, metadata, or formatting styles (such as bold or italics).\n"
        "3. Maintain the original paragraph structure with appropriate **line breaks** and **spaces** between paragraphs.\n"
        "4. Ensure the content is presented in a reader-friendly way, exactly as it would appear in the article, without bullet points or embedded references.\n\n"
        "If the article is not found, blocked, or cannot be retrieved, return exactly this: `None`.\n\n"
        "Ensure that your response is **clear** and **concise**, with no interruptions or artifacts from the original web page, so it is ready to be displayed directly to the user."
    )

    messages = [
        {"role": "system", "content": "You are a content cleaner."},
        {"role": "user", "content": f"{prompt}\n\nHere is the content:\n\n{content}"},
    ]

    response = llm.invoke(messages)
    return response.content.strip()

# Function to fetch and clean content, returning a tuple (success, content/error message)
def get_cleaned_article(url):
    success, result = get_raw_content(url)

    if not success:
        # Extraction failed
        return False, result

    title, raw_content = result

    cleaned_content = clean_content_with_llm(raw_content)

    if cleaned_content == "None":
        # LLM indicates content could not be retrieved or is blocked
        return False, "The content could not be retrieved or is blocked."

    # Combine title and cleaned content
    combined_content = f"{title.strip()}\n\n{cleaned_content}"
    return True, combined_content