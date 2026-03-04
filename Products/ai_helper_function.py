# Communicate with AI API to get product recommendations based on image analysis
import requests
import os
import mimetypes
from BeautyVibe import settings
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from utils.api_response import APIResponse
import mimetypes
import requests


def send_to_ai_api(user_id, image, api_key):
    AI_API_URL = f"{settings.AI_API_URL}/api/v1/analyze?user_id={user_id}"
    
   
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
        
        
from django.conf import settings       
import requests

def send_to_ai_recommendation(user_profile, products, api_key):
    """
    Sends user profile and product list to AI API for recommendations.
    No images are included.
    """
    AI_API_URL = f"{settings.AI_API_URL}/api/v1/recommend"

    # Prepare the payload as JSON
    payload = {
        "user_profile": {
            "id": str(user_profile.id),
            # "full_name": user_profile.full_name,
            "skin_tone": user_profile.skin_tone,
            "undertone": user_profile.undertone,
            "face_shape": user_profile.face_shape,
            "eye_color": user_profile.eye_color,
            "confidence_score": user_profile.confidence_score,
            "summary": user_profile.summary,
        },
        "products": [
            {
                "id": p.id,
                "name": p.name,
                # "slug": p.slug,
                "brand": getattr(p, "brand", ""),
                "shade": getattr(p, "shade", ""),
                "category": p.category.name if p.category else "",
                "colour_hex": getattr(p, "colour_hex", ""),
                "price": float(p.price) if p.price else 0,
                # "discount_percentage": float(getattr(p, "discount_percentage", 0)),
                # "rating": float(getattr(p, "rating", 0)),
                "description": getattr(p, "description", "")
            }
            for p in products
        ]
    }

    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            AI_API_URL,
            json=payload,
            headers=headers,
            timeout=60
        )
        response.raise_for_status()
        return response.json()

    except requests.exceptions.HTTPError as he:
        error_info = he.response.text if he.response else "No body"
        return {"error": f"AI service error ({he.response.status_code}): {error_info[:200]}"}

    except Exception as e:
        return {"error": f"AI service unreachable: {str(e)}"}