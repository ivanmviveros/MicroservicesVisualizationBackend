from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import spacy
# from collections import Counter
import json
from configuraciones.models import Configuracion
from microservicios.models import Microservicio

ingles = True


@csrf_exempt
def api_home(request):
    if request.method != "POST":
        return JsonResponse({})

    user_stories = request.POST.get('user_stories', '')
    if not user_stories:
        JSON = json.loads(request.body)
        datos_JSON = json.dumps(JSON)
        nom_proyecto = JSON[0]["userStories"][0]["project"]
        cant_microservicios = len(JSON)
        cant_historias = 0
        arreglo_stringsHUs = []
        for microservicio in JSON:
            cant_historias = cant_historias + len(microservicio["userStories"])
            cadena_historias = ""  # Todas las historias de un microservicio en un string
            for historia in microservicio["userStories"]:
                historia_sin_guion = historia["id"].replace("US", "") # Quita "US" de historias
                historia_sin_guion = historia_sin_guion.replace("-", "") # Quita "-" de historias
                cadena_historias = cadena_historias + historia_sin_guion + \
                    ","  # Concatena números (IDs) de HUs en string

            cadena_historias = cadena_historias[:-1] # Quita la última coma de la cadena de números (IDs) de historias
            arreglo_historias = cadena_historias.split(',') # Pone los números de HUs en un arreglo
            
            nums = [int(x) for x in arreglo_historias] # Convierte el arreglo de strings a enteros
            nums.sort() # Acomoda en orden el arreglo de enteros
            cadena_historias = ""
            for elemento in nums:
                # Agregar "US" a IDs de HUs de un MS y concatenarlos en un string
                cadena_historias = cadena_historias + "US" + \
                    str(elemento) + "," 

            cadena_historias = cadena_historias[:-1] # Quita la última coma del string de IDs de HUs
            
            arreglo_stringsHUs.append(cadena_historias) # Agrega el string de IDs de HUs al arreglo de HUs de MSs

        # Buscar en la tabla 'Configuraciones' registros que cumplan con los criterios de: nombre de proyecto,
        # cantidad de microservicios y cantidad de historias en un microservicio
        configuraciones = Configuracion.objects.filter( 
            nombre_proyecto=nom_proyecto,
            cantidad_microservicios=cant_microservicios,
            cantidad_historias=cant_historias
        )
        if configuraciones: # Si hay coincidencias:
            for configuracion in configuraciones: # Por cada configuración, buscar en la
                # tabla 'Microservicios' registros que cumplan con el criterio de ID de configuración
                registros = Microservicio.objects.filter(
                    config_id=configuracion.id
                )
                if registros: # Si hay coincidencias:
                    coincidencias_MSs = 0
                    
                    # Comparar si los string de IDs que se envían desde el visualizador y los strings de IDs
                    # que se trajeron desde la BD son iguales
                    for i in range(len(arreglo_stringsHUs)):
                        for j in range(len(registros)):
                            if arreglo_stringsHUs[i] == registros[j].historias:
                                coincidencias_MSs += 1

                    # Si todos son iguales se retorna el JSON de la base de datos
                    if coincidencias_MSs == cant_microservicios:
                        data = {"nueva_config": False,
                                "configuracion": configuracion.json_info}
                        return JsonResponse(data)

            # Si no todos los strings de HUs son iguales entonces se guarda la nueva configuración en BD
            Configuracion.objects.create(
                nombre_proyecto=nom_proyecto,
                cantidad_microservicios=cant_microservicios,
                cantidad_historias=cant_historias,
                json_info=datos_JSON
            )

             # Consulta para obtener el ID de la configuración que se acaba de guardar en BD y guardar
             # los registros strings de HUs en la tabla de 'Microservicios'
            ultimo = Configuracion.objects.all().last()
            if ultimo:
                for microservicios in arreglo_stringsHUs:
                    Microservicio.objects.create(
                        config_id=ultimo.id,
                        historias=microservicios
                    )
                data = {"nueva_config": True}
                return JsonResponse(data)
            
        else: # Si no hay registros entonces se guarda la nueva configuración en BD
            Configuracion.objects.create(
                nombre_proyecto=nom_proyecto,
                cantidad_microservicios=cant_microservicios,
                cantidad_historias=cant_historias,
                json_info=datos_JSON
            )

             # Consulta para obtener el ID de la configuración que se acaba de guardar en BD y guardar
             # los registros strings de HUs en la tabla de 'Microservicios'
            ultimo = Configuracion.objects.all().last()
            if ultimo:
                for microservicios in arreglo_stringsHUs:
                    Microservicio.objects.create(
                        config_id=ultimo.id,
                        historias=microservicios
                    )
                data = {"nueva_config": True}
                return JsonResponse(data)

    else:
        arrayCadena = request.POST.get('user_stories', '')
        if arrayCadena:
            if ingles:
                nlp = spacy.load("en_core_web_md")
            else:
                nlp = spacy.load("es_core_news_md")

            arraySS = []
            arrayCadenas = arrayCadena.split(sep='*')
            for h in range(0, len(arrayCadenas)):
                suma = 0
                divisor = 0
                cadena = arrayCadenas[h]
                cadenas = cadena.split(sep='/')
                if len(cadenas) > 1:
                    for i in range(0, len(cadenas) - 1):
                        for j in range(i+1, len(cadenas)):
                            doc = nlp(cadenas[0])
                            hu1 = ''
                            for token in doc:
                                pos = token.pos_
                                if ingles:
                                    if pos == 'NOUN' or pos == 'PROPN':
                                        hu1 += token.text + ' '
                                else:
                                    if pos == 'NOUN':
                                        hu1 += token.text + ' '
                                    else:
                                        hu1 += token.lemma_ + ' '
                            token1 = nlp(hu1)

                            doc = nlp(cadenas[1])
                            hu2 = ''
                            for token in doc:
                                pos = token.pos_
                                if ingles:
                                    if pos == 'NOUN' or pos == 'PROPN':
                                        hu2 += token.text + ' '
                                else:
                                    if pos == 'NOUN':
                                        hu2 += token.text + ' '
                                    else:
                                        hu2 += token.lemma_ + ' '
                            token2 = nlp(hu2)

                            suma += token1.similarity(token2)
                            divisor += 1

                    semantic_similarity = suma / divisor
                else:
                    semantic_similarity = 1

                arraySS.append(semantic_similarity)

            data = {"semantic_similarity": arraySS}
            return JsonResponse(data)

    return JsonResponse({"invalid": request.POST})

