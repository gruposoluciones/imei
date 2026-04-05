# 📱 Análisis de Reportes IMEI

Aplicación completa para análisis estadístico y visualización de datos de activación/desactivación de IMEI en redes móviles. Disponible como script de escritorio y aplicación web interactiva.

## 🎯 Descripción

Este proyecto procesa archivos Excel con información de IMEI (International Mobile Equipment Identity) y proporciona:

- 📊 **Análisis Estadístico**: Cantidad de IMEI por número de documento
- 📈 **Patrón Temporal**: Gráfico de activaciones por fecha
- 🕸️ **Grafo Relacional**: Visualización de relaciones entre servicios móviles e IMEI
- 🌐 **Interfaz Web**: Aplicación interactiva con Streamlit

## 📋 Estructura de Datos

El archivo Excel debe contener las siguientes columnas:

| Columna | Tipo | Descripción |
|---------|------|------------|
| `IMEI` | String | Identificador único del dispositivo |
| `Número Servicio Móvil` | String | Número telefónico del servicio |
| `Fecha y Hora de Vinculación/Desvinculación` | DateTime | Fecha/hora de activación |
| `Empresa Operadora` | String | Operadora móvil |
| `Tipo de Abonado` | String | Tipo de cliente (persona, empresa) |
| `Tipo Documento Legal del Abonado` | String | Tipo de documento (DNI, RUC) |
| `Número Documento Legal del Abonado` | String | Número de identificación |
| `Tipo` | String | Vinculación o Desvinculación |

## 🚀 Inicio Rápido

### Opción 1: Script de Escritorio

```bash
cd /Users/percybeltran/Proyectos/IMEI
python3 AnalisisReporte.py
```

**Output:**
- Reportes en consola
- Gráficos guardados como PNG (300 DPI)
- `grafico_tiempo.png` - Serie temporal
- `grafico_relacional.png` - Grafo relacional

### Opción 2: Aplicación Web

```bash
cd /Users/percybeltran/Proyectos/IMEI
streamlit run streamlit_app.py
```

Accede a `http://localhost:8501` en tu navegador.

## 📦 Requisitos

### Dependencias Python

```bash
pip install pandas numpy matplotlib seaborn networkx openpyxl streamlit
```

### Versión mínima
- Python 3.9+
- Pandas 1.4+
- NetworkX 2.0+
- Streamlit 1.0+

## 📁 Estructura del Proyecto

```
IMEI/
├── AnalisisReporte.py          # Script principal (refactorizado)
├── streamlit_app.py            # Aplicación web interactiva
├── REFACTORING.md              # Documentación de cambios
├── readme.md                   # Este archivo
├── lista1.xlsx                 # Datos de ejemplo
├── lista2.xlsx                 # Datos adicionales
├── servicio.xlsx               # Datos de servicios
├── dist/                       # Ejecutable compilado
│   └── AnalisisReporte/        # App de escritorio
├── build/                      # Artefactos de compilación
└── grafico_*.png              # Gráficos generados
```

## 🎨 Características

### Análisis Estadístico
- Conteo de IMEI por documento
- Estadísticas resumidas (total, promedio)
- Formato tabular limpio

### Visualizaciones
1. **Gráfico Temporal**: Línea con patrones de activación
2. **Grafo Relacional**: 
   - Nodos circulares = Servicios móviles (región central)
   - Nodos cuadrados = IMEI (alrededor)
   - Conexiones = Relaciones con fechas

### Interfaz Web
- Carga interactiva de archivos
- Tabs organizadas (Estadísticas, Temporal, Grafo)
- Vista previa de datos
- Métricas destacadas
- Manejo de errores

## 📊 Ejemplo de Output

### Consola
```
======================================================================
ANÁLISIS DE REPORTES IMEI
======================================================================

✓ Datos cargados correctamente desde: lista1.xlsx
  Dimensiones: 9 filas, 9 columnas

======================================================================
REPORTE ESTADÍSTICO: CANTIDAD DE IMEI POR DOCUMENTO
======================================================================
 Número Documento  Cantidad de IMEI
         71103614                 9

======================================================================
PATRÓN TEMPORAL: ACTIVACIONES POR FECHA
======================================================================
Fecha y Hora de Vinculación/Desvinculación  Cantidad de Activaciones
                                2024-04-21                         1
                                2024-07-27                         1
...
```

## 🔧 Configuración

Edita las constantes en `AnalisisReporte.py`:

```python
# CONFIGURACIÓN
RUTA_ARCHIVO = '/Users/percybeltran/Proyectos/IMEI/lista1.xlsx'
DIRECTORIO_SALIDA = '/Users/percybeltran/Proyectos/IMEI'
```

## 📚 Funciones Principales

### AnalisisReporte.py

- `cargar_datos()` - Carga archivo Excel
- `preparar_fechas()` - Convierte a datetime
- `analisis_imei_por_documento()` - Estadísticas
- `analisis_activaciones_por_fecha()` - Patrón temporal
- `grafico_serie_temporal()` - Gráfico línea
- `grafico_relacional()` - Grafo de relaciones

### app_streamlit.py → streamlit_app.py

Aplicación web interactiva con las siguientes funciones:

## 🐛 Solución de Problemas

### Error: "Archivo no encontrado"
```
Solución: Verifica la ruta en RUTA_ARCHIVO
```

### Error: "Columna no existe"
```
Solución: Asegúrate que el Excel tenga las columnas esperadas
```

### Error SSL en Streamlit
```
Solución: Instala OpenSSL: brew install openssl
```

## 🚢 Despliegue

### Deploy en Streamlit Cloud

1. Sube a GitHub:
```bash
git init
git add .
git commit -m "Análisis IMEI refactorizado"
git remote add origin https://github.com/usuario/repo.git
git push -u origin main
```

2. Ve a [share.streamlit.io](https://share.streamlit.io)
3. Conecta tu repositorio GitHub
4. Streamlit Cloud automáticamente encontrará `streamlit_app.py`

### Ejecutable de Escritorio

El proyecto incluye un ejecutable compilado en `dist/AnalisisReporte.app` (macOS)

## 💡 Mejoras Recientes

✅ **v2.0** - Refactorización completa:
- Código modularizado en 9 funciones
- Documentación completa con docstrings
- Interfaz web mejorada con tabs
- Manejo de errores robusto
- Estilos visuales mejorados
- Type hints en funciones

Ver [REFACTORING.md](REFACTORING.md) para detalles completos.

## 📖 Documentación

- `REFACTORING.md` - Cambios de refactorización
- Docstrings en código Python
- Comentarios en secciones clave

## 👤 Autor

**Percy Beltrán**
- Fecha: 5 de abril de 2026
- Versión: 2.0

## 📄 Licencia

Proyecto educativo de análisis de datos.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/mejora`)
3. Commit tus cambios (`git commit -m 'Agrega mejora'`)
4. Push a la rama (`git push origin feature/mejora`)
5. Abre un Pull Request

---

**Estado del Proyecto:** ✅ Funcional y Refactorizado