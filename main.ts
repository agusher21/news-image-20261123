import { copyFileSync } from "fs";
import { dirname, join } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const OUT_DIR = process.env.MAKEFUN_OUTPUT_DIR;

if (!OUT_DIR) {
  console.error("MAKEFUN_OUTPUT_DIR not set");
  process.exit(1);
}

const src = join(__dirname, "out", "entry.png");
const dest = join(OUT_DIR, "entry.png");

copyFileSync(src, dest);
console.log(`Copied ${src} -> ${dest}`);