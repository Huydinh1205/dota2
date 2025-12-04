import subprocess
import sys
from d2gsi import create_d2gsi_app

server_options = {
    "port": 3000,
    "tokens": ["my_secret_token_12345", "another_token"],
}

app, host, port = create_d2gsi_app(server_options)

print("GSI up and running and ready to receive data...")

def on_new_client(client):
    print(f"🟢 Client Dota 2 just connected to IP: {client.ip}")

    #
    # === HERO STATUS ===
    #

    # change in health
    client.on("hero:health_percent", lambda hp: print(f"❤️ health hero: {hp}%"))
    client.on("hero:health_percent", lambda hp: print("⚠️ warning: Hero is low!") if hp < 20 else None)

    # level up
    client.on("hero:level", lambda lvl: print(f"🆙 Hero level up: {lvl}"))

    # hero death or respawn
    client.on("hero:alive", lambda alive: print("💀hero has respawned!" if alive else "💀 Hero has died!"))

    #
    # === ABILITIES ===
    #

    # Khi hero học hoặc dùng kỹ năng
    client.on("abilities:ability0:level", lambda lvl: print(f"✨ ability 1 level up: {lvl}"))

    client.on("abilities:ability0:can_cast", lambda can: print(f"🔹 Can cast ability 1: {can}"))

    # You can track main 4 abilities:
    # ability0, ability1, ability2, ability3, ability4, ability5

    #
    # === ITEMS ===
    #

    # When your hero buys an item
    client.on("items:slot0:name", lambda item: print(f"👜 Buying in slot 0: {item}") if item and item != "empty" else None)

    # Track all 6 main slots + backpack
    for i in range(9):
        client.on(f"items:slot{i}:name", lambda item, slot=i: print(f"🛒 Slot {slot}: {item}") if item and item != "empty" else None)

    #
    # === PLAYER INFO ===
    #

    # When you change kill / death / assist
    client.on("player:kills", lambda kills: print(f"🔪 Kills: {kills}"))

    client.on("player:deaths", lambda deaths: print(f"☠️ Deaths: {deaths}"))

    client.on("player:assists", lambda assists: print(f"🤝 Assists: {assists}"))

    #
    # === MAP INFO ===
    #

    # Hero position on the map
    # client.on("hero:xpos", lambda x: print(f"📍 Hero X: {x}"))
    # client.on("hero:ypos", lambda y: print(f"📍 Hero Y: {y}"))

    # When you want to combine position:
    client.on("hero:position", lambda pos: print(f"🧭 Position: ({pos.get('x', '?')}, {pos.get('y', '?')})"))

    #
    # === RAW DATA DEBUG ===
    #
    client.on("newdata", lambda data: None)  # If you want to see full raw JSON, uncomment the line below
    # client.on("newdata", lambda data: print(json.dumps(data, indent=2)))

if __name__ == '__main__':
    # Start combatlog.py as a subprocess
    try:
        combatlog_process = subprocess.Popen([sys.executable, "combatlog.py"],
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE)
        print("Started combatlog process")
    except Exception as e:
        print(f"Failed to start combatlog process: {e}")

    try:
        print(f"Dota 2 GSI listening on {host}:{port}")
        app.run(host=host, port=port, debug=False)
    except KeyboardInterrupt:
        print("Shutting down...")
        if 'combatlog_process' in locals():
            combatlog_process.terminate()
            combatlog_process.wait()
