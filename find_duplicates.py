import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BeautyVibe.settings')
django.setup()

from Products.models import Product
from django.db.models import Count

def find_duplicates():
    duplicates = Product.objects.values('name', 'shade').annotate(count=Count('id')).filter(count__gt=1)
    
    if not duplicates:
        print("No duplicates found by (name, shade).")
        return

    for dup in duplicates:
        name = dup['name']
        shade = dup['shade']
        count = dup['count']
        print(f"Duplicate found: Name='{name}', Shade='{shade}', Count={count}")
        
        products = Product.objects.filter(name=name, shade=shade)
        for p in products:
            print(f"  - ID: {p.id}, Slug: {p.slug}, Category: {p.category.name if p.category else 'None'}, Price: {p.price}")

if __name__ == "__main__":
    find_duplicates()
