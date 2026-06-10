import test from 'node:test';
import assert from 'node:assert';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const BASE_DIR = path.resolve(__dirname, '..');

test('Verifica se as configurações do Expo em app.json são válidas para Android', () => {
  const appJsonPath = path.join(BASE_DIR, 'app.json');
  assert.strictEqual(fs.existsSync(appJsonPath), true, 'O arquivo app.json deve existir.');
  
  const appConfig = JSON.parse(fs.readFileSync(appJsonPath, 'utf8'));
  assert.ok(appConfig.expo, 'O app.json deve conter o objeto expo.');
  assert.strictEqual(appConfig.expo.name, 'CardioIA', 'O nome do app em app.json deve ser CardioIA.');
  assert.strictEqual(appConfig.expo.slug, 'cardioia-mobile', 'O slug do app em app.json deve ser cardioia-mobile.');
  
  assert.ok(appConfig.expo.android, 'O objeto android deve estar configurado.');
  assert.strictEqual(
    appConfig.expo.android.package, 
    'br.com.fiap.cardioia', 
    'O android package de domínio invertido deve ser br.com.fiap.cardioia para a publicação na Google Play.'
  );
});

test('Verifica se o perfil de build preview em eas.json está configurado para APK', () => {
  const easJsonPath = path.join(BASE_DIR, 'eas.json');
  assert.strictEqual(fs.existsSync(easJsonPath), true, 'O arquivo eas.json deve existir.');
  
  const easConfig = JSON.parse(fs.readFileSync(easJsonPath, 'utf8'));
  assert.ok(easConfig.build, 'O eas.json deve conter as regras de build.');
  assert.ok(easConfig.build.preview, 'O perfil preview de build deve estar configurado.');
  assert.strictEqual(
    easConfig.build.preview.android.buildType, 
    'apk', 
    'O buildType do perfil preview no android deve ser apk para permitir instalar o app diretamente.'
  );
});

test('Verifica integridade física dos assets e imagens de publicação', () => {
  const assetsDir = path.join(BASE_DIR, 'assets');
  assert.strictEqual(fs.existsSync(assetsDir), true, 'A pasta assets/ deve existir.');
  
  const requiredImages = ['icon.png', 'splash.png', 'adaptive-icon.png', 'favicon.png'];
  requiredImages.forEach(img => {
    const imgPath = path.join(assetsDir, img);
    assert.strictEqual(fs.existsSync(imgPath), true, `A imagem asset ${img} deve estar presente.`);
    const stats = fs.statSync(imgPath);
    assert.ok(stats.size > 0, `O arquivo de imagem ${img} não deve estar vazio.`);
  });
});

test('Verifica se o aplicativo mobile está integrado com a API do backend CardioIA', () => {
  const appJsPath = path.join(BASE_DIR, 'App.js');
  assert.strictEqual(fs.existsSync(appJsPath), true, 'O arquivo App.js do app mobile deve existir.');
  
  const appContent = fs.readFileSync(appJsPath, 'utf8');
  assert.match(appContent, /api\/telemetry\/latest/i, 'O App.js do mobile deve consultar a telemetria.');
  assert.match(appContent, /api\/predict/i, 'O App.js do mobile deve consultar a rota de predição ML.');
  assert.match(appContent, /api\/analyze/i, 'O App.js do mobile deve consultar a rota de análise dos agentes.');
});
