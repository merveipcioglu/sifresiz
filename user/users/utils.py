import random
import logging
import requests
from django.conf import settings
from urllib.parse import quote
import boto3
from boto3.session import Session

logger = logging.getLogger(__name__)

def generate_verification_code():
    return str(random.randint(100000, 999999))

def send_verification_sms(phone_number, code):
    try:
        phone = str(phone_number).replace('+90', '').replace('90', '')
        if phone.startswith('0'):
            phone = phone[1:]
        
        message = quote(f'Dogrulama kodunuz: {code}')
        
        url = (
            f"https://api.iletimerkezi.com/v1/send-sms/get/?"
            f"key={settings.ILETIMERKEZI_API_KEY}&"
            f"hash={settings.ILETIMERKEZI_SECRET}&"
            f"text={message}&"
            f"receipents={phone}&"
            f"sender={settings.ILETIMERKEZI_SENDER}&"
            f"iys=1&"
            f"iysList=BIREYSEL"
        )
        
        
        response = requests.get(url)
        
        
        if response.status_code == 200:
            return True
        else:
            return False
            
    except Exception as e:
        return False

def get_s3_client():
    """Get configured S3 client"""
    session = Session(
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME
    )
    return session.client('s3')

def upload_file_to_s3(file_obj, file_path, content_type=None):
    try:
        s3 = get_s3_client()
        
        s3.upload_fileobj(
            file_obj,
            settings.AWS_STORAGE_BUCKET_NAME,
            file_path,
            ExtraArgs={
                'ContentType': content_type
            }
        )
        
        # Doğrudan public URL döndür
        return f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/{file_path}"

    except Exception as e:
        logger.error(f"Failed to upload file to S3: {str(e)}")
        raise

def delete_file_from_s3(file_path):
  
    try:
        s3 = get_s3_client()
        s3.delete_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=file_path
        )
    except Exception as e:
        logger.warning(f"Failed to delete file from S3: {str(e)}")

def generate_username_suggestions(first_name, last_name):
    first_name = first_name.lower().strip()
    last_name = last_name.lower().strip()
 
    tr_chars = {'ı': 'i', 'ğ': 'g', 'ü': 'u', 'ş': 's', 'ö': 'o', 'ç': 'c', 'İ': 'i'}
    for tr_char, eng_char in tr_chars.items():
        first_name = first_name.replace(tr_char, eng_char)
        last_name = last_name.replace(tr_char, eng_char)
    
    first_name = "".join(first_name.split())
    last_name = "".join(last_name.split())
    
    from users.models import CustomUser
    
    suggestions = []
    base = f"{first_name}{last_name}"
    
    if len(base) > 30:
        base = base[:30]
    elif len(base) < 3:
        return []  
    

    if not CustomUser.objects.filter(username=base).exists():
        suggestions.append(base)
    

    counter = 1
    while len(suggestions) < 3:
        suggestion = f"{base}{counter}"
        
        if len(suggestion) <= 30 and len(suggestion) >= 3 and not CustomUser.objects.filter(username=suggestion).exists():
            suggestions.append(suggestion)
        
        counter += 1
        if counter > 999: 
            break
            
    return suggestions[:3]

