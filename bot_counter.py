import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import re
from datetime import datetime

# Configuración del logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Diccionario para almacenar el conteo de enlaces de X por usuario, fecha y topic
user_x_links = {}

# Función que maneja el comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Hola, estoy listo para contar enlaces de X')

# Función que cuenta los enlaces de X
async def count_x_links(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message.text
    user_id = update.message.from_user.id
    chat_id = update.message.chat.id
    topic_id = update.message.message_thread_id or 0  # Obtener el topic_id, si existe
    today = datetime.now().strftime('%Y-%m-%d')  # Obtener la fecha de hoy

    # Expresión regular para detectar enlaces de X (x.com)
    x_links = re.findall(r'https?://x\.com/[^\s]+', message)
    
    if x_links:
        if chat_id not in user_x_links:
            user_x_links[chat_id] = {}
        
        if topic_id not in user_x_links[chat_id]:
            user_x_links[chat_id][topic_id] = {}

        if today not in user_x_links[chat_id][topic_id]:
            user_x_links[chat_id][topic_id][today] = {}

        if user_id not in user_x_links[chat_id][topic_id][today]:
            user_x_links[chat_id][topic_id][today][user_id] = 0
        
        user_x_links[chat_id][topic_id][today][user_id] += len(x_links)
        logger.info(f"Usuario {update.message.from_user.full_name} ha compartido {len(x_links)} enlaces de X en {today} en topic {topic_id}.")

# Función para mostrar el conteo de enlaces de X por usuario y topic para hoy
async def show_x_links_count(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat.id
    topic_id = update.message.message_thread_id or 0  # Obtener el topic_id, si existe
    today = datetime.now().strftime('%Y-%m-%d')  # Obtener la fecha de hoy

    if chat_id in user_x_links and topic_id in user_x_links[chat_id] and today in user_x_links[chat_id][topic_id]:
        counts = user_x_links[chat_id][topic_id][today]
        report_lines = []
        for user_id, count in counts.items():
            user = await context.bot.get_chat(user_id)
            report_lines.append(f"{user.full_name}: {count} enlaces de X")
        report = "\n".join(report_lines)
        await update.message.reply_text(f"Conteo de enlaces de X para hoy ({today}) en este topic:\n{report}")
    else:
        await update.message.reply_text(f"No se han compartido enlaces de X en este topic hoy ({today}).")

# Función principal para configurar y ejecutar el bot
def main() -> None:
    # Reemplaza 'YOUR_TOKEN_HERE' por el token de tu bot
    application = ApplicationBuilder().token("6960790751:AAEOpt83y-8VjnB6KLVvh1Hi3lWeIyPqM7w").build()

    # Configurar el manejador del comando /start
    application.add_handler(CommandHandler("start", start))
    
    # Configurar el manejador para contar los enlaces de X
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, count_x_links))
    
    # Configurar el manejador del comando /count para mostrar el conteo
    application.add_handler(CommandHandler("count", show_x_links_count))

    # Iniciar el bot y esperar comandos
    application.run_polling()

if __name__ == '__main__':
    main()
