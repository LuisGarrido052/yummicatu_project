"""
Comando de gestión oficial para poblar la base de datos MySQL (XAMPP).
Uso: python manage.py poblar_datos
Crea exactamente 6 Productos, 6 Clientes y 6 Solicitudes realistas.
"""

from django.core.management.base import BaseCommand
from reposteria.models import Producto, Cliente, Solicitud


class Command(BaseCommand):
    help = "Puebla la base de datos MySQL con exactamente 6 productos, 6 clientes y 6 solicitudes (Evaluación 2)"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Iniciando poblamiento de datos en MySQL (yummicatu_db)..."))

        # ----------------------------------------------------
        # 1. 6 PRODUCTOS REALISTAS DE YUMMI CATU
        # ----------------------------------------------------
        productos_datos = [
            {
                "id": 1,
                "nombre": "Frutillas con Crema Tradicionales",
                "categoria": "Frutillas con crema",
                "descripcion": "La insignia de Yummi Catu: frutillas chilenas seleccionadas a mano, bañadas en abundante crema Chantilly artesanal montada al día y coulis de frutos rojos.",
                "foto": "img/productos/frutillas_tradicionales.jpg",
                "precio": 4500,
                "destacado": True
            },
            {
                "id": 2,
                "nombre": "Torta Tres Leches Catu",
                "categoria": "Tortas",
                "descripcion": "Bizcocho esponjoso remojado en nuestra mezcla secreta de tres leches perfumada con vainilla bourbon, coronada con suave merengue flameado y canela.",
                "foto": "img/productos/torta_tres_leches.jpg",
                "precio": 18900,
                "destacado": True
            },
            {
                "id": 3,
                "nombre": "Cheesecake de Frutos Rojos",
                "categoria": "Postres Fríos",
                "descripcion": "Textura extra cremosa al estilo New York sobre crocante base de galletas de mantequilla, cubierto con mermelada y reducción de frambuesas y moras silvestres.",
                "foto": "img/productos/cheesecake_frutos_rojos.jpg",
                "precio": 16500,
                "destacado": True
            },
            {
                "id": 4,
                "nombre": "Tarta de Chocolate y Nutella",
                "categoria": "Tartas",
                "descripcion": "Masa quebrada crujiente rellena con densa ganache de chocolate belga al 70%, abundante Nutella cremosa y virutas de chocolate semiamargo.",
                "foto": "img/productos/tarta_chocolate.jpg",
                "precio": 15900,
                "destacado": True
            },
            {
                "id": 5,
                "nombre": "Frutillas con Crema Suprema y Oreo",
                "categoria": "Frutillas con crema",
                "descripcion": "Capas generosas de crema dulce artesanal, fresca selección de frutillas picadas, abundante salsa de chocolate y trocitos crocantes de galletas Oreo.",
                "foto": "img/productos/frutillas_nutella.jpg",
                "precio": 5200,
                "destacado": True
            },
            {
                "id": 6,
                "nombre": "Pie de Limón Merengado",
                "categoria": "Tartas",
                "descripcion": "Base crocante de masa sablée con suave crema de limón natural de Pica y abundante merengue italiano flameado a la minuta.",
                "foto": "img/productos/pie_de_limon.jpg",
                "precio": 14900,
                "destacado": False
            }
        ]

        prods_creados = 0
        for p in productos_datos:
            _, created = Producto.objects.update_or_create(
                id=p["id"],
                defaults={
                    "nombre": p["nombre"],
                    "categoria": p["categoria"],
                    "descripcion": p["descripcion"],
                    "foto": p["foto"],
                    "precio": p["precio"],
                    "destacado": p["destacado"],
                }
            )
            if created:
                prods_creados += 1

        self.stdout.write(self.style.SUCCESS(f"[OK] 6 Productos registrados exitosamente ({prods_creados} nuevos)."))

        # ----------------------------------------------------
        # 2. 6 CLIENTES CHILENOS CON RUN VÁLIDO
        # ----------------------------------------------------
        clientes_datos = [
            {
                "run_cliente": "18234567-8",
                "nombre_cliente": "Valentina",
                "apellido": "Morales",
                "correo": "valentina.morales@duocuc.cl",
                "telefono": "+56987654321"
            },
            {
                "run_cliente": "19456789-0",
                "nombre_cliente": "Matías",
                "apellido": "Silva",
                "correo": "matias.silva@gmail.com",
                "telefono": "+56976543210"
            },
            {
                "run_cliente": "17654321-K",
                "nombre_cliente": "Camila",
                "apellido": "González",
                "correo": "camila.gonzalez@inacap.cl",
                "telefono": "+56965432109"
            },
            {
                "run_cliente": "20123456-7",
                "nombre_cliente": "Francisca",
                "apellido": "Rojas",
                "correo": "fran.rojas@gmail.com",
                "telefono": "+56954321098"
            },
            {
                "run_cliente": "16987654-3",
                "nombre_cliente": "Cristóbal",
                "apellido": "Muñoz",
                "correo": "cristobal.munoz@yahoo.es",
                "telefono": "+56943210987"
            },
            {
                "run_cliente": "18765432-1",
                "nombre_cliente": "Javiera",
                "apellido": "Castro",
                "correo": "javiera.castro@profesor.cl",
                "telefono": "+56932109876"
            }
        ]

        clientes_creados = 0
        for c in clientes_datos:
            _, created = Cliente.objects.update_or_create(
                run_cliente=c["run_cliente"],
                defaults={
                    "nombre_cliente": c["nombre_cliente"],
                    "apellido": c["apellido"],
                    "correo": c["correo"],
                    "telefono": c["telefono"]
                }
            )
            if created:
                clientes_creados += 1

        self.stdout.write(self.style.SUCCESS(f"[OK] 6 Clientes registrados exitosamente ({clientes_creados} nuevos)."))

        # ----------------------------------------------------
        # 3. 6 SOLICITUDES CON DETALLES PERSONALIZADOS
        # ----------------------------------------------------
        solicitudes_datos = [
            {
                "id": 1,
                "run_cliente": "18234567-8",
                "id_producto": 1,
                "detalle": "Para cumpleaños sorpresa este sábado a las 17:00 hrs. Agregar dedicatoria en tarjeta: '¡Feliz Cumpleaños Vale!' y crema Chantilly extra."
            },
            {
                "id": 2,
                "run_cliente": "19456789-0",
                "id_producto": 2,
                "detalle": "Torta para 20 personas, retiro en tienda el viernes a las 18:30 hrs. Decoración clásica con merengue flameado y canela."
            },
            {
                "id": 3,
                "run_cliente": "17654321-K",
                "id_producto": 3,
                "detalle": "Retiro para almuerzo familiar el domingo a las 13:00 hrs. Por favor incluir salsa extra de frambuesas silvestres por separado."
            },
            {
                "id": 4,
                "run_cliente": "20123456-7",
                "id_producto": 4,
                "detalle": "Para aniversario de bodas. Escribir dedicatoria sobre placa de chocolate blanco: 'Feliz Aniversario Fran y Diego, 5 años'."
            },
            {
                "id": 5,
                "run_cliente": "16987654-3",
                "id_producto": 5,
                "detalle": "Pedido para compartir en oficina: 3 potes grandes con abundante salsa de chocolate y extra galleta Oreo triturada. Retiro a las 15:30 hrs."
            },
            {
                "id": 6,
                "run_cliente": "18765432-1",
                "id_producto": 6,
                "detalle": "Pie de limón para once familiar el sábado. Solicitud especial: merengue italiano bien dorado y reducción de azúcar en el relleno."
            }
        ]

        sol_creadas = 0
        for s in solicitudes_datos:
            cliente_obj = Cliente.objects.get(run_cliente=s["run_cliente"])
            prod_obj = Producto.objects.get(id=s["id_producto"])
            _, created = Solicitud.objects.update_or_create(
                id=s["id"],
                defaults={
                    "run_cliente": cliente_obj,
                    "id_producto": prod_obj,
                    "detalle": s["detalle"]
                }
            )
            if created:
                sol_creadas += 1

        self.stdout.write(self.style.SUCCESS(f"[OK] 6 Solicitudes registradas exitosamente ({sol_creadas} nuevas)."))
        self.stdout.write(self.style.SUCCESS("Poblamiento completo exitoso! Total: 18 registros en MySQL (6 por modelo)."))
