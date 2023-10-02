# -*- coding: utf-8 -*-

import logging
import ask_sdk_core.utils as ask_utils
import requests

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        speak_output = "Buenas notches como posso te ajudar?"
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class ConsumoIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("ConsumoIntent")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        tipo_dado = slots["tipo_dado"].resolutions.resolutions_per_authority[0].values[0].value.name
        mes = slots["mes"].value
        ano = slots["ano"].value

        url = f"http://demo9951387.mockable.io/consumo"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            for item in data:
                if (
                    item["ano"] == int(ano)
                    and item["mes"] == mes
                    and item["tipo"] == tipo_dado
                ):
                    speak_output = f"Consumo de {tipo_dado} para {mes} de {ano}: {item['consumo']}"
                    break
            else:
                speak_output = "Não existe consumo para essa data"
        else:
            speak_output = "Houve um erro"

        return handler_input.response_builder.speak(speak_output).response

class ListarDadosIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("ListarDadosIntent")(handler_input)

    def handle(self, handler_input):
        url = f"http://demo9951387.mockable.io/consumo"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            dados = []
            for item in data:
                dado = f"Consumo de {item['tipo']} para {item['mes']} de {item['ano']}: {item['consumo']}"
                dados.append(dado)

            speak_output = ". ".join(dados)
        else:
            speak_output = "Houve um erro ao recuperar os dados."

        return handler_input.response_builder.speak(speak_output).response

class HelpIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        speak_output = "Você pode dizer olá para mim! Como posso ajudar?"
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class CancelOrStopIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        speak_output = "Até logo!"
        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

class FallbackIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        logger.info("In FallbackIntentHandler")
        speech = "Hmm, não tenho certeza. Você pode dizer Olá ou Ajuda. O que você gostaria de fazer?"
        reprompt = "Não entendi. Como posso ajudar?"

        return handler_input.response_builder.speak(speech).ask(reprompt).response

class SessionEndedRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        return handler_input.response_builder.response

class IntentReflectorHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "Você acionou a intenção " + intent_name + "."
        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

class CatchAllExceptionHandler(AbstractExceptionHandler):
    def can_handle(self, handler_input, exception):
        return True

    def handle(self, handler_input, exception):
        logger.error(exception, exc_info=True)
        speak_output = "Desculpe, tive problemas para fazer o que você pediu. Por favor, tente novamente."
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(ConsumoIntentHandler())
sb.add_request_handler(ListarDadosIntentHandler()) 
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler())
sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
