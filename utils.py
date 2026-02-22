from faq_data import faqs

from openai import AzureOpenAI

import os

from dotenv import load_dotenv

import requests

from bs4 import BeautifulSoup

load_dotenv()

# Get the GPT model deployment name from environment

GPT_DEPLOYMENT_NAME = os.getenv("gpt-35-turbo", "gpt-35-turbo")


def get_best_faq_answer(user_question: str, client: AzureOpenAI) -> str:

    """

    Find the best FAQ answer using GPT-3.5-turbo for direct matching and response

    """

    # Create a context with all FAQ data

    faq_context = "\n".join([

        f"Q: {faq['question']}\nA: {faq['answer']}\n"

        for faq in faqs

    ])

    # Create a prompt for GPT to find the best matching FAQ

    prompt = f"""You are an ACS FAQ assistant. Based on the following FAQ database, answer the user's question.

If you find a closely related question in the FAQ database, provide the corresponding answer.

If no closely related question exists, respond with: "Sorry, I can only answer based on the official ACS FAQs. Do you want me to provide you an answer from the web?"

FAQ Database:

{faq_context}

User Question: {user_question}

Instructions:

- Only answer based on the provided FAQ database

- If the question closely matches an FAQ, provide the exact answer from the database

- If no close match exists, use the standard "Sorry" response

- Do not make up information not in the FAQ database

Answer:"""

    try:

        response = client.chat.completions.create(

            model=GPT_DEPLOYMENT_NAME,

            messages=[

                {"role": "system", "content": "You are a helpful ACS FAQ assistant. Only answer based on the provided FAQ database."},

                {"role": "user", "content": prompt}

            ],

            max_tokens=500,

            temperature=0.1  # Low temperature for consistent responses

        )

        return response.choices[0].message.content.strip()

    except Exception as e:

        return f"Sorry, I encountered an error while processing your question. Please try again."


def search_duckduckgo_for_answer(question: str) -> str:

    """

    Multiple fallback methods: Instant API → Web scraping → Direct answer

    """

    try:

        print(f"Starting search for: {question}")

        # Step 1: Try instant answer API

        print("Trying instant answer API...")

        instant_result = search_duckduckgo_instant(question)

        if instant_result and "couldn't find" not in instant_result and len(instant_result.strip()) > 50:

            print("✓ Instant API returned good results")

            return instant_result

        # Step 2: Try web scraping with content extraction

        print("Trying web scraping with content extraction...")

        scraping_result = search_duckduckgo_web_scraping_with_content(question)

        if scraping_result and "couldn't find" not in scraping_result and len(scraping_result.strip()) > 50:

            print("✓ Web scraping returned good results")

            return scraping_result

        # Step 3: Provide direct answer with summary

        print("Providing direct answer...")

        return generate_direct_answer(question)

    except Exception as e:

        print(f"Error in search_duckduckgo_for_answer: {str(e)}")

        return generate_direct_answer(question)

 
def search_duckduckgo_instant(question: str) -> str:

    """

    Enhanced instant answer with better result detection

    """

    try:

        url = "https://api.duckduckgo.com/"

        params = {

            "q": question,

            "format": "json",

            "no_html": "1",

            "skip_disambig": "1"

        }

        headers = {

            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

        }

        response = requests.get(url, params=params, headers=headers, timeout=10)

        response.raise_for_status()

        data = response.json()

        answer_text = ""

        # Check for instant answer (direct facts)

        if data.get("Answer") and data.get("Answer").strip():

            answer_text = f"**Direct Answer:** {data['Answer']}\n\n"

        # Check for abstract (Wikipedia-style comprehensive info)

        if data.get("Abstract") and data.get("Abstract").strip():

            answer_text += f"**Summary:** {data['Abstract']}\n\n"

            if data.get("AbstractURL"):

                answer_text += f"**Source:** {data['AbstractURL']}\n\n"

        # Check for definition (dictionary-style)

        if data.get("Definition") and data.get("Definition").strip():

            answer_text += f"**Definition:** {data['Definition']}\n\n"

            if data.get("DefinitionURL"):

                answer_text += f"**Source:** {data['DefinitionURL']}\n\n"

        # Check for related topics (additional context)

        if data.get("RelatedTopics") and len(data["RelatedTopics"]) > 0:

            topics = data["RelatedTopics"][:2]  # Limit to 2 most relevant

            topic_text = ""

            for topic in topics:

                if isinstance(topic, dict) and topic.get("Text") and topic.get("Text").strip():

                    topic_text += f"• {topic['Text']}\n"

                    if topic.get("FirstURL"):

                        topic_text += f"  🔗 {topic['FirstURL']}\n"

            if topic_text:

                answer_text += f"**Related Information:**\n{topic_text}\n"

        # Check for infobox data (structured information)

        if data.get("Infobox") and data.get("Infobox").get("content"):

            infobox_items = data["Infobox"]["content"][:3]  # Top 3 items

            if infobox_items:

                answer_text += "**Key Information:**\n"

                for item in infobox_items:

                    if item.get("label") and item.get("value"):

                        answer_text += f"• **{item['label']}**: {item['value']}\n"

                answer_text += "\n"

        # Return result if we have substantial content

        if answer_text.strip() and len(answer_text.strip()) > 30:

            return f"I couldn't find an exact match in the ACS FAQs. Here's what I found:\n\n{answer_text}"

        return None

    except Exception as e:

        print(f"Error in instant API: {str(e)}")

        return None
 
 
