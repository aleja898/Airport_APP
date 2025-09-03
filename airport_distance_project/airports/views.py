from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
import json

# Vista de página de inicio
def home_view(request):
    """Vista principal que muestra la página de bienvenida"""
    return render(request, 'home.html')

# Vista principal que muestra el formulario de cálculo
def airport_distance_view(request):
    """Vista que muestra el formulario de cálculo de distancias"""
    return render(request, 'airport_distance.html')
@csrf_exempt
def calculate_distance(request):
    """Vista que procesa el cálculo de distancia entre aeropuertos"""
    if request.method == 'POST':
        try:
            aeropuerto_origen = request.POST.get('aeropuerto_origen', '').strip().upper()
            aeropuerto_destino = request.POST.get('aeropuerto_destino', '').strip().upper()

            # ... (Las validaciones de los campos siguen siendo las mismas) ...
            if not aeropuerto_origen or not aeropuerto_destino:
                return JsonResponse({'success': False, 'error': 'Debe ingresar ambos códigos de aeropuerto'})
            
            if len(aeropuerto_origen) != 3 or len(aeropuerto_destino) != 3:
                return JsonResponse({'success': False, 'error': 'Los códigos IATA deben tener exactamente 3 caracteres'})
            
            if not aeropuerto_origen.isalpha() or not aeropuerto_destino.isalpha():
                return JsonResponse({'success': False, 'error': 'Los códigos IATA deben contener solo letras'})
                
            if aeropuerto_origen == aeropuerto_destino:
                return JsonResponse({'success': False, 'error': 'Los códigos IATA de los aeropuertos no pueden ser iguales'})

            base_url = "https://airportgap.com/api"

            # 1. Obtener datos del aeropuerto de origen
            response_origen = requests.get(f"{base_url}/airports/{aeropuerto_origen}", timeout=10)
            if response_origen.status_code != 200:
                return JsonResponse({
                    'success': False,
                    'error': f'Error al obtener datos del aeropuerto de origen: Código {aeropuerto_origen} no es válido.'
                })
            data_origen = response_origen.json()['data']['attributes']

            # 2. Obtener datos del aeropuerto de destino
            response_destino = requests.get(f"{base_url}/airports/{aeropuerto_destino}", timeout=10)
            if response_destino.status_code != 200:
                return JsonResponse({
                    'success': False,
                    'error': f'Error al obtener datos del aeropuerto de destino: Código {aeropuerto_destino} no es válido.'
                })
            data_destino = response_destino.json()['data']['attributes']

            # 3. Calcular la distancia
            airports_data = {"from": aeropuerto_origen, "to": aeropuerto_destino}
            response_distancia = requests.post(
                f"{base_url}/airports/distance",
                json=airports_data,
                timeout=10,
                headers={'Content-Type': 'application/json'}
            )

            if response_distancia.status_code == 200:
                datos_distancia = response_distancia.json()
                
                result_data = {
                    'success': True,
                    'distancia_km': datos_distancia["data"]["attributes"]["kilometers"],
                    'distancia_millas': datos_distancia["data"]["attributes"]["miles"],
                    'distancia_millas_nauticas': datos_distancia["data"]["attributes"]["nautical_miles"],
                    'aeropuerto_origen': {
                        'nombre': data_origen['name'],
                        'ciudad': data_origen['city'],
                        'pais': data_origen['country'],
                        'codigo': aeropuerto_origen,
                        'zona_horaria': data_origen['timezone']
                    },
                    'aeropuerto_destino': {
                        'nombre': data_destino['name'],
                        'ciudad': data_destino['city'],
                        'pais': data_destino['country'],
                        'codigo': aeropuerto_destino,
                        'zona_horaria': data_destino['timezone']
                    }
                }
                return JsonResponse(result_data)

            # ... (Manejo de errores de la API de distancia) ...
            elif response_distancia.status_code == 422:
                return JsonResponse({
                    'success': False,
                    'error': 'Uno o ambos códigos de aeropuerto no son válidos. Verifique que sean códigos IATA correctos.'
                })
            elif response_distancia.status_code == 404:
                return JsonResponse({
                    'success': False,
                    'error': 'Aeropuerto no encontrado. Verifique los códigos IATA ingresados.'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': f'Error en la API: {response_distancia.status_code}. Intente nuevamente.'
                })

        except requests.exceptions.Timeout:
            return JsonResponse({'success': False, 'error': 'Tiempo de espera agotado. La API está tardando mucho en responder.'})
        except requests.exceptions.ConnectionError:
            return JsonResponse({'success': False, 'error': 'Error de conexión. Verifique su conexión a internet e intente nuevamente.'})
        except (json.JSONDecodeError, KeyError) as e:
            return JsonResponse({'success': False, 'error': f'Error al procesar la respuesta de la API. Intente nuevamente. Detalles: {e}'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Error inesperado: {str(e)}'})

    return JsonResponse({'success': False, 'error': 'Método no permitido. Use POST para calcular distancias.'})