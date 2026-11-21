import { CHARACTERS } from "./catalog.js";
import { registerCritEffects } from "./crit-effects.js";
import { addLivingInterior } from "./living-inside.js";

const MODULE_ID = "mlp-dice";
const GROUP = "MLP Dice";
const ASSETS = `modules/${MODULE_ID}/assets/dice`;
const TYPES = ["d2", "d4", "d6", "d8", "d10", "d12", "d20", "d100"];

function labelsFor(type, crest) {
    const count = type === "d100" ? 10 : Number(type.slice(1));
    const labels = Array.from({ length: count }, (_, index) => {
        const value = index + 1;
        if (type === "d100") return String(value % 10 * 10).padStart(2, "0");
        if (type === "d10") return String(value % 10);
        return String(value);
    });
    if (type === "d20") labels[19] = crest;
    return labels;
}

function registerColorset(dice3d, id, description, [outline, background], material) {
    dice3d.addColorset({
        name: id,
        description,
        foreground: "#fff8ee",
        background,
        outline,
        texture: "none",
        material,
        visibility: "hidden",
    });
}

Hooks.once("init", () => {
    game.settings.register(MODULE_ID, "criticalEffects", {
        name: "MLP Dice critical effects",
        hint: "Play a character-themed effect on natural 20s and natural 1s rolled with MLP Dice.",
        scope: "client",
        config: true,
        type: Boolean,
        default: true,
    });
});

Hooks.once("diceSoNiceReady", (dice3d) => {
    const DiceSystem = dice3d.DiceSystem;
    const hasLivingInside = DiceSystem && DiceSystem === globalThis.DicerAPI?.DiceSystem
        && typeof DiceSystem.prototype.registerBeforeShaderCompileCallback === "function";
    const reduceMotion = hasLivingInside && globalThis.matchMedia?.("(prefers-reduced-motion: reduce)");
    const attachCritEffects = registerCritEffects(dice3d, ASSETS);

    for (const character of CHARACTERS) {
        const { slug, name, palette } = character;
        const id = `${MODULE_ID}-${slug}`;
        const crest = `${ASSETS}/crests/${slug}.png`;
        const skin = `${id}-skinned`;
        const skinName = `${name} (Skinned)`;
        registerColorset(dice3d, skin, skinName, palette, "plastic");
        const skinSystem = attachCritEffects
            ? new DiceSystem(skin, skinName, "default", GROUP)
            : { id: skin, name: skinName, group: GROUP };
        attachCritEffects?.(skinSystem, character);
        dice3d.addSystem(skinSystem, "default");
        for (const type of TYPES) {
            dice3d.addDicePreset({
                type,
                system: skin,
                colorset: skin,
                labels: "",
                modelFile: `${ASSETS}/skins/${slug}/${type}.glb`,
            });
        }

        if (!hasLivingInside) continue;
        const living = `${id}-living`;
        const description = `${name} (Living Inside)`;
        const system = new DiceSystem(living, description, "default", GROUP);
        addLivingInterior(system, character, `${ASSETS}/marks/${slug}.png`, reduceMotion);
        attachCritEffects?.(system, character);
        registerColorset(dice3d, living, description, palette, "glass");
        dice3d.addSystem(system, "default");
        for (const type of TYPES) {
            dice3d.addDicePreset({ type, system: living, colorset: living, labels: labelsFor(type, crest) });
        }
    }
});
