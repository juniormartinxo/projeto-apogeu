# PlayCanvas Primitive Arena Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a playable React + Vite + PlayCanvas arena where Cadete and Boss Molock are visible, animated, and created only from PlayCanvas primitives.

**Architecture:** Add an isolated `frontend/` app because the current repo is a Streamlit MVP and has no React/Vite project yet. Keep primitive actor construction in `createCadet.ts`, `createMolock.ts`, `createArena.ts`, and `createEffects.ts`, with battle state emitting animation cues so GLB models can replace primitive builders later without changing answer logic.

**Tech Stack:** React, Vite, TypeScript, PlayCanvas, Vitest, Testing Library, Playwright.

---

## Current Repo Context

The existing app is Python/Streamlit:

- `app.py` owns battle flow, answer handling, and screen routing.
- `src/game_logic.py` owns damage, XP, ELO, and phase rules.
- `src/ui_components.py` owns the current HTML/CSS game shell and still uses `assets/molock-boss.png`.
- There is no `package.json`, Vite config, TypeScript source, or React app.

This plan adds the PlayCanvas MVP in `frontend/` rather than replacing Streamlit in the same change. That keeps the new 3D arena testable and avoids disturbing the existing Python tests.

## File Structure

- Create `frontend/package.json`: npm scripts and dependencies for Vite, React, PlayCanvas, tests, and Playwright.
- Create `frontend/index.html`: Vite HTML entry.
- Create `frontend/vite.config.ts`: React plugin and Vitest jsdom config.
- Create `frontend/tsconfig.json`: TypeScript app config.
- Create `frontend/tsconfig.node.json`: TypeScript config for Vite tooling.
- Create `frontend/src/main.tsx`: React mount point.
- Create `frontend/src/App.tsx`: playable MVP UI with answer selection and combat cues.
- Create `frontend/src/styles.css`: tactical arena layout and controls around the canvas.
- Create `frontend/src/game/battleState.ts`: pure answer-to-cue battle reducer.
- Create `frontend/src/game/battleState.test.ts`: unit coverage for correct and wrong answer cues.
- Create `frontend/src/arena/types.ts`: shared actor, effect, primitive, and combat cue contracts.
- Create `frontend/src/arena/createPrimitive.ts`: PlayCanvas primitive/material helper.
- Create `frontend/src/arena/createArena.ts`: industrial platform, grid, lights, camera, and geometric sci-fi background.
- Create `frontend/src/arena/createCadet.ts`: stylized humanoid Cadete primitives and idle/attack animation state.
- Create `frontend/src/arena/createMolock.ts`: large mechanical Molock primitives and idle/hit/counter animation state.
- Create `frontend/src/arena/createEffects.ts`: cyan projectile, red counter pulse, Molock hit flash, and camera shake.
- Create `frontend/src/arena/ApogeuArena.tsx`: React wrapper that initializes PlayCanvas and dispatches animation cues.
- Create `frontend/src/arena/primitiveContracts.test.ts`: unit checks that actor blueprints use primitives only and preserve scale/position intent.
- Create `frontend/src/App.test.tsx`: UI checks that correct answers cue Cadete and wrong answers cue Molock.
- Create `frontend/tests/arena.spec.ts`: browser smoke test for visible canvas and combat actions.
- Modify `Makefile:1-35`: add frontend serve/test targets without changing existing Streamlit targets.
- Modify `README.md:5-141`: document the new React + Vite + PlayCanvas MVP commands and primitive-only constraint.

## Task 1: Frontend Scaffold And Battle Cue Reducer

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/package-lock.json`
- Create: `frontend/index.html`
- Create: `frontend/vite.config.ts`
- Create: `frontend/tsconfig.json`
- Create: `frontend/tsconfig.node.json`
- Create: `frontend/src/setupTests.ts`
- Create: `frontend/src/game/battleState.test.ts`
- Create: `frontend/src/game/battleState.ts`

- [ ] **Step 1: Create the Vite package files**

Write `frontend/package.json`:

```json
{
  "name": "protocolo-apogeu-arena",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite --host 127.0.0.1 --port 5173",
    "build": "tsc -b && vite build",
    "test": "vitest run",
    "test:watch": "vitest",
    "test:e2e": "playwright test"
  },
  "dependencies": {
    "playcanvas": "^2.4.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0"
  },
  "devDependencies": {
    "@playwright/test": "^1.52.0",
    "@testing-library/jest-dom": "^6.6.3",
    "@testing-library/react": "^16.3.0",
    "@testing-library/user-event": "^14.6.1",
    "@types/react": "^19.0.0",
    "@types/react-dom": "^19.0.0",
    "@vitejs/plugin-react": "^4.4.0",
    "jsdom": "^26.1.0",
    "typescript": "^5.8.0",
    "vite": "^6.3.0",
    "vitest": "^3.1.0"
  }
}
```

Write `frontend/index.html`:

```html
<!doctype html>
<html lang="pt-BR">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Protocolo Apogeu Arena</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

Write `frontend/vite.config.ts`:

```ts
import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/setupTests.ts'],
  },
});
```

