import requests, os
from crewai import Agent, Task, Crew, LLM
from crewai.tools import tool
from bs4 import BeautifulSoup


class BrowserTools():

    @tool("Scrape website content")
    def scrape_and_summarize_website(website: str) -> str:
        """Useful to scrape and summarize a website content.
        
        Args:
            website: The URL of the website to scrape and summarize
        
        Returns:
            Summarized content from the website
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(website, headers=headers, timeout=60)
            response.raise_for_status()
            html_text = response.text
        except Exception as e:
            return f"Error fetching website content: {str(e)}"

        soup = BeautifulSoup(html_text, 'html.parser')
        
        # Remove script and style elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header']):
            element.decompose()
        
        # Extract text content
        text_elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'td', 'th', 'span', 'div'])
        content = "\n\n".join([el.get_text(strip=True) for el in text_elements if el.get_text(strip=True)])
        content = [content[i:i + 8000] for i in range(0, len(content), 8000)]

        maximum_chunks = 3
        content = content[:maximum_chunks]

        summaries = []
        for idx, chunk in enumerate(content):
            ollama_model = os.getenv("OLLAMA_MODEL", "llama3.2:latest")
            ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            llm = LLM(
                model=f"ollama/{ollama_model}",
                base_url=ollama_base_url
            )
            agent = Agent(
                llm=llm,
                role='Principal Researcher',
                goal=
                'Do amazing researches and summaries based on the content you are working with',
                backstory=
                "You're a Principal Researcher at a big company and you need to do a research about a given topic.",
                allow_delegation=False)
            task = Task(
                agent=agent,
                description=
                f'Analyze and summarize the content below, return only the summary nothing else.\n\nCONTENT\n----------\n{chunk}\n\nRemember: Analyze and summarize the content above, return only the summary nothing else.',
                expected_output="A concise markdown summary capturing key facts, figures, entities, and links (if present)."
            )
            try:
                crew = Crew(agents=[agent], tasks=[task], verbose=False)
                result = crew.kickoff()
                summary = str(result)
            except Exception as e:
                # Fallback summarization if LLM execution fails
                sample = (chunk[:1000] + '...') if len(chunk) > 1000 else chunk
                summary = f"Fallback summary (no LLM available)\n\nError: {str(e)}\n\n{sample}"
            print(f"Summary for chunk {idx + 1}:\n{summary}\n{'-'*40}")
            summaries.append(summary)
        return "\n\n".join(summaries)


if __name__ == "__main__":
    import sys
    
    test_url = sys.argv[1] if len(sys.argv) > 1 else "https://example.com"
    
    print(f"Testing scrape_and_summarize_website with: {test_url}")
    print("-" * 50)
    
    result = BrowserTools.scrape_and_summarize_website.run(test_url)
    print("Final summary:\n", result)
