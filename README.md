# 🎓 Sistema de Gestión de Proyectos Académicos

Sistema web completo desarrollado en Django para la gestión integral de proyectos educativos, facilitando la colaboración efectiva entre estudiantes y profesores con seguimiento detallado del progreso y evaluación automatizada.

## 🚀 Funcionalidades Principales

### 👨‍🎓 **Para Estudiantes:**

#### **🔐 Autenticación y Perfil**
- ✅ Registro e inicio de sesión seguro
- ✅ Recuperación de contraseña por email
- ✅ Perfil personalizable con información académica
- ✅ Asignación automática a profesores

#### **📁 Gestión de Proyectos**
- ✅ **Vista "Mis Proyectos"** - Lista completa de proyectos donde participa
- ✅ **Roles múltiples** - Puede ser propietario o miembro de proyectos
- ✅ **Creación de proyectos** con descripción, fechas y miembros
- ✅ **Edición colaborativa** de proyectos existentes
- ✅ **Dashboard de progreso** con estadísticas visuales
- ✅ **Cálculo automático de calificaciones** basado en tareas completadas

#### **📋 Gestión de Tareas**
- ✅ **CRUD completo** - Crear, leer, actualizar y eliminar tareas
- ✅ **Estados dinámicos** - Pendiente, En Progreso, Completada
- ✅ **Asignación flexible** - Tareas propias y de proyectos donde participa
- ✅ **Fechas límite** con alertas visuales
- ✅ **Porcentaje de progreso** ajustable manualmente
- ✅ **Comentarios** en tareas para comunicación
- ✅ **Archivos adjuntos** y enlaces externos

#### **🎯 Gestión de Hitos**
- ✅ **Creación de hitos** para proyectos donde participa
- ✅ **Fechas de entrega** con seguimiento automático
- ✅ **Estados personalizables** (Pendiente, En Progreso, Completado)
- ✅ **Progreso visual** con barras de avance
- ✅ **Integración con tareas** del proyecto

#### **📊 Reportes y Estadísticas**
- ✅ **Reportes automáticos** de rendimiento personal
- ✅ **Estadísticas detalladas** de proyectos y tareas
- ✅ **Gráficos de progreso** visual
- ✅ **Historial de actividades** y logros
- ✅ **Métricas de productividad** personalizadas

### 👨‍🏫 **Para Profesores:**

#### **👥 Gestión de Estudiantes**
- ✅ **Dashboard de supervisión** con vista general de estudiantes asignados
- ✅ **Lista de estudiantes** con información académica completa
- ✅ **Seguimiento individual** por estudiante específico
- ✅ **Estadísticas de rendimiento** por estudiante

#### **📁 Supervisión de Proyectos**
- ✅ **Vista completa** de todos los proyectos de estudiantes asignados
- ✅ **Visibilidad total** - Ve proyectos donde estudiantes son propietarios O miembros
- ✅ **Creación de proyectos** para asignar a estudiantes
- ✅ **Monitoreo de progreso** en tiempo real
- ✅ **Sistema de calificaciones** integrado

#### **📋 Supervisión de Tareas**
- ✅ **Lista completa** de tareas de estudiantes asignados
- ✅ **Vista individual** de tareas por estudiante
- ✅ **Sistema de calificación** con notas numéricas (0-100)
- ✅ **Comentarios y feedback** en cada tarea
- ✅ **Filtros avanzados** por estado, estudiante, proyecto
- ✅ **Alertas de fechas** límite próximas

#### **🎯 Seguimiento de Hitos**
- ✅ **Monitoreo completo** de hitos de todos los proyectos estudiantiles
- ✅ **Vista cronológica** de entregas y fechas límite
- ✅ **Estado de cumplimiento** de objetivos académicos

#### **📊 Reportes Académicos**
- ✅ **Reportes generales** de todos los estudiantes asignados
- ✅ **Reportes individuales** detallados por estudiante
- ✅ **Estadísticas de clase** y rendimiento grupal
- ✅ **Métricas de participación** y colaboración
- ✅ **Historial de calificaciones** y progreso temporal

