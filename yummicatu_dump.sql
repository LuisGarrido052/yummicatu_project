-- ========================================================
-- YUMMI CATU - SCRIPT DE VOLCADO Y POBLAMIENTO MYSQL (XAMPP)
-- Asignatura: Programación Back End (Evaluación 2)
-- Motor: MySQL / MariaDB (Puerto 3306)
-- Codificación: utf8mb4 / utf8mb4_unicode_ci
-- ========================================================

SET FOREIGN_KEY_CHECKS = 0;
SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "-03:00";

-- 1. CREACIÓN Y SELECCIÓN DE BASE DE DATOS
CREATE DATABASE IF NOT EXISTS `yummicatu_db` 
  DEFAULT CHARACTER SET utf8mb4 
  COLLATE utf8mb4_unicode_ci;

USE `yummicatu_db`;

-- --------------------------------------------------------
-- 2. TABLA: reposteria_producto
-- Representa el catálogo de repostería artesanal
-- --------------------------------------------------------
DROP TABLE IF EXISTS `reposteria_producto`;

CREATE TABLE `reposteria_producto` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `categoria` varchar(100) NOT NULL,
  `descripcion` longtext NOT NULL,
  `foto` varchar(255) NOT NULL,
  `imagen_subida` varchar(100) DEFAULT NULL,
  `precio` int(10) unsigned NOT NULL CHECK (`precio` >= 0),
  `destacado` tinyint(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- POBLADO DE 6 PRODUCTOS REALISTAS
INSERT INTO `reposteria_producto` (`id`, `nombre`, `categoria`, `descripcion`, `foto`, `imagen_subida`, `precio`, `destacado`) VALUES
(1, 'Frutillas con Crema Tradicionales', 'Frutillas con crema', 'La insignia de Yummi Catu: frutillas chilenas seleccionadas a mano, bañadas en abundante crema Chantilly artesanal montada al día y coulis de frutos rojos.', 'img/productos/frutillas_tradicionales.jpg', NULL, 4500, 1),
(2, 'Torta Tres Leches Catu', 'Tortas', 'Bizcocho esponjoso remojado en nuestra mezcla secreta de tres leches perfumada con vainilla bourbon, coronada con suave merengue flameado y canela.', 'img/productos/torta_tres_leches.jpg', NULL, 18900, 1),
(3, 'Cheesecake de Frutos Rojos', 'Postres Fríos', 'Textura extra cremosa al estilo New York sobre crocante base de galletas de mantequilla, cubierto con mermelada y reducción de frambuesas y moras silvestres.', 'img/productos/cheesecake_frutos_rojos.jpg', NULL, 16500, 1),
(4, 'Tarta de Chocolate y Nutella', 'Tartas', 'Masa quebrada crujiente rellena con densa ganache de chocolate belga al 70%, abundante Nutella cremosa y virutas de chocolate semiamargo.', 'img/productos/tarta_chocolate.jpg', NULL, 15900, 1),
(5, 'Frutillas con Crema Suprema y Oreo', 'Frutillas con crema', 'Capas generosas de crema dulce artesanal, fresca selección de frutillas picadas, abundante salsa de chocolate y trocitos crocantes de galletas Oreo.', 'img/productos/frutillas_nutella.jpg', NULL, 5200, 1),
(6, 'Pie de Limón Merengado', 'Tartas', 'Base crocante de masa sablée con suave crema de limón natural de Pica y abundante merengue italiano flameado a la minuta.', 'img/productos/pie_de_limon.jpg', NULL, 14900, 0);

-- --------------------------------------------------------
-- 3. TABLA: reposteria_cliente
-- Representa a los clientes registrados (RUN como PK)
-- --------------------------------------------------------
DROP TABLE IF EXISTS `reposteria_cliente`;

CREATE TABLE `reposteria_cliente` (
  `run_cliente` varchar(10) NOT NULL,
  `nombre_cliente` varchar(100) NOT NULL,
  `apellido` varchar(100) NOT NULL,
  `correo` varchar(254) NOT NULL,
  `telefono` varchar(12) NOT NULL,
  PRIMARY KEY (`run_cliente`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- POBLADO DE 6 CLIENTES CHILENOS
INSERT INTO `reposteria_cliente` (`run_cliente`, `nombre_cliente`, `apellido`, `correo`, `telefono`) VALUES
('16987654-3', 'Cristóbal', 'Muñoz', 'cristobal.munoz@yahoo.es', '+56943210987'),
('17654321-K', 'Camila', 'González', 'camila.gonzalez@inacap.cl', '+56965432109'),
('18234567-8', 'Valentina', 'Morales', 'valentina.morales@duocuc.cl', '+56987654321'),
('18765432-1', 'Javiera', 'Castro', 'javiera.castro@profesor.cl', '+56932109876'),
('19456789-0', 'Matías', 'Silva', 'matias.silva@gmail.com', '+56976543210'),
('20123456-7', 'Francisca', 'Rojas', 'fran.rojas@gmail.com', '+56954321098');

-- --------------------------------------------------------
-- 4. TABLA: reposteria_solicitud
-- Representa los pedidos personalizados (ForeignKeys)
-- --------------------------------------------------------
DROP TABLE IF EXISTS `reposteria_solicitud`;

CREATE TABLE `reposteria_solicitud` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `detalle` longtext NOT NULL,
  `fecha` datetime(6) NOT NULL,
  `id_producto_id` bigint(20) NOT NULL,
  `run_cliente_id` varchar(10) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `reposteria_solicitud_id_producto_id_fk` (`id_producto_id`),
  KEY `reposteria_solicitud_run_cliente_id_fk` (`run_cliente_id`),
  CONSTRAINT `reposteria_solicitud_id_producto_fk` FOREIGN KEY (`id_producto_id`) REFERENCES `reposteria_producto` (`id`) ON DELETE CASCADE,
  CONSTRAINT `reposteria_solicitud_run_cliente_fk` FOREIGN KEY (`run_cliente_id`) REFERENCES `reposteria_cliente` (`run_cliente`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- POBLADO DE 6 SOLICITUDES PERSONALIZADAS
INSERT INTO `reposteria_solicitud` (`id`, `detalle`, `fecha`, `id_producto_id`, `run_cliente_id`) VALUES
(1, 'Para cumpleaños sorpresa este sábado a las 17:00 hrs. Agregar dedicatoria en tarjeta: \'¡Feliz Cumpleaños Vale!\' y crema Chantilly extra.', NOW(), 1, '18234567-8'),
(2, 'Torta para 20 personas, retiro en tienda el viernes a las 18:30 hrs. Decoración clásica con merengue flameado y canela.', NOW(), 2, '19456789-0'),
(3, 'Retiro para almuerzo familiar el domingo a las 13:00 hrs. Por favor incluir salsa extra de frambuesas silvestres por separado.', NOW(), 3, '17654321-K'),
(4, 'Para aniversario de bodas. Escribir dedicatoria sobre placa de chocolate blanco: \'Feliz Aniversario Fran y Diego, 5 años\'.', NOW(), 4, '20123456-7'),
(5, 'Pedido para compartir en oficina: 3 potes grandes con abundante salsa de chocolate y extra galleta Oreo triturada. Retiro a las 15:30 hrs.', NOW(), 5, '16987654-3'),
(6, 'Pie de limón para once familiar el sábado. Solicitud especial: merengue italiano bien dorado y reducción de azúcar en el relleno.', NOW(), 6, '18765432-1');

SET FOREIGN_KEY_CHECKS = 1;