Write `frontend/tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "useDefineForClassFields": true,
    "lib": ["DOM", "DOM.Iterable", "ES2022"],
    "allowJs": false,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "module": "ESNext",
    "moduleResolution": "Node",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx"
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

Write `frontend/tsconfig.node.json`:

```json
{
  "compilerOptions": {
    "composite": true,
    "module": "ESNext",
    "moduleResolution": "Node",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts"]
}
```

Write `frontend/src/setupTests.ts`:

```ts
import '@testing-library/jest-dom/vitest';
```

- [ ] **Step 2: Install frontend dependencies**

Run:

```bash
cd frontend
npm install
```

Expected: `package-lock.json` is created and npm exits with code 0.

- [ ] **Step 3: Write the failing reducer test**

Write `frontend/src/game/battleState.test.ts`:

```ts
import { describe, expect, it } from 'vitest';
import { answerBattleQuestion, createInitialBattleState } from './battleState';

describe('battleState', () => {
  it('emits a cadet attack cue when the selected answer is correct', () => {
    const state = createInitialBattleState();

    const next = answerBattleQuestion(state, 'B');

    expect(next.lastCue).toBe('cadetAttack');
    expect(next.bossHp).toBe(130);
    expect(next.playerHp).toBe(100);
    expect(next.eventId).toBe(1);
    expect(next.feedback).toBe('ATAQUE EFETIVO');
  });

  it('emits a Molock counter cue when the selected answer is wrong', () => {
    const state = createInitialBattleState();

    const next = answerBattleQuestion(state, 'A');

    expect(next.lastCue).toBe('molockCounter');
    expect(next.bossHp).toBe(160);
    expect(next.playerHp).toBe(82);
    expect(next.eventId).toBe(1);
    expect(next.feedback).toBe('CONTRA-ATAQUE DE MOLOCK');
  });
});
```

- [ ] **Step 4: Run the reducer test and verify it fails**

Run:

```bash
cd frontend
npm run test -- src/game/battleState.test.ts
```

Expected: FAIL with an import error for `./battleState`.

- [ ] **Step 5: Implement the reducer**

Write `frontend/src/game/battleState.ts`:

```ts
export type CombatCue = 'idle' | 'cadetAttack' | 'molockCounter';

export type AnswerId = 'A' | 'B' | 'C' | 'D';

export interface ArenaQuestion {
  id: string;
  stem: string;
  options: Record<AnswerId, string>;
  correctAnswer: AnswerId;
}

export interface BattleState {
  playerHp: number;
  bossHp: number;
  eventId: number;
  lastCue: CombatCue;
  selectedAnswer: AnswerId | null;
  feedback: string;
  question: ArenaQuestion;
}

export const ARENA_QUESTION: ArenaQuestion = {
  id: 'Q-MOL-001',
  stem: 'Uma amostra de 18 g de agua corresponde a quantos mols?',
  options: {
    A: '0,5 mol',
    B: '1,0 mol',
    C: '2,0 mol',
    D: '18 mol',
  },
  correctAnswer: 'B',
};

export function createInitialBattleState(): BattleState {
  return {
    playerHp: 100,
    bossHp: 160,
    eventId: 0,
    lastCue: 'idle',
    selectedAnswer: null,
    feedback: 'Aguardando decisao do cadete',
    question: ARENA_QUESTION,
  };
}

export function answerBattleQuestion(state: BattleState, selectedAnswer: AnswerId): BattleState {
  const isCorrect = selectedAnswer === state.question.correctAnswer;

  if (isCorrect) {
    return {
      ...state,
      selectedAnswer,
      bossHp: Math.max(0, state.bossHp - 30),
      eventId: state.eventId + 1,
      lastCue: 'cadetAttack',
      feedback: 'ATAQUE EFETIVO',
    };
  }

  return {
    ...state,
    selectedAnswer,
    playerHp: Math.max(0, state.playerHp - 18),
    eventId: state.eventId + 1,
    lastCue: 'molockCounter',
    feedback: 'CONTRA-ATAQUE DE MOLOCK',
  };
}
```

- [ ] **Step 6: Run the reducer test and verify it passes**

Run:

```bash
cd frontend
npm run test -- src/game/battleState.test.ts
```

Expected: PASS for both reducer tests.

- [ ] **Step 7: Commit**

```bash
git add frontend/package.json frontend/package-lock.json frontend/index.html frontend/vite.config.ts frontend/tsconfig.json frontend/tsconfig.node.json frontend/src/setupTests.ts frontend/src/game/battleState.ts frontend/src/game/battleState.test.ts
git commit -m "feat: add arena frontend battle cues"
```

## Task 2: Primitive Contracts And Blueprints

**Files:**
- Create: `frontend/src/arena/types.ts`
- Create: `frontend/src/arena/createCadet.ts`
- Create: `frontend/src/arena/createMolock.ts`
- Create: `frontend/src/arena/createArena.ts`
- Create: `frontend/src/arena/primitiveContracts.test.ts`

- [ ] **Step 1: Write failing primitive contract tests**

Write `frontend/src/arena/primitiveContracts.test.ts`:

```ts
import { describe, expect, it } from 'vitest';
import { ARENA_BLUEPRINT } from './createArena';
import { CADET_BLUEPRINT, CADET_START_POSITION } from './createCadet';
import { MOLOCK_BLUEPRINT, MOLOCK_START_POSITION } from './createMolock';

function totalHeight(parts: Array<{ scale: readonly [number, number, number] }>): number {
  return parts.reduce((sum, part) => sum + part.scale[1], 0);
}

describe('primitive arena contracts', () => {
  it('uses only built-in primitive render types and no external asset keys', () => {
    const allParts = [...CADET_BLUEPRINT, ...MOLOCK_BLUEPRINT, ...ARENA_BLUEPRINT];

    for (const part of allParts) {
      expect(['box', 'sphere', 'cylinder', 'cone', 'capsule', 'plane']).toContain(part.kind);
      expect(Object.keys(part)).not.toContain('assetUrl');
      expect(Object.keys(part)).not.toContain('meshUrl');
      expect(Object.keys(part)).not.toContain('glb');
    }
  });

  it('places the Cadete left of center and Molock on the right', () => {
    expect(CADET_START_POSITION[0]).toBeLessThan(0);
    expect(CADET_START_POSITION[0]).toBeGreaterThan(-3);
    expect(MOLOCK_START_POSITION[0]).toBeGreaterThan(1.5);
  });

  it('makes Molock visually larger and more complex than the Cadete', () => {
    expect(MOLOCK_BLUEPRINT.length).toBeGreaterThan(CADET_BLUEPRINT.length);
    expect(totalHeight(MOLOCK_BLUEPRINT)).toBeGreaterThan(totalHeight(CADET_BLUEPRINT));
  });

  it('includes emissive combat identity parts for both actors', () => {
    expect(CADET_BLUEPRINT.some((part) => part.name === 'cadet-visor' && part.material === 'cadetVisor')).toBe(true);
    expect(MOLOCK_BLUEPRINT.some((part) => part.name === 'molock-core' && part.material === 'molockCore')).toBe(true);
    expect(MOLOCK_BLUEPRINT.some((part) => part.name === 'molock-eyes' && part.material === 'molockEyes')).toBe(true);
  });
});
```

- [ ] **Step 2: Run the primitive contract test and verify it fails**

Run:

```bash
cd frontend
npm run test -- src/arena/primitiveContracts.test.ts
```

Expected: FAIL with import errors for the missing arena modules.

- [ ] **Step 3: Define shared arena contracts**

Write `frontend/src/arena/types.ts`:

```ts
import type * as pc from 'playcanvas';
import type { CombatCue } from '../game/battleState';

export type PrimitiveKind = 'box' | 'sphere' | 'cylinder' | 'cone' | 'capsule' | 'plane';

export type MaterialRole =
  | 'platform'
  | 'platformTrim'
  | 'gridLine'
  | 'cadetArmor'
  | 'cadetDark'
  | 'cadetVisor'
  | 'cadetJoint'
  | 'molockArmor'
  | 'molockDark'
  | 'molockCore'
  | 'molockEyes'
  | 'warningLight'
  | 'cyanProjectile'
  | 'redPulse';

export interface PrimitiveSpec {
  name: string;
  kind: PrimitiveKind;
  position: readonly [number, number, number];
  scale: readonly [number, number, number];
  rotation?: readonly [number, number, number];
  material: MaterialRole;
}

export interface CombatEvent {
  id: number;
  cue: CombatCue;
}

export interface CombatActor {
  root: pc.Entity;
  update(dt: number, elapsed: number): void;
  getMuzzlePosition(): pc.Vec3;
  getTargetPosition(): pc.Vec3;
}

export interface CadetActor extends CombatActor {
  playAttack(): void;
}

export interface MolockActor extends CombatActor {
  playHit(): void;
  playCounterCharge(): void;
}

export interface ArenaHandles {
  camera: pc.Entity;
  platform: pc.Entity;
  destroy(): void;
}

export interface CombatEffects {
  cadetAttack(): Promise<void>;
  molockCounter(): Promise<void>;
  destroy(): void;
}
```

- [ ] **Step 4: Add primitive blueprints for Cadete, Molock, and arena**

Write `frontend/src/arena/createCadet.ts`:

```ts
import type { PrimitiveSpec } from './types';

export const CADET_START_POSITION = [-1.75, 0, 0.15] as const;

export const CADET_BLUEPRINT: PrimitiveSpec[] = [
  { name: 'cadet-boots', kind: 'box', position: [0, 0.18, 0], scale: [0.62, 0.28, 0.52], material: 'cadetDark' },
  { name: 'cadet-torso', kind: 'box', position: [0, 0.82, 0], scale: [0.72, 0.86, 0.46], rotation: [0, 0, -2], material: 'cadetArmor' },
  { name: 'cadet-chest-core', kind: 'box', position: [0.02, 0.93, -0.25], scale: [0.28, 0.12, 0.04], material: 'cadetVisor' },
  { name: 'cadet-head', kind: 'sphere', position: [0, 1.42, 0], scale: [0.42, 0.42, 0.42], material: 'cadetArmor' },
  { name: 'cadet-helmet-ridge', kind: 'box', position: [0, 1.66, -0.02], scale: [0.5, 0.12, 0.3], material: 'cadetDark' },
  { name: 'cadet-visor', kind: 'box', position: [0, 1.43, -0.38], scale: [0.46, 0.12, 0.04], material: 'cadetVisor' },
  { name: 'cadet-left-shoulder', kind: 'box', position: [-0.52, 1.08, 0], scale: [0.3, 0.24, 0.44], rotation: [0, 0, 12], material: 'cadetDark' },
  { name: 'cadet-right-shoulder', kind: 'box', position: [0.52, 1.08, 0], scale: [0.3, 0.24, 0.44], rotation: [0, 0, -12], material: 'cadetDark' },
  { name: 'cadet-left-arm', kind: 'capsule', position: [-0.78, 0.72, 0], scale: [0.16, 0.46, 0.16], rotation: [0, 0, 8], material: 'cadetJoint' },
  { name: 'cadet-right-arm', kind: 'capsule', position: [0.78, 0.74, 0], scale: [0.16, 0.5, 0.16], rotation: [0, 0, -18], material: 'cadetJoint' },
];
```

Write `frontend/src/arena/createMolock.ts`:

```ts
import type { PrimitiveSpec } from './types';

export const MOLOCK_START_POSITION = [2.15, 0, -0.1] as const;

export const MOLOCK_BLUEPRINT: PrimitiveSpec[] = [
  { name: 'molock-base', kind: 'box', position: [0, 0.32, 0], scale: [1.35, 0.42, 0.82], material: 'molockDark' },
  { name: 'molock-torso', kind: 'box', position: [0, 1.05, 0], scale: [1.28, 1.3, 0.72], rotation: [0, -6, 0], material: 'molockArmor' },
  { name: 'molock-core', kind: 'sphere', position: [0, 1.12, -0.44], scale: [0.34, 0.34, 0.34], material: 'molockCore' },
  { name: 'molock-head', kind: 'box', position: [0, 1.96, -0.02], scale: [0.86, 0.42, 0.48], material: 'molockDark' },
  { name: 'molock-eyes', kind: 'box', position: [0, 1.98, -0.31], scale: [0.58, 0.08, 0.05], material: 'molockEyes' },
  { name: 'molock-left-pauldron', kind: 'box', position: [-0.92, 1.55, 0], scale: [0.62, 0.34, 0.76], rotation: [0, 0, -18], material: 'molockArmor' },
  { name: 'molock-right-pauldron', kind: 'box', position: [0.92, 1.55, 0], scale: [0.62, 0.34, 0.76], rotation: [0, 0, 18], material: 'molockArmor' },
  { name: 'molock-left-arm-upper', kind: 'box', position: [-1.3, 1.02, 0], scale: [0.34, 0.9, 0.34], rotation: [0, 0, -12], material: 'molockDark' },
  { name: 'molock-right-arm-upper', kind: 'box', position: [1.3, 1.02, 0], scale: [0.34, 0.9, 0.34], rotation: [0, 0, 12], material: 'molockDark' },
  { name: 'molock-left-claw', kind: 'cone', position: [-1.48, 0.42, -0.04], scale: [0.32, 0.52, 0.32], rotation: [180, 0, -10], material: 'warningLight' },
  { name: 'molock-right-claw', kind: 'cone', position: [1.48, 0.42, -0.04], scale: [0.32, 0.52, 0.32], rotation: [180, 0, 10], material: 'warningLight' },
  { name: 'molock-back-fin-left', kind: 'box', position: [-0.44, 1.25, 0.48], scale: [0.22, 1.2, 0.2], rotation: [0, 0, -20], material: 'molockArmor' },
  { name: 'molock-back-fin-right', kind: 'box', position: [0.44, 1.25, 0.48], scale: [0.22, 1.2, 0.2], rotation: [0, 0, 20], material: 'molockArmor' },
];
```

Write `frontend/src/arena/createArena.ts`:

```ts
import type { PrimitiveSpec } from './types';

export const ARENA_BLUEPRINT: PrimitiveSpec[] = [
  { name: 'arena-platform', kind: 'box', position: [0, -0.08, 0], scale: [6.4, 0.16, 3.2], material: 'platform' },
  { name: 'arena-front-trim', kind: 'box', position: [0, 0.02, -1.72], scale: [6.8, 0.08, 0.08], material: 'platformTrim' },
  { name: 'arena-back-trim', kind: 'box', position: [0, 0.02, 1.72], scale: [6.8, 0.08, 0.08], material: 'platformTrim' },
  { name: 'grid-line-x-1', kind: 'box', position: [-2.4, 0.03, 0], scale: [0.03, 0.035, 3.0], material: 'gridLine' },
  { name: 'grid-line-x-2', kind: 'box', position: [-1.2, 0.03, 0], scale: [0.03, 0.035, 3.0], material: 'gridLine' },
  { name: 'grid-line-x-3', kind: 'box', position: [0, 0.03, 0], scale: [0.03, 0.035, 3.0], material: 'gridLine' },
  { name: 'grid-line-x-4', kind: 'box', position: [1.2, 0.03, 0], scale: [0.03, 0.035, 3.0], material: 'gridLine' },
  { name: 'grid-line-x-5', kind: 'box', position: [2.4, 0.03, 0], scale: [0.03, 0.035, 3.0], material: 'gridLine' },
  { name: 'grid-line-z-1', kind: 'box', position: [0, 0.035, -0.95], scale: [6.1, 0.03, 0.025], material: 'gridLine' },
  { name: 'grid-line-z-2', kind: 'box', position: [0, 0.035, 0], scale: [6.1, 0.03, 0.025], material: 'gridLine' },
  { name: 'grid-line-z-3', kind: 'box', position: [0, 0.035, 0.95], scale: [6.1, 0.03, 0.025], material: 'gridLine' },
  { name: 'back-structure-left', kind: 'box', position: [-2.6, 0.86, 1.35], scale: [0.42, 1.7, 0.24], rotation: [0, 0, -10], material: 'platformTrim' },
  { name: 'back-structure-right', kind: 'box', position: [2.7, 1.05, 1.25], scale: [0.5, 2.1, 0.22], rotation: [0, 0, 8], material: 'warningLight' },
  { name: 'warning-beacon-left', kind: 'sphere', position: [-3.05, 1.78, 1.1], scale: [0.14, 0.14, 0.14], material: 'warningLight' },
  { name: 'warning-beacon-right', kind: 'sphere', position: [3.05, 2.08, 0.95], scale: [0.16, 0.16, 0.16], material: 'warningLight' },
];
```

- [ ] **Step 5: Run the primitive contract test and verify it passes**

Run:

```bash
cd frontend
npm run test -- src/arena/primitiveContracts.test.ts
```

Expected: PASS for all primitive contract tests.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/arena/types.ts frontend/src/arena/createCadet.ts frontend/src/arena/createMolock.ts frontend/src/arena/createArena.ts frontend/src/arena/primitiveContracts.test.ts
git commit -m "feat: define primitive arena blueprints"
```

## Task 3: Arena Platform, Camera, Lights, And Primitive Helper

**Files:**
- Create: `frontend/src/arena/createPrimitive.ts`
- Modify: `frontend/src/arena/createArena.ts`

- [ ] **Step 1: Write the primitive helper**

Write `frontend/src/arena/createPrimitive.ts`:

```ts
import * as pc from 'playcanvas';
import type { MaterialRole, PrimitiveSpec } from './types';

type MaterialConfig = {
  diffuse: [number, number, number];
  emissive?: [number, number, number];
  metalness?: number;
  gloss?: number;
};

const MATERIAL_CONFIG: Record<MaterialRole, MaterialConfig> = {
  platform: { diffuse: [0.08, 0.1, 0.13], metalness: 0.65, gloss: 0.45 },
  platformTrim: { diffuse: [0.2, 0.27, 0.32], emissive: [0.02, 0.12, 0.16], metalness: 0.75, gloss: 0.58 },
  gridLine: { diffuse: [0.05, 0.5, 0.65], emissive: [0.02, 0.55, 0.75], metalness: 0.2, gloss: 0.7 },
  cadetArmor: { diffuse: [0.23, 0.35, 0.42], metalness: 0.55, gloss: 0.62 },
  cadetDark: { diffuse: [0.06, 0.09, 0.12], metalness: 0.7, gloss: 0.5 },
  cadetVisor: { diffuse: [0.04, 0.75, 0.9], emissive: [0.0, 0.95, 1.0], metalness: 0.1, gloss: 0.88 },
  cadetJoint: { diffuse: [0.12, 0.17, 0.2], metalness: 0.7, gloss: 0.48 },
  molockArmor: { diffuse: [0.34, 0.2, 0.13], metalness: 0.85, gloss: 0.42 },
  molockDark: { diffuse: [0.08, 0.07, 0.07], metalness: 0.78, gloss: 0.36 },
  molockCore: { diffuse: [1.0, 0.26, 0.03], emissive: [1.0, 0.2, 0.0], metalness: 0.12, gloss: 0.95 },
  molockEyes: { diffuse: [1.0, 0.04, 0.02], emissive: [1.0, 0.0, 0.0], metalness: 0.1, gloss: 0.9 },
  warningLight: { diffuse: [0.95, 0.32, 0.04], emissive: [0.9, 0.12, 0.0], metalness: 0.25, gloss: 0.72 },
  cyanProjectile: { diffuse: [0.04, 0.9, 1.0], emissive: [0.0, 0.95, 1.0], metalness: 0.05, gloss: 1.0 },
  redPulse: { diffuse: [1.0, 0.08, 0.02], emissive: [1.0, 0.04, 0.0], metalness: 0.05, gloss: 1.0 },
};

export function createArenaMaterials(): Record<MaterialRole, pc.StandardMaterial> {
  return Object.fromEntries(
    Object.entries(MATERIAL_CONFIG).map(([role, config]) => {
      const material = new pc.StandardMaterial();
      material.diffuse = new pc.Color(...config.diffuse);
      material.metalness = config.metalness ?? 0;
      material.gloss = config.gloss ?? 0.45;
      if (config.emissive) {
        material.emissive = new pc.Color(...config.emissive);
        material.emissiveIntensity = 1.35;
      }
      material.update();
      return [role, material];
    }),
  ) as Record<MaterialRole, pc.StandardMaterial>;
}

export function createPrimitiveEntity(
  spec: PrimitiveSpec,
  materials: Record<MaterialRole, pc.StandardMaterial>,
): pc.Entity {
  const entity = new pc.Entity(spec.name);
  entity.addComponent('render', {
    type: spec.kind,
    material: materials[spec.material],
  });
  entity.setLocalPosition(...spec.position);
  entity.setLocalScale(...spec.scale);
  if (spec.rotation) {
    entity.setLocalEulerAngles(...spec.rotation);
  }
  return entity;
}
```

- [ ] **Step 2: Replace `createArena.ts` with the PlayCanvas implementation**

In `frontend/src/arena/createArena.ts`, keep `ARENA_BLUEPRINT` from Task 2 and replace only the `createArena` function:

```ts
import * as pc from 'playcanvas';
import type { ArenaHandles, PrimitiveSpec } from './types';
import { createArenaMaterials, createPrimitiveEntity } from './createPrimitive';

export const ARENA_BLUEPRINT: PrimitiveSpec[] = [
  { name: 'arena-platform', kind: 'box', position: [0, -0.08, 0], scale: [6.4, 0.16, 3.2], material: 'platform' },
  { name: 'arena-front-trim', kind: 'box', position: [0, 0.02, -1.72], scale: [6.8, 0.08, 0.08], material: 'platformTrim' },
  { name: 'arena-back-trim', kind: 'box', position: [0, 0.02, 1.72], scale: [6.8, 0.08, 0.08], material: 'platformTrim' },
  { name: 'grid-line-x-1', kind: 'box', position: [-2.4, 0.03, 0], scale: [0.03, 0.035, 3.0], material: 'gridLine' },
  { name: 'grid-line-x-2', kind: 'box', position: [-1.2, 0.03, 0], scale: [0.03, 0.035, 3.0], material: 'gridLine' },
  { name: 'grid-line-x-3', kind: 'box', position: [0, 0.03, 0], scale: [0.03, 0.035, 3.0], material: 'gridLine' },
  { name: 'grid-line-x-4', kind: 'box', position: [1.2, 0.03, 0], scale: [0.03, 0.035, 3.0], material: 'gridLine' },
  { name: 'grid-line-x-5', kind: 'box', position: [2.4, 0.03, 0], scale: [0.03, 0.035, 3.0], material: 'gridLine' },
  { name: 'grid-line-z-1', kind: 'box', position: [0, 0.035, -0.95], scale: [6.1, 0.03, 0.025], material: 'gridLine' },
  { name: 'grid-line-z-2', kind: 'box', position: [0, 0.035, 0], scale: [6.1, 0.03, 0.025], material: 'gridLine' },
  { name: 'grid-line-z-3', kind: 'box', position: [0, 0.035, 0.95], scale: [6.1, 0.03, 0.025], material: 'gridLine' },
  { name: 'back-structure-left', kind: 'box', position: [-2.6, 0.86, 1.35], scale: [0.42, 1.7, 0.24], rotation: [0, 0, -10], material: 'platformTrim' },
  { name: 'back-structure-right', kind: 'box', position: [2.7, 1.05, 1.25], scale: [0.5, 2.1, 0.22], rotation: [0, 0, 8], material: 'warningLight' },
  { name: 'warning-beacon-left', kind: 'sphere', position: [-3.05, 1.78, 1.1], scale: [0.14, 0.14, 0.14], material: 'warningLight' },
  { name: 'warning-beacon-right', kind: 'sphere', position: [3.05, 2.08, 0.95], scale: [0.16, 0.16, 0.16], material: 'warningLight' },
];

export function createArena(app: pc.Application): ArenaHandles {
  const materials = createArenaMaterials();
  const platform = new pc.Entity('primitive-arena-root');
  app.root.addChild(platform);

  for (const spec of ARENA_BLUEPRINT) {
    platform.addChild(createPrimitiveEntity(spec, materials));
  }

  const camera = new pc.Entity('arena-camera');
  camera.addComponent('camera', {
    clearColor: new pc.Color(0.015, 0.02, 0.032),
    fov: 43,
    nearClip: 0.1,
    farClip: 100,
  });
  camera.setLocalPosition(0.15, 2.25, 5.9);
  camera.setLocalEulerAngles(-18, 2, 0);
  app.root.addChild(camera);

  const keyLight = new pc.Entity('arena-key-light');
  keyLight.addComponent('light', {
    type: 'directional',
    color: new pc.Color(0.72, 0.88, 1),
    intensity: 1.2,
    castShadows: true,
  });
  keyLight.setLocalEulerAngles(42, -32, 0);
  app.root.addChild(keyLight);

  const warningLight = new pc.Entity('arena-warning-light');
  warningLight.addComponent('light', {
    type: 'omni',
    color: new pc.Color(1, 0.22, 0.04),
    intensity: 0.95,
    range: 6,
  });
  warningLight.setLocalPosition(2.4, 2.2, 1.1);
  app.root.addChild(warningLight);

  const cyanLight = new pc.Entity('arena-cadet-light');
  cyanLight.addComponent('light', {
    type: 'omni',
    color: new pc.Color(0.05, 0.8, 1),
    intensity: 0.55,
    range: 4,
  });
  cyanLight.setLocalPosition(-1.8, 1.1, -0.8);
  app.root.addChild(cyanLight);

  return {
    camera,
    platform,
    destroy() {
      platform.destroy();
      camera.destroy();
      keyLight.destroy();
      warningLight.destroy();
      cyanLight.destroy();
    },
  };
}
```

- [ ] **Step 3: Run primitive tests and TypeScript check**

Run:

```bash
cd frontend
npm run test -- src/arena/primitiveContracts.test.ts
npx tsc -b --pretty false
```

Expected: primitive tests PASS and TypeScript completes without errors.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/arena/createPrimitive.ts frontend/src/arena/createArena.ts
git commit -m "feat: create primitive industrial arena"
```

## Task 4: Cadete Primitive Actor

**Files:**
- Modify: `frontend/src/arena/createCadet.ts`

- [ ] **Step 1: Replace `createCadet` with an animated primitive actor**

In `frontend/src/arena/createCadet.ts`, keep `CADET_START_POSITION` and `CADET_BLUEPRINT` from Task 2 and replace the file with:

```ts
import * as pc from 'playcanvas';
import type { CadetActor, PrimitiveSpec } from './types';
import { createArenaMaterials, createPrimitiveEntity } from './createPrimitive';

export const CADET_START_POSITION = [-1.75, 0, 0.15] as const;

export const CADET_BLUEPRINT: PrimitiveSpec[] = [
  { name: 'cadet-boots', kind: 'box', position: [0, 0.18, 0], scale: [0.62, 0.28, 0.52], material: 'cadetDark' },
  { name: 'cadet-torso', kind: 'box', position: [0, 0.82, 0], scale: [0.72, 0.86, 0.46], rotation: [0, 0, -2], material: 'cadetArmor' },
  { name: 'cadet-chest-core', kind: 'box', position: [0.02, 0.93, -0.25], scale: [0.28, 0.12, 0.04], material: 'cadetVisor' },
  { name: 'cadet-head', kind: 'sphere', position: [0, 1.42, 0], scale: [0.42, 0.42, 0.42], material: 'cadetArmor' },
  { name: 'cadet-helmet-ridge', kind: 'box', position: [0, 1.66, -0.02], scale: [0.5, 0.12, 0.3], material: 'cadetDark' },
  { name: 'cadet-visor', kind: 'box', position: [0, 1.43, -0.38], scale: [0.46, 0.12, 0.04], material: 'cadetVisor' },
  { name: 'cadet-left-shoulder', kind: 'box', position: [-0.52, 1.08, 0], scale: [0.3, 0.24, 0.44], rotation: [0, 0, 12], material: 'cadetDark' },
  { name: 'cadet-right-shoulder', kind: 'box', position: [0.52, 1.08, 0], scale: [0.3, 0.24, 0.44], rotation: [0, 0, -12], material: 'cadetDark' },
  { name: 'cadet-left-arm', kind: 'capsule', position: [-0.78, 0.72, 0], scale: [0.16, 0.46, 0.16], rotation: [0, 0, 8], material: 'cadetJoint' },
  { name: 'cadet-right-arm', kind: 'capsule', position: [0.78, 0.74, 0], scale: [0.16, 0.5, 0.16], rotation: [0, 0, -18], material: 'cadetJoint' },
];

export function createCadet(app: pc.Application): CadetActor {
  const materials = createArenaMaterials();
  const root = new pc.Entity('cadet-root');
  root.setLocalPosition(...CADET_START_POSITION);
  app.root.addChild(root);

  const rightArm = new pc.Entity('cadet-right-arm-pivot');
  rightArm.setLocalPosition(0.55, 1.03, 0);
  root.addChild(rightArm);

  for (const spec of CADET_BLUEPRINT) {
    const entity = createPrimitiveEntity(spec, materials);
    if (spec.name === 'cadet-right-arm') {
      entity.setLocalPosition(0.23, -0.29, 0);
      rightArm.addChild(entity);
    } else {
      root.addChild(entity);
    }
  }

  let attackTimer = 0;

  return {
    root,
    playAttack() {
      attackTimer = 0.82;
    },
    update(dt: number, elapsed: number) {
      attackTimer = Math.max(0, attackTimer - dt);
      const attackProgress = attackTimer > 0 ? 1 - attackTimer / 0.82 : 0;
      const lunge = attackTimer > 0 ? Math.sin(attackProgress * Math.PI) * 0.34 : 0;
      const bob = Math.sin(elapsed * 2.4) * 0.035;

      root.setLocalPosition(CADET_START_POSITION[0] + lunge, CADET_START_POSITION[1] + bob, CADET_START_POSITION[2]);
      root.setLocalEulerAngles(0, 0, Math.sin(elapsed * 1.6) * 1.4);
      rightArm.setLocalEulerAngles(0, 0, attackTimer > 0 ? -48 * Math.sin(attackProgress * Math.PI) : -8);
    },
    getMuzzlePosition() {
      return root.getPosition().clone().add(new pc.Vec3(0.78, 1.18, -0.32));
    },
    getTargetPosition() {
      return root.getPosition().clone().add(new pc.Vec3(0, 1.05, -0.2));
    },
  };
}
```

- [ ] **Step 2: Run contract tests and TypeScript check**

Run:

```bash
cd frontend
npm run test -- src/arena/primitiveContracts.test.ts
npx tsc -b --pretty false
```

Expected: primitive tests PASS and TypeScript completes without errors.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/arena/createCadet.ts
git commit -m "feat: create animated primitive cadet"
```

## Task 5: Molock Primitive Boss Actor

**Files:**
- Modify: `frontend/src/arena/createMolock.ts`

- [ ] **Step 1: Replace `createMolock` with an animated primitive boss**

In `frontend/src/arena/createMolock.ts`, keep `MOLOCK_START_POSITION` and `MOLOCK_BLUEPRINT` from Task 2 and replace the file with:

```ts
import * as pc from 'playcanvas';
import type { MolockActor, PrimitiveSpec } from './types';
import { createArenaMaterials, createPrimitiveEntity } from './createPrimitive';

export const MOLOCK_START_POSITION = [2.15, 0, -0.1] as const;

export const MOLOCK_BLUEPRINT: PrimitiveSpec[] = [
  { name: 'molock-base', kind: 'box', position: [0, 0.32, 0], scale: [1.35, 0.42, 0.82], material: 'molockDark' },
  { name: 'molock-torso', kind: 'box', position: [0, 1.05, 0], scale: [1.28, 1.3, 0.72], rotation: [0, -6, 0], material: 'molockArmor' },
  { name: 'molock-core', kind: 'sphere', position: [0, 1.12, -0.44], scale: [0.34, 0.34, 0.34], material: 'molockCore' },
  { name: 'molock-head', kind: 'box', position: [0, 1.96, -0.02], scale: [0.86, 0.42, 0.48], material: 'molockDark' },
  { name: 'molock-eyes', kind: 'box', position: [0, 1.98, -0.31], scale: [0.58, 0.08, 0.05], material: 'molockEyes' },
  { name: 'molock-left-pauldron', kind: 'box', position: [-0.92, 1.55, 0], scale: [0.62, 0.34, 0.76], rotation: [0, 0, -18], material: 'molockArmor' },
  { name: 'molock-right-pauldron', kind: 'box', position: [0.92, 1.55, 0], scale: [0.62, 0.34, 0.76], rotation: [0, 0, 18], material: 'molockArmor' },
  { name: 'molock-left-arm-upper', kind: 'box', position: [-1.3, 1.02, 0], scale: [0.34, 0.9, 0.34], rotation: [0, 0, -12], material: 'molockDark' },
  { name: 'molock-right-arm-upper', kind: 'box', position: [1.3, 1.02, 0], scale: [0.34, 0.9, 0.34], rotation: [0, 0, 12], material: 'molockDark' },
  { name: 'molock-left-claw', kind: 'cone', position: [-1.48, 0.42, -0.04], scale: [0.32, 0.52, 0.32], rotation: [180, 0, -10], material: 'warningLight' },
  { name: 'molock-right-claw', kind: 'cone', position: [1.48, 0.42, -0.04], scale: [0.32, 0.52, 0.32], rotation: [180, 0, 10], material: 'warningLight' },
  { name: 'molock-back-fin-left', kind: 'box', position: [-0.44, 1.25, 0.48], scale: [0.22, 1.2, 0.2], rotation: [0, 0, -20], material: 'molockArmor' },
  { name: 'molock-back-fin-right', kind: 'box', position: [0.44, 1.25, 0.48], scale: [0.22, 1.2, 0.2], rotation: [0, 0, 20], material: 'molockArmor' },
];

export function createMolock(app: pc.Application): MolockActor {
  const materials = createArenaMaterials();
  const root = new pc.Entity('molock-root');
  root.setLocalPosition(...MOLOCK_START_POSITION);
  app.root.addChild(root);

  let coreMaterial: pc.StandardMaterial | null = null;
  let hitTimer = 0;
  let chargeTimer = 0;

  for (const spec of MOLOCK_BLUEPRINT) {
    const entity = createPrimitiveEntity(spec, materials);
    if (spec.name === 'molock-core' && entity.render?.material instanceof pc.StandardMaterial) {
      coreMaterial = entity.render.material;
    }
    root.addChild(entity);
  }

  return {
    root,
    playHit() {
      hitTimer = 0.34;
    },
    playCounterCharge() {
      chargeTimer = 0.72;
    },
    update(dt: number, elapsed: number) {
      hitTimer = Math.max(0, hitTimer - dt);
      chargeTimer = Math.max(0, chargeTimer - dt);

      const idleSway = Math.sin(elapsed * 1.35) * 1.8;
      const shake = hitTimer > 0 ? Math.sin(hitTimer * 90) * 0.07 : 0;
      root.setLocalPosition(MOLOCK_START_POSITION[0] + shake, MOLOCK_START_POSITION[1], MOLOCK_START_POSITION[2]);
      root.setLocalEulerAngles(0, -6, idleSway);

      if (coreMaterial) {
        const idlePulse = 1.2 + Math.sin(elapsed * 3.2) * 0.35;
        const hitPulse = hitTimer > 0 ? 2.4 : 0;
        const chargePulse = chargeTimer > 0 ? 1.8 + Math.sin(elapsed * 14) * 0.7 : 0;
        coreMaterial.emissiveIntensity = idlePulse + hitPulse + chargePulse;
        coreMaterial.emissive = hitTimer > 0 ? new pc.Color(1, 0.42, 0.02) : new pc.Color(1, 0.18, 0);
        coreMaterial.update();
      }
    },
    getMuzzlePosition() {
      return root.getPosition().clone().add(new pc.Vec3(-0.08, 1.12, -0.54));
    },
    getTargetPosition() {
      return root.getPosition().clone().add(new pc.Vec3(0, 1.08, -0.28));
    },
  };
}
```

- [ ] **Step 2: Run contract tests and TypeScript check**

Run:

```bash
cd frontend
npm run test -- src/arena/primitiveContracts.test.ts
npx tsc -b --pretty false
```

Expected: primitive tests PASS and TypeScript completes without errors.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/arena/createMolock.ts
git commit -m "feat: create animated primitive molock"
```

## Task 6: Combat Effects And React PlayCanvas Bridge

**Files:**
- Create: `frontend/src/arena/createEffects.ts`
- Create: `frontend/src/arena/ApogeuArena.tsx`

- [ ] **Step 1: Create projectile, hit, counter, and camera shake effects**

Write `frontend/src/arena/createEffects.ts`:

```ts
import * as pc from 'playcanvas';
import { createArenaMaterials } from './createPrimitive';
import type { CadetActor, CombatEffects, MolockActor } from './types';

interface EffectActors {
  cadet: CadetActor;
  molock: MolockActor;
  camera: pc.Entity;
}

interface FlyingEffect {
  entity: pc.Entity;
  from: pc.Vec3;
  to: pc.Vec3;
  age: number;
  duration: number;
  onDone: () => void;
}

function createOrb(name: string, material: pc.StandardMaterial, scale: number): pc.Entity {
  const orb = new pc.Entity(name);
  orb.addComponent('render', { type: 'sphere', material });
  orb.setLocalScale(scale, scale, scale);
  return orb;
}

export function createCombatEffects(app: pc.Application, actors: EffectActors): CombatEffects {
  const materials = createArenaMaterials();
  const flying: FlyingEffect[] = [];
  const cameraBase = actors.camera.getLocalPosition().clone();
  let shakeTimer = 0;

  const update = (dt: number) => {
    for (let index = flying.length - 1; index >= 0; index -= 1) {
      const effect = flying[index];
      effect.age += dt;
      const t = Math.min(1, effect.age / effect.duration);
      const eased = t * t * (3 - 2 * t);
      effect.entity.setLocalPosition(effect.from.clone().lerp(effect.from, effect.to, eased));
      const pulseScale = 0.18 + Math.sin(t * Math.PI) * 0.14;
      effect.entity.setLocalScale(pulseScale, pulseScale, pulseScale);
      if (t >= 1) {
        effect.entity.destroy();
        flying.splice(index, 1);
        effect.onDone();
      }
    }

    shakeTimer = Math.max(0, shakeTimer - dt);
    if (shakeTimer > 0) {
      const shake = Math.sin(shakeTimer * 95) * 0.045;
      actors.camera.setLocalPosition(cameraBase.x + shake, cameraBase.y - shake * 0.35, cameraBase.z);
    } else {
      actors.camera.setLocalPosition(cameraBase);
    }
  };

  app.on('update', update);

  function fly(name: string, material: pc.StandardMaterial, from: pc.Vec3, to: pc.Vec3, duration: number): Promise<void> {
    const entity = createOrb(name, material, 0.18);
    app.root.addChild(entity);
    entity.setLocalPosition(from);

    return new Promise((resolve) => {
      flying.push({ entity, from, to, age: 0, duration, onDone: resolve });
    });
  }

  return {
    async cadetAttack() {
      actors.cadet.playAttack();
      await fly('cadet-cyan-projectile', materials.cyanProjectile, actors.cadet.getMuzzlePosition(), actors.molock.getTargetPosition(), 0.46);
      actors.molock.playHit();
    },
    async molockCounter() {
      actors.molock.playCounterCharge();
      await new Promise((resolve) => window.setTimeout(resolve, 360));
      await fly('molock-red-pulse', materials.redPulse, actors.molock.getMuzzlePosition(), actors.cadet.getTargetPosition(), 0.42);
      shakeTimer = 0.32;
    },
    destroy() {
      app.off('update', update);
      for (const effect of flying) {
        effect.entity.destroy();
      }
      flying.length = 0;
      actors.camera.setLocalPosition(cameraBase);
    },
  };
}
```

- [ ] **Step 2: Create the React PlayCanvas wrapper**

Write `frontend/src/arena/ApogeuArena.tsx`:

```tsx
import { useEffect, useRef } from 'react';
import * as pc from 'playcanvas';
import type { CombatEvent, CombatEffects } from './types';
import { createArena } from './createArena';
import { createCadet } from './createCadet';
import { createCombatEffects } from './createEffects';
import { createMolock } from './createMolock';

interface ApogeuArenaProps {
  combatEvent: CombatEvent;
}

export function ApogeuArena({ combatEvent }: ApogeuArenaProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const effectsRef = useRef<CombatEffects | null>(null);
  const latestEventRef = useRef(0);

  useEffect(() => {
    if (!canvasRef.current) {
      return;
    }

    const app = new pc.Application(canvasRef.current, {
      graphicsDeviceOptions: {
        antialias: true,
        alpha: false,
      },
    });

    app.setCanvasFillMode(pc.FILLMODE_FILL_WINDOW);
    app.setCanvasResolution(pc.RESOLUTION_AUTO);
    app.start();

    const arena = createArena(app);
    const cadet = createCadet(app);
    const molock = createMolock(app);
    const effects = createCombatEffects(app, { cadet, molock, camera: arena.camera });
    effectsRef.current = effects;

    let elapsed = 0;
    const updateActors = (dt: number) => {
      elapsed += dt;
      cadet.update(dt, elapsed);
      molock.update(dt, elapsed);
    };
    app.on('update', updateActors);

    const resize = () => app.resizeCanvas();
    window.addEventListener('resize', resize);

    return () => {
      window.removeEventListener('resize', resize);
      app.off('update', updateActors);
      effects.destroy();
      arena.destroy();
      cadet.root.destroy();
      molock.root.destroy();
      app.destroy();
      effectsRef.current = null;
    };
  }, []);

  useEffect(() => {
    if (!effectsRef.current || combatEvent.id === latestEventRef.current) {
      return;
    }

    latestEventRef.current = combatEvent.id;
    if (combatEvent.cue === 'cadetAttack') {
      void effectsRef.current.cadetAttack();
    }
    if (combatEvent.cue === 'molockCounter') {
      void effectsRef.current.molockCounter();
    }
  }, [combatEvent]);

  return (
    <div className="arena-shell" data-last-event={combatEvent.cue}>
      <canvas ref={canvasRef} className="arena-canvas" aria-label="Arena 3D do Protocolo Apogeu" />
    </div>
  );
}
```

- [ ] **Step 3: Run TypeScript check**

Run:

```bash
cd frontend
npx tsc -b --pretty false
```

Expected: TypeScript completes without errors.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/arena/createEffects.ts frontend/src/arena/ApogeuArena.tsx
git commit -m "feat: wire primitive arena combat effects"
```

## Task 7: Playable React MVP UI

**Files:**
- Create: `frontend/src/main.tsx`
- Create: `frontend/src/App.tsx`
- Create: `frontend/src/styles.css`
- Create: `frontend/src/App.test.tsx`

- [ ] **Step 1: Write failing UI tests**

Write `frontend/src/App.test.tsx`:

```tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import App from './App';

vi.mock('./arena/ApogeuArena', () => ({
  ApogeuArena: ({ combatEvent }: { combatEvent: { cue: string } }) => (
    <div data-testid="arena" data-last-event={combatEvent.cue} />
  ),
}));

describe('App', () => {
  it('fires the Cadete attack on a correct answer', async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.click(screen.getByRole('button', { name: /B - 1,0 mol/i }));
    await user.click(screen.getByRole('button', { name: 'ATACAR' }));

    expect(screen.getByTestId('arena')).toHaveAttribute('data-last-event', 'cadetAttack');
    expect(screen.getByText('ATAQUE EFETIVO')).toBeInTheDocument();
  });

  it('fires Molock counter-attack on a wrong answer', async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.click(screen.getByRole('button', { name: /A - 0,5 mol/i }));
    await user.click(screen.getByRole('button', { name: 'ATACAR' }));

    expect(screen.getByTestId('arena')).toHaveAttribute('data-last-event', 'molockCounter');
    expect(screen.getByText('CONTRA-ATAQUE DE MOLOCK')).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run UI tests and verify they fail**

Run:

```bash
cd frontend
npm run test -- src/App.test.tsx
```

Expected: FAIL with an import error for `./App`.

- [ ] **Step 3: Implement React entry, app, and styles**

Write `frontend/src/main.tsx`:

```tsx
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';
import './styles.css';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
```

Write `frontend/src/App.tsx`:

```tsx
import { useMemo, useState } from 'react';
import { ApogeuArena } from './arena/ApogeuArena';
import type { CombatEvent } from './arena/types';
import type { AnswerId } from './game/battleState';
import { answerBattleQuestion, createInitialBattleState } from './game/battleState';

export default function App() {
  const [battle, setBattle] = useState(createInitialBattleState);
  const [selected, setSelected] = useState<AnswerId | null>(null);

  const combatEvent: CombatEvent = useMemo(
    () => ({ id: battle.eventId, cue: battle.lastCue }),
    [battle.eventId, battle.lastCue],
  );

  function attack() {
    if (!selected) {
      return;
    }
    setBattle((current) => answerBattleQuestion(current, selected));
  }

  return (
    <main className="app-shell">
      <section className="battle-stage">
        <div className="hud-strip" aria-label="Telemetria de combate">
          <div>
            <span>CADETE</span>
            <strong>{battle.playerHp} HP</strong>
          </div>
          <div>
            <span>MOLOCK</span>
            <strong>{battle.bossHp} HP</strong>
          </div>
          <div>
            <span>ESTADO</span>
            <strong>{battle.feedback}</strong>
          </div>
        </div>
        <ApogeuArena combatEvent={combatEvent} />
      </section>

      <aside className="command-panel" aria-label="Cartas de acao">
        <div className="panel-heading">
          <span>PROTOCOLO APOGEU</span>
          <h1>Arena tática</h1>
        </div>

        <p className="question-text">{battle.question.stem}</p>

        <div className="answer-grid">
          {Object.entries(battle.question.options).map(([answerId, label]) => {
            const typedAnswer = answerId as AnswerId;
            return (
              <button
                type="button"
                key={answerId}
                className={selected === typedAnswer ? 'answer-card selected' : 'answer-card'}
                onClick={() => setSelected(typedAnswer)}
              >
                <span>{answerId}</span>
                {answerId} - {label}
              </button>
            );
          })}
        </div>

        <button type="button" className="attack-button" disabled={!selected} onClick={attack}>
          ATACAR
        </button>
      </aside>
    </main>
  );
}
```

Write `frontend/src/styles.css`:

```css
:root {
  color: #e7f7ff;
  background: #05080d;
  font-family:
    Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI",
    sans-serif;
  font-synthesis: none;
  text-rendering: optimizeLegibility;
}

* {
  box-sizing: border-box;
}

html,
body,
#root {
  width: 100%;
  min-height: 100%;
  margin: 0;
}