#### **💬 Sistema de Comunicación**
- ✅ **Comentarios en proyectos** para feedback directo
- ✅ **Comentarios en tareas** para evaluación detallada
- ✅ **Historial de interacciones** con cada estudiante

### 🔧 **Funcionalidades del Sistema:**

#### **🔒 Seguridad y Autenticación**
- ✅ **Sistema de roles** robusto (Estudiante/Profesor)
- ✅ **Recuperación de contraseña** por email con Gmail
- ✅ **Sesiones seguras** con protección CSRF
- ✅ **Validación de permisos** en todas las vistas
- ✅ **Logs de seguridad** para auditoría

#### **📧 Sistema de Email**
- ✅ **Configuración Gmail** para recuperación de contraseñas
- ✅ **Plantillas de email** personalizadas
- ✅ **Envío automático** de notificaciones

#### **🎨 Interfaz de Usuario**
- ✅ **Diseño responsive** con Bootstrap
- ✅ **Dashboard personalizado** por rol de usuario
- ✅ **Navegación intuitiva** con menús contextuales
- ✅ **Alertas visuales** para estados y fechas
- ✅ **Gráficos interactivos** de progreso
- ✅ **Formularios optimizados** con validación en tiempo real

#### **📊 Sistema de Calificaciones**
- ✅ **Calificación automática** de proyectos basada en tareas
- ✅ **Escalas personalizables** (0-100, A-F, etc.)
- ✅ **Promedio ponderado** de calificaciones
- ✅ **Historial de calificaciones** por estudiante
- ✅ **Reportes de rendimiento** académico

#### **🔄 Consistencia de Datos**
- ✅ **Lógica unificada** en todas las vistas
- ✅ **Visibilidad coherente** para profesores y estudiantes
- ✅ **Integridad referencial** en base de datos
- ✅ **Consultas optimizadas** con Q objects de Django

## Estructura del Proyecto

```
project_manager/
├── authentication/     # Gestión de usuarios y autenticación
├── projects/          # Gestión de proyectos y hitos
├── tasks/            # Gestión de tareas
├── reports/          # Generación y visualización de reportes
├── templates/        # Plantillas HTML
├── static/          # Archivos estáticos (CSS, JS)
├── media/           # Archivos subidos por usuarios
└── project_manager/ # Configuración principal
```

## 📦 Instalación y Configuración

### **1. Requisitos Previos:**
- Python 3.8+ instalado
- Git (opcional)
- Editor de código (VSCode recomendado)

### **2. Instalación:**

```bash
# 1. Descargar el proyecto
git clone <url-del-repo>
cd gestion-de-proyectos

# 2. Crear entorno virtual
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac

# 5. Configurar base de datos
python manage.py makemigrations
python manage.py migrate

# 6. Cargar datos de prueba (opcional)
python manage.py loaddata fixtures/sample_data.json

# 7. Ejecutar servidor
python manage.py runserver
```

### **3. Acceso al Sistema:**
- **URL:** `http://127.0.0.1:8000`
- **Admin:** `http://127.0.0.1:8000/admin/`
- **Credenciales:** Ver `CREDENCIALES_SISTEMA.md`

### **4. Configuración de Email (Opcional):**
Editar `.env.email` con tu configuración SMTP para recuperación de contraseñas.

## 🛠️ Tecnologías Utilizadas

### **Backend:**
- **Django 5.2** - Framework web principal
- **Python 3.x** - Lenguaje de programación
- **SQLite** - Base de datos (desarrollo)
- **Django ORM** - Mapeo objeto-relacional

### **Frontend:**
- **HTML5** - Estructura de páginas
- **CSS3** - Estilos y animaciones
- **Bootstrap 5** - Framework CSS responsive
- **JavaScript** - Interactividad del cliente
- **Django Templates** - Sistema de plantillas

