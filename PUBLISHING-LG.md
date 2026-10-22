# Publicar na LG Apps (a loja de apps das TVs LG webOS)

Análise de 21/10/2026, feita contra o estado atual deste fork (`com.fdimas.customwebos`).
Fontes externas citadas com data; o que não deu para verificar está no fim, na seção 8.

---

## 1. O veredito

**Dá para publicar na loja da LG — mas não como "tela inicial substituta".** O que a loja entrega
é um *app*; virar a home da TV não existe como possibilidade na plataforma webOS (não é política
da LG, é ausência de API). E o app publicado é outro produto: empacotado pela LG, assinado pelo
servidor dela e **cifrado em disco** (DRM com CEK por app) — nada que dependa de shell, ADB, SSH,
root ou auto-start passa por lá.

Então o caminho é: **reposicionar o app na LG como um "painel/central"** (relógio, clima, destaques,
atalhos, prateleira com um catálogo embutido) e publicar isso; manter o "substitui a home" só no
Android/Google TV, onde ele existe de verdade (`HomeMode`).

Três bloqueios mudam o projeto. O resto é papelada.

---

## 2. Os três bloqueios que mudam o projeto

### 2.1 Não existe como um app de terceiro virar a home da TV (webOS)

A LG diz isso abertamente, três vezes, no fórum de desenvolvedores:

- 22/05/2024 — *"Currently, there is **no API** provided to automatically launch an app when the TV is
  turned on. Only the user can launch the app."*
  <https://forum.webostv.developer.lge.com/t/embed-applications-that-have-been-developed-using-webos-tv-as-the-default-display/7275>
- 24/01/2025 → 03/02/2025 — pedido explícito de "set home screen to app": a LG **desvia para o
  atendimento ao cliente**, ou seja, a capacidade não existe.
  <https://forum.webostv.developer.lge.com/t/add-ability-to-set-home-screen-to-app-of-default-home-page/19246>
- 05/04/2026 (usuário no mesmo tópico) — *"For LG webOS TVs, **third-party applications cannot be set
  as the default home screen**."*
- 13/07/2023 — *"Currently, **no APIs to list all the installed apps** are provided."*
  <https://forum.webostv.developer.lge.com/t/socket-connection-to-lg-tv/3360>

A home do webOS é um app Flutter assinado e read-only. Consequência: **na loja, o app não substitui
a home e não "desliga" nada** — o que já é verdade no webOS desde sempre (o `HomeMode` do Android é
que troca a home; o build webOS nunca trocou).

**O que muda no projeto:** a promessa de venda na LG tem que ser outra. "Painel pessoal" / "Central"
em vez de "tela inicial". E o botão de voltar para a home da LG tem que existir dentro do app
(§4.6).

### 2.2 O pacote da loja é assinado e cifrado pela LG — não é o nosso `.ipk`

Fonte primária: a própria avaliação Common Criteria da LG,

- **KECS-CR-17-19 — Application Security Solution V1.0 for LG webOS TV** (19/04/2017)
  <http://www.commoncriteriaportal.org/files/epfiles/KECS-CR-17-19%20Application%20Security%20Solution%20V1.0%20for%20LG%20webOS%20TV(eng).pdf>

  > *"The digital signature generation process for the app takes place from the **LG App Store server
  > side**, and this enables only the apps that are downloaded from the LG App Store server to be
  > installable on the Smart TV."*

  > *"a **unique CEK (Contents Encryption Key) is generated for each app**… The app contents files are
  > **always stored being encrypted** in the app installation directory and are decrypted using CEK
  > **only when they are loaded in RAM**."*

- A **Privacy Guideline** da LG confirma o caminho: *"LG performs security reviews on submitted apps
  before distribution… the app package is digitally signed… If any problem is detected after the app
  distribution, distribution is suspended."*
  <https://webostv.developer.lge.com/develop/guides/privacy-guideline>

Erros da API que confirmam: **-301** "Failed to download RO", **-302** "Failed to check DRM",
**-303** "Failed to check App Signing".

**O que muda no projeto:** nada de shell/ADB/SSH/root/auto-start pode entrar no build de loja. O
`HomeMode` (que usa o ADB da própria TV) é **só Android** — e isso já é verdade no código
(`web/` nunca teve ADB). O build webOS da loja é essencialmente o que já temos, mais o que está
na seção 4.

