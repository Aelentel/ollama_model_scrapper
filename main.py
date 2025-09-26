import requests
import string
from bs4 import BeautifulSoup as BS
from pydantic import BaseModel,TypeAdapter
from typing import List
from tqdm import tqdm


OLLAMA_SEARCH_URL = 'https://registry.ollama.ai/search?q='

class OllamaModel(BaseModel):
    name: str
    description: str
    capabilities: List[str]
    tags: List[str]

def parse_model_page(page_html:str) -> List[OllamaModel]:
    soup = BS(page_html, 'html.parser')
    model_html_root=soup.find("ul",attrs={'role':'list'})
    result=[]
    for model_html in model_html_root.find_all("li"):
        header=model_html.find("div",attrs={'title':True})
        name=header.find("span",attrs={'x-test-search-response-title':True}).text.strip()
        description=header.find("p").text.strip()
        capabilities_html=model_html.find_all("span",attrs={'x-test-capability':True})
        capabilities=[span.text.strip() for span in capabilities_html]
        if "embedding" not in capabilities:
            capabilities.append('chat')
        size_tags_html=model_html.find_all("span",attrs={'x-test-size':True})
        size_tags=[tags.text.strip() for tags in size_tags_html]
        #
        result.append(OllamaModel(name=name,description=description,capabilities=capabilities,tags=size_tags))
    return result

def fetch_model_page(query: str) -> List[OllamaModel]:
    response=requests.post(OLLAMA_SEARCH_URL+query)
    return parse_model_page(response.text)
    
def fetch_model_list() -> List[OllamaModel]:
    chars = string.ascii_lowercase
    progress = tqdm(desc="Scraping Ollama",total=len(chars))
    result=[]
    for character in chars:
        result=result+fetch_model_page(character)
        progress.update(1)
        progress.refresh()
    progress.close()
    return result

def main():
    model_list=fetch_model_list()
    model_list_adapter = TypeAdapter(List[OllamaModel])
    json_string = model_list_adapter.dump_json(model_list).decode('utf-8')
    # maybe output anoter model to store the date of extraction and put it in a file
    print(json_string)

if __name__ == "__main__":
    main()
