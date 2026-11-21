import { CRIT_EFFECTS } from "./crit-catalog.js";

const EFFECT = "mlp-dice.critical";
const ID = "mlp-dice";
const RAINBOW = ["#ff636e", "#ffb348", "#ffe564", "#8bea9e", "#61dfff", "#cb96ff"];
const PARTICLES = {
    apple: "●", bolt: "ϟ", bubble: "○", candy: "◆", cloud: "●",
    compass: "✥", confetti: "▪", dust: "•", flame: "▲", gem: "◆",
    heart: "♥", leaf: "◒", moon: "☾", note: "♪", page: "▱", petal: "❀",
    record: "◎", ribbon: "━", sand: "•", shield: "⬟", spark: "✦",
    spoon: "◕", stone: "⬢", sun: "☼", wing: "❧",
};
const WAVEFORMS = {
    bolt: "sawtooth", bubble: "sine", cloud: "triangle", flame: "sawtooth",
    gem: "sine", note: "triangle", record: "square", stone: "triangle",
};

let privateAudio;

function playCue(pitch, glyph, success) {
    if (!game.settings.get("dicer", "sounds")) return;
    const volume = game.settings.get("dicer", "effectsVolume") * game.settings.get("dicer", "soundVolume");
    if (!(volume > 0)) return;
    try {
        const context = game.audio?.context ?? (privateAudio ??= new AudioContext());
        // Playback for other users still depends on their browser allowing audio.
        if (context.state !== "running") return;
        const intervals = success ? [0, 4, 7, 12] : [0, -3, -8];
        const wave = WAVEFORMS[glyph] ?? "triangle";
        for (const [index, interval] of intervals.entries()) {
            const at = context.currentTime + index * 0.062;
            const tone = context.createOscillator();
            const level = context.createGain();
            tone.type = wave;
            tone.frequency.value = 329.63 * 2 ** ((interval + pitch) / 12);
            level.gain.setValueAtTime(0.0001, at);
            level.gain.exponentialRampToValueAtTime(Math.max(0.0002, volume * 0.057), at + 0.013);
            level.gain.exponentialRampToValueAtTime(0.0001, at + 0.18);
            tone.connect(level);
            level.connect(context.destination);
            tone.start(at);
            tone.stop(at + 0.19);
            tone.onended = () => { tone.disconnect(); level.disconnect(); };
        }
    } catch (error) {
        if (!(error instanceof DOMException)) console.debug("MLP Dice | Effect sound unavailable", error);
    }
}

function landingPoint(mesh, box) {
    const bounds = box.renderer?.domElement?.getBoundingClientRect();
    const point = mesh.position?.clone();
    if (!bounds?.width || !bounds.height || !point || !box.camera) return null;
    mesh.getWorldPosition(point).project(box.camera);
    if (Math.abs(point.x) > 1 || Math.abs(point.y) > 1 || Math.abs(point.z) > 1) return null;
    return [
        Math.max(130, Math.min(innerWidth - 130, bounds.left + (point.x + 1) * bounds.width / 2)),
        Math.max(118, Math.min(innerHeight - 56, bounds.top + (1 - point.y) * bounds.height / 2)),
    ];
}

function pulseTrack(motion, index, count) {
    const angle = index * Math.PI * 2 / count + 0.13;
    const distance = 68 + (index % 5) * 10;
    const x = Math.cos(angle);
    const y = Math.sin(angle);
    switch (motion) {
        case "sweep": return [[-95, 23 + 11 * y], [-11 + x * 26, -15 + y * 19], [112, -34 + y * 35]];
        case "rise": return [[x * 25, 15], [x * 49, -47 + y * 20], [x * 68, -104 + y * 33]];
        case "spill": return [[x * 12, 0], [x * 55, -15 + y * 25], [x * 104, 42 + index % 5 * 11]];
        case "drift": return [[x * 19, 4], [x * 69, -31 + y * 29], [x * 114, -48 + y * 41]];
        case "collapse": return [[x * distance, y * distance], [x * distance * .57, y * distance * .49], [x * 7, y * 7]];
        case "orbit": return [[x * 45, y * 45], [-y * 68, x * 68], [-x * distance, -y * distance]];
        case "flutter": return [[x * 11, 9], [x * 67 - y * 22, -42 + y * 28], [x * 93, -70 + y * 34]];
        default: return [[x * 8, y * 8], [x * distance * .68, y * distance * .68], [x * distance, y * distance]];
    }
}