Detalhe de caminhos que **vai** quebrar se não for ajustado — a LG documenta:

> *"The path to each asset should be specified relative to the index.html file… **not start with
> `/media/developer/`**. The latter may work in the Developer Mode app but will not when the app is
> released through LG Seller Lounge."*
> <https://webostv.developer.lge.com/develop/getting-started/app-resources>

O nosso já usa caminhos relativos (`config.js`, `icons/…`, `symbols/…`) — **ok**, mas precisa
continuar assim, e o `web/icons/` embutido é justamente o que salva a listagem (§4.5).

### 2.3 A listagem de apps da TV é negada — e na loja é negada por arquitetura

A API pública do webOS TV tem **dois métodos**: `launch` e `getAppLoadStatus` (webOS 4.0+).
<https://webostv.developer.lge.com/develop/references/application-manager>

`listLaunchPoints`, `listApps`, `getAppInfo`, `getForegroundAppInfo` **não são API pública** e são
negados a web apps — *"Denied method call \"listApps\" for category \"/\""* (23/07/2024)
<https://forum.webostv.developer.lge.com/t/denied-method-call-listapps-for-category/8572>

E a LG é mais dura com app de loja: *"App IDs are generally not disclosed to the public. You can use
the Application Manager API only for **your own apps or partner apps**."* (25/07/2024)
<https://forum.webostv.developer.lge.com/t/how-to-get-applist/8616>

**O que muda no projeto:** a "Todos os Apps" da loja tem que vir de um **catálogo embutido** no
pacote, filtrado por `getAppLoadStatus` (que é permitido). É exatamente o que o `webos-launcher`
faz (catálogo em `src/config/catalog.ts` + `public/icons/apps/`).

**O que já está feito aqui** é justamente isso: o `webos/sync_apps.py` coleta a lista real da TV e
o `tools/prepare_icons.py` tira o campo de cor de trás de cada logo. O `web/icons/` com 46 ícones é
o catálogo. Falta transformar isso em **repositório versionado do fork** (hoje está no `.gitignore`,
§4.5).

---

## 3. E o checklist de QA da LG — onde o nome "Custom webOS Home" morre

A LG publica um checklist de auto-avaliação (aba "Other Check Points") que pega o nome do projeto
diretamente:

| Item | Texto (traduzido) |
|---|---|
| 1 | "Palavras enganosas ou genéricas demais que possam ser mal interpretadas" |
| 3 | "Nomes ou descrições do app que violem marcas ou direitos autorais" |
| 4 | "Qualquer insinuação possível de enganar sobre quem é o Vendedor" |
| 13 | idem 4 |

<https://webostv.developer.lge.com/assets/checklist/documents_for_app_qa.zip> (baixado 21/10/2026)

**"Custom webOS Home" usa a marca da LG (`webOS`) e descreve uma tela inicial que imita a da LG.**
Para a loja, o nome tem que ser neutro (ex.: "Meu Painel", "Hub da TV"). O nome do fork pode
continuar "Custom webOS Home" no GitHub; o **nome publicado** é outro campo.

Outro item duro: **o idioma default tem que ser inglês** — *"The default language of globally
serviced apps must be English"* (checklist 15). pt-BR é obrigatório-se-quis, mas **sempre junto com
o inglês**, e com o inglês como default.

