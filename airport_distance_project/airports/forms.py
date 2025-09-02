from django import forms

# Validaciones adicionales para los códigos IATA

class AirportDistanceForm(forms.Form):
    aeropuerto_origen = forms.CharField(
        max_length=3,
        min_length=3,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Origen (ej. BOG)',
            'pattern': '^[A-Z]{3}$',
            'title': 'Ingrese código IATA de 3 letras',
        }),
        label='Aeropuerto de Origen (código IATA)',
    )

    aeropuerto_destino = forms.CharField(
        max_length=3,
        min_length=3,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Destino (ej. JFK)',
            'pattern': '^[A-Z]{3}$',
            'title': 'Ingrese código IATA de 3 letras',
        }),
        label='Aeropuerto de Destino (código IATA)',
    )

    def clean_aeropuerto_origen(self):
        """Validar que el código contenga solo letras"""
        codigo = self.cleaned_data['aeropuerto_origen'].upper()
        if not codigo.isalpha():  # Solo letras
            raise forms.ValidationError("El código debe contener solo letras.")
        return codigo  # ← CORREGIDO: Faltaba retornar el código

    def clean_aeropuerto_destino(self):
        """Validar que el código contenga solo letras"""
        codigo = self.cleaned_data['aeropuerto_destino'].upper()
        if not codigo.isalpha():  # Solo letras
            raise forms.ValidationError("El código debe contener solo letras.")
        return codigo

    def clean(self):
        """Validación general del formulario"""
        cleaned_data = super().clean()
        origen = cleaned_data.get('aeropuerto_origen')
        destino = cleaned_data.get('aeropuerto_destino')
        
        # Validar que los aeropuertos no sean iguales
        if origen and destino and origen == destino:
            raise forms.ValidationError("Los códigos de aeropuerto no pueden ser iguales.")
        
        return cleaned_data