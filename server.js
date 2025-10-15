var d2gsi = require("./index.js");

var serverOptions = {
  port: 3000,
  tokens: ["my_secret_token_12345", "another_token"],
};

var server = new d2gsi(serverOptions);

console.log("Máy chủ GSI đang chạy và sẵn sàng nhận dữ liệu...");

server.events.on("newclient", function (client) {
  console.log("🟢 Client Dota 2 mới kết nối từ IP:", client.ip);

  //
  // === HERO STATUS ===
  //

  // Khi hero thay đổi máu
  client.on("hero:health_percent", (hp) => {
    console.log(`❤️ Máu hero: ${hp}%`);
    if (hp < 20) console.log("⚠️  CẢNH BÁO: Máu tướng dưới 20%!");
  });

  // Khi hero lên cấp
  client.on("hero:level", (lvl) => {
    console.log(`🆙 Hero lên cấp: ${lvl}`);
  });

  // Khi hero chết hoặc hồi sinh
  client.on("hero:alive", (alive) => {
    if (alive) console.log("💀 Hero đã hồi sinh!");
    else console.log("💀 Hero đã chết!");
  });

  //
  // === ABILITIES (KỸ NĂNG) ===
  //

  // Khi hero học hoặc dùng kỹ năng
  client.on("abilities:ability0:level", (lvl) => {
    console.log(`✨ Kỹ năng 1 lên cấp: ${lvl}`);
  });

  client.on("abilities:ability0:can_cast", (can) => {
    console.log(`🔹 Có thể cast kỹ năng 1: ${can}`);
  });

  // Bạn có thể bắt cho 4 kỹ năng chính:
  // ability0, ability1, ability2, ability3, ability4, ability5

  //
  // === ITEMS (VẬT PHẨM) ===
  //

  // Khi hero mua vật phẩm
  client.on("items:slot0:name", (item) => {
    if (item && item !== "empty") console.log(`👜 Mua đồ ở slot 0: ${item}`);
  });

  // Theo dõi tất cả 6 slot chính + backpack
  for (let i = 0; i < 9; i++) {
    client.on(`items:slot${i}:name`, (item) => {
      if (item && item !== "empty") console.log(`🛒 Slot ${i}: ${item}`);
    });
  }

  //
  // === PLAYER INFO ===
  //

  // Khi bạn thay đổi kill / death / assist
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

  // Vị trí hero trên bản đồ
  //   client.on("hero:xpos", (x) => console.log(`📍 Hero X: ${x}`));
  //   client.on("hero:ypos", (y) => console.log(`📍 Hero Y: ${y}`));

  // Nếu bạn muốn gộp vị trí:
  client.on("hero:position", (pos) => {
    console.log(`🧭 Vị trí: (${pos.x}, ${pos.y})`);
  });

  //
  // === RAW DATA DEBUG ===
  //
  client.on("newdata", (data) => {
    // Nếu bạn muốn xem toàn bộ JSON gốc, bỏ comment dòng này:
    // console.log(JSON.stringify(data, null, 2));
  });
});

console.log("Máy chủ GSI đang chạy và sẵn sàng nhận dữ liệu...");
