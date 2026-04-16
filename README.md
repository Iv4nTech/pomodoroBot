# Bot de Pomodoro para Discord

Bot de Discord con la tecnica Pomodoro que gestiona sesiones de estudio/trabajo. Se une al canal de voz del usuario, reproduce musica lofi durante el tiempo de concentracion, y avisa por voz y por texto al inicio y fin de cada sesion.

## Caracteristicas

- Gestion de sesiones Pomodoro (25 min concentracion / 5 min descanso)
- Union automatica al canal de voz del usuario
- Reproduccion de musica lofi en bucle durante las sesiones
- Notificaciones de voz mediante TTS (Texto a Voz) en español
- Notificaciones por el canal de texto con el estado de la sesion
- Contador de sesiones completadas y tiempo total acumulado
- Soporte para multiples servidores de forma simultanea
- Entorno completamente dockerizado

## Comandos

| Comando | Descripcion |
|---|---|
| `/start-pomodoro` | Inicia una sesion Pomodoro. El bot se une al canal de voz del usuario |
| `/view-session` | Muestra las sesiones completadas y el tiempo total de concentracion |
| `/end-bot` | Detiene la sesion activa y desconecta el bot del canal de voz |

## Requisitos previos

- [Docker](https://docs.docker.com/engine/install/) y [Docker Compose](https://docs.docker.com/compose/install/)
- Una aplicacion de bot creada en el [Discord Developer Portal](https://discord.com/developers/applications)
- Un archivo `lofi.mp3` con la musica que quieras durante las sesiones

## Instalacion

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/pomodoro-bot.git
cd pomodoro-bot
```

### 2. Configurar el token

Crea tu archivo `.env` copiando la plantilla:

```bash
cp .env.example .env
```

Abre `.env` y rellena tu token de Discord:

```
DISCORD_TOKEN=tu_token_aqui
```

### 3. Obtener el token del bot

1. Ve a [Discord Developer Portal](https://discord.com/developers/applications)
2. Crea una nueva aplicacion o selecciona una existente
3. Ve a la seccion **Bot**
4. Copia el **Token** y pegalo en tu `.env`
5. En la seccion **OAuth2 > URL Generator**, selecciona los scopes `bot` y `applications.commands`
6. En **Bot Permissions**, marca: `Connect`, `Speak`, `Send Messages`
7. Usa la URL generada para invitar tu bot al servidor

### 4. Añadir la musica

Coloca un archivo de musica llamado `lofi.mp3` en la carpeta raiz del proyecto.

```
pomodoro-bot/
├── bot.py
├── lofi.mp3        <-- aqui
├── .env
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

> Si no añades el archivo, el bot funcionara correctamente pero sin musica durante las sesiones.

### 5. Ejecutar con Docker

```bash
docker compose up -d --build
```

El bot se inicializara y sincronizara automaticamente los slash commands con Discord.

## Uso

1. Entra a cualquier canal de voz de tu servidor
2. Escribe `/start-pomodoro` en cualquier canal de texto
3. El bot se unira, anunciara el inicio por voz, y comenzara la musica
4. Cuando acaben los 25 minutos, avisara por voz y por texto y pausara la musica
5. Tras el descanso de 5 minutos, comenzara la siguiente sesion automaticamente
6. Usa `/view-session` en cualquier momento para ver tu progreso
7. Usa `/end-bot` para finalizar y ver el resumen

## Gestion del contenedor

```bash
# Ver el estado del bot en tiempo real
docker compose logs -f

# Detener el bot
docker compose down

# Reiniciar el bot
docker compose restart
```

## Estructura del proyecto

```
pomodoro-bot/
├── bot.py              # Logica principal del bot
├── Dockerfile          # Configuracion del contenedor
├── docker-compose.yml  # Orquestacion del servicio
├── requirements.txt    # Dependencias de Python
├── .env.example        # Plantilla de variables de entorno
└── README.md
```

## Dependencias

| Libreria | Uso |
|---|---|
| `discord.py[voice]` | Interfaz con la API de Discord y soporte de voz |
| `gTTS` | Generacion de audio Texto a Voz |
| `python-dotenv` | Carga de variables de entorno desde `.env` |

## Variables de entorno

| Variable | Descripcion | Obligatoria |
|---|---|---|
| `DISCORD_TOKEN` | Token del bot de Discord | Si |

## Notas tecnicas

- El bot usa `network_mode: host` en Docker para garantizar la estabilidad de la conexion de voz (protocolo UDP)
- La libreria `libopus0` se instala automaticamente en el contenedor para el soporte de audio
- Las sesiones se gestionan de forma asincrona, por lo que multiples servidores pueden usarlo simultaneamente sin interferencias
- Los archivos TTS temporales se eliminan automaticamente al finalizar cada sesion

## Licencia

MIT
