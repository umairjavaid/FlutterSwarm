"""
LLM Response Parsing Monitor and Debugger

This module provides monitoring and debugging capabilities for LLM response parsing issues.
It helps identify patterns in failed responses and provides insights for improvement.
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
import logging

# Avoid circular imports - don't import EnhancedLLMResponseParser here


class ParsingMonitor:
    """Monitor and analyze LLM response parsing patterns."""
    
    def __init__(self, log_file: str = "parsing_monitor.log"):
        self.log_file = log_file
        self.parsing_attempts = []
        self.success_patterns = defaultdict(int)
        self.failure_patterns = defaultdict(int)
        self.logger = logging.getLogger("ParsingMonitor")
        
    def log_parsing_attempt(self, response: str, success: bool, 
                          parse_method: str, error: Optional[str] = None,
                          files_extracted: int = 0):
        """Log a parsing attempt for analysis."""
        attempt = {
            "timestamp": datetime.now().isoformat(),
            "response_preview": response[:500] if response else "",
            "response_length": len(response) if response else 0,
            "success": success,
            "parse_method": parse_method,
            "error": error,
            "files_extracted": files_extracted,
            "response_characteristics": self._analyze_response(response)
        }
        
        self.parsing_attempts.append(attempt)
        
        # Update pattern tracking
        if success:
            self.success_patterns[parse_method] += 1
        else:
            self.failure_patterns[f"{parse_method}:{error[:50] if error else 'unknown'}"] += 1
        
        # Write to log file
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(attempt) + "\n")
    
    def _analyze_response(self, response: str) -> Dict[str, Any]:
        """Analyze response characteristics."""
        if not response:
            return {"empty": True}
        
        characteristics = {
            "starts_with_json": response.strip().startswith('{'),
            "ends_with_json": response.strip().endswith('}'),
            "has_code_blocks": '```' in response,
            "has_json_blocks": '```json' in response,
            "has_dart_blocks": '```dart' in response,
            "has_file_paths": bool(re.search(r'lib/[\w/]+\.dart', response)),
            "has_explanatory_text": bool(re.search(r'(here\'s|this is|below|following)', response, re.I)),
            "json_brace_balance": response.count('{') - response.count('}'),
            "likely_pure_json": self._is_likely_pure_json(response)
        }
        
        return characteristics
    
    def _is_likely_pure_json(self, response: str) -> bool:
        """Check if response is likely pure JSON."""
        trimmed = response.strip()
        if not (trimmed.startswith('{') and trimmed.endswith('}')):
            return False
        
        try:
            json.loads(trimmed)
            return True
        except:
            return False
    
    def get_parsing_stats(self) -> Dict[str, Any]:
        """Get parsing statistics."""
        total_attempts = len(self.parsing_attempts)
        successful = sum(1 for a in self.parsing_attempts if a["success"])
        
        stats = {
            "total_attempts": total_attempts,
            "successful": successful,
            "failed": total_attempts - successful,
            "success_rate": successful / total_attempts if total_attempts > 0 else 0,
            "successful_methods": dict(self.success_patterns),
            "failure_patterns": dict(self.failure_patterns),
            "common_characteristics": self._analyze_common_patterns()
        }
        
        return stats
    
    def _analyze_common_patterns(self) -> Dict[str, Any]:
        """Analyze common patterns in successful vs failed attempts."""
        if not self.parsing_attempts:
            return {}
        
        successful_chars = defaultdict(int)
        failed_chars = defaultdict(int)
        
        for attempt in self.parsing_attempts:
            chars = attempt.get("response_characteristics", {})
            target = successful_chars if attempt["success"] else failed_chars
            
            for key, value in chars.items():
                if isinstance(value, bool) and value:
                    target[key] += 1
        
        total_success = sum(1 for a in self.parsing_attempts if a["success"])
        total_failed = len(self.parsing_attempts) - total_success
        
        patterns = {
            "successful_patterns": {
                k: v / total_success if total_success > 0 else 0 
                for k, v in successful_chars.items()
            },
            "failed_patterns": {
                k: v / total_failed if total_failed > 0 else 0 
                for k, v in failed_chars.items()
            }
        }
        
        return patterns
    
    def generate_report(self) -> str:
        """Generate a detailed parsing analysis report."""
        stats = self.get_parsing_stats()
        
        report = f"""
# LLM Response Parsing Analysis Report
Generated: {datetime.now().isoformat()}

