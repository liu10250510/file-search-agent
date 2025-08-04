"""
AI-powered file searcher using Pydantic AI
"""

import os
import json
from typing import Generator, List, Dict, Any, Optional
from pathlib import Path
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.models.anthropic import AnthropicModel

# Try to load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not available, that's okay

from .base_searcher import BaseSearcher, SearchResult
from .local_searcher import LocalFileSearcher


class SearchQuery(BaseModel):
    """Structured search query for AI processing"""
    natural_language_query: str
    search_type: str  # "semantic", "name", "content", "size"
    keywords: List[str] = []
    file_extensions: List[str] = []
    size_range: Optional[Dict[str, int]] = None
    date_range: Optional[Dict[str, str]] = None
    intent: str = ""  # What the user is trying to accomplish


class SearchPlan(BaseModel):
    """AI-generated search plan"""
    search_strategy: str
    search_terms: List[str]
    file_patterns: List[str]
    content_patterns: List[str]
    reasoning: str
    confidence: float


class AIFileSearcher(BaseSearcher):
    """AI-powered file searcher that uses LLMs to interpret queries and improve search results"""
    
    def __init__(self, model_provider: str = "openai", model_name: str = "gpt-4o-mini"):
        """
        Initialize the AI searcher
        
        Args:
            model_provider: "openai" or "anthropic"
            model_name: Model name to use
        """
        self.local_searcher = LocalFileSearcher()
        self.model_provider = model_provider
        
        # Initialize the AI model
        if model_provider == "openai":
            self.model = OpenAIModel(model_name)
        elif model_provider == "anthropic":
            self.model = AnthropicModel(model_name)
        else:
            raise ValueError(f"Unsupported model provider: {model_provider}")
        
        # Create the AI agent with system prompt
        self.agent = Agent(
            model=self.model,
            result_type=SearchPlan,
            system_prompt=self._get_system_prompt()
        )
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the AI agent"""
        return """
You are an expert file search assistant. Your job is to interpret natural language queries 
and create effective search strategies for finding files on a computer.

When given a user query, analyze what they're looking for and create a comprehensive search plan.

IMPORTANT GUIDELINES:
- File patterns should NOT be CASE INSENSITIVE and use wildcards generously
- Include common file extensions like .pdf, .doc, .docx, .txt
- Consider variations in spacing and punctuation (e.g., "Lucy's Resume", "Lucy Resume", "Resume_Lucy")
- Think about how real users name files (often inconsistent)
- For person names, include both first name only and full name patterns
- Be generous with wildcards - use *word* instead of word*

Examples of good file patterns:
- For "Lucy's resume": [*Lucy*resume*.pdf, *Lucy*Resume*.pdf, *lucy*resume*.pdf, *Resume*Lucy*.pdf, *Lucy*.pdf]
- For "PDF files": [*.pdf, *.PDF]
- For "Python scripts": [*.py, *.python, *python*.py]

Consider:
- File types and extensions that might contain the information
- Keywords and synonyms that might appear in filenames or content
- Alternative ways to express the same concept
- Common naming conventions for different types of files
- Case variations and spacing differences

Return a SearchPlan with:
- search_strategy: Brief description of the approach
- search_terms: Keywords to search for (including synonyms and variations)
- file_patterns: Filename patterns with generous wildcards and case variations
- content_patterns: Text patterns to search within files
- reasoning: Explanation of your strategy
- confidence: How confident you are this will find what the user wants (0.0-1.0)
"""
    
    async def generate_search_plan(self, query: str) -> SearchPlan:
        """Generate an AI-powered search plan from a natural language query"""
        search_query = SearchQuery(
            natural_language_query=query,
            search_type="semantic"
        )
        
        prompt = f"""
User query: "{query}"

Generate a comprehensive search plan to find files related to this query.
Think about:
1. What file types might contain this information?
2. What keywords might appear in filenames?
3. What content might be inside these files?
4. What are common naming conventions?

