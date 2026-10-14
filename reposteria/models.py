"""
Modelos ORM de la aplicación Repostería - Negocio Yummi Catu.
Requisito Evaluación 2:
- Modelo Producto (catálogo de repostería y frutillas con crema)
- Modelo Cliente (identificado por RUN chileno)
- Modelo Solicitud (relación entre Cliente y Producto con detalle del encargo)
"""

from django.db import models


class Producto(models.Model):
    """
    Representa un producto dulce o postre artesanal ofrecido en Yummi Catu.
    Cumple con los 4 campos obligatorios de la pauta:
    - nombre
    - categoria (o tipo)
    - descripcion
    - foto
    """
    nombre = models.CharField(
        max_length=100,
        verbose_name="Nombre del Producto"
    )
    categoria = models.CharField(
        max_length=100,
        verbose_name="Categoría / Tipo",
        help_text="Ej: Especialidad de la Casa, Tortas y Pasteles, Postres Fríos"
    )
    descripcion = models.TextField(
        verbose_name="Descripción detallada"
    )
    foto = models.CharField(
        max_length=255,
        default="img/productos/frutillas_tradicionales.jpg",
        verbose_name="Ruta estática de la foto",
        help_text="Ruta relativa dentro de static/ (ej: img/productos/frutillas_tradicionales.jpg)"
    )
    imagen_subida = models.ImageField(
        upload_to="productos/",
        blank=True,
        null=True,
        verbose_name="Imagen subida (opcional vía Admin)",
        help_text="Opcional: subir archivo directamente al servidor (carpeta media/)"
    )
    precio = models.PositiveIntegerField(
        default=4500,
        verbose_name="Precio en CLP"
    )
    destacado = models.BooleanField(
        default=True,
        verbose_name="¿Producto Destacado?"
    )

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['id']

    def __str__(self):
        return f"{self.nombre} ({self.categoria})"

    @property
    def url_imagen(self):
        """Retorna la URL apropiada ya sea de media o static"""
        if self.imagen_subida:
            return self.imagen_subida.url
        if self.foto:
            if self.foto.startswith('http') or self.foto.startswith('/'):
                return self.foto
            return f"/static/{self.foto}"
        return "/static/img/productos/frutillas_tradicionales.jpg"


class Cliente(models.Model):
    """
    Representa a un cliente registrado o que realiza un encargo en Yummi Catu.
    Identificado unívocamente por su RUN chileno (sin puntos y con guion, o numérico).
    """
    run_cliente = models.CharField(
        max_length=10,
        primary_key=True,
        verbose_name="RUN del Cliente",
        help_text="Formato: 12345678-9 o 12345678-K"
    )
    nombre_cliente = models.CharField(
        max_length=100,
        verbose_name="Nombre"
    )
    apellido = models.CharField(
        max_length=100,
        verbose_name="Apellido"
    )
    correo = models.EmailField(
        verbose_name="Correo Electrónico"
    )
    telefono = models.CharField(
        max_length=12,
        verbose_name="Teléfono / WhatsApp",
        help_text="Ej: +56912345678"
    )

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['nombre_cliente', 'apellido']

    def __str__(self):
        return f"{self.nombre_cliente} {self.apellido} ({self.run_cliente})"


class Solicitud(models.Model):
    """
    Representa un encargo o pedido personalizado realizado por un cliente en Yummi Catu.
    Relaciona en base de datos al Cliente y al Producto mediante claves foráneas (ForeignKey).
    """
    id = models.AutoField(
        primary_key=True,
        verbose_name="ID de Solicitud"
    )
    run_cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name="pedidos",
        verbose_name="Cliente Solicitante"
    )
    id_producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name="solicitudes",
        verbose_name="Producto Solicitado"
    )
    detalle = models.TextField(
        verbose_name="Detalle del Encargo / Requisitos",
        help_text="Ej: dedicatoria especial, fecha y hora de entrega, porciones, sin azúcar"
    )
    fecha = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha y Hora de Creación"
    )

    class Meta:
        verbose_name = "Solicitud de Encargo"
        verbose_name_plural = "Solicitudes de Encargo"
        ordering = ['-fecha']

    def __str__(self):
        return f"Solicitud #{self.id} - {self.run_cliente.nombre_cliente} ({self.id_producto.nombre})"
