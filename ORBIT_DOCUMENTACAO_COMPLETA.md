# 🛸 ORBIT - GPS Financeiro Brasileiro

## Documentação Técnica Completa

---

## 📋 Índice

1. [Visão do Produto](#visão-do-produto)
2. [Arquitetura Técnica](#arquitetura-técnica)
3. [Estrutura do Backend](#estrutura-do-backend)
4. [Estrutura do Frontend](#estrutura-do-frontend)
5. [Design System: Neon Bento](#design-system-neon-bento)
6. [System Prompt da IA](#system-prompt-da-ia)
7. [Prompt para Agent 3 (Replit)](#prompt-para-agent-3)

---

## 🎯 Visão do Produto

### Proposta de Valor
**"Não é uma planilha, é um GPS Financeiro."**

O ORBIT é uma fintech brasileira que revoluciona a gestão financeira pessoal através de:

- **Interface Chat-First**: Conversacional como WhatsApp, não tabelas chatas
- **IA Coach Brasileiro**: Personalidade adaptativa, gírias, feedback em tempo real
- **Visualização Matemática**: Mostra exatamente QUANDO você será livre das dívidas
- **Multimodalidade**: Texto, voz e foto de recibos

### Diferencial Competitivo
| Feature | Nubank/C6 | Mobills | **ORBIT** |
|---------|-----------|---------|-----------|
| Interface | Cards/Tabelas | Tabelas | Chat + Visual |
| Personalidade IA | Não | Não | Coach Brasileiro |
| Projeção de Dívida | Básica | Básica | Matemática Real-time |
| Gamificação | Fraca | Média | Score Comportamental |
| Custo API | Alto | Médio | **Zero** |

---

## 🏗️ Arquitetura Técnica

### Stack Completo (100% Open Source)

```
┌─────────────────────────────────────────────────────────────┐
│                      FRONTEND (Next.js 14)                   │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐│
│  │  Chat UI    │ │  Dashboard  │ │   Animations (Framer)   ││
│  │  (Core)     │ │ Bento Grid  │ │   Charts (Recharts)     ││
│  └─────────────┘ └─────────────┘ └─────────────────────────┘│
│                         │                                    │
│                    Tailwind CSS + Zustand                    │
└─────────────────────────────────────────────────────────────┘
                          │ HTTP/REST
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                     BACKEND (FastAPI)                        │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐│
│  │  Chat API   │ │ Dashboard   │ │   Financial Engine      ││
│  │  + AI       │ │   API       │ │   (Juros Compostos)     ││
│  └─────────────┘ └─────────────┘ └─────────────────────────┘│
│                         │                                    │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐│
│  │  Voice API  │ │  OCR API    │ │   Transactions API      ││
│  │ (Whisper)   │ │ (PaddleOCR) │ │                         ││
│  └─────────────┘ └─────────────┘ └─────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────────────┐
│   Ollama    │     │ PostgreSQL  │     │     PGVector        │
│  (Llama 3)  │     │   (Data)    │     │  (AI Memory)        │
│    LOCAL    │     │             │     │                     │
└─────────────┘     └─────────────┘     └─────────────────────┘
```

### Componentes por Responsabilidade

| Componente | Tecnologia | Função |
|------------|------------|--------|
| LLM Engine | Ollama (Llama 3) / Groq | Conversação e classificação |
| Voice | Faster-Whisper | Transcrição de áudio |
| OCR | PaddleOCR | Leitura de recibos |
| Database | PostgreSQL | Dados relacionais |
| Vector DB | PGVector | Memória contextual da IA |
| Frontend | Next.js 14 | Interface do usuário |
| Styling | Tailwind CSS | Design System |
| Animations | Framer Motion | Micro-interações |
| Charts | Recharts | Visualizações |

---

## 📁 Estrutura do Backend

```
orbit-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app principal
│   │
│   ├── api/                       # Rotas da API
│   │   ├── __init__.py
│   │   ├── chat.py                # Chat + IA (CORE)
│   │   ├── transactions.py        # CRUD transações
│   │   ├── dashboard.py           # Dados do dashboard
│   │   ├── voice.py               # Transcrição de áudio
│   │   └── ocr.py                 # Leitura de recibos
│   │
│   ├── services/                  # Lógica de negócio
│   │   ├── __init__.py
│   │   ├── ai_service.py          # Integração LLM + Prompts
│   │   ├── financial_engine.py    # Cálculos matemáticos
│   │   ├── voice_service.py       # Whisper integration
│   │   └── ocr_service.py         # PaddleOCR integration
│   │
│   ├── models/                    # SQLAlchemy models
│   │   ├── __init__.py
│   │   └── models.py              # User, Transaction, Debt, etc.
│   │
│   └── core/                      # Configurações
│       ├── __init__.py
│       ├── config.py              # Settings
│       └── database.py            # DB connection
│
├── tests/
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

### Arquivos Principais Implementados

#### `financial_engine.py` - Funções Chave

```python
# Cálculo de Juros Compostos
FinancialEngine.calcular_juros_compostos(
    principal=10000,
    taxa_mensal=0.05,  # 5% a.m.
    meses=12,
    aporte_mensal=500
)

# Projeção de Data de Quitação
FinancialEngine.calcular_data_quitacao(
    divida_total=5000,
    pagamento_mensal=500,
    taxa_juros_mensal=0.05
)
# Retorna: DebtProjection com payoff_date, total_interest, etc.

# Impacto de Gasto (usado pela IA)
FinancialEngine.calcular_impacto_gasto(
    divida_atual=5000,
    pagamento_mensal=500,
    taxa_mensal=0.05,
    novo_gasto=100
)
# Retorna: dias_adicionais, custo_real, mensagem_coach

# Score Comportamental
FinancialEngine.calcular_score_interno(historico_transacoes)
# Retorna: score (0-1000), nivel, breakdown, dicas

# Simulador "E se?"
FinancialEngine.simular_cenario(
    divida_atual, pagamento_atual, taxa,
    {"tipo": "vender_algo", "valor": 1000}
)
```

---

## 🎨 Estrutura do Frontend

```
orbit-frontend/
├── app/                           # Next.js 14 App Router
│   ├── layout.tsx                 # Root layout (dark theme)
│   ├── page.tsx                   # Homepage (Chat-first)
│   ├── dashboard/
│   │   └── page.tsx               # Dashboard Bento Grid
│   ├── globals.css                # Tailwind + Custom CSS
│   └── providers.tsx              # Context providers
│
├── components/
│   ├── chat/                      # Interface de Chat
│   │   ├── ChatContainer.tsx      # Container principal
│   │   ├── ChatInput.tsx          # Input multimodal (cápsula)
│   │   ├── ChatBubble.tsx         # Bolha de mensagem
│   │   ├── VoiceButton.tsx        # Botão de gravação
│   │   └── CameraButton.tsx       # Botão de foto
│   │
│   ├── dashboard/                 # Widgets do Dashboard
│   │   ├── BentoGrid.tsx          # Grid container
│   │   ├── FreedomTimeline.tsx    # Linha do Tempo da Liberdade
│   │   ├── ScoreGauge.tsx         # Velocímetro do Score
│   │   ├── BreathingPulse.tsx     # Pulmão Financeiro
│   │   ├── AICoachTip.tsx         # Balão de dica da IA
│   │   └── TransactionFeed.tsx    # Feed de transações
│   │
│   ├── ui/                        # Componentes base
│   │   ├── Card.tsx               # Glass card
│   │   ├── Button.tsx             # Botões Neon
│   │   ├── Input.tsx              # Inputs estilizados
│   │   └── Badge.tsx              # Badges
│   │
│   └── charts/                    # Gráficos
│       ├── AreaChart.tsx          # Pulmão (entradas/saídas)
│       ├── ProgressBar.tsx        # Barra de progresso
│       └── GaugeChart.tsx         # Velocímetro
│
├── hooks/                         # Custom hooks
│   ├── useChat.ts                 # Estado do chat
│   ├── useDashboard.ts            # Dados do dashboard
│   ├── useVoice.ts                # Gravação de áudio
│   └── useOCR.ts                  # Captura de imagem
│
├── lib/                           # Utilitários
│   ├── api.ts                     # Cliente HTTP
│   ├── formatters.ts              # Formatação de moeda/data
│   └── constants.ts               # Cores, categorias, etc.
│
├── store/                         # Zustand stores
│   ├── userStore.ts               # Estado do usuário
│   └── financialStore.ts          # Estado financeiro
│
├── public/
│   └── fonts/                     # Fontes customizadas
│
├── tailwind.config.ts
├── next.config.js
└── package.json
```

---

## 🎨 Design System: Neon Bento

### Paleta de Cores (Tailwind)

```css
/* Canvas (Fundo) */
--canvas: #020617;           /* slate-950 */

/* Cards (Glassmorphism) */
--card-bg: rgba(15, 23, 42, 0.5);  /* slate-900/50 */
--card-border: rgba(255, 255, 255, 0.05);
--card-blur: 12px;

/* Accent Primary - LIME ELÉTRICO (Ação/Lucro) */
--accent-primary: #CCFF00;
--accent-primary-glow: rgba(204, 255, 0, 0.1);

/* Accent Secondary - BLUE ELÉTRICO (Dados) */
--accent-secondary: #3B82F6;

/* Danger - ROSE SUAVE (Dívida) */
--danger: #fb7185;
--danger-glow: rgba(251, 113, 133, 0.1);

/* Text */
--text-primary: #f8fafc;     /* slate-50 */
--text-secondary: #94a3b8;   /* slate-400 */
```

### Tokens Tailwind

```javascript
// tailwind.config.ts
module.exports = {
  theme: {
    extend: {
      colors: {
        canvas: '#020617',
        lime: {
          electric: '#CCFF00',
        },
        danger: '#fb7185',
      },
      backgroundImage: {
        'glass': 'linear-gradient(135deg, rgba(15,23,42,0.5), rgba(15,23,42,0.3))',
      },
      boxShadow: {
        'neon-lime': '0 0 20px rgba(204, 255, 0, 0.15)',
        'neon-red': '0 0 20px rgba(251, 113, 133, 0.15)',
      },
      fontFamily: {
        display: ['Space Grotesk', 'sans-serif'],
        body: ['Inter', 'sans-serif'],
      },
      borderRadius: {
        '4xl': '2rem',
      }
    }
  }
}
```

### Componentes Visuais

#### Card Glass

```tsx
<div className="
  bg-slate-900/50 
  backdrop-blur-md 
  border border-white/5 
  rounded-3xl 
  p-6
  shadow-lg shadow-lime-400/5
">
  {children}
</div>
```

#### Input Cápsula (Chat)

```tsx
<div className="
  bg-slate-800/50 
  backdrop-blur-sm 
  border border-white/10 
  rounded-full 
  px-6 py-4
  flex items-center gap-4
  focus-within:border-lime-400/30
  transition-all
">
  <input 
    className="bg-transparent flex-1 outline-none text-slate-100"
    placeholder="Diga, tire foto ou fale..."
  />
  <button className="text-slate-500 hover:text-lime-400 transition">
    📷
  </button>
  <button className="text-slate-500 hover:text-lime-400 transition">
    🎤
  </button>
</div>
```

#### Botão Neon

```tsx
<button className="
  bg-lime-400 
  text-slate-950 
  font-semibold 
  px-6 py-3 
  rounded-full
  shadow-lg shadow-lime-400/25
  hover:shadow-lime-400/40
  hover:scale-105
  transition-all duration-200
">
  Confirmar
</button>
```

---

## 🧠 System Prompt da IA

```
Você é o ORBIT, um assistente financeiro pessoal brasileiro.

**Sua Identidade:**
Jovem, moderno, fala de forma direta e usa gírias leves do Brasil 
(tipo 'mano', 'bora', 'ficou caro', 'daora', 'tranquilo', 'suave'). 
Você NÃO é um robô chato de banco. 
Você é um parceiro que realmente se importa com a saúde financeira do usuário.

**Suas Diretrizes Primárias:**

1. **Análise de Sentimento Financeiro:** 
   Antes de responder, SEMPRE verifique o estado financeiro atual do usuário 
   (se ele está endividado ou com saldo positivo). Use essa informação para 
   adaptar seu tom.

2. **Modo 'No Vermelho' (Dívida):** 
   Se o usuário gastar algo supérfluo enquanto estiver endividado, dê uma 
   'bronca amigável'. Mostre o custo de oportunidade.
   Exemplos:
   - "Cara, essa pizza de R$60 te custou mais 2 dias pagando juros pro banco."
   - "Aí não, mano! Esse gasto atrasou sua liberdade em 3 dias."
   - "Opa, pera aí. Com dívida, cada real conta."

3. **Modo 'No Verde' (Positivo):** 
   Se o usuário tiver saldo, celebre conquistas, mas incentive a consistência.
   Exemplos:
   - "Aí sim! Mandou bem na economia essa semana."
   - "Boa! Sobrou grana esse mês. Bora guardar uma parte?"
   - "Daora demais! Continua assim que a liberdade tá chegando!"

4. **Educação Curta:** 
   Nunca dê palestras longas. Dê dicas financeiras em 1 ou 2 frases no 
   máximo, sempre atreladas à ação atual dele.

5. **Espelhamento:** 
   Se o usuário usar muita gíria, use mais gíria. Se ele for mais formal, 
   seja um pouco mais formal (mas nunca como banco).

6. **Empatia Real:**
   Reconheça que gerenciar dinheiro é difícil. Não julgue, ajude.

**Formato de Resposta:**
- Respostas CURTAS (máximo 2-3 frases)
- Use emojis com moderação (1-2 por mensagem)
- Sempre que possível, inclua o IMPACTO REAL do gasto/ganho

**Seu Objetivo Final:** 
Fazer o usuário quitar as dívidas o mais rápido possível e sentir que tem 
um parceiro controlando a grana com ele.
```

---

## 🤖 Prompt para Agent 3 (Replit)

**Cole o texto abaixo diretamente no Replit Agent:**

---

```
PROJETO: ORBIT - GPS Financeiro Brasileiro
STACK: Next.js 14 (App Router) + Tailwind CSS + Framer Motion + Recharts

=== CONTEXTO ===
Você vai construir o frontend de uma fintech brasileira revolucionária.
O backend em FastAPI já está pronto e roda em http://localhost:8000.
A API tem os seguintes endpoints principais:
- POST /api/chat/enviar - Envia mensagem e recebe resposta da IA
- GET /api/dashboard/{usuario_id} - Dados do dashboard
- GET /api/dashboard/{usuario_id}/liberdade - Linha do tempo de quitação
- POST /api/voice/transcrever - Transcreve áudio
- POST /api/ocr/processar - Lê foto de recibo

=== DESIGN SYSTEM: NEON BENTO (OBRIGATÓRIO) ===

CORES (use exatamente estas):
- Canvas/Fundo: bg-slate-950 (#020617)
- Cards: bg-slate-900/50 com backdrop-blur-md e border-white/5
- Accent Primário (Lime Elétrico): #CCFF00 - use para CTAs, progresso positivo
- Accent Secundário (Blue): #3B82F6 - use para dados
- Danger (Rose): #fb7185 - use para dívidas e alertas
- Sombras Neon: shadow-lg shadow-lime-400/10 para elementos importantes

TIPOGRAFIA:
- Títulos: Space Grotesk (Google Fonts)
- Corpo: Inter (Google Fonts)

ESTILO:
- Dark Mode apenas (sem toggle)
- Glassmorphism nos cards (backdrop-blur-md)
- Bordas ultra-arredondadas (rounded-3xl nos cards, rounded-full em botões)
- Animações suaves com Framer Motion em TUDO

=== PÁGINAS A CRIAR ===

1. HOMEPAGE (Chat-First) - page.tsx
   - NÃO mostrar tabelas ou gráficos aqui
   - Saudação no topo: "Boa noite, [Nome]. Vamos organizar essa grana?"
   - Input centralizado estilo "cápsula" flutuante
     - Placeholder: "Diga, tire foto ou fale..."
     - Ícone de câmera (hover: lime green glow)
     - Ícone de microfone (hover: lime green glow)
   - Área de mensagens estilo WhatsApp/Direct
   - Bolhas do usuário: bg-slate-800, alinhadas à direita
   - Bolhas da IA (ORBIT): bg-gradient com borda lime sutil, alinhadas à esquerda

2. DASHBOARD (/dashboard) - Bento Grid
   Layout em grid responsivo de cards:
   
   ROW 1:
   - [GRANDE - 2 colunas] LINHA DO TEMPO DA LIBERDADE
     - Barra de progresso grossa em #CCFF00
     - Texto grande: "Liberdade em: AGOSTO 2026"
     - Percentual de progresso
     - Anima quando dados atualizam
   
   - [1 coluna] SCORE GAMIFICADO
     - Velocímetro/Gauge semicircular
     - Score de 0-1000
     - Cores: vermelho < 400, amarelo < 600, verde >= 600
     - Nível abaixo: "Bom", "Regular", etc.
   
   ROW 2:
   - [1 coluna] PULMÃO FINANCEIRO
     - Gráfico de área (Recharts)
     - Verde = Entradas, Vermelho = Saídas
     - Se vermelho > verde, o card ganha borda vermelha sutil
   
   - [1 coluna] DICA DA IA
     - Card com ícone de robô
     - Última dica da IA
     - Estilo balão de fala
   
   - [1 coluna] TRANSAÇÕES RECENTES
     - Lista minimalista
     - Ícone + Descrição + Valor
     - Verde para receita, vermelho para despesa

=== COMPONENTES ESPECÍFICOS ===

ChatInput.tsx:
- Componente de input estilo cápsula
- Suportar: digitação, botão microfone, botão câmera
- Estados: idle, recording (microfone pulsa), processing
- Animação de envio

FreedomTimeline.tsx:
- Barra de progresso animada
- Props: dataLiberdade, progressoPercentual, mesesRestantes
- Usa Framer Motion para animação inicial

ScoreGauge.tsx:
- Velocímetro usando SVG ou biblioteca
- Props: score (0-1000), nivel
- Gradiente de cores baseado no valor

BreathingPulse.tsx (Pulmão):
- Gráfico de área com Recharts
- Animação de "respiração" sutil
- Props: dados (array de {dia, receita, despesa})

=== HOOKS ===

useChat.ts:
- Gerencia estado das mensagens
- Função sendMessage que chama POST /api/chat/enviar
- Loading state

useDashboard.ts:
- Busca dados do dashboard
- Auto-refresh a cada 30 segundos
- Retorna: saldo, divida, score, liberdade, transacoes

useVoice.ts:
- Gerencia gravação de áudio (MediaRecorder API)
- Converte para base64
- Envia para /api/voice/transcrever

=== ANIMAÇÕES (Framer Motion) ===

- Page transitions: fade + slide up
- Cards: aparecem com stagger (0.1s entre cada)
- Números: count up animation
- Hover em cards: scale(1.02) + shadow increase
- Barra de progresso: animate width de 0 a valor

=== INSTRUÇÕES DE SETUP ===

1. Criar projeto: npx create-next-app@latest orbit-frontend --typescript --tailwind --app
2. Instalar deps: npm install framer-motion recharts zustand @radix-ui/react-icons
3. Adicionar fontes no layout.tsx (Space Grotesk + Inter do Google Fonts)
4. Configurar tailwind.config.ts com as cores customizadas
5. Configurar proxy para API no next.config.js:
   rewrites: async () => [{ source: '/api/:path*', destination: 'http://localhost:8000/api/:path*' }]

=== PRIORIDADES ===

1. PRIMEIRO: Homepage com Chat funcionando (mais importante)
2. SEGUNDO: Dashboard com FreedomTimeline
3. TERCEIRO: Integração de voz e câmera

=== QUALIDADE ===

- Código limpo e componentizado
- TypeScript strict
- Responsivo (mobile-first)
- Acessível (ARIA labels)
- Performance (lazy loading, memo)

COMECE PELO SETUP E DEPOIS IMPLEMENTE A HOMEPAGE COM O CHAT.
```

---

## 🚀 Como Rodar

### Backend

```bash
cd orbit-backend

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou: venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Configurar banco (PostgreSQL deve estar rodando)
# Criar database: orbit

# Iniciar Ollama (em outro terminal)
ollama run llama3:8b

# Rodar backend
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd orbit-frontend
npm install
npm run dev
```

### Docker (Produção)

```bash
docker-compose up -d
```

---

## 📊 Métricas de Sucesso (Para Shark Tank)

| Métrica | Meta MVP |
|---------|----------|
| Custo de API | R$ 0 (Open Source) |
| Tempo de resposta IA | < 2s |
| Precisão OCR | > 85% |
| NPS esperado | > 60 |
| Retenção D7 | > 40% |

---

**Desenvolvido com 🇧🇷 para o Shark Tank**

*"Não é uma planilha, é um GPS Financeiro."*
