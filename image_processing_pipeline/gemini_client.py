# """
# Gemini API client module for parsing OCR text extracted from receipts.
# Handles sending text to Google's Gemini API and parsing the structured information.
# """

# import json
# import logging
# import os
# import sys
# from typing import Any, Dict, Optional

# # Set up logger
# logger = logging.getLogger(__name__)

# class GeminiClient:
#     """Client for interacting with Google's Gemini API to parse receipt text."""
    
#     def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.0-flash"):
#         """
#         Initialize the Gemini API client.
        
#         Args:
#             api_key: Gemini API key (defaults to GEMINI_API_KEY environment variable)
#             model: Gemini model to use (defaults to gemini-2.0-flash)
#         """
#         try:
#             # Clean up the API key if it has any extra characters
#             self.api_key = api_key or os.environ.get("GEMINI_API_KEY", "")
#             self.api_key = self.api_key.strip().replace("-n ", "").replace('"', "")
            
#             if not self.api_key:
#                 logger.error("No Gemini API key provided")
#                 print("DIRECT PRINT: No Gemini API key provided")
#                 raise ValueError("No Gemini API key provided. Set GEMINI_API_KEY environment variable.")
                
#             self.model = model
            
#             # Import genai here to delay any potential errors until the API key is cleaned
#             import google.generativeai as genai

#             # Configure the Gemini client with additional safety settings to prevent errors
#             genai.configure(
#                 api_key=self.api_key,
#                 transport="rest"  # Force REST transport instead of gRPC
#             )
            
#             # Test the API key by trying to get the model info
#             # Just accessing the models without trying to count them
#             _ = genai.list_models()
#             logger.info(f"Successfully connected to Gemini API")
#             print(f"DIRECT PRINT: Successfully connected to Gemini API")
            
#             self._genai = genai
#             logger.info(f"Gemini client initialized with model: {self.model}")
#             print(f"DIRECT PRINT: Gemini client initialized with model: {self.model}")
            
#         except ImportError as e:
#             logger.error(f"Failed to import google.generativeai: {e}")
#             print(f"DIRECT PRINT: Failed to import google.generativeai: {e}")
#             print("DIRECT PRINT: Please install with: pip install google-generativeai")
#             raise
#         except Exception as e:
#             logger.error(f"Error initializing Gemini client: {e}")
#             print(f"DIRECT PRINT: Error initializing Gemini client: {e}")
#             raise
        
#     def parse_receipt_text(self, text: str) -> Dict[str, Any]:
#         """
#         Parse OCR-extracted text to extract structured receipt information.
        
#         Args:
#             text: Raw OCR text from a receipt image
            
#         Returns:
#             Dictionary with structured receipt information
            
#         Raises:
#             Exception: If Gemini API request fails
#         """
#         try:
#             logger.info(f"Sending OCR text to Gemini API for parsing")
#             print("DIRECT PRINT: Sending OCR text to Gemini API for parsing")
            
#             # Craft the prompt
#             prompt = self._create_parsing_prompt(text)
            
#             # Get the model using the stored genai reference
#             model = self._genai.GenerativeModel(model_name=self.model)
            
#             # Configure generation parameters - using a dictionary instead of types
#             # to avoid potential compatibility issues
#             generation_config = {
#                 "temperature": 0.2,
#                 "top_k": 40,
#                 "top_p": 0.95,
#                 "max_output_tokens": 1024,
#             }
            
#             # Send request to Gemini API with safety settings and fallbacks
#             try:
#                 response = model.generate_content(
#                     prompt,
#                     generation_config=generation_config
#                 )
                
#                 # Extract the text response from Gemini
#                 if not response or not hasattr(response, 'text') or not response.text:
#                     logger.warning("Empty response from Gemini API, trying alternative approach")
#                     print("DIRECT PRINT: Empty response from Gemini API, trying alternative approach")
                    