function particlesFor(root, motion, glyph, colors, duration) {
    const count = motion === "rainbow" ? 24 : 15;
    for (let index = 0; index < count; index++) {
        const mote = document.createElement("span");
        mote.className = "mlp-dice-crit__particle";
        mote.textContent = PARTICLES[glyph];
        mote.style.color = colors[index % colors.length];
        mote.style.fontSize = `${11 + (index * 7 % 17)}px`;
        root.append(mote);
        const path = pulseTrack(motion, index, count);
        const frames = path.map(([x, y], frame) => ({
            transform: `translate(${x}px, ${y}px) rotate(${(index % 2 ? 1 : -1) * (index * 8 + frame * 48)}deg) scale(${frame === 1 ? 1.2 : 0.62})`,
            opacity: [0, 0.94, 0][frame],
            offset: [0, 0.36, 1][frame],
        }));
        mote.animate(frames, { duration: duration - 140, delay: index % 6 * 20, fill: "both" });
    }
}

function renderEffect(character, value, point, markUrl) {
    const success = value === 20;
    const [title, motion, glyph, pitch] = CRIT_EFFECTS[character.slug][success ? 0 : 1];
    const reduced = globalThis.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
    const duration = reduced ? 800 : 1200;
    const [base, mid, accent] = character.palette;
    const colors = motion === "rainbow" ? RAINBOW : [accent, "#fff3dd", mid];
    const root = document.createElement("div");
    root.className = `mlp-dice-crit mlp-dice-crit--${success ? "high" : "low"}`;
    root.setAttribute("aria-hidden", "true");
    root.style.left = `${point[0]}px`;
    root.style.top = `${point[1]}px`;
    root.style.setProperty("--mlp-base", base);
    root.style.setProperty("--mlp-accent", accent);
    if (!reduced) {
        particlesFor(root, motion, glyph, colors, duration);
        if (motion === "corona" || motion === "rainbow") {
            for (const [index, color] of colors.entries()) {
                const ring = document.createElement("span");
                ring.className = "mlp-dice-crit__ring";
                ring.style.borderColor = color;
                root.append(ring);
                ring.animate([
                    { transform: "translate(-50%, -50%) scale(.32)", opacity: 0 },
                    { opacity: .68, offset: .2 },
                    { transform: "translate(-50%, -50%) scale(2.8)", opacity: 0 },
                ], { duration: 730, delay: index * 55, fill: "both" });
            }
        }
    }
    const badge = document.createElement("div");
    badge.className = "mlp-dice-crit__badge";
    const mark = document.createElement("img");
    mark.src = globalThis.foundry?.utils?.getRoute?.(markUrl) ?? markUrl;
    mark.alt = "";
    const heading = document.createElement("strong");
    heading.textContent = title;
    const result = document.createElement("span");
    result.textContent = `NAT ${value}`;
    badge.append(mark, heading, result);
    root.append(badge);
    document.body.append(root);
    const animation = badge.animate([
        { opacity: 0 },
        { opacity: 1, offset: .14 },
        { opacity: 1, offset: .72 },
        { opacity: 0 },
    ], { duration, fill: "both" });
    playCue(pitch, glyph, success);
    return { root, finished: animation.finished.catch(() => {}), animation };
}

export function registerCritEffects(dice3d, assets) {
    const { DiceSystem, DiceSFX } = globalThis.DicerAPI ?? {};
    if (dice3d.DiceSystem !== DiceSystem || !DiceSFX || DiceSystem?.DICE_EVENT_TYPE?.SPAWN === undefined
        || typeof dice3d.addSFXMode !== "function" || typeof dice3d.addSFXDefaults !== "function") return;
    const presets = new WeakMap();

    class CriticalEffect extends DiceSFX {
        static id = EFFECT;
        static specialEffectName = "MLP Dice critical effects";
        static PLAY_ONLY_ONCE_PER_MESH = true;

        async play() {
            const character = presets.get(this.dicemesh);
            const value = this.dicemesh?.result;
            if (!character || (value !== 20 && value !== 1) || !game.settings.get(ID, "criticalEffects")) return;
            const point = landingPoint(this.dicemesh, this.box);
            if (!point) return;
            this.effect = renderEffect(character, value, point, `${assets}/marks/${character.slug}.png`);
            await this.effect.finished;
        }

        destroy() {
            this.effect?.animation.cancel();
            this.effect?.root.remove();
        }
    }

    dice3d.addSFXMode(CriticalEffect);
    // Dicer 1.3.7 resolves these defaults after its own privacy and effects checks.
    // Its rule format has no system filter, so only meshes tagged by our systems can play.
    dice3d.addSFXDefaults([
        ...(dice3d.getSFXDefaults?.() ?? []),
        { diceType: "d20", specialEffect: EFFECT, onResult: ["20", "1"] },
    ]);
    return (system, character) => {
        if (!CRIT_EFFECTS[character.slug]) return;
        system.on(DiceSystem.DICE_EVENT_TYPE.SPAWN, ({ dice }) => {
            if (dice[0]?.type === "d20" && dice.mesh) presets.set(dice.mesh, character);
        });
    };
}