### **Librerías Adicionales:**
- **Pillow** - Procesamiento de imágenes
- **python-decouple** - Gestión de variables de entorno
- **Django Crispy Forms** - Formularios mejorados

### **Herramientas de Desarrollo:**
- **VSCode** - Editor configurado para Django
- **Git** - Control de versiones
- **Virtual Environment** - Aislamiento de dependencias

## 📊 Modelos de Datos

### **🔐 Authentication (Autenticación)**
- **User** - Usuario base de Django extendido
- **UserProfile** - Perfil con rol (estudiante/profesor) y relaciones

### **📁 Projects (Proyectos)**
- **Project** - Proyecto con título, descripción, fechas, estado y calificación
- **ProjectComment** - Comentarios en proyectos para feedback
- **Milestone** - Hitos del proyecto con fechas y progreso

### **📋 Tasks (Tareas)**
- **Task** - Tareas con estado, progreso, fechas y asignación
- **TaskComment** - Comentarios en tareas para comunicación
- **TaskAttachment** - Archivos adjuntos a tareas
- **TaskLink** - Enlaces externos relacionados con tareas
- **TaskGrade** - Calificaciones de tareas (0-100)

### **📈 Reports (Reportes)**
- **Report** - Reportes generados automáticamente
- **ReportData** - Datos específicos de cada reporte

### **🔗 Relaciones Clave:**
- **Muchos a Muchos:** Project ↔ User (miembros)
- **Uno a Muchos:** Project → Task, Project → Milestone
- **Uno a Muchos:** User → Task (asignación), User → Comments
- **Uno a Uno:** UserProfile ↔ User (profesor asignado)

## 🚀 Uso del Sistema

### **🔑 Credenciales de Acceso:**
Ver archivo `CREDENCIALES_SISTEMA.md` para usuarios de prueba.

### **👨‍🎓 Como Estudiante:**
1. **Acceder**: `http://127.0.0.1:8000/auth/login/`
2. **Dashboard**: Ver resumen de proyectos y tareas
3. **Mis Proyectos**: Gestionar proyectos donde participa
4. **Mis Tareas**: Crear y actualizar tareas
5. **Hitos**: Crear hitos para proyectos
6. **Reportes**: Ver estadísticas de rendimiento

### **👨‍🏫 Como Profesor:**
1. **Acceder**: `http://127.0.0.1:8000/auth/login/`
2. **Dashboard**: Ver resumen de estudiantes asignados
3. **Estudiantes**: Lista y seguimiento individual
4. **Proyectos**: Supervisar todos los proyectos estudiantiles
5. **Tareas**: Calificar y comentar tareas
6. **Reportes**: Generar reportes académicos

## 🎯 Estado del Proyecto

### **✅ COMPLETADO AL 100%**
- ✅ **Sistema base** Django funcional
- ✅ **Autenticación completa** con recuperación de contraseña
- ✅ **Gestión de proyectos** con roles múltiples
- ✅ **Sistema de tareas** con calificaciones
- ✅ **Hitos y seguimiento** de progreso
- ✅ **Reportes automáticos** y estadísticas
- ✅ **Interfaz responsive** y optimizada
- ✅ **Consistencia de datos** en todo el sistema
- ✅ **Testing completo** y validado

## 🔮 Funcionalidades Futuras

- [ ] **Notificaciones push** en tiempo real
- [ ] **API REST** para integración móvil
- [ ] **Exportación PDF** de reportes
- [ ] **Calendario integrado** con eventos
- [ ] **Chat en tiempo real** entre usuarios
- [ ] **Integración con Git** para proyectos de código
- [ ] **Sistema de badges** y gamificación

## 📁 Estructura del Proyecto

