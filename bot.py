import os
import asyncio
import discord
from discord.ext import commands
from gtts import gTTS
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')

class PomodoroState:
    def __init__(self, text_channel, voice_client):
        self.text_channel = text_channel
        self.voice_client = voice_client
        self.sessions_completed = 0
        self.is_running = True
        self.task = None

# Diccionario para almacenar los estados de las sesiones en diferentes servidores
states = {}

# Configurar intents básicos
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)

def play_tts(voice_client, text, guild_id):
    """Genera audio de Texto-a-Voz y lo reproduce en el canal de voz."""
    filename = f"temp_tts_{guild_id}.mp3"
    tts = gTTS(text=text, lang='es')
    tts.save(filename)
    source = discord.FFmpegPCMAudio(filename)
    voice_client.play(source)

def play_lofi(voice_client):
    """Reproduce el archivo local lofi.mp3 en un bucle infinito."""
    if os.path.exists("lofi.mp3"):
        source = discord.FFmpegPCMAudio("lofi.mp3", before_options="-stream_loop -1")
        voice_client.play(source)
    else:
        print("Advertencia: Archivo 'lofi.mp3' no encontrado. Saltando reproduccion de musica.")

async def pomodoro_loop(guild_id):
    """Bucle principal de la sesion Pomodoro."""
    state = states.get(guild_id)
    if not state:
        print(f"Estado no encontrado para el servidor {guild_id}")
        return
    
    # Duracion en segundos (25 min trabajo, 5 min descanso)
    WORK_TIME = 25 * 60
    BREAK_TIME = 5 * 60
    
    print(f"Iniciando bucle Pomodoro en el servidor {guild_id}")
    
    try:
        while state.is_running:
            # --- INICIO SESION DE TRABAJO ---
            print("Iniciando bloque de trabajo - Enviando mensaje de texto...")
            await state.text_channel.send("Iniciando bloque de concentracion de 25 minutos. Buena suerte.")
            
            if not state.voice_client.is_connected():
                print("El cliente de voz se desconecto inesperadamente antes de empezar.")
                break

            if state.voice_client.is_playing():
                state.voice_client.stop()
            
            # Reproducir TTS
            print("Reproduciendo TTS: Sesion iniciada")
            try:
                play_tts(state.voice_client, "Sesion iniciada", guild_id)
            except Exception as tts_err:
                print(f"Error al reproducir TTS: {tts_err}")
            
            # Esperar a que el TTS termine de hablar
            while state.voice_client.is_playing() and state.is_running:
                await asyncio.sleep(1)
                
            if not state.is_running:
                break
                
            # Reproducir musica
            print("Intentando reproducir musica lofi...")
            try:
                play_lofi(state.voice_client)
            except Exception as music_err:
                print(f"Error al reproducir musica: {music_err}")
            
            # Esperar 25 minutos (comprobando señal de parada)
            print(f"Esperando {WORK_TIME} segundos para la sesion de trabajo...")
            for i in range(WORK_TIME):
                if not state.is_running:
                    print("Sesion cancelada por el usuario.")
                    break
                if not state.voice_client.is_connected():
                    print("Desconexion de voz detectada durante la sesion.")
                    state.is_running = False
                    break
                await asyncio.sleep(1)
                
            if not state.is_running:
                break
                
            if state.voice_client.is_playing():
                state.voice_client.stop()
                
            # --- TRABAJO COMPLETADO ---
            state.sessions_completed += 1
            
            # --- INICIO DESCANSO ---
            minutos_totales = state.sessions_completed * 25
            print(f"Sesion #{state.sessions_completed} completada - Descanso iniciado.")
            await state.text_channel.send(f"Sesion #{state.sessions_completed} finalizada. Tiempo total de concentracion: {minutos_totales} minutos. Toma un descanso de 5 minutos.")
            
            try:
                play_tts(state.voice_client, "Sesion finalizada", guild_id)
            except Exception as tts_err:
                print(f"Error al reproducir TTS final: {tts_err}")
            
            while state.voice_client.is_playing() and state.is_running:
                await asyncio.sleep(1)
                
            # Esperar 5 minutos de descanso
            print(f"Esperando {BREAK_TIME} segundos de descanso...")
            for i in range(BREAK_TIME):
                if not state.is_running:
                    break
                if not state.voice_client.is_connected():
                    print("Desconexion de voz detectada durante el descanso.")
                    state.is_running = False
                    break
                await asyncio.sleep(1)
                
    except asyncio.CancelledError:
        print(f"Tarea Pomodoro cancelada para el servidor {guild_id}")
    except Exception as e:
        print(f"Error critico en el bucle Pomodoro: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print(f"Limpiando recursos y desconectando para el servidor {guild_id}")
        try:
            if state.voice_client.is_connected():
                await state.voice_client.disconnect()
        except:
            pass
        if guild_id in states:
            del states[guild_id]
        
        # Eliminar archivo de audio TTS temporal
        filename = f"temp_tts_{guild_id}.mp3"
        if os.path.exists(filename):
            try:
                os.remove(filename)
            except OSError:
                pass


@bot.event
async def on_ready():
    # Sincronizar Slash Commands globalmente
    await bot.tree.sync()
    print(f"Bot conectado y listo: {bot.user}")

@bot.tree.command(name="start-pomodoro", description="Inicia una sesion de Pomodoro (25 min trabajo / 5 min descanso)")
async def start_pomodoro(interaction: discord.Interaction):
    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.response.send_message("Debes estar conectado a un canal de voz para que me pueda unir.", ephemeral=True)
        return
        
    guild_id = interaction.guild_id
    if guild_id in states:
        await interaction.response.send_message("Ya hay una sesion de Pomodoro activa en este servidor.", ephemeral=True)
        return
        
    voice_channel = interaction.user.voice.channel
    await interaction.response.send_message("Preparando conexion de voz segura...")
    
    # --- LIMPIEZA DE SESION PREVIA ---
    existing_vc = interaction.guild.voice_client
    if existing_vc:
        print(f"Limpiando sesion de voz fantasma en {interaction.guild.name}...")
        try:
            await existing_vc.disconnect(force=True)
            await asyncio.sleep(1)
        except:
            pass

    try:
        # Comprobar si Opus esta cargado
        if not discord.opus.is_loaded():
            print("Cargando libreria Opus...")
            try:
                discord.opus.load_opus('libopus.so.0')
            except:
                pass

        print(f"Conectando al canal {voice_channel.name}...")
        voice_client = await voice_channel.connect(timeout=30.0, self_deaf=True)
        
        print("Estabilizando conexion (3s)...")
        await asyncio.sleep(3)
        
    except Exception as e:
        print(f"Error al conectar: {e}")
        await interaction.followup.send(f"No pude unirme al canal de voz. Error: {e}")
        return

    # Inicializar estado
    state = PomodoroState(interaction.channel, voice_client)
    states[guild_id] = state
    
    # Iniciar bucle
    state.task = asyncio.create_task(pomodoro_loop(guild_id))

@bot.tree.command(name="view-session", description="Muestra el progreso de la sesion Pomodoro actual")
async def view_session(interaction: discord.Interaction):
    guild_id = interaction.guild_id
    
    if guild_id not in states:
        await interaction.response.send_message("No hay ninguna sesion Pomodoro activa. Usa `/start-pomodoro` para empezar.", ephemeral=True)
        return
        
    state = states[guild_id]
    minutos_totales = state.sessions_completed * 25
    await interaction.response.send_message(
        f"Estado de la Sesion:\n"
        f"Sesiones completadas: {state.sessions_completed}\n"
        f"Tiempo total de concentracion: {minutos_totales} minutos.",
        ephemeral=False
    )

@bot.tree.command(name="end-bot", description="Detiene la sesion Pomodoro y desconecta de la voz")
async def end_bot(interaction: discord.Interaction):
    guild_id = interaction.guild_id
    
    if guild_id not in states:
        await interaction.response.send_message("No hay ninguna sesion activa. Si sigo en un canal, desconectame manualmente.", ephemeral=True)
        if interaction.guild.voice_client:
            await interaction.guild.voice_client.disconnect()
        return
        
    state = states[guild_id]
    state.is_running = False
    
    if state.task:
        state.task.cancel()
        
    if state.voice_client.is_playing():
        state.voice_client.stop()
        
    if state.voice_client.is_connected():
        await state.voice_client.disconnect()
        
    if guild_id in states:
        del states[guild_id]
    
    minutos_totales = state.sessions_completed * 25
    await interaction.response.send_message(f"Flujo Pomodoro finalizado. Gran trabajo. Has completado {state.sessions_completed} sesiones ({minutos_totales} minutos).")

if __name__ == "__main__":
    if not TOKEN or TOKEN == "tu_token_aqui":
        print("Token de Discord no configurado en el entorno.")
    else:
        bot.run(TOKEN)