# if ingles:
#     nlp = spacy.load("en_core_web_md")
# else:
#     nlp = spacy.load("es_core_news_md")


# def api_home(request):
#     arraySS = []
#     arrayCadena = request.GET.get('user_stories', '')
#     arrayCadenas = arrayCadena.split(sep='*')
#     for h in range(0, len(arrayCadenas)):
#         suma = 0
#         divisor = 0
#         cadena = arrayCadenas[h]
#         cadenas = cadena.split(sep='/')
#         if len(cadenas) > 1:
#             for i in range(0, len(cadenas) - 1):
#                 for j in range(i+1, len(cadenas)):
#                     hu1 = seleccionarSustantivosVerbos(cadenas[0])
#                     token1 = nlp(hu1)
#                     hu2 = seleccionarSustantivosVerbos(cadenas[1])
#                     token2 = nlp(hu2)
#                     suma += token1.similarity(token2)
#                     divisor += 1

#             semantic_similarity = suma / divisor
#         else:
#             semantic_similarity = 1

#         arraySS.append(semantic_similarity)
#     data = {"semantic_similarity": arraySS}
#     return JsonResponse(data)


# if ingles:
#     def seleccionarSustantivosVerbos(historia):
#         doc = nlp(historia)
#         listaText = ''
#         for token in doc:
#             pos = token.pos_
#             if pos == 'NOUN' or pos == 'PROPN':
#                 listaText += token.text + ' '
#         return listaText
# else:
#     def seleccionarSustantivosVerbos(historia):
#         doc = nlp(historia)
#         listaText = ''
#         for token in doc:
#             pos = token.pos_
#             if pos == 'NOUN':
#                 listaText += token.text + ' '
#             else:
#                 listaText += token.lemma_ + ' '
#         return listaText


######  Código dado por el profe Vera (aún por adaptar e implementar)  ###########


# def init(self, lenguaje, modulo):
#     spacy.prefer_gpu()
#     if lenguaje == 'es':
#         if modulo == 'md':
#             self.nlp = spacy.load("es_core_news_md")
#         if modulo == 'sm':
#             self.nlp = spacy.load("es_core_news_sm")
#     if lenguaje == 'en':
#         if modulo == 'md':
#             self.nlp = spacy.load("en_core_web_md")
#         if modulo == 'sm':
#             self.nlp = spacy.load("en_core_web_sm")


