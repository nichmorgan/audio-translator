import pydash as py_
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import SpeechToTextV1, TextToSpeechV1, LanguageTranslatorV3


def speech_to_text(buffer, pt_lang=True):
    service = SpeechToTextV1(
        authenticator=IAMAuthenticator('Iya3FQrSrvZQi6FN6Gg7cXUOUB9imtbB54Wv_uQDhMcQ'))
    status, text, score = False, None, None
    try:
        model = 'pt-BR_BroadbandModel' if pt_lang else None
        response = service.recognize(buffer,
                                     model=model,
                                     content_type='audio/wav')

        alternatives = py_.get(response.get_result(), 'results.0.alternatives.0')
        status = alternatives is not None
        if alternatives is not None:
            text, score = alternatives.values()
    except Exception as e:
        print('Error: ' + str(e))
    finally:
        return status, text.strip(), score


def text_to_speech(text, pt_lang=False, female=False):
    service = TextToSpeechV1(authenticator=IAMAuthenticator('J_eT6UF74E6_hxhQHp9BffGNwCFve9iNDYiRU7KmoupX'))

    if pt_lang:
        voice = 'pt-BR_IsabelaV3Voice'
    elif female:
        voice = 'en-US_AllisonV3Voice'
    else:
        voice = 'en-US_HenryV3Voice'

    response = service.synthesize(text, accept='audio/wav', voice=voice).get_result()
    return response.content


def translate_text(text, model):
    service = LanguageTranslatorV3(version='2018-05-01',
                                   authenticator=IAMAuthenticator('twXIJP-10FISqL-tH1DJ_E3nmr26j_1UDhyZH-ExzpMT'))

    response = service.translate(text, model_id=model).get_result()
    result = py_.get(response, 'translations.0.translation')
    return result
