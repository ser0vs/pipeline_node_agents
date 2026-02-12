import time

from crewai.tools import tool
from ddgs import DDGS

from pipeline_node_agents.core.logging_config import get_logger

logger = get_logger(__name__)


class SearchTools():

  @tool("Search the internet")
  def search_internet(query: str) -> str:
    """Useful to search the internet about a given topic and return relevant results.
    
    Args:
        query: The search query string to look up on the internet
    
    Returns:
        Search results with titles, links, and snippets
    """
    logger.info("Tool 'Search the internet' is used with parameters: query=%s", query)
    top_result_to_return = 4
    max_attempts = 5
    
    with DDGS() as ddgs:
      for attempt in range(max_attempts):
        try:
          results = ddgs.text(
            query=query,
            max_results=top_result_to_return,
            region='wt-wt',
            backend='lite'
          )
          
          string = []
          for result in results:
            try:
              string.append('\n'.join([
                  f"Title: {result.get('title', 'N/A')}",
                  f"Link: {result.get('href', 'N/A')}",
                  f"Snippet: {result.get('body', 'N/A')}",
                  "\n-----------------"
              ]))
            except KeyError:
              continue
          
          return '\n'.join(string) if string else "No results found."
          
        except Exception as e:
          print(f"Retry due to: {e}")
          time.sleep(1.2 * (attempt + 1))
    
    return "Sorry, I couldn't find anything about that. DuckDuckGo search failed after retries."


if __name__ == "__main__":
  import sys
  
  test_query = sys.argv[1] if len(sys.argv) > 1 else "best restaurants in Vienna"
  
  print(f"Testing search_internet with: {test_query}")
  print("-" * 50)
  
  result = SearchTools.search_internet.run(test_query)
  print(result)