#                     # Alternative approach with simpler settings
#                     response = model.generate_content(prompt)
#                     model_response = response.text
#                 else:
#                     model_response = response.text
                    
#             except Exception as api_error:
#                 logger.warning(f"Error with primary Gemini API call: {api_error}, trying fallback")
#                 print(f"DIRECT PRINT: Error with primary Gemini API call: {api_error}, trying fallback")
                
#                 # Fallback to simpler approach
#                 response = model.generate_content(prompt)
#                 model_response = response.text
            
#             # Try to extract JSON from the response
#             result = self._extract_json_from_response(model_response)
#             print(f"DIRECT PRINT: Extracted receipt data: {json.dumps(result)}")
#             return result
                
#         except Exception as e:
#             logger.error(f"Error parsing receipt with Gemini API: {str(e)}")
#             print(f"DIRECT PRINT: Error parsing receipt with Gemini API: {str(e)}")
#             print(f"DIRECT PRINT: Exception type: {type(e).__name__}")
#             print(f"DIRECT PRINT: Python version: {sys.version}")
#             return self._get_empty_result()
    
#     def _create_parsing_prompt(self, text: str) -> str:
#         """
#         Create a prompt for the Gemini API to parse receipt text.
        
#         Args:
#             text: Raw OCR text from a receipt
            
#         Returns:
#             Formatted prompt string
#         """
#         prompt = f"""
# You are a specialized receipt parser. I'll provide you with raw OCR text extracted from a receipt image.
# Extract the following information in JSON format:
# - store_name: The name of the store/business
# - store_address: The full address of the store
# - date: The purchase date in YYYY-MM-DD format
# - time: The purchase time
# - total_amount: The total amount paid (just the number, without currency symbols)

# For any fields you cannot confidently extract, use null.

# Here's the OCR text from the receipt:
# ```
# {text}
# ```

# Respond with a JSON object containing only these fields, nothing else.
# Example format:
# {{
#   "store_name": "Example Store",
#   "store_address": "123 Main St, City, State ZIP",
#   "date": "2023-01-01",
#   "time": "14:30",
#   "total_amount": 42.99
# }}
# """
#         return prompt
    
#     def _extract_json_from_response(self, response_text: str) -> Dict[str, Any]:
#         """
#         Extract a JSON object from the Gemini response text.
        
#         Args:
#             response_text: Raw text response from Gemini API
            
#         Returns:
#             Parsed JSON as a dictionary
#         """
#         try:
#             print(f"DIRECT PRINT: Raw Gemini response: {response_text[:200]}...")
            
#             # Try to find JSON object in the response
#             start_idx = response_text.find('{')
#             end_idx = response_text.rfind('}')
            
#             if start_idx != -1 and end_idx != -1:
#                 json_str = response_text[start_idx:end_idx + 1]
#                 print(f"DIRECT PRINT: Extracted JSON string: {json_str}")
                
#                 result = json.loads(json_str)
                
#                 # Ensure all expected fields are present
#                 expected_fields = ["store_name", "store_address", "date", "time", "total_amount"]
#                 for field in expected_fields:
#                     if field not in result:
#                         result[field] = None
                
#                 logger.info(f"Successfully extracted receipt information: {list(result.keys())}")
#                 return result
#             else:
#                 logger.error("No JSON object found in Gemini response")
#                 print("DIRECT PRINT: No JSON object found in Gemini response")
#                 return self._get_empty_result()
                
#         except json.JSONDecodeError as e:
#             logger.error(f"Error parsing JSON from Gemini response: {e}")
#             print(f"DIRECT PRINT: Error parsing JSON from Gemini response: {e}")
#             return self._get_empty_result()
    
#     def _get_empty_result(self) -> Dict[str, Any]:
#         """
#         Get an empty result dictionary with all fields set to null.
        