```
project_manager/
├── authentication/          # 🔐 Sistema de autenticación y perfiles
│   ├── models.py           # UserProfile y extensiones de User
│   ├── views.py            # Login, registro, recuperación
│   ├── forms.py            # Formularios de autenticación
│   └── urls.py             # URLs de autenticación
├── projects/               # 📁 Gestión de proyectos
│   ├── models.py           # Project, Milestone, ProjectComment
│   ├── student_views.py    # Vistas específicas de estudiantes
│   ├── teacher_views.py    # Vistas específicas de profesores
│   ├── dashboard_views.py  # Dashboards personalizados
│   └── urls.py             # URLs de proyectos
├── tasks/                  # 📋 Gestión de tareas
│   ├── models.py           # Task, TaskComment, TaskGrade, etc.
│   ├── views.py            # CRUD de tareas y calificaciones
│   └── urls.py             # URLs de tareas
├── reports/                # 📊 Sistema de reportes
│   ├── models.py           # Report y ReportData
│   ├── views.py            # Generación de reportes
│   └── urls.py             # URLs de reportes
├── templates/              # 🎨 Plantillas HTML
│   ├── base.html           # Plantilla base responsive
│   ├── authentication/     # Templates de login/registro
│   ├── projects/           # Templates de proyectos
│   └── tasks/              # Templates de tareas
├── static/                 # 🎨 Archivos estáticos
│   ├── css/                # Estilos personalizados
│   ├── js/                 # JavaScript interactivo
│   └── images/             # Imágenes del sistema
├── media/                  # 📎 Archivos subidos
│   └── task_attachments/   # Adjuntos de tareas
├── project_manager/        # ⚙️ Configuración Django
│   ├── settings.py         # Configuraciones principales
│   ├── urls.py             # URLs principales
│   └── middleware.py       # Middleware personalizado
├── .vscode/                # 🔧 Configuración VSCode
│   └── settings.json       # Configuración para Django
├── requirements.txt        # 📦 Dependencias Python
├── manage.py               # 🚀 Script de gestión Django
├── db.sqlite3              # 💾 Base de datos SQLite
├── .env.example            # ⚙️ Ejemplo de configuración
├── .env.email              # 📧 Configuración de email
└── README.md               # 📖 Esta documentación
```

## 👥 Contribuir

¿Quieres contribuir al proyecto? ¡Genial!

### **🔧 Para Desarrolladores:**
1. **Fork** del repositorio
2. **Crear rama** para nueva funcionalidad: `git checkout -b feature/nueva-funcionalidad`
3. **Desarrollar** con pruebas incluidas
4. **Commit** con mensajes descriptivos: `git commit -m "Agregar nueva funcionalidad X"`
5. **Push** a tu rama: `git push origin feature/nueva-funcionalidad`
6. **Crear Pull Request** con descripción detallada

### **🐛 Para Reportar Bugs:**
1. **Verificar** que no existe un issue similar
2. **Crear issue** con descripción detallada
3. **Incluir pasos** para reproducir el error
4. **Agregar screenshots** si es relevante

### **💡 Para Sugerir Funcionalidades:**
1. **Abrir issue** con etiqueta "enhancement"
2. **Describir** la funcionalidad propuesta
3. **Justificar** la necesidad y beneficios
4. **Proponer** implementación si tienes ideas

## 📄 Licencia

Este proyecto está desarrollado con fines educativos y se distribuye bajo la **Licencia MIT**.

### **✅ Puedes:**
- ✅ Usar comercialmente
- ✅ Modificar el código
- ✅ Distribuir
- ✅ Usar privadamente

### **⚠️ Condiciones:**
- ⚠️ Incluir la licencia y copyright
- ⚠️ Los cambios deben estar documentados

---

## 🎓 Créditos

**Sistema de Gestión de Proyectos Académicos**  
Desarrollado con Django 5.2 y mucho ☕

### **📞 Soporte:**
- **Documentación:** Ver archivos .md en el proyecto
- **Credenciales:** `CREDENCIALES_SISTEMA.md`
- **Historias de Usuario:** `Historias_Usuario.md`

---

**¡Gracias por usar nuestro Sistema de Gestión de Proyectos!** 🎉

*Última actualización: Septiembre 2025*