button {
  font: inherit;
}

.app-shell {
  min-height: 100vh;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 360px;
  background:
    linear-gradient(rgba(79, 212, 255, 0.045) 1px, transparent 1px),
    linear-gradient(90deg, rgba(79, 212, 255, 0.035) 1px, transparent 1px),
    radial-gradient(circle at 72% 22%, rgba(255, 76, 18, 0.2), transparent 32%),
    #05080d;
  background-size: 36px 36px, 36px 36px, auto, auto;
}

.battle-stage {
  display: grid;
  grid-template-rows: auto minmax(0, 1fr);
  min-height: 100vh;
  padding: 18px;
  gap: 12px;
}

.hud-strip {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}

.hud-strip div,
.command-panel {
  border: 1px solid rgba(93, 217, 255, 0.32);
  border-radius: 8px;
  background: rgba(8, 14, 22, 0.86);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.08);
}

.hud-strip div {
  padding: 12px 14px;
}

.hud-strip span,
.panel-heading span {
  display: block;
  color: #8fb2bf;
  font-size: 0.72rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.hud-strip strong {
  display: block;
  margin-top: 4px;
  font-size: 1.05rem;
}

.arena-shell {
  position: relative;
  min-height: 540px;
  border: 1px solid rgba(93, 217, 255, 0.38);
  border-radius: 8px;
  overflow: hidden;
  background: #05080d;
}

.arena-canvas {
  display: block;
  width: 100%;
  height: 100%;
}

.command-panel {
  min-height: 100vh;
  padding: 22px;
  border-width: 0 0 0 1px;
  border-radius: 0;
}

.panel-heading h1 {
  margin: 6px 0 24px;
  font-size: 2rem;
  line-height: 1;
}

.question-text {
  margin: 0 0 18px;
  color: #d8edf5;
  line-height: 1.45;
}

.answer-grid {
  display: grid;
  gap: 10px;
}

.answer-card,
.attack-button {
  min-height: 54px;
  border: 1px solid rgba(93, 217, 255, 0.3);
  border-radius: 8px;
  background: linear-gradient(180deg, rgba(30, 45, 58, 0.96), rgba(12, 18, 28, 0.98));
  color: #e7f7ff;
  text-align: left;
  cursor: pointer;
}

.answer-card {
  padding: 12px;
}

.answer-card span {
  display: inline-grid;
  place-items: center;
  width: 28px;
  height: 28px;
  margin-right: 8px;
  border-radius: 50%;
  background: rgba(93, 217, 255, 0.14);
  color: #61e6ff;
  font-weight: 800;
}

.answer-card.selected {
  border-color: #61e6ff;
  box-shadow: 0 0 0 1px rgba(97, 230, 255, 0.32), 0 0 22px rgba(97, 230, 255, 0.16);
}

.attack-button {
  width: 100%;
  margin-top: 18px;
  padding: 0 16px;
  text-align: center;
  font-weight: 900;
  letter-spacing: 0.08em;
  background: linear-gradient(180deg, rgba(255, 94, 27, 0.95), rgba(121, 24, 16, 0.98));
}

.attack-button:disabled {
  cursor: not-allowed;
  opacity: 0.48;
}

@media (max-width: 980px) {
  .app-shell {
    grid-template-columns: 1fr;
  }

  .battle-stage,
  .command-panel {
    min-height: auto;
  }

  .command-panel {
    border-width: 1px 0 0;
  }

  .hud-strip {
    grid-template-columns: 1fr;
  }

  .arena-shell {
    min-height: 420px;
  }
}
```

- [ ] **Step 4: Run UI tests and build**

Run:

```bash
cd frontend
npm run test -- src/App.test.tsx src/game/battleState.test.ts src/arena/primitiveContracts.test.ts
npm run build
```

Expected: all Vitest tests PASS and build completes.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/main.tsx frontend/src/App.tsx frontend/src/styles.css frontend/src/App.test.tsx
git commit -m "feat: add playable primitive arena ui"
```

## Task 8: Browser Smoke Test For Canvas And Combat Cues

**Files:**
- Create: `frontend/playwright.config.ts`
- Create: `frontend/tests/arena.spec.ts`

- [ ] **Step 1: Add Playwright config**

Write `frontend/playwright.config.ts`:

```ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  timeout: 30_000,
  fullyParallel: true,
  webServer: {
    command: 'npm run dev',
    url: 'http://127.0.0.1:5173',
    reuseExistingServer: true,
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
});
```

- [ ] **Step 2: Add the browser smoke test**

Write `frontend/tests/arena.spec.ts`:

```ts
import { expect, test } from '@playwright/test';

test('renders primitive PlayCanvas arena and reacts to correct and wrong attacks', async ({ page }) => {
  const blockedAssetRequests: string[] = [];
  page.on('request', (request) => {
    const url = request.url();
    if (/\.(glb|gltf|fbx|obj|png|jpg|jpeg|webp)$/i.test(url)) {
      blockedAssetRequests.push(url);
    }
  });

  await page.goto('/');
  const canvas = page.getByLabel('Arena 3D do Protocolo Apogeu');
  await expect(canvas).toBeVisible();
  await expect
    .poll(async () => canvas.evaluate((element) => (element as HTMLCanvasElement).width))
    .toBeGreaterThan(300);

  await page.getByRole('button', { name: /B - 1,0 mol/i }).click();
  await page.getByRole('button', { name: 'ATACAR' }).click();
  await expect(page.locator('.arena-shell')).toHaveAttribute('data-last-event', 'cadetAttack');
  await expect(page.getByText('ATAQUE EFETIVO')).toBeVisible();

  await page.getByRole('button', { name: /A - 0,5 mol/i }).click();
  await page.getByRole('button', { name: 'ATACAR' }).click();
  await expect(page.locator('.arena-shell')).toHaveAttribute('data-last-event', 'molockCounter');
  await expect(page.getByText('CONTRA-ATAQUE DE MOLOCK')).toBeVisible();

  expect(blockedAssetRequests).toEqual([]);
});
```

- [ ] **Step 3: Run Playwright smoke test**

Run:

```bash
cd frontend
npx playwright install chromium
npm run test:e2e
```

Expected: Chromium installs if it is not already present, the Vite dev server starts, the canvas is visible, correct attack sets `data-last-event="cadetAttack"`, wrong attack sets `data-last-event="molockCounter"`, and no image or 3D asset requests are recorded.

- [ ] **Step 4: Commit**

```bash
git add frontend/playwright.config.ts frontend/tests/arena.spec.ts
git commit -m "test: cover primitive arena browser smoke"
```

## Task 9: Makefile And README Handoff

**Files:**
- Modify: `Makefile:1-35`
- Modify: `README.md:5-141`

- [ ] **Step 1: Update Makefile targets**

Modify `Makefile` so the first line and the new targets read:

```make
.PHONY: share share-linux serve serve-linux serve-frontend test test-frontend stop-funnel
```

Append after the existing `serve-linux` target:

```make
serve-frontend:
	npm --prefix frontend run dev

test-frontend:
	npm --prefix frontend run test
	npm --prefix frontend run build
```

- [ ] **Step 2: Update README run and structure sections**

In `README.md`, add this block after line 19:

````markdown
Para rodar o MVP 3D com React + Vite + PlayCanvas:

```bash
cd frontend
npm install
npm run dev
```

Ou pela raiz do repositorio:

```bash
make serve-frontend
```

O MVP 3D usa apenas primitivas do PlayCanvas para Cadete, Molock, plataforma, grid, luzes e efeitos. Ele nao depende de GLB, Mixamo, Blender, imagens de fundo ou downloads de assets 3D.
````

In the `## Testes` section, replace the existing command block with:

````markdown
```powershell
python -m unittest discover -s tests
```

```bash
npm --prefix frontend run test
npm --prefix frontend run build
```
````

In the `## Estrutura` code block, add:

```text
frontend/
frontend/src/arena/createArena.ts
frontend/src/arena/createCadet.ts
frontend/src/arena/createMolock.ts
frontend/src/arena/createEffects.ts
frontend/src/game/battleState.ts
```

- [ ] **Step 3: Verify Makefile commands and full frontend test path**

Run:

```bash
make -n serve-frontend
make -n test-frontend
npm --prefix frontend run test
npm --prefix frontend run build
```

Expected: dry-run Makefile output shows npm commands, Vitest tests PASS, and build completes.

- [ ] **Step 4: Commit**

```bash
git add Makefile README.md
git commit -m "docs: add primitive arena frontend commands"
```

## Final Verification

- [ ] Run Python tests from the repo root:

```bash
python -m unittest discover -s tests
```

Expected: existing Streamlit/Python tests PASS.

- [ ] Run frontend unit tests and build:

```bash
npm --prefix frontend run test
npm --prefix frontend run build
```

Expected: reducer, primitive contract, and UI tests PASS; Vite build completes.

- [ ] Run browser smoke test:

```bash
npm --prefix frontend run test:e2e
```

Expected: Playwright verifies visible canvas, correct attack cue, wrong counter cue, and no external image or 3D asset requests.

- [ ] Start the local frontend for manual review:

```bash
npm --prefix frontend run dev
```

Expected: Vite prints a local URL at `http://127.0.0.1:5173/`. In the browser, the Cadete is left/center, Molock is larger on the right, the platform/grid/background are visible, answer B triggers Cadete attack with cyan projectile and Molock hit flash, and answer A triggers Molock charge/counter pulse with camera shake.

## Self-Review

- Spec coverage: Cadete primitive humanoid, Molock primitive mechanical boss, industrial arena, abstract sci-fi background, cyan projectile, red counter pulse, idle/hit/attack/counter animations, no external assets, and GLB-replaceable logic are each mapped to tasks above.
- Placeholder scan: every code-writing step includes concrete file content or exact replacement snippets, and every command includes expected output.
- Type consistency: `CombatCue`, `CombatEvent`, actor interfaces, and blueprint names are defined once and used consistently across reducer, React wrapper, effects, and tests.
