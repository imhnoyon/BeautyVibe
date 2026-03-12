# Communicate with AI API to get product recommendations based on image analysis
import requests
import os
import mimetypes
from BeautyVibe import settings
from UserAuthentication.models import User
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
    
    # try:
      
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
            
    # except Exception as e:
    #     return {"error": f"{str(e)}"}
    #     # error_info = he.response.text if he.response else "No body"
    #     # return {"error": f"AI service error ({he.response.status_code}): {error_info[:200]}"}
        
    # except Exception as e:
    #     return {"error": f"AI service unreachable: {str(e)}"}
        
    # finally:
    #     try:
    #         image.close()
    #     except:
    #         pass
        
import requests
from django.conf import settings


def build_ai_payload(user_profile, products, categories,request):
    return {
        "user_id": str(user_profile.id),
        "user_profile": {
            "skin_tone": getattr(user_profile, "skin_tone", "") or "",
            "undertone": getattr(user_profile, "undertone", "") or "",
            "face_shape": getattr(user_profile, "face_shape", "") or "",
            "eye_color": getattr(user_profile, "eye_color", "") or "",
            "confidence_score": int(getattr(user_profile, "confidence_score", 0) or 0),
            "summary": getattr(user_profile, "summary", "") or "",
        },
        "categories": [
            {
                "id": c.id,
                "name": c.name or "",
                "slug": getattr(c, "slug", "") or ""
            }
            for c in categories
        ],
        "products": [
            {
                "id": p.id,
                "name": p.name or "",
                "hex_code": getattr(p, "colour_hex", "") or "",
                "category_id": p.category.id if p.category else None,
                "category": p.category.name if p.category else "",
                "brand": p.brand or "",
                "shade": p.shade or "",
                "rating": str(getattr(p, "rating", "0.0") or "0.0"),
                "price": float(p.price or 0),
                 "image": request.build_absolute_uri(p.image.url) if p.image else "",
                "description": getattr(p, "description", "") or ""
            }
            for p in products
        ]
    }


def send_to_ai_recommendation(payload, api_key):
    AI_API_URL = f"{settings.AI_API_URL}/api/v1/recommend"

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

        try:
            return response.json()
        except ValueError:
            return {
                "error": f"AI service returned non-JSON response: {response.text[:300]}"
            }

    except requests.exceptions.HTTPError as he:
        if he.response is not None:
            error_info = he.response.text or "No body"
            status_code = he.response.status_code
        else:
            error_info = "No response received"
            status_code = 500

        return {
            "error": f"AI service error ({status_code}): {error_info[:300]}"
        }

    except requests.exceptions.Timeout:
        return {
            "error": "AI service timeout"
        }

    except requests.exceptions.ConnectionError as ce:
        return {
            "error": f"AI service connection error: {str(ce)}"
        }

    except Exception as e:
        return {
            "error": f"AI service unreachable: {str(e)}"
        }