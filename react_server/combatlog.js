const fs = require("fs");
const src =
  "D:/SteamLibrary/steamapps/common/dota 2 beta/game/dota/combatlog.txt";
const dest = "D:/HuyDinh/dota2-gsi/combatlog.txt";

setInterval(() => {
  try {
    fs.copyFileSync(src, dest);
  } catch {}
}, 1000); // copy mỗi giây
