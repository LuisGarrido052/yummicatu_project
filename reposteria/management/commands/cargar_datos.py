"""
Comando de gestión de Django para poblar la Base de Datos desde productos.json.
Uso: python manage.py cargar_datos
Permite pasar de la Fase 1 (Mock JSON) a la Fase 2 (Base de Datos ORM) con un solo comando.
"""

import json
from pathlib import Path
from django.core.management.base import BaseCommand
from reposteria.models import Producto, Cliente, Solicitud


class Command(BaseCommand):
    help = "Carga los productos de data/productos.json en el modelo ORM Producto"

    def handle(self, *args, **options):
        ruta_json = Path(__file__).resolve().parent.parent.parent / 'data' / 'productos.json'
        if not ruta_json.exists():
            self.stderr.write(self.style.ERROR(f"No se encontró el archivo {ruta_json}"))
            return

        with open(ruta_json, mode='r', encoding='utf-8') as f:
            productos_data = json.load(f)

        creados = 0
        actualizados = 0

        for item in productos_data:
            obj, created = Producto.objects.update_or_create(
                id=item.get('id'),
                defaults={
                    'nombre': item.get('nombre'),
                    'categoria': item.get('categoria'),
                    'descripcion': item.get('descripcion'),
                    'foto': item.get('foto', 'img/productos/frutillas_tradicionales.jpg'),
                    'precio': item.get('precio', 4500),
                    'destacado': item.get('destacado', True),
                }
            )
            if created:
                creados += 1
            else:
                actualizados += 1

        self.stdout.write(self.style.SUCCESS(
            f"¡Carga completada! {creados} productos creados, {actualizados} productos actualizados."
        ))

        # Crear cliente de prueba si no existe
        cliente_demo, created_cliente = Cliente.objects.get_or_create(
            run_cliente="19876543-2",
            defaults={
                'nombre_cliente': 'Valentina',
                'apellido': 'Pérez Morales',
                'correo': 'valentina.perez@duocuc.cl',
                'telefono': '+56987654321',
            }
        )
        if created_cliente:
            self.stdout.write(self.style.SUCCESS(f"Cliente de demostración creado: {cliente_demo}"))

            # Crear solicitud de prueba para visualizar en Admin
            prod_primer = Producto.objects.first()
            if prod_primer:
                solicitud_demo = Solicitud.objects.create(
                    run_cliente=cliente_demo,
                    id_producto=prod_primer,
                    detalle="Pedido para cumpleaños este sábado: 2 potes grandes de frutillas con crema chantilly y dedicatoria 'Feliz Cumple Vale'."
                )
                self.stdout.write(self.style.SUCCESS(f"Solicitud de demostración creada: #{solicitud_demo.id}"))
