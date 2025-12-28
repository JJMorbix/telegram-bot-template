from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from config import Config
import pkgutil
import importlib
import inspect
import atexit, signal, sys
from utils import command_logger as cmd_logger
from utils.cooldown import cooldown_watcher
import asyncio
import bot_status
from utils.permissions import global_restrict

async def log_command_middleware(update, context):
    if update.message and update.message.text.startswith("/"):
        user = update.effective_user
        command = update.message.text.split()[0][1:]
        cmd_logger.log_command(user.id, user.username or "", command)

def load_commands(application):
    import modules

    def walk_modules(package, prefix="modules"):
        for _, modname, ispkg in pkgutil.iter_modules(package.__path__):
            full_modname = f"{prefix}.{modname}"
            module = importlib.import_module(full_modname)

            for name, func in inspect.getmembers(module, inspect.iscoroutinefunction):
                wrapped_func = global_restrict(func)
                if name.endswith("_command"):
                    cmd_name = name.replace("_command", "")
                    application.add_handler(CommandHandler(cmd_name, wrapped_func), group=0)
                    #print(f"Carico comando /{cmd_name} da {full_modname}")

                elif name.endswith("_inline"):
                    prefix_name = name.replace("_inline", "")
                    application.add_handler(
                        #CallbackQueryHandler(func, pattern=f"^{prefix_name}:")
                        CallbackQueryHandler(wrapped_func, pattern=r".*")
                    )
                    # print(f"Carico pulsanti inline per {prefix_name} da {full_modname}")


            if ispkg:
                walk_modules(module, full_modname)

    walk_modules(modules)

def init_status():
    print("Inizializzazione del bot...")
    from utils.data_reading import init_readers
    init_readers()
    from utils.cooldown import load_previous_cooldowns
    load_previous_cooldowns()
    from modules import lang
    lang.read_preferences()
    from database import initialize_database
    initialize_database()
    print("Il bot è pronto!")


async def cleanup():
    print("Bot in chiusura.")
    # Qui puoi aggiungere eventuali operazioni di pulizia
    print("Salvo i cooldown attivi")
    from utils.cooldown import save_pending_cooldowns
    save_pending_cooldowns()

    print("Salvo le preferenze di lingua")
    from modules import lang
    lang.save_preferences()

    print("Salvo la cache di ogni Reader")
    from utils.data_reading import save_caches
    await save_caches()

    print("Chiudo la connessione al database")
    from database import close_db_connection
    close_db_connection()

    print("Operazioni di spegnimento sicuro completate. Arresto il bot.")

async def signal_handler(sig, frame):
    print("Ricevuto segnale di arresto.")
    await cleanup()
    bot_status.stop_event.set()  # fa uscire l'attesa di asyncio

#signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

import bot_instance
async def main():
    init_status()

    config = Config()
    bot_instance.app = ApplicationBuilder().token(config.token).build()
    bot_instance.app.add_handler(MessageHandler(filters.COMMAND, log_command_middleware), group=-1)
    load_commands(bot_instance.app)

    # inizializza l'app
    await bot_instance.app.initialize()

    # avvia polling in background senza bloccare
    await bot_instance.app.updater.start_polling()
    polling_task = asyncio.create_task(bot_instance.app.start())

    # avvia watcher o altri task paralleli
    watcher_task = asyncio.create_task(cooldown_watcher())

    try:
        # attendi fino a stop signal
        await bot_status.stop_event.wait()
    except (KeyboardInterrupt, SystemExit, asyncio.CancelledError):
        pass
    finally:
        # chiudi tutto correttamente
        await bot_instance.app.updater.stop()
        await bot_instance.app.stop()
        await bot_instance.app.shutdown()
        polling_task.cancel()
        watcher_task.cancel()

        await cleanup()
        exit(bot_status.exit_code)

if __name__ == "__main__":
    asyncio.run(main())