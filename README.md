# Agency Dashboard Backend 🚀

Este proyecto es el backend de una plataforma de administración para agencias (Agency Dashboard). Proporciona una API RESTful robusta y eficiente para gestionar clientes (Clients) y sus respectivos agentes (Agents) asignados.

## 🏗️ Arquitectura y Tecnologías
El sistema está construido en **Python** utilizando **FastAPI**, lo que garantiza un alto rendimiento y la generación automática de documentación interactiva (Swagger UI). 

El código está estructurado bajo los principios de la **Arquitectura Hexagonal (Ports and Adapters)**, lo cual divide la aplicación en capas claras:
- **Domain**: Contiene las entidades puras de negocio.
- **Application**: Define los casos de uso y los puertos (interfaces) del sistema.
- **Infrastructure**: Implementa los detalles técnicos como los controladores de la API y la conexión a la base de datos a través de repositorios.

Para la persistencia de datos, se utiliza **PostgreSQL** orquestado mediante contenedores de **Docker** (`docker-compose`), y se interactúa con la base de datos utilizando **SQLAlchemy** como ORM.

## ⚙️ Características Principales
- **Gestión de Clientes**: Endpoints para crear clientes, consultar el catálogo completo o buscar detalles por ID.
- **Gestión de Agentes**: Funcionalidad para listar todos los agentes operativos asignados a un cliente en específico.
- **Validación de Datos**: Uso exhaustivo de Pydantic para garantizar la integridad de las peticiones.

## 🚀 Cómo ejecutarlo localmente
1. Levantar la base de datos: `docker-compose up -d`
2. Crear el entorno virtual: `python -m venv venv` e instalar dependencias: `pip install -r requirements.txt`
3. Arrancar el servidor: `uvicorn src.main:app --reload`
4. Visitar `http://127.0.0.1:8000/docs` para explorar la API.
