"""Real MCP Knowledge Server - reads from actual files.

This server reads compliance rules from .txt and .md files in knowledge/sources/.
Replaces MockKnowledgeServer with real file reading.

Supports:
- Filtering rules (scheduling_policy.txt)
- Scoring weights (scoring_weights.txt)
- Payer rules (medicare_rules.txt)
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Any


class FileKnowledgeServer:
    """Real implementation that reads from .txt and .md files.
    
    Loads all compliance documents from knowledge/sources/ on startup.
    Provides simple keyword-based search to return relevant rules.
    """
    
    def __init__(self, knowledge_path: str = None):
        """Initialize knowledge server and load all files.
        
        Args:
            knowledge_path: Path to knowledge directory (default: knowledge/sources)
        """
        self.name = "knowledge-server"
        
        # Set knowledge path
        if knowledge_path is None:
            # Try to find knowledge/sources relative to this file
            base_path = Path(__file__).parent.parent.parent / "knowledge" / "sources"
            self.knowledge_path = base_path
        else:
            self.knowledge_path = Path(knowledge_path)
        
        self.cache = {}  # Cache loaded files
        
        print(f"[REAL MCP] Knowledge Server initialized (FILE-BASED)")
        print(f"[REAL MCP] Reading from: {self.knowledge_path}")
        
        # Pre-load all knowledge files
        self._load_all_files()
    
    def _load_all_files(self):
        """Load all .txt and .md files into cache."""
        if not self.knowledge_path.exists():
            print(f"[REAL MCP] ⚠️  Warning: Knowledge path does not exist: {self.knowledge_path}")
            print(f"[REAL MCP] Creating directory...")
            self.knowledge_path.mkdir(parents=True, exist_ok=True)
            return
        
        files_loaded = 0
        
        # Load .txt files
        for file_path in self.knowledge_path.rglob("*.txt"):
            key = file_path.stem
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.cache[key] = {
                        "content": f.read(),
                        "path": str(file_path),
                        "type": "clinic" if "clinic" in str(file_path) else "payer",
                        "format": "txt"
                    }
                files_loaded += 1
                print(f"[REAL MCP]   ✓ Loaded: {file_path.stem}.txt")
            except Exception as e:
                print(f"[REAL MCP]   ✗ Error loading {file_path}: {e}")
        
        # Load .md files
        for file_path in self.knowledge_path.rglob("*.md"):
            key = file_path.stem
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.cache[key] = {
                        "content": f.read(),
                        "path": str(file_path),
                        "type": "clinic" if "clinic" in str(file_path) else "payer",
                        "format": "md"
                    }
                files_loaded += 1
                print(f"[REAL MCP]   ✓ Loaded: {file_path.stem}.md")
            except Exception as e:
                print(f"[REAL MCP]   ✗ Error loading {file_path}: {e}")
        
        print(f"[REAL MCP] Total files loaded: {files_loaded}")
        
        if files_loaded == 0:
            print(f"[REAL MCP] ⚠️  No knowledge files found. Using fallback rules.")
    
    def search_knowledge(self, query: str, source: str = "all") -> str:
        """Search knowledge files for relevant information.
        
        Args:
            query: Search query (e.g., "provider matching rules")
            source: Filter by source (clinic, payers, all)
        
        Returns:
            Relevant knowledge text from files
        """
        print(f"[REAL MCP] search_knowledge(query='{query}', source='{source}')")
        
        query_lower = query.lower()
        results = []
        
        # Simple keyword matching based on query
        if ("filter" in query_lower or "matching" in query_lower or 
            "provider" in query_lower or "compliance" in query_lower):
            # Look for scheduling policy
            if "scheduling_policy" in self.cache:
                results.append({
                    "source": "scheduling_policy",
                    "content": self.cache["scheduling_policy"]["content"]
                })
                print(f"[REAL MCP]   → Found: scheduling_policy.txt")
        
        if "scoring" in query_lower or "weights" in query_lower or "rank" in query_lower:
            # Look for scoring weights
            if "scoring_weights" in self.cache:
                results.append({
                    "source": "scoring_weights",
                    "content": self.cache["scoring_weights"]["content"]
                })
                print(f"[REAL MCP]   → Found: scoring_weights.txt")
        
        if "medicare" in query_lower or "payer" in query_lower or "insurance" in query_lower:
            # Look for payer rules
            if "medicare_rules" in self.cache:
                results.append({
                    "source": "medicare_rules",
                    "content": self.cache["medicare_rules"]["content"]
                })
                print(f"[REAL MCP]   → Found: medicare_rules.txt")
        
        # Filter by source type if specified
        if source != "all":
            results = [r for r in results if self.cache.get(r["source"], {}).get("type") == source]
        
        # If no specific matches, return all clinic rules as fallback
        if not results and self.cache:
            print(f"[REAL MCP]   → No specific match, returning all clinic rules")
            results = [
                {"source": k, "content": v["content"]} 
                for k, v in self.cache.items()
                if v["type"] == "clinic"
            ]
        
        # If still nothing, use hardcoded fallback
        if not results:
            print(f"[REAL MCP]   → Using hardcoded fallback (no files found)")
            return self._get_fallback_knowledge(query_lower)
        
        # Combine results with source attribution
        combined = []
        for result in results:
            combined.append(f"SOURCE: {result['source']}\n\n{result['content']}")
        
        return "\n\n" + "="*60 + "\n\n".join(combined)
    
    def _get_fallback_knowledge(self, query_lower: str) -> str:
        """Fallback hardcoded knowledge if no files found."""
        if "filter" in query_lower or "matching" in query_lower:
            return """
