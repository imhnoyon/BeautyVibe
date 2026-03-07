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
        
        

# import requests
# from django.conf import settings


# def send_to_ai_recommendation(user_profile, products, api_key):
#     """
#     Sends user profile and product list to AI API for recommendations.
#     """

#     AI_API_URL = f"{settings.AI_API_URL}/api/v1/recommend"

#     payload = {
#         "user_id": str(user_profile.id),

#         "user_profile": {
#             "skin_tone": user_profile.skin_tone,
#             "undertone": user_profile.undertone,
#             "face_shape": user_profile.face_shape,
#             "eye_color": user_profile.eye_color,
#             "confidence_score": user_profile.confidence_score,
#             "summary": user_profile.summary,
#         },

#         "products": [
#             {
#                 "id": str(p.id),
#                 "name": p.name,
#                 "hex_code": getattr(p, "colour_hex", ""),
#                 "category": p.category.name if p.category else "",
#                 "price": float(p.price) if p.price else 0,
#                 "description": getattr(p, "description", "")
#             }
#             for p in products
#         ]
#     }

#     headers = {
#         "X-API-KEY": api_key,
#         "Content-Type": "application/json"
#     }

#     try:
#         response = requests.post(
#             AI_API_URL,
#             json=payload,
#             headers=headers,
#             timeout=60
#         )

#         response.raise_for_status()

#         return response.json()

#     except requests.exceptions.HTTPError as he:
#         error_info = he.response.text if he.response else "No body"
#         return {
#             "error": f"AI service error ({he.response.status_code}): {error_info[:200]}"
#         }

#     except Exception as e:
#         return {
#             "error": f"AI service unreachable: {str(e)}"
#         }






import requests
from django.conf import settings
from django.db.models import Q

from UserAuthentication.serializers import AICategorySerializer, AIProductSerializer


def build_ai_payload(user_profile, categories, products, request=None):
    """
    Build payload exactly like AI API expects.
    """

    category_data = AICategorySerializer(categories, many=True, context={"request": request}).data
    product_data = AIProductSerializer(products, many=True, context={"request": request}).data

    payload = {
        "user_id": str(user_profile.id),
        "user_profile": {
            "skin_tone": getattr(user_profile, "skin_tone", ""),
            "undertone": getattr(user_profile, "undertone", ""),
            "face_shape": getattr(user_profile, "face_shape", ""),
            "eye_color": getattr(user_profile, "eye_color", ""),
            "confidence_score": getattr(user_profile, "confidence_score", 0),
            "summary": getattr(user_profile, "summary", ""),
        },
        "categories": category_data,
        "products": product_data,
    }

    return payload


def send_to_ai_recommendation(user_profile, categories, products, api_key, request=None):
    """
    Sends user profile, categories and product list to AI API.
    """

    AI_API_URL = f"{settings.AI_API_URL}/api/v1/recommend"

    payload = build_ai_payload(
        user_profile=user_profile,
        categories=categories,
        products=products,
        request=request
    )

    headers = {
        "X-API-KEY": api_key or "",
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
        return {
            "error": f"AI service error ({he.response.status_code if he.response else 500}): {error_info[:500]}"
        }

    except Exception as e:
        return {
            "error": f"AI service unreachable: {str(e)}"
        }

def filter_products_queryset(products, category_value=None, search_value=None):
    """
    Filter queryset by category and search text.
    category_value can be category id, name, or slug.
    search_value matches product name, brand, shade.
    """

    if category_value:
        category_query = Q()

        # if category is numeric, filter by id
        if str(category_value).isdigit():
            category_query |= Q(category__id=int(category_value))

        # always allow slug and name match
        category_query |= Q(category__slug__iexact=str(category_value))
        category_query |= Q(category__name__iexact=str(category_value))

        products = products.filter(category_query)

    if search_value:
        products = products.filter(
            Q(name__icontains=search_value) |
            Q(brand__icontains=search_value) |
            Q(shade__icontains=search_value)
        )

    return products