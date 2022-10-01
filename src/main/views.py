from django.shortcuts import render, redirect
from django.urls import reverse
from ibm_watson.natural_language_understanding_v1 import Features, EmotionOptions

from main.models import Film, Comment
from ibm_watson import SpeechToTextV1, NaturalLanguageUnderstandingV1, LanguageTranslatorV3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator


def index(request):
    context = {'films': Film.objects.all()}
    return render(request, template_name='main/index.html', context=context)


def add_comment(request, film_id):
    film = Film.objects.filter(id=film_id)[0]
    context = {'film': film}
    if request.method == 'POST':
        sound = request.FILES.get('sound')
        if sound is not None:
            comment = s_to_t(sound)
            anger, disgust = NLU(comment)
            if anger < 0.5 and disgust < 0.5:
                Comment(film=film, text=comment).save()
                return redirect(reverse('home'))
            else:
                context['error'] = "Comment can't be posted."
    return render(request, template_name='main/add_comment.html', context=context)


def NLU(comment):
    authenticator = IAMAuthenticator('TdnRPhLcL3HLWSy_eTH2pEHDi_xl0GfpkoQwE2hCsUcr')
    natural_language_understanding = NaturalLanguageUnderstandingV1(version='2021-08-01', authenticator=authenticator)
    natural_language_understanding.set_service_url(
        'https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/6719b548-13d0-4423-8ad0-778af2233933')
    response = natural_language_understanding.analyze(text=comment, features=Features(emotion=EmotionOptions()))
    out = response.get_result()
    return out['emotion']['document']['emotion']['anger'], out['emotion']['document']['emotion']['disgust']


def s_to_t(sound):
    authenticator = IAMAuthenticator('meaKTcg56zj8DSWswLFXVbP9eKB6ciCniidbnS0NoVKE')
    s_2_t = SpeechToTextV1(authenticator=authenticator)
    s_2_t.set_service_url('https://api.us-south.speech-to-text.watson.cloud.ibm.com/instances/c7841820-ef7b'
                          '-4c6e-9d75-d8106076fdb3')
    response = s_2_t.recognize(audio=sound, content_type='audio/ogg', model='en-US_BroadbandModel')
    out = response.get_result()
    return out['results'][0]['alternatives'][0]['transcript']


def comments(request, film_id):
    film = Film.objects.filter(id=film_id)[0]
    query = Comment.objects.filter(film__id=film_id)
    comment_list = [comment.text for comment in query]
    if 'language' in request.GET:
        language = request.GET.get('language')
        comment_list = [TL(language, comment) for comment in comment_list]
    context = {'comments': comment_list, 'film' : film}
    return render(request, template_name='main/comments.html', context=context)


def TL(language, text):
    authenticator = IAMAuthenticator('M9UBdB0c8fTeRW_79VTGcaXktL90xezlUu-_FfxD7LML')
    language_translator = LanguageTranslatorV3(version='2018-05-01', authenticator=authenticator)
    language_translator.set_service_url(
        'https://api.us-south.language-translator.watson.cloud.ibm.com/instances/a60a1807-3ed2-4f5c-be69-6c1015450024')
    translate = language_translator.translate(text=text, model_id=f'en-{language}').get_result()
    return translate['translations'][0]['translation']
