const fs = require("fs");

const INPUT = "combatlog.txt";
const OUTPUT = "combatlog_format.txt";

// Convert seconds → HH:mm:ss.SSS
function fmt(t) {
  const ms = Math.floor(t * 1000);
  const d = new Date(ms);
  return "[" + d.toISOString().substr(11, 12) + "]";
}

function toLine(obj) {
  const time = fmt(obj.timestamp);
  const attacker = obj.attacker_name || obj.target || "UNKNOWN";
  const target = obj.target || "UNKNOWN";
  const value = obj.value;

  switch (obj.type) {
    case 0:
      return (
        `${time} ${attacker} hits ${target}` +
        `${obj.inflictor ? " with " + obj.inflictor : ""}` +
        ` for ${obj.value} damage (${obj.value + obj.value2}->${obj.value2})`
      );
    case 1:
      return `${time} ${attacker} deals ${value} pure damage to ${target}`;
    case 2:
      return `${time} ${attacker} heals ${target} for ${value} health`;
    case 3:
      return `${time} ${target} receives ${obj.inflictor} buff/debuff from ${attacker}`;
    case 4:
      return `${time} ${target} loses ${obj.inflictor} buff/debuff`;
    case 5:
      return `${time} ${attacker} casts ${obj.inflictor} (lvl ${obj.ability_level})`;
    case 6:
      return `${time} ${attacker} uses ability ${obj.inflictor}`;
    case 7:
      return `${time} ${attacker} purchases item ${obj.inflictor}`;
    case 8:
      return `${time} ${attacker} picks up ${obj.inflictor}`;
    case 9:
      return `${time} ${target} gains ${value} gold`;
    case 10:
      return `${time} ${target} gains ${value} XP`;
    case 11:
      return `${time} ${attacker} kills ${target}`;
    case 12:
      return `${time} ${target} has died`;
    case 13:
      return `${time} ${target} gains ${value} mana`;
    case 14:
      return `${time} ${target} loses ${value} mana`;
    case 15:
      return `${time} ${target} blocks ${value} damage`;
    case 16:
      return `${time} Projectile launched from ${attacker} to ${target}`;
    case 17:
      return `${time} ${target} modifier ${obj.inflictor} stacks → ${value}`;
    case 18:
      return `${time} ${target} receives a shield of ${value}`;
    case 19:
      return (
        `${time} ${attacker} hits ${target}` +
        `${obj.inflictor ? " with " + obj.inflictor : ""}` +
        ` for ${obj.value} damage (${obj.value + obj.value2}->${obj.value2})`
      );
    default:
      return `${time} [UNKNOWN TYPE ${obj.type}]`;
  }
}

function parseBlock(block) {
  const obj = {};
  block
    .trim()
    .split("\n")
    .forEach((line) => {
      const m = line.match(/(\w+):\s*(.+)/);
      if (m) {
        const key = m[1];
        let val = m[2];

        if (!isNaN(val)) val = Number(val);
        obj[key] = val;
      }
    });
  return obj;
}

function run() {
  const txt = fs.readFileSync(INPUT, "utf8");

  // <---- THIS FIXES YOUR PROBLEM
  const blocks = txt.match(/\{[^]*?\}/g);

  if (!blocks) {
    console.log("No combatlog blocks found!");
    return;
  }

  const formatted = blocks
    .map((b) => {
      const clean = b.replace(/[{}]/g, "");
      const obj = parseBlock(clean);
      return toLine(obj);
    })
    .join("\n");

  fs.writeFileSync(OUTPUT, formatted);
}

module.exports = { run };
