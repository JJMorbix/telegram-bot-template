from datetime import datetime, timedelta
import asyncio
import heapq
import json
import pickle
import dill
from utils.callback import Callback

JSON_FILE = "data/status/cooldowns.json"
PICKLE_FILE = "data/status/callbacks.pkl"

cooldowns = {}
cooldowns_heap = []

# ----------------- Salvataggio -----------------
def save_pending_cooldowns():
    # JSON salva solo dati serializzabili
    heap_serializable = [
        (until.timestamp(), user_id, action_id, {k: v for k, v in callback.__dict__.items() if k != "func" and k != "_bot"})
        for until, user_id, action_id, callback in cooldowns_heap
    ]

    with open(JSON_FILE, "w") as f:
        json.dump({
            "cooldowns": {
                uid: {aid: ts.timestamp() for aid, ts in acts.items()}
                for uid, acts in cooldowns.items()
            },
            "cooldowns_heap": heap_serializable
        }, f)

    # Pickle salva solo le funzioni dei callback
    funcs = [callback.func for _, _, _, callback in cooldowns_heap]
    with open(PICKLE_FILE, "wb") as f:
        dill.dump(funcs, f)

# -------------- Caricamento -----------------
def load_previous_cooldowns():
    global cooldowns_heap, cooldowns
    try:
        with open(JSON_FILE) as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        cooldowns_heap, cooldowns = [], {}
        return

    cooldowns = {
        int(uid): {aid: datetime.fromtimestamp(ts) for aid, ts in acts.items()}
        for uid, acts in data.get("cooldowns", {}).items()
    }

    try:
        with open(PICKLE_FILE, "rb") as f:
            funcs = dill.load(f)
    except FileNotFoundError:
        funcs = [None] * len(data.get("cooldowns_heap", []))

    # ricostruisci l'heap unendo dati e funzioni
    cooldowns_heap = [
        (datetime.fromtimestamp(ts), uid, aid, Callback(async_func=func, **attrs))
        for (ts, uid, aid, attrs), func in zip(data.get("cooldowns_heap", []), funcs)
    ]

    heapq.heapify(cooldowns_heap)

# ----------------- Aggiungi cooldown -----------------
def add_cooldown(user_id, action_id, duration_seconds, callback):
    until = datetime.utcnow() + timedelta(seconds=duration_seconds)

    if user_id not in cooldowns:
        cooldowns[user_id] = {}
    cooldowns[user_id][action_id] = until

    heapq.heappush(cooldowns_heap, (until, user_id, action_id, callback))
    #print(f"Cooldown aggiunto: {user_id}-{action_id} fino a {until}")

# ----------------- Watcher asyncio -----------------
async def cooldown_watcher():
    import bot_instance
    while True:
        now = datetime.utcnow()
        to_remove = []
        for i, (until, user_id, action_id, callback) in enumerate(cooldowns_heap):
            #print("Checker:", user_id, action_id, until, callback)
            if now >= until:
                #print(f"dict: {cooldowns.get(user_id, {}).get(action_id)} - heap {until}")
                if cooldowns.get(user_id, {}).get(action_id) == until:
                    callback.set_bot(bot_instance.app.bot)  # assegna il bot al callback
                    try:
                        callback.set_bot(bot_instance.app.bot)
                        await callback()
                    except Exception as e:
                        # stampa l'errore completo
                        import traceback
                        print(f"Errore nella callback {callback} per user {user_id}, action {action_id}:")
                        traceback.print_exc()
                    #finally:
                    # rimuove la cooldown anche se c'è stato errore
                    del cooldowns[user_id][action_id]
                    if not cooldowns[user_id]:
                        del cooldowns[user_id]
                to_remove.append(i)
            else:
                break
        for i in reversed(to_remove):
            cooldowns_heap.pop(i)
        await asyncio.sleep(1)

# ----------------- Utilities -----------------
def is_in_cooldown(user_id, action_id):
    """Controlla se un'azione è in cooldown per un utente."""
    return user_id in cooldowns and action_id in cooldowns[user_id]