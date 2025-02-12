from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from deep_translator import GoogleTranslator
import openai
import json
import logging
from openai import OpenAI,OpenAIError
from django.http import StreamingHttpResponse, JsonResponse
import os
logger = logging.getLogger(__name__)
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
def chat_interface(request):
    return render(request, 'index.html')



@csrf_exempt
def chat_api(request):
    if request.method == 'POST':
        try:
            user_message = request.POST.get('message', '')[:500]
            if not user_message.strip():
                return JsonResponse({'error': 'Empty input', 'response': ''}, status=400)

            # Oromo → English translation
            try:
                translated_input = GoogleTranslator(source='om', target='en').translate(user_message)
            except Exception as e:
                logger.error(f"Initial translation error: {str(e)}")
                translated_input = user_message  # Fallback to original text

            # OpenAI processing
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are assisting an Oromo speaker. Respond in simple English."},
                        {"role": "user", "content": translated_input}
                    ]
                )
                english_response = response.choices[0].message.content
            except Exception as e:
                logger.error(f"OpenAI error: {str(e)}")
                return JsonResponse({
                    'response': 'Sirriin hin dandeenye (Error occurred)',
                    'error': str(e)
                }, status=500)

            # English → Oromo translation with fallback
            try:
                translated_response = GoogleTranslator(source='en', target='om').translate(english_response)
            except Exception as e:
                logger.error(f"Final translation error: {str(e)}")
                translated_response = f"{english_response} (Afaan Inglizii qofa)"

            return JsonResponse({
                'response': translated_response,
                'original_english': english_response
            })

        except Exception as e:
            logger.error(f"General error: {str(e)}")
            return JsonResponse({
                'response': 'Sirriin hin dandeenye (System error)',
                'error': str(e)
            }, status=500)

    return JsonResponse({'error': 'Invalid request method', 'response': ''}, status=400)