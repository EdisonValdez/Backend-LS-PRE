[![Local Secrets](https://img.shields.io/badge/Base%20Project-v1.0-red.svg)](#)
[![Python 3.10.2](https://img.shields.io/badge/python-3.10.2-blue.svg)](https://www.python.org/downloads/release/python-3102/)
[![Django 3.2.12](https://img.shields.io/badge/Django-3.2.12-green.svg)](https://www.djangoproject.com/download/)
[![Pipenv](https://img.shields.io/badge/Pipenv-2020%2B-yellow.svg)](https://pipenv.readthedocs.io/en/latest/basics/)

# Local Secrets

## Project structure
It's time to define the recommended project structure that we advise using this base_project based-project:

```bash
├── .docker
│         ├── app
│         │         └── Dockerfile
│         ├── environments
│         │         ├── local.env
│         │         ├── production.env
│         │         └── staging.env
│         ├── nginx
│         │         └── Dockerfile
│         ├── dev.yml
│         └── pro.yml
├── .editorconfig
├── .gitignore
├── .python-version
├── .scripts
├── .well-known
├── Pipfile
├── Pipfile.lock
├── README.md
├── local_secrets
│         ├── __init__.py
│         ├── cities
│         │         ├── __init__.py
│         │         ├── admin.py
│         │         ├── apps.py
│         │         ├── models.py
│         │         ├── serializers.py
│         │         ├── tests
│         │         │         └── ...
│         │         └── urls.py
│         ├── languages
│         │         ├── __init__.py
│         │         ├── admin.py
│         │         ├── apps.py
│         │         ├── models.py
│         │         ├── serializers.py
│         │         ├── tests
│         │         │         └── ...
│         │         └── urls.py
│         ├── messaging
│         │         ├── __init__.py
│         │         ├── providers.py
│         │         ├── tests
│         │         │         └── ...
│         ├── sites
│         │         ├── __init__.py
│         │         ├── admin.py
│         │         ├── apps.py
│         │         ├── models.py
│         │         ├── serializers.py
│         │         ├── tests
│         │         │         └── ...
│         │         └── urls.py
│         ├── travels
│         │         ├── __init__.py
│         │         ├── admin.py
│         │         ├── apps.py
│         │         ├── models.py
│         │         ├── serializers.py
│         │         ├── tests
│         │         │         └── ...
│         │         └── urls.py
│         ├── users
│         │         ├── __init__.py
│         │         ├── admin.py
│         │         ├── apps.py
│         │         ├── models.py
│         │         ├── serializers.py
│         │         ├── tests
│         │         │         └── ...
│         │         └── urls.py
│         ├── core
│         │           ├── __init__.py
│         │           ├── management
│         │           │         └── ...
│         │           ├── templates
│         │           │         └── ...
│         │           ├── templatetags
│         │           │         └── ...
│         │           ├── tests
│         │           │         └── ...
│         │           ├── utils
│         │           │         └── ...
│         │           ├── admin.py
│         │           ├── apps.py
│         │           ├── exception_handlers.py
│         │           ├── managers.py
│         │           ├── models.py
│         │           ├── serializers.py
│         │           └── storages.py
│         └── google-services.json
├── config
│         ├── __init__.py
│         ├── settings
│         │         ├── __init__.py
│         │         ├── base.py
│         │         ├── development.py
│         │         ├── local.py
│         │         ├── production.py
│         │         └── test.py
│         ├── urls.py
│         └── wsgi.py
├── docker-compose.yml
├── locale
│         └── [iso639-1-language-code]
│             └── LC_MESSAGES
│                 ├── django.mo
│                 └── django.po
├── manage.py
├── postman
│         └── ...
├── setup.cfg
├── static
│         └── ...
└── templates
          └── ...

```

## Modelos

### 1. Travel

El modelo `Travel` representa un viaje que incluye varias paradas (`stops`) en diferentes ciudades y sitios. Cada viaje es gestionado por un usuario.

- **Campos:**
  - `title`: Título del viaje.
  - `type`: Tipo de viaje (elegido de un conjunto de opciones predefinidas).
  - `cities`: Relación many-to-many con el modelo `City`.
  - `initial_date`: Fecha de inicio del viaje.
  - `end_date`: Fecha de finalización del viaje.
  - `stops`: Relación many-to-many con el modelo `Site` (utilizando el modelo intermedio `Stop`).
  - `user`: Usuario que gestiona el viaje (relación ForeignKey con `CustomUser`).

- **Relaciones:**
  - Un `Travel` tiene varias `stops` (sitios).
  - Un `Travel` puede abarcar múltiples `cities`.
  - Está asociado a un único `CustomUser`.

### 2. Stop

El modelo `Stop` representa una parada en un sitio específico dentro de un viaje.

- **Campos:**
  - `travel`: Relación ForeignKey con `Travel`, indicando a qué viaje pertenece la parada.
  - `site`: Relación ForeignKey con `Site`, indicando el sitio donde se realiza la parada.
  - `order`: Indica el orden de la parada dentro del viaje.

- **Relaciones:**
  - Un `Stop` pertenece a un `Travel` y está asociado a un `Site`.

### 3. CustomUser

El modelo `CustomUser` extiende el modelo de usuario estándar de Django. Además de la información básica del usuario, incluye detalles adicionales como el número de teléfono, imagen de perfil y preferencias de etiquetas.

- **Campos:**
  - `tags`: Relación many-to-many con `Tag`, a través de `UserTags`.
  - `phone_prefix`: Prefijo telefónico.
  - `phone`: Número de teléfono del usuario.
  - `profile_picture`: Imagen de perfil del usuario.
  - `language`: Relación ForeignKey con `Language`, indicando el idioma preferido del usuario.

- **Relaciones:**
  - Un `CustomUser` puede tener múltiples `tags` (relación many-to-many con `Tag`).
  - Puede recibir varias `notifications`.

### 4. Tag

El modelo `Tag` representa una etiqueta que puede ser asociada a un usuario o a otros objetos.

- **Campos:**
  - `title`: Nombre de la etiqueta.

- **Relaciones:**
  - Un `Tag` puede estar asociado a varios usuarios a través del modelo intermedio `UserTags`.

### 5. UserTags

El modelo intermedio `UserTags` gestiona la relación entre los usuarios y las etiquetas (`tags`).

- **Campos:**
  - `user`: Relación ForeignKey con `CustomUser`.
  - `tag`: Relación ForeignKey con `Tag`.

- **Relaciones:**
  - Asocia un `CustomUser` con uno o más `Tag`.

### 6. Notification

El modelo `Notification` representa una notificación que se envía a los usuarios. Puede estar asociada a un sitio específico.

- **Campos:**
  - `title`: Título de la notificación.
  - `body`: Cuerpo del mensaje.
  - `site`: Relación opcional con un `Site` al que la notificación está relacionada.
  - `link`: Enlace opcional asociado a la notificación.

- **Relaciones:**
  - Una notificación puede estar asociada a varios usuarios a través de `UserNotification`.

### 7. UserNotification

El modelo `UserNotification` representa la relación entre un usuario y una notificación, indicando si la notificación ha sido vista por el usuario.

- **Campos:**
  - `user`: Relación ForeignKey con `CustomUser`.
  - `notification`: Relación ForeignKey con `Notification`.
  - `has_been_seen`: Booleano que indica si la notificación ha sido vista.

- **Relaciones:**
  - Cada `UserNotification` asocia un usuario con una notificación.

### 8. Ambassador

El modelo `Ambassador` extiende el modelo `CustomUser` y representa un embajador que está asociado a varias ciudades.

- **Campos:**
  - `cities`: Relación many-to-many con `City`.

- **Relaciones:**
  - Un `Ambassador` puede estar asociado a varias `cities`.

## PhoneCode

El modelo `PhoneCode` se utiliza para almacenar información sobre códigos telefónicos. Incluye los siguientes campos:

- **name**: El nombre del código telefónico.
- **code**: El código ISO del país.
- **phone_code**: El código de teléfono (por defecto 34).

## TranslatedPhoneCode

Este modelo almacena las traducciones de los nombres de los códigos telefónicos para diferentes idiomas. Contiene los siguientes campos:

- **phone_code**: Clave foránea que hace referencia a `PhoneCode`.
- **language**: Clave foránea que hace referencia a `Language`.
- **name**: El nombre traducido del código telefónico.

## Country

El modelo `Country` representa países en la aplicación. Tiene los siguientes campos:

- **name**: El nombre del país.
- **code**: El código ISO del país.
- **phone_code**: El código de teléfono (por defecto 34).

## TranslatedCountry

Este modelo almacena las traducciones de los nombres de los países para diferentes idiomas. Incluye los siguientes campos:

- **country**: Clave foránea que hace referencia a `Country`.
- **language**: Clave foránea que hace referencia a `Language`.
- **name**: El nombre traducido del país.

## City

El modelo `City` se utiliza para almacenar información sobre ciudades. Sus campos incluyen:

- **name**: El nombre de la ciudad.
- **cp**: El código postal de la ciudad.
- **province**: La provincia donde se encuentra la ciudad.
- **point**: Campo geográfico que almacena la geolocalización de la ciudad.
- **description**: Descripción de la ciudad.
- **country**: Clave foránea que hace referencia a `Country`.
- **slogan**: Un eslogan asociado con la ciudad.
- **link**: Enlace opcional relacionado con la ciudad.
- **media**: Archivo de video asociado a la ciudad.
- **latitude**: Latitud de la ciudad.
- **longitude**: Longitud de la ciudad.
- **activated**: Booleano que indica si la ciudad está activa.

## TranslatedCity

Este modelo almacena las traducciones de la información de las ciudades en diferentes idiomas. Contiene los siguientes campos:

- **city**: Clave foránea que hace referencia a `City`.
- **language**: Clave foránea que hace referencia a `Language`.
- **name**: El nombre traducido de la ciudad.
- **province**: La provincia traducida.
- **description**: La descripción traducida de la ciudad.
- **slogan**: El eslogan traducido de la ciudad.

## CityImage

El modelo `CityImage` permite almacenar imágenes asociadas a las ciudades. Tiene los siguientes campos:

- **city**: Clave foránea que hace referencia a `City`.
- **image**: Campo para almacenar la imagen de la ciudad.

## Address

El modelo `Address` se utiliza para almacenar información de direcciones específicas. Incluye los siguientes campos:

- **street**: El nombre de la calle.
- **city**: Clave foránea que hace referencia a `City`.
- **cp**: El código postal de la dirección.
- **point**: Campo geográfico que almacena la geolocalización de la dirección.
- **latitude**: Latitud de la dirección.
- **longitude**: Longitud de la dirección.
- **google_place_id**: Identificador de lugar de Google.
- **details**: Detalles adicionales sobre la dirección.
- **number**: Número de la dirección.
- **door**: Puerta asociada a la dirección.
- **floor**: Piso asociado a la dirección.
- **creation_date**: Fecha de creación de la dirección.

## Relaciones entre Modelos

- **PhoneCode** y **TranslatedPhoneCode**: `TranslatedPhoneCode` tiene una relación de muchos a uno con `PhoneCode`, permitiendo múltiples traducciones por cada código telefónico.
- **Country** y **TranslatedCountry**: Similarmente, `TranslatedCountry` se relaciona con `Country`, permitiendo traducciones para los nombres de los países.
- **City** y **TranslatedCity**: `TranslatedCity` tiene una relación de muchos a uno con `City`, para las traducciones de las ciudades.
- **City** y **CityImage**: Cada `City` puede tener múltiples imágenes asociadas.
- **City** y **Address**: Cada `Address` está relacionada con una sola `City`, pero una `City` puede tener múltiples direcciones.

- Un `Travel` puede incluir varias `stops`, que son sitios representados por el modelo `Site`.
- Un `CustomUser` puede gestionar varios viajes (`Travel`), tener múltiples etiquetas (`Tag`) y recibir múltiples notificaciones (`Notification`).
- El modelo `Stop` sirve como enlace entre `Travel` y `Site`.
- Las notificaciones (`Notification`) pueden estar asociadas a usuarios a través de `UserNotification` y ser vistas o no vistas.
- Los embajadores (`Ambassador`) son usuarios especiales que pueden estar asociados a varias ciudades.

# Modelos de la Aplicación

## Site
El modelo `Site` representa un lugar que puede tener diferentes niveles, categorías y subcategorías. Incluye campos para el título, descripción, frecuencia, dirección, medios asociados, y su estado de aceptación.
Este modelo se usa tanto para los Lugares (type='place') como para los eventos (type='event').
Por lo general, los Lugare usan los horarios de Schedule y los eventos usan los horarios de SpecialSchedule

### Campos:
- `title`: `CharField`, máximo 500 caracteres, requerido.
- `levels`: `ManyToManyField` relacionado con el modelo `Level`.
- `categories`: `ManyToManyField` relacionado con el modelo `Category`.
- `subcategories`: `ManyToManyField` relacionado con el modelo `SubCategory`, opcional.
- `type`: `CharField`, opciones de `SiteType`, por defecto `PLACE`.
- `description`: `TextField`, requerido.
- `is_suggested`: `BooleanField`, por defecto `False`.
- `has_been_accepted`: `BooleanField`, por defecto `True`.
- `frequency`: `CharField`, opciones de `FrequencyChoices`, por defecto `never`.
- `media`: `FileField`, permite archivos de video, opcional.
- `url`: `CharField`, máximo 500 caracteres, opcional.
- `phone`: `CharField`, máximo 500 caracteres, opcional.
- `tags`: `ManyToManyField` relacionado con el modelo `Tag`.
- `users`: `ManyToManyField` relacionado con el modelo `CustomUser` a través de `FavoriteSites`.
- `address`: `ForeignKey` relacionado con el modelo `Address`, opcional.
- `city`: `ForeignKey` relacionado con el modelo `City`, opcional.
- `created_by`: `ForeignKey` relacionado con el modelo `CustomUser`, opcional.
- `always_open`: `BooleanField`, por defecto `False`.
- `is_top_10`: `BooleanField`, por defecto `False`.

## TranslatedSite
Modelo para almacenar las traducciones del título y la descripción de un `Site` en diferentes idiomas.

### Campos:
- `site`: `ForeignKey` relacionado con el modelo `Site`.
- `language`: `ForeignKey` relacionado con el modelo `Language`.
- `title`: `CharField`, máximo 500 caracteres, requerido.
- `description`: `TextField`, requerido.

## SiteImage
Modelo que asocia imágenes a un `Site` utilizando `ThumbnailerImageField` para manejar imágenes de miniatura.

### Campos:
- `site`: `ForeignKey` relacionado con el modelo `Site`.
- `image`: `ThumbnailerImageField`, permite subir imágenes.

## Level
Representa los niveles de búsqueda, con un campo de orden para definir su jerarquía.

### Campos:
- `title`: `CharField`, máximo 500 caracteres, requerido.
- `type`: `CharField`, opciones de `SiteType`, por defecto `PLACE`.
- `order`: `IntegerField`, por defecto `0`.

## TranslatedLevel
Modelo que gestiona las traducciones del `Level` en diferentes idiomas.

### Campos:
- `level`: `ForeignKey` relacionado con el modelo `Level`.
- `language`: `ForeignKey` relacionado con el modelo `Language`.
- `title`: `CharField`, máximo 500 caracteres, requerido.

## Category
Modelo que representa las categorías de un `Level`, con un campo de orden.

### Campos:
- `level`: `ForeignKey` relacionado con el modelo `Level`, opcional.
- `title`: `CharField`, máximo 500 caracteres, requerido.
- `type`: `CharField`, opciones de `SiteType`, por defecto `PLACE`.
- `order`: `IntegerField`, por defecto `0`.

## TranslatedCategory
Modelo para las traducciones de las categorías en diferentes idiomas.

### Campos:
- `category`: `ForeignKey` relacionado con el modelo `Category`.
- `language`: `ForeignKey` relacionado con el modelo `Language`.
- `title`: `CharField`, máximo 500 caracteres, requerido.

## SubCategory
Modelo que representa subcategorías dentro de una `Category`.

### Campos:
- `title`: `CharField`, máximo 500 caracteres, requerido.
- `type`: `CharField`, opciones de `SiteType`, por defecto `PLACE`.
- `category`: `ForeignKey` relacionado con el modelo `Category`, opcional.
- `order`: `IntegerField`, por defecto `0`.

## TranslatedSubCategory
Modelo para las traducciones de subcategorías en diferentes idiomas.

### Campos:
- `subcategory`: `ForeignKey` relacionado con el modelo `SubCategory`.
- `language`: `ForeignKey` relacionado con el modelo `Language`.
- `title`: `CharField`, máximo 500 caracteres, requerido.

## FavoriteSites
Modelo que gestiona la relación entre usuarios y sus sitios favoritos.

### Campos:
- `user`: `ForeignKey` relacionado con el modelo `CustomUser`.
- `site`: `ForeignKey` relacionado con el modelo `Site`.

## Schedule
Representa el horario regular de un `Site` y se relaciona con el modelo `HourRange`.

### Campos:
- `day`: `CharField`, máximo 100 caracteres, opciones de `Day.choices`.
- `site`: `ForeignKey` relacionado con el modelo `Site`.

## HourRange
Define los rangos de horas de apertura y cierre para un `Schedule`.

### Campos:
- `initial_hour`: `TimeField`, por defecto `08:00 AM`.
- `end_hour`: `TimeField`, por defecto `11:00 PM`.
- `schedule`: `ForeignKey` relacionado con el modelo `Schedule`.

## SpecialSchedule
Modelo para manejar horarios especiales que pueden aplicarse en días específicos.

### Campos:
- `day`: `DateField`.
- `site`: `ForeignKey` relacionado con el modelo `Site`.

## SpecialHourRange
Define los rangos de horas para horarios especiales.

### Campos:
- `initial_hour`: `TimeField`, por defecto `08:00`.
- `end_hour`: `TimeField`, por defecto `23:00`.
- `schedule`: `ForeignKey` relacionado con el modelo `SpecialSchedule`.

## Comment
Modelo que permite a los usuarios dejar comentarios y calificaciones sobre un `Site`.

### Campos:
- `user`: `ForeignKey` relacionado con el modelo `CustomUser`.
- `site`: `ForeignKey` relacionado con el modelo `Site`.
- `body`: `TextField`, requerido.
- `rating`: `IntegerField`, requerido, con un validador de máximo `5`.
- `created_at`: `DateTimeField`, requerido.

## DefaultImage
Modelo para almacenar imágenes predeterminadas.

### Campos:
- `title`: `CharField`, máximo 100 caracteres, requerido.
- `image`: `ThumbnailerImageField`, permite subir imágenes.

## ImageSize
Modelo que define las restricciones de tamaño mínimo y máximo para las imágenes.

### Campos:
- `min_width`: `IntegerField`, por defecto `512`.
- `min_height`: `IntegerField`, por defecto `512`.
- `max_width`: `IntegerField`, por defecto `4096`.
- `max_height`: `IntegerField`, por defecto `2160`.

## VideoSize
Modelo que define las restricciones de tamaño mínimo y máximo para los videos.

### Campos:
- `min_size`: `IntegerField`, por defecto `512`.
- `max_size`: `IntegerField`, por defecto `4096`.

&nbsp;

![logo rudo](https://sp-ao.shortpixel.ai/client/to_webp,q_lossless,ret_img,w_32,h_32/https://rudo.es/wp-content/uploads/2022/01/cropped-favicon-512x512-1.png)
Developed by **rudo apps** | desarrollo@rudo.es | [https://rudo.es](https://rudo.es)

<!-- MARKDOWN REFERENCE -->
<!-- https://www.markdownguide.org/basic-syntax/ -->



#   B a c k e n d - L S - P R E 
 
 
 