E não existe categoria "launcher" na LG Apps: só *game, entertainment, life, education, news-info*
(<https://webostv.developer.lge.com/distribute/app-ecosystem>). O app entraria como **"life"**.

---

## 4. As alterações no código

### 4.1 `webos/appinfo.json` — o arquivo que a LG lê de dentro do ipk

O Seller Lounge **extrai o `appinfo.json` de dentro do `.ipk`** e preenche o formulário a partir
dele. Campos que faltam hoje:

```jsonc
{
  "id": "com.fdimas.customwebos",     // definitivo: imutável depois de publicar (ver §5)
  "version": "1.0.0",                  // 3 inteiros, sem zero à esquerda
  "vendor": "…",                       // obrigatório: não pode sugerir que a LG é a vendedora
  "type": "web",
  "main": "index.html",
  "title": "…",                        // ≤ 20 caracteres (hoje: "Custom webOS Home" = 18 ✓)
  "appDescription": "…",               // ≤ 60 caracteres — FALTA
  "icon": "icon.png",                  // 80x80  ✓ já está
  "largeIcon": "largeIcon.png",        // 130x130 ✓ já está
  "iconColor": "#FF7A9E",              // tem que casar com o fundo do ícone, senão reprova
  "splashBackground": "splash.png",    // 1920x1080 PNG, obrigatório, não pode ser preto — FALTA
  "resolution": "1920x1080",           // webOS TV não suporta UHD para web apps
  "handlesRelaunch": true,
  "disableBackHistoryAPI": true,
  "requiredACG": [                     // FALTA — obrigatório a partir do webOS 27
    "application.launcher",            // launch
    "application.query",               // getAppLoadStatus
    "network.query", "time.query", "systemconfig.query"
  ]
}
```

Dois detalhes que a documentação oficial não deixa claros e que a gente descobriu na prática:

- **`requiredPermissions` é o mecanismo do webOS OSE, não do webOS TV.** No webOS TV o nome é
  **`requiredACG`**, e os grupos são `application.launcher` / `application.query` — não
  `applications.launcher` / `applications.query`.
  <https://webostv.developer.lge.com/develop/guides/acg-guide> (21/10/2026) e, para contraste,
  <https://www.webosose.org/docs/guides/development/configuration-files/appinfo-json/>
  O que está no `appinfo.json` hoje (`["applications", "applications.launcher", "applications.query"]`)
  é **inerte no webOS TV** — não é o que faz a LG liberar o `launch`.
- **A partir do webOS 27, `requiredACG` é obrigatório em todos os apps, mesmo vazio (`[]`)**, e é
  item de elegibilidade do Seller Lounge: sem ele o app **falha na validação e não pode ser
  submetido**.

### 4.2 `tools/make_art.py` — as imagens que a loja exige

O `mark()`/`banner()` de hoje geram o ícone 192x192 e o banner 640x360 (usados no Android). Para a
loja é preciso:

| Arquivo | Tamanho | Onde |
|---|---|---|
| `webos/icon.png` | 80x80 | já existe ✓ |
| `webos/largeIcon.png` | 130x130 | já existe ✓ |
| `webos/splash.png` | **1920x1080** | **novo** — obrigatório, não pode ser preto |
| ícone da listagem | **≥ 400x400**, quadrado, **cantos arredondados**, fundo transparente | upload separado no Seller Lounge (o `mark(512)` de hoje serve) |
| App Tile Color | HEX | tem que casar com o fundo do ícone |

E o `banner()` desenha o texto `"Free My TV"` (hoje `"Custom webOS Home"`) — precisa do **nome de
loja**, que é diferente do nome do fork.

### 4.3 `tools/webapp.py` — a chave do TMDB não pode ir no cliente

Hoje o `config.js` embarcado é:

```js
window.CONFIG = {"tmdbKey": "8ac14c1f92708a4a38638621b6a02ae1", …}
```

O checklist de privacidade/credenciais da LG diz: *"Avoid inserting privacy or credential
information directly into the source code"*, e a Privacy Guideline avisa que a LG faz *"security
reviews"* com *"vulnerability analyzing system"*.

Além do risco de reprovação, a chave está pública para qualquer um que baixe o app.

**Duas saídas:** (a) um proxy próprio com cache (recomendado se os destaques continuarem na loja);
(b) publicar sem chave → o app abre, mas sem "tendências" (só clima e atalhos). Isso exige uma
flag no build — algo como `--no-tmdb` / um `tmdb_key` vazio no `config.properties` do build de
loja. Hoje `web/data.js:190` já tolerate `CONFIG.tmdbKey` vazio (`(CONFIG.tmdbKey || '').trim()`) →
**o caminho (b) já funciona sem mexer em nada**; o que falta é o proxy (a) e a decisão.

### 4.4 `web/data.js` — os endereços que vão para a política de privacidade

O app fala com três serviços (e um CDN de imagem):

| Endpoint | Para quê | Precisa declarar? |
|---|---|---|
| `https://api.themoviedb.org/3` | destaques (tendências, lançamentos) | sim |
| `https://image.tmdb.org/t/p/` | pôsteres | sim (compartilhamento com a TMDB) |
| `https://api.open-meteo.com/v1/forecast` | clima | sim |
| `https://api.binance.com/api/v3/ticker/24hr` | preços de cripto (desligado no seu build: `show_crypto=false`) | se ligar |

E uma cláusula da Privacy Guideline que pega o projeto de frente:

> *"You must not integrate any third-party SDK, library, script, or service that uses an LG Smart TV
> device, the user's IP address, network connection, bandwidth, storage, or processing resources to
> provide proxy, residential proxy, web crawling, web scraping, web indexing, traffic routing, data
> collection, or similar services… This restriction applies even if the functionality is described
> as app monetization, **ad reduction**, rewards… This policy applies to all apps on the webOS
> platform, **including apps already published**. LG may review, request modification of, reject, or
> remove any app, and may **suspend the associated developer account**."*

Ou seja: **nenhuma função de bloquear/filtrar anúncio de terceiros.** No build webOS não existe
isso (o `DEBLOAT` do Android desliga apps de promoção da LG — é o Android, que vai para o Google
Play, não para a loja da LG). Mas o texto de marketing ("No ads", "ad-free") e qualquer promessa
semelhante no app da LG é alvo do revisor. As chamadas precisam ser **diretas** (fetch do app para a
API), sem proxy — que é o que já fazemos.

### 4.5 `web/icons/` + `webos/sync_apps.py` — o catálogo tem que virar repositório

Hoje `web/icons/` e `webos/apps.json` estão no `.gitignore` (são arte da TV, com marca de terceiros
— decisão certa para não publicar logotipos no GitHub). Mas **para publicar na loja o catálogo tem
que estar no pacote**. Duas saídas:

- **(a) Embutir os ícones no pacote, mas só os que a LG permite**: a LG proíbe "nomes ou descrições
  que violem marcas", não os ícones; o `webos-launcher` embarca ícones de terceiros e tem um
  `THIRD_PARTY_NOTICES.md` para isso. Ainda assim, publicar 46 logotipos no seu repositório é uma
  decisão de negócio sua, não técnica.
- **(b) Não embarcar ícones**: a prateleira da loja mostra só o **nome** (com a cor da marca), o que
  já é o fallback do app (`face()` → `word` quando o ícone não carrega). Menos bonito, zero risco
  jurídico.

O meio-termo: **embutir só os 7 da prateleira** (Netflix, YouTube, Prime, Disney+, Max, Apple TV,
Globoplay) e deixar o resto como nome. É o conjunto que o `home.js` já trata com gradiente de marca.

### 4.6 `web/home.js` — o Back e o "voltar para a home da LG"

O checklist de UX da LG exige:

> *"A click on the Back button on the entry page of the app must display the Home screen (webOS23 -
> webOS25 only)."*
> <https://webostv.developer.lge.com/develop/guides/back-button>

