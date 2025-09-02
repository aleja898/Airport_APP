from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
import requests
import json

# Contiene la lógica para procesar las peticiones a la API de Airport Gap

# Vista de página de inicio
def home_view(request):
    """Vista principal que muestra la página de bienvenida"""
    return render(request, 'home.html')

# Vista principal que muestra el formulario de cálculo
def airport_distance_view(request):
    """Vista que muestra el formulario de cálculo de distancias"""
    return render(request, 'airport_distance.html')

@csrf_exempt  # Desactivar CSRF para simplificar las pruebas con herramientas externas
def calculate_distance(request):
    """Vista que procesa el cálculo de distancia entre aeropuertos"""
    
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            aeropuerto_origen = request.POST.get('aeropuerto_origen', '').strip().upper()
            aeropuerto_destino = request.POST.get('aeropuerto_destino', '').strip().upper()
            
            # Validar que ambos campos estén llenos
            if not aeropuerto_origen or not aeropuerto_destino:
                return JsonResponse({
                    'success': False,
                    'error': 'Debe ingresar ambos códigos de aeropuerto'
                })
            
            # Validar que los códigos tengan 3 caracteres
            if len(aeropuerto_origen) != 3 or len(aeropuerto_destino) != 3:
                return JsonResponse({
                    'success': False,
                    'error': 'Los códigos IATA deben tener exactamente 3 caracteres'
                })
            
            # Validar que sean solo letras
            if not aeropuerto_origen.isalpha() or not aeropuerto_destino.isalpha():
                return JsonResponse({
                    'success': False,
                    'error': 'Los códigos IATA deben contener solo letras'
                })
                
            # Validar que los aeropuertos NO sean iguales
            if aeropuerto_origen == aeropuerto_destino:
                return JsonResponse({
                    'success': False,
                    'error': 'Los códigos IATA de los aeropuertos no pueden ser iguales'
                })
            
            # URL de la API
            base_url = "https://airportgap.com/api/airports"
            
            # Datos para el POST request
            airports_data = {
                "from": aeropuerto_origen,
                "to": aeropuerto_destino
            }
            
            # Realizar la petición POST
            response_post = requests.post(
                f"{base_url}/distance", 
                json=airports_data, 
                timeout=10,
                headers={'Content-Type': 'application/json'}
            )
            
            if response_post.status_code == 200:
                datos = response_post.json()
                
                # Extraer información de la respuesta
                result_data = {
                    'success': True,
                    'codigo': datos["data"]["id"],
                    'aeropuerto_origen': {
                        'pais': datos["data"]["attributes"]["from_airport"]["country"],
                        'nombre': datos["data"]["attributes"]["from_airport"]["name"],
                        'ciudad': datos["data"]["attributes"]["from_airport"]["city"],
                        'codigo': aeropuerto_origen
                    },
                    'aeropuerto_destino': {
                        'pais': datos["data"]["attributes"]["to_airport"]["country"],
                        'nombre': datos["data"]["attributes"]["to_airport"]["name"],
                        'ciudad': datos["data"]["attributes"]["to_airport"]["city"],
                        'codigo': aeropuerto_destino,
                    },
                    'zona_horaria': datos["data"]["attributes"]["timezone"],
                    'distancia_km': datos["data"]["attributes"]["kilometers"],
                    'distancia_millas': datos["data"]["attributes"]["miles"],
                    'distancia_millas_nauticas': datos["data"]["attributes"]["nautical_miles"]
                }
                
                return JsonResponse(result_data)
            
            elif response_post.status_code == 422:
                return JsonResponse({
                    'success': False,
                    'error': 'Uno o ambos códigos de aeropuerto no son válidos. Verifique que sean códigos IATA correctos.'
                })
            elif response_post.status_code == 404:
                return JsonResponse({
                    'success': False,
                    'error': 'Aeropuerto no encontrado. Verifique los códigos IATA ingresados.'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': f'Error en la API: {response_post.status_code}. Intente nuevamente.'
                })
                
        except requests.exceptions.Timeout:
            return JsonResponse({
                'success': False,
                'error': 'Tiempo de espera agotado. La API está tardando mucho en responder.'
            })
        except requests.exceptions.ConnectionError:
            return JsonResponse({
                'success': False,
                'error': 'Error de conexión. Verifique su conexión a internet e intente nuevamente.'
            })
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Error al procesar la respuesta de la API. Intente nuevamente.'
            })
        except KeyError as e:
            return JsonResponse({
                'success': False,
                'error': f'Error en la estructura de datos de la API: {str(e)}'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error inesperado: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Método no permitido. Use POST para calcular distancias.'
    })