PROVIDER MATCHING RULES (FALLBACK)

Filter 1: Skills & Certification Match
- Orthopedic cases require "Orthopedic PT" certification
- Neurological cases require "Neurological PT" certification

Filter 2: Location Constraint
- Provider must be within patient's max distance
- Default: 10 miles from patient address

Source: Fallback (no files found)
"""
        elif "scoring" in query_lower:
            return """
PROVIDER SCORING WEIGHTS (FALLBACK)

Total: 150 points
- Continuity: 40 pts
- Specialty Match: 35 pts
- Patient Preference: 30 pts
- Schedule Load: 25 pts
- Day/Time Match: 20 pts

Source: Fallback (no files found)
"""
        else:
            return "No knowledge found for query."
    
    def get_all_rules(self, rule_type: str = "all") -> Dict[str, str]:
        """Get all rules of a specific type.
        
        Args:
            rule_type: "filtering", "scoring", "payer", or "all"
        
        Returns:
            Dictionary of rule name to content
        """
        if rule_type == "all":
            return {k: v["content"] for k, v in self.cache.items()}
        
        return {
            k: v["content"] for k, v in self.cache.items()
            if rule_type.lower() in k.lower()
        }
    
    def reload_files(self):
        """Reload all files from disk (useful for live updates)."""
        print(f"[REAL MCP] Reloading files from {self.knowledge_path}...")
        self.cache = {}
        self._load_all_files()
        print(f"[REAL MCP] Reload complete: {len(self.cache)} files")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get information about cached files.
        
        Returns:
            Dictionary with cache statistics
        """
        return {
            "total_files": len(self.cache),
            "files": list(self.cache.keys()),
            "by_type": {
                "clinic": len([k for k, v in self.cache.items() if v["type"] == "clinic"]),
                "payer": len([k for k, v in self.cache.items() if v["type"] == "payer"])
            }
        }


def create_file_knowledge_server() -> FileKnowledgeServer:
    """Factory function to create file-based knowledge server."""
    return FileKnowledgeServer()


if __name__ == "__main__":
    # Test the file knowledge server
    print("=== FILE KNOWLEDGE SERVER TEST ===\n")
    
    server = FileKnowledgeServer()
    
    print("\n" + "="*60)
    print("TEST 1: Cache Info")
    print("="*60)
    info = server.get_cache_info()
    print(f"Total files: {info['total_files']}")
    print(f"Files: {info['files']}")
    print(f"By type: {info['by_type']}")
    
    print("\n" + "="*60)
    print("TEST 2: Search for filtering rules")
    print("="*60)
    rules = server.search_knowledge("provider matching filters")
    print(f"Found {len(rules)} characters")
    print(rules[:300])  # First 300 chars
    
    print("\n" + "="*60)
    print("TEST 3: Search for scoring weights")
    print("="*60)
    weights = server.search_knowledge("scoring weights")
    print(f"Found {len(weights)} characters")
    print(weights[:300])
    
    print("\n✅ File knowledge server test complete!")