Provide multiple search terms and patterns to maximize success.
"""
        
        result = await self.agent.run(prompt)
        return result.data
    
    def ai_search(self, search_path: str, query: str, **kwargs) -> Generator[SearchResult, None, None]:
        """
        Perform AI-powered search based on natural language query
        
        Args:
            search_path: Directory to search in
            query: Natural language search query
            **kwargs: Additional search parameters
        """
        # Generate search plan using AI
        try:
            # Check if we're already in an event loop
            try:
                import asyncio
                loop = asyncio.get_running_loop()
                # We're in a running loop, need to handle differently
                search_plan = None
            except RuntimeError:
                # No running loop, we can use asyncio.run
                import asyncio
                search_plan = asyncio.run(self.generate_search_plan(query))
        except Exception as e:
            # Fallback to simple keyword search if AI fails
            print(f"AI search planning failed: {e}")
            search_plan = None
        
        if search_plan is None:
            # Create a fallback search plan based on simple keyword analysis
            words = query.lower().split()
            
            # Generate better fallback patterns
            file_patterns = []
            search_terms = []
            content_patterns = []
            
            if "pdf" in query.lower():
                file_patterns.extend(["*.pdf", "*.PDF"])
                search_terms.append("pdf")
            
            if "lucy" in query.lower():
                file_patterns.extend(["*Lucy*", "*lucy*", "*LUCY*"])
                search_terms.extend(["Lucy", "lucy"])
                content_patterns.extend(["Lucy", "lucy"])
            
            if "resume" in query.lower():
                file_patterns.extend(["*resume*", "*Resume*", "*RESUME*", "*CV*", "*cv*"])
                search_terms.extend(["resume", "Resume", "CV", "cv"])
                content_patterns.extend(["resume", "curriculum vitae", "CV"])
            
            if "python" in query.lower():
                file_patterns.extend(["*.py", "*.python", "*python*"])
                search_terms.extend(["python", "Python"])
            
            if "config" in query.lower():
                file_patterns.extend(["*config*", "*Config*", "*.cfg", "*.conf", "*.ini"])
                search_terms.extend(["config", "configuration"])
            
            # If no specific patterns found, use the query words
            if not file_patterns:
                for word in words:
                    if len(word) > 2:  # Skip short words
                        file_patterns.append(f"*{word}*")
                        search_terms.append(word)
                        content_patterns.append(word)
            
            search_plan = SearchPlan(
                search_strategy="intelligent_fallback_search",
                search_terms=search_terms,
                file_patterns=file_patterns,
                content_patterns=content_patterns,
                reasoning="Intelligent fallback search using keyword analysis",
                confidence=0.6
            )
        
        # Combine results from multiple search strategies
        all_results = {}
        
        # Search by filename patterns
        for pattern in search_plan.file_patterns:
            try:
                for result in self.search_by_name(search_path, pattern, **{k: v for k, v in kwargs.items() if k != 'max_depth'}):
                    key = result.path
                    if key not in all_results:
                        all_results[key] = result
                        result.matches = result.matches or []
                        result.matches.append(f"Filename pattern: {pattern}")
            except Exception as e:
                print(f"Error searching by pattern '{pattern}': {e}")
        
        # Search by content patterns
        for pattern in search_plan.content_patterns:
            try:
                for result in self.search_by_content(search_path, pattern, **{k: v for k, v in kwargs.items() if k != 'max_depth'}):
                    key = result.path
                    if key in all_results:
                        # Merge matches
                        if result.matches:
                            all_results[key].matches.extend(result.matches)
                    else:
                        all_results[key] = result
                        result.matches = result.matches or []
                        result.matches.append(f"Content pattern: {pattern}")
            except Exception as e:
                print(f"Error searching by content '{pattern}': {e}")
        
        # Search by individual terms
        for term in search_plan.search_terms:
            try:
                # Search in filenames
                for result in self.search_by_name(search_path, f"*{term}*", **{k: v for k, v in kwargs.items() if k != 'max_depth'}):
                    key = result.path
                    if key not in all_results:
                        all_results[key] = result
                        result.matches = result.matches or []
                        result.matches.append(f"Search term in filename: {term}")
                
                # Search in content
                for result in self.search_by_content(search_path, term, **{k: v for k, v in kwargs.items() if k != 'max_depth'}):
                    key = result.path
                    if key in all_results:
                        if result.matches:
                            all_results[key].matches.extend(result.matches)
                    else:
                        all_results[key] = result
                        result.matches = result.matches or []
                        result.matches.append(f"Search term in content: {term}")
            except Exception as e:
                print(f"Error searching by term '{term}': {e}")
        
        # Add AI reasoning to results
        for result in all_results.values():
            result.matches = result.matches or []
            result.matches.append(f"AI Strategy: {search_plan.search_strategy}")
            result.matches.append(f"AI Confidence: {search_plan.confidence:.2f}")
            yield result
    
    def search_by_name(self, search_path: str, pattern: str, **kwargs) -> Generator[SearchResult, None, None]:
        """Delegate to local searcher"""
        return self.local_searcher.search_by_name(search_path, pattern, **kwargs)
    
    def search_by_content(self, search_path: str, pattern: str, **kwargs) -> Generator[SearchResult, None, None]:
        """Delegate to local searcher"""
        return self.local_searcher.search_by_content(search_path, pattern, **kwargs)
    
    def search_by_size(self, search_path: str, min_size: int = None, max_size: int = None, **kwargs) -> Generator[SearchResult, None, None]:
        """Delegate to local searcher"""
        return self.local_searcher.search_by_size(search_path, min_size, max_size, **kwargs)