#         Returns:
#             Dictionary with all fields set to null
#         """
#         return {
#             "store_name": None,
#             "store_address": None,
#             "date": None,
#             "time": None,
#             "total_amount": None
#         }

# # Create a singleton instance for use throughout the application
# try:
#     gemini_client = GeminiClient()
# except Exception as e:
#     print(f"DIRECT PRINT: Failed to initialize gemini_client at module level: {e}")
#     # Use a function to create it on-demand in case the environment variables aren't available yet
#     gemini_client = None

# def parse_receipt_text(text: str) -> Dict[str, Any]:
#     """Convenience function to parse receipt text using the singleton client."""
#     global gemini_client
    
#     # Initialize the client if needed
#     if gemini_client is None:
#         try:
#             gemini_client = GeminiClient()
#         except Exception as e:
#             print(f"DIRECT PRINT: Failed to initialize client on demand: {e}")
#             return {
#                 "store_name": None,
#                 "store_address": None,
#                 "date": None,
#                 "time": None,
#                 "total_amount": None,
#                 "error": str(e)
#             }
    
#     return gemini_client.parse_receipt_text(text)



"""
Gemini API client module for parsing OCR text extracted from receipts.
Uses Google's official genai library to interact with the Gemini API.
"""

import json
import logging
import os
import sys
from typing import Any, Dict, Optional

# Set up logger
logger = logging.getLogger(__name__)

class GeminiClient:
    """Client for interacting with Google's Gemini API to parse receipt text."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.0-flash"):
        """
        Initialize the Gemini API client.
        
        Args:
            api_key: Gemini API key (defaults to GEMINI_API_KEY environment variable)
            model: Gemini model to use (defaults to gemini-2.0-flash)
        """
        try:
            # Clean up the API key if it has any extra characters
            self.api_key = api_key or os.environ.get("GEMINI_API_KEY", "")
            self.api_key = self.api_key.strip().replace("-n ", "").replace('"', "")
            
            if not self.api_key:
                logger.error("No Gemini API key provided")
                print("DIRECT PRINT: No Gemini API key provided")
                raise ValueError("No Gemini API key provided. Set GEMINI_API_KEY environment variable.")
                
            self.model = model
            
            # Import genai here to delay any potential errors until the API key is cleaned
            try:
                from google import genai
                from google.genai import types

                # Create client with API key
                self._client = genai.Client(api_key=self.api_key)
                self._types = types
                
                logger.info(f"Gemini client initialized with model: {self.model}")
                print(f"DIRECT PRINT: Gemini client initialized with model: {self.model}")
                
            except ImportError:
                print("DIRECT PRINT: Failed to import google.genai. Please install with: pip install google-genai")
                raise
                
        except Exception as e:
            logger.error(f"Error initializing Gemini client: {e}")
            print(f"DIRECT PRINT: Error initializing Gemini client: {e}")
            raise
        
    def parse_receipt_text(self, text: str) -> Dict[str, Any]:
        """
        Parse OCR-extracted text to extract structured receipt information.
        
        Args:
            text: Raw OCR text from a receipt image
            
        Returns:
            Dictionary with structured receipt information
            
        Raises:
            Exception: If Gemini API request fails
        """
        try:
            logger.info(f"Sending OCR text to Gemini API for parsing")
            print("DIRECT PRINT: Sending OCR text to Gemini API for parsing")
            
            # Craft the prompt
            prompt = self._create_parsing_prompt(text)
            
            # Send request to Gemini API with safety settings and fallbacks
            try:
                # Use the proper configuration pattern
                response = self._client.models.generate_content(
                    model=self.model,
                    contents=[prompt],
                    config=self._types.GenerateContentConfig(
                        temperature=0.2,
                        top_p=0.95,
                        top_k=40,
                        max_output_tokens=1024
                    )
                )
                
                # Extract the response text
                model_response = response.text
                    
            except Exception as api_error:
                logger.warning(f"Error with primary Gemini API call: {api_error}, trying fallback")
                print(f"DIRECT PRINT: Error with primary Gemini API call: {api_error}, trying fallback")
                
                # Fallback to simpler approach without generation config
                response = self._client.models.generate_content(
                    model=self.model,
                    contents=[prompt]
                )
                model_response = response.text
            
            # Try to extract JSON from the response
            result = self._extract_json_from_response(model_response)
            print(f"DIRECT PRINT: Extracted receipt data: {json.dumps(result)}")
            return result
                
        except Exception as e:
            logger.error(f"Error parsing receipt with Gemini API: {str(e)}")
            print(f"DIRECT PRINT: Error parsing receipt with Gemini API: {str(e)}")
            print(f"DIRECT PRINT: Exception type: {type(e).__name__}")
            return self._get_empty_result()
    
    def _create_parsing_prompt(self, text: str) -> str:
        """
        Create a prompt for the Gemini API to parse receipt text.
        
        Args:
            text: Raw OCR text from a receipt
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""
You are a specialized receipt parser. I'll provide you with raw OCR text extracted from a receipt image.
Extract the following information in JSON format:
- store_name: The name of the store/business
- store_address: The full address of the store
- date: The purchase date in YYYY-MM-DD format
- time: The purchase time
- total_amount: The total amount paid (just the number, without currency symbols)

