// Sample motion and the floating cutie mark along Dicer's refracted ray.
const DENSITIES = {
    arcana: `float r = length(p.xz);
        return smoothstep(0.77, 1.65, cos(25.0 * r + t) + cos(9.0 * atan(p.z, p.x + 0.001) - t))
            * exp(-4.1 * abs(p.y));`,
    leaves: `vec3 drift = p * 4.6 + vec3(0.55 * sin(t), t, 0.21 * t);
        vec3 cell = floor(drift);
        vec3 q = fract(drift) - 0.5 - 0.12 * sin(cell.zxy * 5.0);
        q.xy = mat2(cos(t), -sin(t), sin(t), cos(t)) * q.xy;
        return 1.0 - smoothstep(0.07, 0.22, length(q * vec3(1.0, 2.6, 3.1)));`,
    storm: `float vein = cos(4.0 * atan(p.z, p.x + 0.001) + 8.0 * p.y + sin(15.0 * p.y - t) - t);
        return smoothstep(0.91, 0.995, vein) * (0.7 + 0.3 * sin(3.0 * t));`,
    prism: `vec3 q = abs(p * 3.6 - 0.36 * sin(vec3(t, t + 2.0, t + 4.0)));
        float facet = abs(fract(q.x + q.y + q.z) - 0.5);
        return (1.0 - smoothstep(0.018, 0.10, facet))
            * (0.45 + 0.55 * pow(abs(cos(t + dot(p, vec3(3.0, 5.0, 2.0)))), 4.0));`,
    flutter: `float wing = p.y - abs(p.x) * sin(4.0 * t + 6.0 * p.z);
        float lobe = length(vec2((abs(p.x) - 0.34) * 2.6, p.z * 1.6));
        return exp(-13.0 * abs(wing)) * (1.0 - smoothstep(0.34, 0.66, lobe));`,
    bubbles: `vec3 drift = p * 4.5 - vec3(0.18 * sin(t), 1.6 * t, 0.15 * t);
        vec3 cell = floor(drift);
        vec3 q = fract(drift) - 0.5 - 0.12 * sin(cell.zxy * 7.0);
        return 1.0 - smoothstep(0.015, 0.085, abs(length(q) - 0.18));`,
    corona: `float r = length(p);
        float ring = 0.47 + 0.035 * sin(8.0 * atan(p.z, p.x + 0.001) - t);
        return 0.42 * exp(-5.0 * r) + 0.86 * exp(-20.0 * abs(r - ring));`,
    nebula: `return smoothstep(-0.22, 0.74,
        mlpWave(p * 3.7, t * 0.54) + 0.27 * mlpWave(p * 7.0 + 2.0, -t));`,
    pulse: `float beat = pow(0.5 + 0.5 * cos(3.0 * t), 4.0);
        return exp(-19.0 * abs(length(p) - 0.44 - 0.19 * beat));`,
    vortices: `float r = length(p.xz);
        float ribbon = cos(3.0 * atan(p.z, p.x + 0.001) + 11.0 * r - 4.0 * p.y + 2.0 * t);
        return smoothstep(0.60, 0.98, ribbon) * exp(-1.9 * abs(p.y));`,
    fire: `vec3 rising = p * vec3(5.1, 2.2, 5.1) - vec3(0.0, 2.5 * t, 0.0);
        return smoothstep(0.0, 0.63, mlpWave(rising, t) - 0.44 * p.y);`,
    smoke: `vec3 drift = p * 4.0 + vec3(0.4 * t, -1.3 * t, 0.15 * t);
        return 0.8 * smoothstep(-0.13, 0.58, mlpWave(drift, t * 0.67)
            + 0.21 * mlpWave(drift * 2.0, -t));`,
    blossoms: `float a = atan(p.z, p.x + 0.001);
        float petal = 0.39 + 0.13 * cos(5.0 * a - t);
        return exp(-17.0 * (abs(length(p.xz) - petal) + 0.53 * abs(p.y)));`,
    sound: `float r = length(p.xz);
        float ripple = cos(29.0 * r - 4.0 * t + 4.0 * p.y);
        return smoothstep(0.43, 0.97, ripple) * exp(-4.2 * abs(p.y));`,
    sediment: `float layer = sin(35.0 * (p.y + 0.11 * sin(5.0 * p.x + p.z)) + 2.0 * t);
        return smoothstep(0.53, 0.98, layer) * (0.5 + 0.5 * cos(3.3 * p.z + t));`,
    motes: `vec3 drift = p * 4.4 + vec3(0.45 * t, -0.56 * t, 0.19 * t);
        vec3 cell = floor(drift);
        float r = length(fract(drift) - 0.5 - 0.18 * sin(cell.zxy * 7.0));
        return (1.0 - smoothstep(0.06, 0.27, r))
            * (0.62 + 0.38 * sin(2.0 * t + dot(cell, vec3(1.0, 3.0, 5.0))));`,
    ink: `float ribbon = p.y + 0.29 * sin(4.8 * p.x - 1.2 * t) + 0.13 * cos(5.0 * p.z + t);
        return 1.0 - smoothstep(0.04, 0.27, abs(ribbon));`,
};

function linearColor(hex) {
    const channels = hex.slice(1).match(/../g).map((part) => {
        const srgb = parseInt(part, 16) / 255;
        return (srgb <= 0.04045 ? srgb / 12.92 : ((srgb + 0.055) / 1.055) ** 2.4).toFixed(5);
    });
    return `vec3(${channels.join(", ")})`;
}

