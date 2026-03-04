# Communicate with AI API to get product recommendations based on image analysis
import requests
import os
import mimetypes
from BeautyVibe import settings
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from utils.api_response import APIResponse


def send_to_ai_api(user_id, image, api_key):
    AI_API_URL = f"{settings.AI_API_URL_image}/api/v1/analyze?user_id={user_id}"
    
   
    content_type, _ = mimetypes.guess_type(image.name)
    content_type = content_type or "image/jpeg"
    
    headers = {
        "X-API-KEY": api_key  
    }
    
    try:
      
        image.open("rb")
        image.seek(0)
        
        # Prepare the files dictionary
        files = {
            "image": (image.name, image.file, content_type)
        }

        print(f"DEBUG: Connecting to AI API: {AI_API_URL}")
        
 
        response = requests.post(
            AI_API_URL,
            files=files,
            headers=headers,
            timeout=300 
        )
        

        response.raise_for_status()
        
        return response.json()
            
    except requests.exceptions.HTTPError as he:
        error_info = he.response.text if he.response else "No body"
        return {"error": f"AI service error ({he.response.status_code}): {error_info[:200]}"}
        
    except Exception as e:
        return {"error": f"AI service unreachable: {str(e)}"}
        
    finally:
        try:
            image.close()
        except:
            pass