For any fields you cannot confidently extract, use null.

Here's the OCR text from the receipt:
```
{text}
```

Respond with a JSON object containing only these fields, nothing else.
Example format:
{{
  "store_name": "Example Store",
  "store_address": "123 Main St, City, State ZIP",
  "date": "2023-01-01",
  "time": "14:30",
  "total_amount": 42.99
}}
"""
        return prompt
    
    def _extract_json_from_response(self, response_text: str) -> Dict[str, Any]:
        """
        Extract a JSON object from the Gemini response text.
        
        Args:
            response_text: Raw text response from Gemini API
            
        Returns:
            Parsed JSON as a dictionary
        """
        try:
            print(f"DIRECT PRINT: Raw Gemini response: {response_text[:200]}...")
            
            # Try to find JSON object in the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}')
            
            if start_idx != -1 and end_idx != -1:
                json_str = response_text[start_idx:end_idx + 1]
                print(f"DIRECT PRINT: Extracted JSON string: {json_str}")
                
                result = json.loads(json_str)
                
                # Ensure all expected fields are present
                expected_fields = ["store_name", "store_address", "date", "time", "total_amount"]
                for field in expected_fields:
                    if field not in result:
                        result[field] = None
                
                logger.info(f"Successfully extracted receipt information: {list(result.keys())}")
                return result
            else:
                logger.error("No JSON object found in Gemini response")
                print("DIRECT PRINT: No JSON object found in Gemini response")
                return self._get_empty_result()
                
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON from Gemini response: {e}")
            print(f"DIRECT PRINT: Error parsing JSON from Gemini response: {e}")
            return self._get_empty_result()
    
    def _get_empty_result(self) -> Dict[str, Any]:
        """
        Get an empty result dictionary with all fields set to null.
        
        Returns:
            Dictionary with all fields set to null
        """
        return {
            "store_name": None,
            "store_address": None,
            "date": None,
            "time": None,
            "total_amount": None
        }

# Create a singleton instance with delayed initialization
gemini_client = None

def parse_receipt_text(text: str) -> Dict[str, Any]:
    """Convenience function to parse receipt text using the singleton client."""
    global gemini_client
    
    # Initialize the client if needed
    if gemini_client is None:
        try:
            gemini_client = GeminiClient()
        except Exception as e:
            print(f"DIRECT PRINT: Failed to initialize client on demand: {e}")
            return {
                "store_name": None,
                "store_address": None,
                "date": None,
                "time": None,
                "total_amount": None,
                "error": str(e)
            }
    
    return gemini_client.parse_receipt_text(text)