def search_duckduckgo_web_scraping_with_content(question: str) -> str:

    """

    Enhanced web scraping that extracts actual content snippets

    """

    try:

        # Use DuckDuckGo's lite search

        url = "https://lite.duckduckgo.com/lite/"

        params = {"q": f"site:nyc.gov/site/acs {question}"}

        headers = {

            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

        }

        response = requests.get(url, params=params, headers=headers, timeout=15)

        response.raise_for_status()

        html_content = response.text

        # Extract content snippets along with links

        import re

        # Look for result blocks with content

        result_pattern = r'<tr.*?>(.*?)</tr>'

        result_blocks = re.findall(result_pattern, html_content, re.DOTALL)

        extracted_results = []

        for block in result_blocks:

            # Extract link and title

            link_match = re.search(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', block, re.DOTALL)

            if link_match:

                href, title = link_match.groups()

                # Clean title

                clean_title = re.sub(r'<[^>]+>', '', title).strip()

                # Extract snippet/description

                snippet_match = re.search(r'</a>(.*?)(?:<a|$)', block, re.DOTALL)

                snippet = ""

                if snippet_match:

                    snippet = re.sub(r'<[^>]+>', '', snippet_match.group(1)).strip()

                    snippet = re.sub(r'\s+', ' ', snippet)  # Clean whitespace

                # Filter valid results

                if (href.startswith("https://www.nyc.gov") and clean_title):
                    extracted_results.append({
                        'title': clean_title,
                        'link': href,
                        'snippet': snippet[:200] if snippet else "No descriptin available"
                        # 'snippet': snippet[:200] if snippet else ""
                    })

            if len(extracted_results) >= 3:

                break

        if extracted_results:

            result_text = "Here's what I found on the official NYC ACS website:\n\n"

            for i, result in enumerate(extracted_results, 1):

                result_text += f"**{i}. {result['title']}**\n"
                result_text += f"{result['snippet']}\n"
                extracted_text = extract_content_from_acs_page(result['link'])
                result_text += f"{extracted_text}\n\n"

            return result_text

        return "I couldn't find a relevant answer on the NYC ACS site."

    except Exception as e:

        print(f"Error in web scraping: {str(e)}")

        return None
 
def generate_direct_answer(question: str) -> str:

    """

    Generate a direct answer when other methods fail

    """

    try:

        # Analyze the question to provide a more helpful response

        question_lower = question.lower()

        # Common question patterns and responses

        if any(keyword in question_lower for keyword in ['what is', 'what are', 'define', 'definition']):

            if 'acs' in question_lower:

                return """I couldn't find an exact match in the ACS FAQs. Based on the context, ACS could refer to:
 
**Possible meanings:**

• **Administration for Children's Services** - A government agency that provides child welfare services

• **American Chemical Society** - A professional organization for chemists

• **American Cancer Society** - A health organization focused on cancer research and support

• **Access Control System** - A security system for managing entry permissions
 
**For more specific information about ACS in your context, you can:**

• Contact your local ACS office directly

• Visit their official website

• Check their official documentation

• Ask a more specific question about the particular ACS service you're interested in
 
Would you like me to help you find contact information for a specific ACS organization?"""

            elif 'nyc' in question_lower and 'acs' in question_lower:

                return """I couldn't find an exact match in the ACS FAQs. For NYC ACS (Administration for Children's Services):
 
**NYC ACS Overview:**

• NYC ACS is the city agency responsible for child welfare services in New York City

• They provide child protective services, foster care, adoption services, and family support

• ACS works to ensure the safety and well-being of children and families
 
**Common Services:**

• Child protective investigations

• Foster care and adoption services

• Family support and prevention programs

• Emergency services for children in crisis
 
**For specific information:**

• Visit: nyc.gov/site/acs

• Call: 311 for general NYC services

• Emergency child abuse hotline: 1-800-342-3720
 
**Note:** This is general information. For specific questions about cases, services, or procedures, please contact NYC ACS directly through their official channels."""

        elif any(keyword in question_lower for keyword in ['how to', 'how do', 'process', 'procedure']):

            return f"""I couldn't find an exact match in the ACS FAQs for your question about "{question}".
 
**For process and procedure questions:**

• Contact ACS directly for the most accurate information

• Visit their official website for detailed guides

• Speak with a caseworker or representative

• Check their official documentation
 
**General steps for most ACS processes:**

1. Initial contact or application

2. Documentation review

3. Assessment or investigation (if applicable)

4. Service planning

5. Implementation and follow-up
 
**Important:** Procedures can vary by location and specific circumstances. Always verify information through official ACS channels."""

        else:

            return f"""I couldn't find an exact match in the ACS FAQs for your question: "{question}"
 
**To get accurate information:**

• Contact ACS directly through their official channels

• Visit their official website

• Speak with a caseworker or representative

• Check their current documentation and policies
 
**Alternative resources:**

• Local social services office

• Community organizations that work with ACS

• Legal aid societies (for legal questions)

• Professional associations related to your specific question
 
**Need immediate help?**

• For emergencies: Call 911

• For child abuse reports: Call the child abuse hotline

• For general questions: Contact your local ACS office
 
Would you like help finding contact information for your local ACS office?"""

    except Exception as e:

        return f"""I couldn't find an exact match in the ACS FAQs for your question: "{question}"
 
**For the most accurate information:**

• Contact ACS directly through their official website

• Call their main office or helpline

• Visit their local office in person

• Check their official documentation
 
**Emergency contacts:**

• For immediate child safety concerns: Call 911

• For non-emergency questions: Contact your local ACS office
 
I apologize that I couldn't provide a more specific answer. ACS policies and procedures can be complex and vary by location."""
 
 
# Enhanced search with conversation flow and fallback sequence

def search_with_conversation_flow(question: str) -> dict:

    """

    Enhanced conversation flow with multiple fallback methods

    """

    try:

        # Try the complete fallback sequence immediately

        result = search_duckduckgo_for_answer(question)

        # If we got a good result, return it

        if result and len(result.strip()) > 50:

            return {"answer": result, "needs_confirmation": False}

        # If all methods failed, ask for confirmation to try alternative approaches

        return {

            "answer": f"I couldn't find comprehensive information about '{question}' in the ACS FAQs or through web search. Would you like me to provide general guidance or contact information instead?",

            "needs_confirmation": True,

            "search_query": question

        }

    except Exception as e:

        return {"answer": f"Sorry, I encountered an error: {str(e)}", "needs_confirmation": False}
 
 
def search_duckduckgo_web_scraping(question: str) -> str:

    """

    Simplified web scraping for backward compatibility

    """

    return search_duckduckgo_web_scraping_with_content(question) or generate_direct_answer(question)
 
def extract_content_from_acs_page(url: str, max_paragraphs: int = 3) -> str:
    """
    Fetches and extracts readable text from a given ACS page.
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Collect paragraphs from main content
        paragraphs = soup.find_all('p')
        clean_paragraphs = []

        for p in paragraphs:
            text = p.get_text(strip=True)
            if len(text) > 40:  # Filter out short or empty lines
                clean_paragraphs.append(text)
            if len(clean_paragraphs) >= max_paragraphs:
                break

        if clean_paragraphs:
            return "\n\n".join(clean_paragraphs)
        else:
            return "No relevant text content found on this page."

    except Exception as e:
        print(f"Error extracting from {url}: {str(e)}")
        return "Couldn't extract content from the official page." 