function interiorShader({ palette, motion, speed }) {
    return `
#ifdef DICER_RESIN
uniform float uMlpInside;
uniform float uMlpTime;
uniform float uMlpMarkReady;
uniform sampler2D uMlpMark;

float mlpWave(vec3 p, float t) {
    return sin(p.x + cos(p.y * 1.7 - t)) * cos(p.z * 1.4 + t)
        + 0.31 * cos(p.y + sin(p.z - t));
}

float mlpDensity(vec3 p, float t) {
    ${DENSITIES[motion]}
}

vec4 mlpVolume(vec3 entry, vec3 ray, float chord, vec3 radii) {
    vec4 volume = vec4(0.0);
    float stepLength = length(ray * chord / radii) / 8.0;
    for (int i = 0; i < 8; ++i) {
        vec3 p = (entry + ray * chord * (float(i) + 0.5) / 8.0) / radii;
        float envelope = 1.0 - smoothstep(0.64, 0.93, length(p));
        float density = clamp(mlpDensity(p, uMlpTime), 0.0, 1.0);
        float alpha = 1.0 - exp(-2.8 * density * envelope * stepLength);
        vec3 color = mix(${linearColor(palette[1])}, ${linearColor(palette[2])}, 0.25 + 0.75 * density);
        volume += vec4(color * alpha, alpha) * (1.0 - volume.a);
    }
    return volume;
}

vec4 mlpFloatingMark(vec3 entry, vec3 ray, float chord, vec3 radii, vec3 forward, vec3 cameraUp) {
    vec3 right = normalize(cross(cameraUp, forward));
    vec3 up = cross(forward, right);
    vec3 center = radii * vec3(0.12 * sin(uMlpTime), 0.09 * sin(0.8 * uMlpTime), 0.12 * cos(uMlpTime));
    float cosine = dot(ray, forward);
    if (abs(cosine) < 0.001) return vec4(0.0);
    float hit = dot(center - entry, forward) / cosine;
    if (hit <= 0.0 || hit >= chord) return vec4(0.0);

    vec3 displacement = (entry + ray * hit - center) / radii;
    vec2 uv = vec2(dot(displacement, right), -dot(displacement, up));
    float angle = 0.22 * sin(0.73 * uMlpTime);
    uv = mat2(cos(angle), -sin(angle), sin(angle), cos(angle)) * uv * 1.30 + 0.5;
    if (any(lessThan(uv, vec2(0.0))) || any(greaterThan(uv, vec2(1.0)))) return vec4(0.0);

    vec4 mark = texture2D(uMlpMark, uv);
    vec3 color = pow(mark.rgb, vec3(2.2));
    return vec4(color * mix(0.96, 0.62, hit / chord), mark.a * 0.90);
}
#endif
`;
}

function loadMark(url) {
    let image;
    let pixels;
    let texture;

    return (material) => {
        if (texture) return texture;
        if (!image) {
            image = new Image();
            image.onload = () => {
                const canvas = document.createElement("canvas");
                canvas.width = image.width;
                canvas.height = image.height;
                const context = canvas.getContext("2d", { willReadFrequently: true });
                if (!context) return;
                context.drawImage(image, 0, 0);
                pixels = context.getImageData(0, 0, canvas.width, canvas.height);
            };
            image.onerror = () => console.warn("MLP Dice | Could not load cutie mark", url);
            image.src = globalThis.foundry?.utils?.getRoute?.(url) ?? url;
        }
        const uniforms = material.userData.uniforms;
        const labels = uniforms?.uLabels?.value;
        if (!pixels || !labels?.isDataTexture) return null;
        // Reuse Dicer's DataTexture class to avoid a second copy of Three.js.
        texture = new labels.constructor(new Uint8Array(pixels.data), pixels.width, pixels.height);
        const atlas = uniforms.uAtlas?.value;
        if (atlas?.isDataTexture) {
            texture.minFilter = atlas.minFilter;
            texture.magFilter = atlas.magFilter;
        }
        texture.needsUpdate = true;
        pixels = undefined;
        return texture;
    };
}

export function addLivingInterior(system, character, url, reduceMotion) {
    const common = "#include <common>";
    const hook = "// dicer:interior";
    const textureFor = loadMark(url);
    const shaderFunctions = interiorShader(character);
    system.registerBeforeShaderCompileCallback((shader, material) => {
        const source = shader.fragmentShader;
        if (!source.includes(common) || !source.includes(hook)) return;
        shader.uniforms.uMlpInside = {
            get value() { return game.settings.get("dicer", "interiors") ? 1 : 0; },
        };
        shader.uniforms.uMlpTime = {
            get value() {
                const animate = !reduceMotion?.matches && game.settings.get("dicer", "insideMotion");
                return animate ? performance.now() * character.speed / 1000 : 0;
            },
        };
        shader.uniforms.uMlpMark = { get value() { return textureFor(material); } };
        shader.uniforms.uMlpMarkReady = { get value() { return textureFor(material) ? 1 : 0; } };
        shader.fragmentShader = source.replace(common, `${common}\n${shaderFunctions}`).replace(hook, `
        if (uMlpInside > 0.5 && dcRt1 > 0.0) {
            vec4 mlpTint = mlpVolume(vLocalPos, dcRd, dcRt1, uResinRadii);
            dcRefracted = dcRefracted * (1.0 - mlpTint.a) + mlpTint.rgb;
            if (uMlpMarkReady > 0.5) {
                vec3 mlpUp = normalize(transpose(dcRm) * inverseTransformDirection(vec3(0.0, 1.0, 0.0), viewMatrix));
                vec4 mlpMark = mlpFloatingMark(vLocalPos, dcRd, dcRt1, uResinRadii, normalize(vLocalCam), mlpUp);
                dcRefracted = mix(dcRefracted, mlpMark.rgb, mlpMark.a);
            }
        }
`);
    });
}