## Overall Statistics
- Total Parsing Attempts: {stats['total_attempts']}
- Successful: {stats['successful']} ({stats['success_rate']:.1%})
- Failed: {stats['failed']} ({100 - stats['success_rate'] * 100:.1%})

## Successful Parsing Methods
"""
        
        for method, count in stats['successful_methods'].items():
            report += f"- {method}: {count} times\n"
        
        report += "\n## Common Failure Patterns\n"
        for pattern, count in sorted(stats['failure_patterns'].items(), 
                                   key=lambda x: x[1], reverse=True)[:10]:
            report += f"- {pattern}: {count} times\n"
        
        report += "\n## Response Characteristics Analysis\n"
        common = stats.get('common_characteristics', {})
        
        if common:
            report += "\n### Successful Responses Typically Have:\n"
            for char, pct in sorted(common.get('successful_patterns', {}).items(), 
                                   key=lambda x: x[1], reverse=True):
                if pct > 0.3:  # Show characteristics present in >30% of successful cases
                    report += f"- {char}: {pct:.1%}\n"
            
            report += "\n### Failed Responses Typically Have:\n"
            for char, pct in sorted(common.get('failed_patterns', {}).items(), 
                                   key=lambda x: x[1], reverse=True):
                if pct > 0.3:
                    report += f"- {char}: {pct:.1%}\n"
        
        report += self._generate_recommendations()
        
        return report
    
    def _generate_recommendations(self) -> str:
        """Generate recommendations based on analysis."""
        stats = self.get_parsing_stats()
        recommendations = "\n## Recommendations\n"
        
        if stats['success_rate'] < 0.7:
            recommendations += "- ⚠️ Low success rate detected. Consider:\n"
            recommendations += "  - Adding more explicit JSON formatting instructions\n"
            recommendations += "  - Using few-shot examples in prompts\n"
            recommendations += "  - Implementing more robust parsing strategies\n"
        
        common = stats.get('common_characteristics', {})
        failed = common.get('failed_patterns', {})
        
        if failed.get('has_explanatory_text', 0) > 0.5:
            recommendations += "- 📝 Many failed responses contain explanatory text. Consider:\n"
            recommendations += "  - Emphasizing 'ONLY JSON' in prompts\n"
            recommendations += "  - Adding negative examples showing what NOT to do\n"
        
        if failed.get('json_brace_balance', 0) != 0:
            recommendations += "- 🔧 JSON brace imbalance detected in failures. Consider:\n"
            recommendations += "  - Implementing brace-counting validation\n"
            recommendations += "  - Using more forgiving JSON parsers\n"
        
        return recommendations


# Integration with Implementation Agent
# Note: This was moved directly into EnhancedLLMResponseParser
# to avoid circular imports

# Alternative implementation that doesn't rely on inheritance
def create_monitored_parser(logger: logging.Logger, monitor_log_file: str = None):
    """
    Creates a monitored parser without circular imports.
    
    Returns:
        A tuple of (parser, monitor) that work together
    """
    from utils.enhancedLLMResponseParser import EnhancedLLMResponseParser
    
    monitor = ParsingMonitor(log_file=monitor_log_file or "parsing_monitor.log")
    parser = EnhancedLLMResponseParser(logger, monitor=monitor)
    
    return parser, monitor


# Usage example for debugging
def debug_parsing_issues(log_file: str = "parsing_monitor.log", 
                       output_file: str = "parsing_analysis_report.md"):
    """
    Debug parsing issues by analyzing recent attempts.
    
    Args:
        log_file: Path to the parsing monitor log file
        output_file: Path to save the analysis report
    """
    monitor = ParsingMonitor()
    
    # Load recent parsing attempts from log
    try:
        with open(log_file, 'r') as f:
            for line in f:
                if line.strip():
                    try:
                        attempt = json.loads(line)
                        monitor.parsing_attempts.append(attempt)
                    except json.JSONDecodeError:
                        print(f"Warning: Skipping invalid JSON line in log file: {line[:50]}...")
    except FileNotFoundError:
        print(f"No parsing log found at {log_file}. Run the system first to generate logs.")
        return
    
    # Generate and print report
    report = monitor.generate_report()
    print(report)
    
    # Save report to file
    with open(output_file, 'w') as f:
        f.write(report)
    
    print(f"\nReport saved to {output_file}")


if __name__ == "__main__":
    # Run debugging analysis
    debug_parsing_issues()