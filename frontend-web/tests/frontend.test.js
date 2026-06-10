import test from 'node:test';
import assert from 'node:assert';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const BASE_DIR = path.resolve(__dirname, '..');

test('Verifica se a pasta dist foi criada no build', () => {
  const distExists = fs.existsSync(path.join(BASE_DIR, 'dist'));
  assert.strictEqual(distExists, true, 'A pasta dist/ de build de produção deve existir. Certifique-se de rodar o npm run build.');
});

test('Verifica se o index.html gerado é válido', () => {
  const htmlPath = path.join(BASE_DIR, 'dist', 'index.html');
  const htmlContent = fs.readFileSync(htmlPath, 'utf8');
  
  assert.match(htmlContent, /<div id="root"><\/div>/i, 'O index.html do build deve conter a tag root do React.');
  assert.match(htmlContent, /CardioIA/i, 'O título da página no index.html do build deve conter CardioIA.');
});

test('Verifica integridade do vercel.json para SPA', () => {
  const vercelPath = path.join(BASE_DIR, 'vercel.json');
  assert.strictEqual(fs.existsSync(vercelPath), true, 'O arquivo vercel.json deve existir.');
  
  const vercelConfig = JSON.parse(fs.readFileSync(vercelPath, 'utf8'));
  assert.ok(vercelConfig.rewrites, 'O vercel.json deve conter as regras de rewrites.');
  assert.strictEqual(vercelConfig.rewrites[0].destination, '/index.html', 'O rewrite da Vercel deve redirecionar para /index.html.');
});

test('Verifica se o código fonte React está integrado com endpoints de API', () => {
  const appJsxPath = path.join(BASE_DIR, 'src', 'App.jsx');
  const appJsxContent = fs.readFileSync(appJsxPath, 'utf8');
  
  assert.match(appJsxContent, /api\/telemetry\/latest/i, 'O App.jsx deve fazer chamadas ao endpoint de telemetria mais recente.');
  assert.match(appJsxContent, /api\/predict/i, 'O App.jsx deve fazer chamadas ao endpoint de predição.');
  assert.match(appJsxContent, /api\/analyze/i, 'O App.jsx deve fazer chamadas ao endpoint de análise dos agentes.');
});