# def identificarVerbosEntidades(self, historiaUsuario):
#     texto = historiaUsuario.nombre + ": " + historiaUsuario.descripcion
#     #texto = historiaUsuario.nombre
#     doc = self .n1p(texto)
#     listaText = ''
#     listLemmas = ''
#     lista = []
#     for token in doc:
#         pos = token.pos_
#         if pos == 'NOUN' or pos == 'PROPN':
#             hutoken = [token.text, token.lemma_, token.pos_, token.vector_norm, token.has_vector]
#             listaText += token.text + ' '
#             listLemmas += token.lemma_ + ' '
#     lista = [historiaUsuario, listaText, listLemmas]
#     return lista


# def identificarEntidadHistorias(self, listaHistorias):
#     listaEntidadesHU = []
#     for historia in listaHistorias:
#         lista = self.identificarVerbosEntidades(historia)
#         textos = lista[1]
#         lemmas = lista[2]
#         frecuenciaText = Counter(textos.split(' '))
#         frecuencaLema = Counter(lemmas.split(' '))

#         dicText = frecuenciaText.most_common(2)
#         dicLema = frecuencaLema.most_common(2)

#         entidadText = ""
#         for txt in dicText:
#             entidadText += str(txt[0]) + " "

#         entidadLema = ""
#         for txt in dicLema:
#             entidadLema += str(txt[0]) + " "

#         vector = [historia, entidadText, entidadLema]
#         listaEntidadesHU.append(vector)
#     return listaEntidadesHU


# def identificarEntidadesMicroservicio(self, ms):
#     historias = ms.getHistorias()
#     texto = ''
#     listaText = ""
#     listLemmas = ""
#     for hu in historias:
#         texto, " " + hu.historia.nombre + " " + hu.historia.descripcion + " "

#     doc = self.n1p(texto)
#     for token in doc:
#         pos = token.pos_
#         if pos == 'NOUN' or pos == 'PROPN':
#             listaText += token.text + ' '
#             listLemmas += token.lemma_ + ' '

#     frecuenciaText = Counter(listaText.split(' '))
#     frecuencaLema = Counter(listLemmas.split(' '))

#     dicText = frecuenciaText.most_common(3)
#     dicLema = frecuencaLema.most_common(3)

#     entidadText = ''
#     for txt in dicText:
#         entidadText += str(txt[0]) + " "

#     entidadLema = ''
#     for txt in dicLema:
#         entidadLema += str(txt[0]) + " "

#     lista = [ms, listaText, listLemmas, entidadText, entidadLema]
#     return lista


# def calcularSimilitud(self, listaHistorias, aplicarEn):
#     matrizSimilitud = []
#     textos = []
#     for historia in listaHistorias:
#         lista = self.identificarVerbosEntidades(historia)
#         textos.append(lista)

#     for texto in textos:
#         hu = texto[0]
#         tex = texto[1]
#         lem = texto[2]
#         if aplicarEn == 'lemma':
#             doc1 = self.n1p(lem)
#         if aplicarEn == 'text':
#             doc1 = self.n1p(tex)
#         similitudes = [hu]

#         for tex_hu in textos:
#             hu2 = tex_hu[0]
#             texto2 = tex_hu[1]
#             lemma2 = tex_hu[2]
#             if aplicarEn == 'lemma':
#                 doc2 = self.n1p(lemma2)
#             if aplicarEn == 'text':
#                 doc2 = self.n1p(texto2)
#             similitud = doc1.similarity(doc2)
#             dicc = [hu2, similitud]
#             similitudes.append(dicc)

#         matrizSimilitud.append(similitudes)
#     return matrizSimilitud


# def calcularDiccionarioSimilitud(self, listaHistorias, aplicarEn):
#     dicSimilitud = {}
#     n = len(listaHistorias)
#     for i in range(0, n-1):
#         for j in range((i+1), n):
#             historia = listaHistorias[i]
#             historia2 = listaHistorias[j]

#             texto1 = self.identificarVerbosEntidades(historia)
#             texto2 = self.identificarVerbosEntidades(historia2)

#             tex = texto1[1]
#             lem = texto1[2]

#             tex2 = texto2[1]
#             lem2 = texto2[2]

#             # tex = historia.nombre + ":" + historia.descripcion
#             # tex2 = historia2.nombre + ":" + historia2.descripcion

#             if aplicarEn == 'lemma':
#                 docl = self.n1p(lem)
#                 doc2 = self.n1p(lem2)
#             if aplicarEn == 'text':
#                 docl = self.n1p(tex)
#                 doc2 = self.n1p(tex2)

#             similitud = docl.similarity(doc2)
#             key = historia.identificador + '-' + historia2.identificador
#             dicSimilitud[key] = similitud

#             # print("---- Diccionario: , str(diccionario))
#             return dicSimilitud
