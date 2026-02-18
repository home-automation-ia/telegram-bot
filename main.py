import os
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, ContextTypes, CommandHandler

# Cargar variables de entorno
load_dotenv()
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Configuración de Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("¡Hola! Soy el bot de la lista de la compra. Esperando a recibir la lista semanal.")

async def handle_checklist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja los callbacks de los botones de la lista de la compra."""
    query = update.callback_query
    await query.answer()

    data = query.data
    
    # Ignorar botones que no hacen nada (headers)
    if not data or data == "noop":
         return

    # Verificamos si es un callback de checklist (chk_...)
    if not data.startswith("chk_"):
        return

    try:
        # Obtener el teclado actual
        current_markup = query.message.reply_markup
        if not current_markup:
            return
            
        keyboard = current_markup.inline_keyboard
        new_keyboard = []
        
        # Iterar sobre las filas y botones para encontrar el que se pulsó
        for row in keyboard:
            new_row = []
            for btn in row:
                if btn.callback_data == data:
                    text = btn.text
                    # Lógica de toggle
                    if "⬜" in text:
                        new_text = text.replace("⬜", "✅")
                    elif "✅" in text:
                        new_text = text.replace("✅", "⬜")
                    else:
                        # Si por alguna razón no tiene icono, añadir check
                        new_text = f"✅ {text}"
                    
                    # Crear nuevo botón con el texto actualizado
                    new_btn = InlineKeyboardButton(text=new_text, callback_data=btn.callback_data)
                    new_row.append(new_btn)
                else:
                    # Mantener el botón tal cual
                    new_row.append(btn)
            new_keyboard.append(new_row)

        reply_markup = InlineKeyboardMarkup(new_keyboard)
        await query.edit_message_reply_markup(reply_markup=reply_markup)

    except Exception as e:
        logging.error(f"Error procesando callback: {e}")

def main():
    if not TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN no encontrado en las variables de entorno.")
        return

    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_checklist))

    print("Bot iniciado... Pulsa Ctrl+C para detener.")
    application.run_polling()

if __name__ == '__main__':
    main()