**Isso já está certo.** `web/home.js:713` → `back()` → quando não há sheet nem gaveta, chama
`TV.back()` → `web/tv.js:318` → `PalmSystem.platformBack()` → volta para a home da LG. ✓

Falta só o **botão explícito** de sair (o app é uma "central" dentro da loja, e o revisor vai
procurar a saída). Sugestão: uma entrada na gaveta, "Ir para a Início da TV", chamando o mesmo
`TV.back()`.

### 4.7 `web/tv.js` — `requiredACG` no lugar de `requiredPermissions`

Além do `appinfo.json` (§4.1), o `web/tv.js` não muda — as chamadas (`launch`,
`getAppLoadStatus`) já são as duas que o `public` group permite. O que muda é o **catálogo**: na
loja o `listLaunchPoints` **não vai funcionar** (negado a app de loja), então o caminho que
funciona é o `getAppLoadStatus` sobre o catálogo embutido — que é o fallback que o `web/tv.js` já
tem (`knownApps()`), **desde que o catálogo esteja no pacote** (§4.5).

---

## 5. O que é papelada (não é código)

Todo o resto do Seller Lounge:

| Item | Exigência |
|---|---|
| Conta | conta LG (a mesma do Developer). **Sem taxa** — não existe taxa de certificação na LG |
| Seller Lounge | 9 menus + UX Scenario (.ppt) + **Self Checklist 5.0** (104 itens) preenchido com resultado real — *"the app can be rejected without App QA"* |
| App ID | o `id` do `appinfo.json` **e** o campo App ID do Seller Lounge têm que bater — houve caso de **rejeição após 6 semanas** por divergência (28/09/2026) <https://forum.webostv.developer.lge.com/t/app-id-changed-during-submission-in-lg-seller-lounge/28435> |
| SDK Ver. | define **quais modelos** o app alcança. SDK 11.0.0 = webOS 26 (só TVs 2026!). 6.0.0 = webOS 6.0 (2021) é o piso prático. **A tabela oficial:** SDK 1.0.0=2014/webOS 1.0 … 3.0.0=2016/webOS 3.0 … 6.0.0=2021/webOS 6.0 … 11.0.0=2026/webOS 26 |
| Listagem | ícone ≥400x400, tile color, ≤6 screenshots (o 1º é o destaque), splash 1920x1080, título/descrição **por idioma com inglês como default**, categoria (*life*), tags, e-mail **e/ou** site |
| Privacidade | **URL de política de privacidade** + a política **dentro do app**, em todas as línguas; seção **Data Safety** obrigatória (dados, propósito, compartilhamento, país de armazenamento) |
| Classificação | **Brasil exige certificado** (LG's Assessment of Content Rating ou o do governo brasileiro) se Brazil estiver em Service Country Info; 18+ não pode ser vendido |
| Test Info | UX Scenario, Test IPK (≤3), conta de teste, **Geo-IP Block = N** (senão precisa liberar os IPs da LG QA — a lista está no FAQ), Billing = Not applicable, In-App Ad = Not applicable (+ `app-ads.txt` se houver) |
| QA | média de **2–3 semanas** (pode passar de 6). Cada atualização = novo ciclo |
| Publicação | no dia ou no dia seguinte à aprovação |

**Prazo total realista do primeiro deployment: 2 semanas de preparação + 2–3 semanas de QA ≈ 4–5
semanas**, com chance alta de pelo menos uma rodada de rejeição.

---

## 6. O que fazer AGORA para chegar em outras TVs LG (sem a loja)

A loja não é o único canal, e para o seu caso (pessoas com a TV na mão, willing to install) o
**Developer Mode já funciona** — é o que a gente usou. O que falta é transformar isso em
**produto**:

1. **Instalador de uma linha** — o `webos/install.py` já faz tudo; falta um wrapper para leigo:
   - **[Nuvio WebTV Installer](https://github.com/NuvioMedia/NuvioWebTVInstaller)** — app desktop
     (Windows/macOS/Linux) que instala em **webOS 5+** usando as ferramentas oficiais da LG
     (`ares-setup-device`, `ares-novacom --getkey`, `ares-install`). É o "TizenBrew Installer para LG"
     (o TizenBrew é **só Samsung** — confirmado no README dele).
   - Alternativa: **webOS Dev Manager** (arrastar e soltar o `.ipk`).
2. **Documentar o custo real do Developer Mode** (é o que assusta o cliente):
   - sessão de **1000 horas (~41,6 dias)**; quando expira, **os apps instalados são desinstalados**;
   - **1 conta LG = 1 TV por vez** → cada cliente cria a conta dele;
   - a TV reinicia ao ativar; aparece a passphrase de 6 caracteres e o prompt de pareamento SSAP.
   <https://www.webosbrew.org/devmode/> e <https://webostv.developer.lge.com/develop/getting-started/developer-mode-app>
3. **Aviso de segurança** — duas cadeias de root pré-autenticação em webOS foram publicadas em
   2025/2026 (porta 3001, `pmlogd`). Ligar Dev Mode numa TV de cliente aumenta a superfície:
   <https://thehackernews.com/2026/10/lg-smart-tvs-vulnerable-to-pre-auth.html> e
   <https://ssd-disclosure.com/lg-webos-tv-path-traversal-authentication-bypass-and-full-device-takeover/>
4. **Se quiser o HOME de verdade**: root + **Homebrew Channel** (categoria `launcher` oficial lá)
   + **LG Input Hook** para remapear o botão. O root é por firmware e a maioria dos exploits já foi
   corrigida — "root disponível" é propriedade de **modelo + firmware exatos**, não do modelo.
   <https://cani.rootmy.tv/> e <https://www.webosbrew.org/rooting/>

---

## 7. O teste de 1 hora que pode mudar a estratégia

O único trabalho público que mediu isso (Glasshouse, outubro/2026, em OLED55G36LA e **G5**) achou
um caminho que **não precisa de root**:

> Em webOS 10.3.1 (G5): *"LG's Home's `appinfo.json` declares `"appCategory": ["home"]`… A web app
> mounted under the same id **without** it gets 'no default app is set for the category', whatever
> `defaultApps.home` names, and the Home button does nothing. **With the field, Home from live TV
> had the app on screen 0.09 s after the press.**"*
> <https://rorygallagher2024.github.io/glasshouse/development/TV-RESEARCH/>

Ou seja: **declarar `"appCategory": ["home"]` no `appinfo.json`** pode fazer o app ser aceito como
`defaultApps.home` — o botão HOME abriria ele, **sem root**.

Ressalvas honestas: foi medido por **sideload** (não pela loja), em webOS 9.2.2 e 10.3.1 — **não
em webOS 26/11** (o firmware da sua G5), e `defaultApps.home` **é apagado a cada reboot** (o takeover
do botão funciona; "ligar a TV já no launcher" não persiste sem hook de boot).

**O teste:** adicionar `"appCategory": ["home"]` no `webos/appinfo.json`, `python3 webos/build.py`,
instalar, e apertar HOME na TV. Custa 10 minutos e decide se o produto é "app na loja" ou
"launcher de verdade".

---

## 8. O que não deu para verificar

1. **Não existe texto público que proíba launcher na LG Apps.** A negativa aqui é **técnica** (não
   há API) + **de guideline** (checklist 1/3/4/13) + **precedente negativo**: em 2026 existem
   pelo menos três projetos iguais ao deste — `partridgeworks/webos-launcher` (23/09/2026),
   `zzeppieri/webos-custom-home`, `ammar027/lumen-webos` — e **nenhum foi para a loja**, todos
   sideload/homebrew. *Ausência de evidência não é prova de banimento.*
2. **Se o Seller Lounge aceita um `.ipk` montado à mão** (o nosso) — a doc diz que ele lê o
   `appinfo.json` de dentro do ipk, mas não achei texto explícito. Mitigação: gerar com o
   `ares-package` (`npm i -g @webos-tools/cli`), que é o mesmo formato e custa zero.
3. **`closedApp` e `webOS-Packager-Version`** — não aparecem na documentação do webOS TV nem na
   referência do webosbrew. O mecanismo equivalente e documentado é o App DRM/CEK (§2.2). Se você
   achou esses nomes em binário de firmware ou post antigo, **trate como não confirmado**.
4. **Se o `appCategory: ["home"]` funciona em webOS 26/11** e se funciona para app **da loja**
   (o Glasshouse só testou sideload).
5. **Se o Seller Lounge deixa rebaixar manualmente o SDK Ver.** para 6.0.0 (a doc diz que ele
   "auto-configura" ao escolher a plataforma). **É a pergunta que mais vale a pena fazer ao
   Seller Lounge antes de submeter** — é ela que decide o alcance do app.
6. **O SLA de aprovação** — não publicado; os "1–3 semanas" são relatos de terceiros.
7. **Se a LG já rejeitou publicamente um app por "ser launcher"** — nenhum caso documentado.
8. **A política de marca "webOS"** para uso por terceiros no nome de um app — não há página pública
   de trademark; a conclusão sobre o nome (§3) se apoia no checklist de QA, não em política de marca.
9. **O campo de "vídeo de promo"** — não encontrei nas guias do Seller Lounge; pode existir no
   formulário sem estar documentado.

---

## 9. Resumo em uma página

| | |
|---|---|
| **Publicar na loja da LG?** | Dá — como **app utilitário** ("painel/central"), não como home |
| **Custo** | R$ 0 (sem taxa de certificação na LG) |
| **Prazo** | 2 semanas de preparo + 2–3 semanas de QA + rodadas de correção |
| **Mudanças de código** | §4 (appinfo, splash, ACG, chave TMDB, catálogo, botão de sair) |
| **Papelada** | §5 (9 menus, UX Scenario, Self Checklist, política de privacidade, rating BR) |
| **O que não dá** | virar a home, listar apps da TV em runtime, usar ADB/root, auto-start |
| **O que dá, e é o canal real hoje** | Developer Mode + instalador desktop (§6) |
| **O teste de 10 min** | `"appCategory": ["home"]` na sua G5 (§7) |
