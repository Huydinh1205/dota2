var d2gsi = require("./index.js");

var serverOptions = {
  port: 3000,
  tokens: ["my_secret_token_12345", "another_token"],
};

var server = new d2gsi(serverOptions);

console.log("GSI up and running and ready to receive data...");

server.events.on("newclient", function (client) {
  console.log("🟢 Client Dota 2 just connected to IP:", client.ip);

  //
  // === HERO STATUS ===
  //

  // change in health
  client.on("hero:health_percent", (hp) => {
    console.log(`❤️ health hero: ${hp}%`);
    if (hp < 20) console.log("⚠️ warning: Hero is low!");
  });

  // level up
  client.on("hero:level", (lvl) => {
    console.log(`🆙 Hero level up: ${lvl}`);
  });

  // hero death or respawn
  client.on("hero:alive", (alive) => {
    if (alive) console.log("💀hero has respawned!");
    else console.log("💀 Hero has died!");
  });

  //
  // === ABILITIES ===
  //

  // Khi hero học hoặc dùng kỹ năng
  client.on("abilities:ability0:level", (lvl) => {
    console.log(`✨ ability 1 level up: ${lvl}`);
  });

  client.on("abilities:ability0:can_cast", (can) => {
    console.log(`🔹 Can cast ability 1: ${can}`);
  });

  // You can track main 4 abilities:
  // ability0, ability1, ability2, ability3, ability4, ability5

  //
  // === ITEMS ===
  //

  // When your hero buys an item
  client.on("items:slot0:name", (item) => {
    if (item && item !== "empty") console.log(`👜 Buying in slot 0: ${item}`);
  });

  // Track all 6 main slots + backpack
  for (let i = 0; i < 9; i++) {
    client.on(`items:slot${i}:name`, (item) => {
      if (item && item !== "empty") console.log(`🛒 Slot ${i}: ${item}`);
    });
  }

  //
  // === PLAYER INFO ===
  //

  // When you change kill / death / assist
  client.on("player:kills", (kills) => {
    console.log(`🔪 Kills: ${kills}`);
  });

  client.on("player:deaths", (deaths) => {
    console.log(`☠️ Deaths: ${deaths}`);
  });

  client.on("player:assists", (assists) => {
    console.log(`🤝 Assists: ${assists}`);
  });

  //
  // === MAP INFO ===
  //

  // Hero position on the map
  //   client.on("hero:xpos", (x) => console.log(`📍 Hero X: ${x}`));
  //   client.on("hero:ypos", (y) => console.log(`📍 Hero Y: ${y}`));

  // When you want to combine position:
  client.on("hero:position", (pos) => {
    console.log(`🧭 Position: (${pos.x}, ${pos.y})`);
  });

  //
  // === RAW DATA DEBUG ===
  //
  client.on("newdata", (data) => {
    // If you want to see full raw JSON, uncomment this line:
    // console.log(JSON.stringify(data, null, 2));
  });
});
const { spawn } = require("child_process");

// Chạy combatlog.js như một tiến trình con
const combatlogProcess = spawn("node", ["combatlog.js"], {
  stdio: "inherit", // output từ combatlog.js sẽ hiện trên terminal
});

combatlogProcess.on("close", (code) => {
  console.log(`combatlog.js đã thoát với code ${code}`);
});

// const { run } = require("./combatlog_converter.js");

// // ... khởi động GSI server như trước ...

// // Mỗi 1 giây format combatlog
// setInterval(() => {
//   try {
//     run();
//   } catch (err) {
//     console.error("Error formatting combatlog:", err);
//   }
// }, 1000);
