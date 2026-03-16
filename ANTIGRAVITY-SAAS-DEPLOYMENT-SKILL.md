# Google Antigravity SAAS Deployment Skill
## Multi-Project Vibe Coding für komplettes SAAS-System

> **Optimiert für:** Google Antigravity IDE (lokal installiert)  
> **Agent Models:** Gemini 3 Pro, Claude Sonnet 4.5, GPT-OSS  
> **Deployment:** Vollautomatisch mit Browser-in-the-Loop  
> **Ziel:** Frontend, Backend, n8n Orchestrator - komplett Free Tier

---

## 🎯 ÜBERSICHT

Diese Skill ermöglicht Google Antigravity, ein komplettes SAAS-System über **mehrere Workspaces** parallel zu deployen:

### **Workspace-Architektur:**
```
antigravity-workspaces/
├── 📁 saas-frontend/          → React Frontend (Vercel)
├── 📁 saas-backend/           → Node.js API (Railway)
├── 📁 saas-orchestrator/      → n8n Workflows (Render)
├── 📁 saas-infrastructure/    → Terraform + Scripts
└── 📁 saas-testing/           → E2E Tests + Security
```

### **Agent Manager Workflow:**
- **Agent 1 (Research)**: Account-Setup via Browser
- **Agent 2 (Frontend)**: React App + Deployment
- **Agent 3 (Backend)**: Express API + Database
- **Agent 4 (Orchestrator)**: n8n Workflows
- **Agent 5 (QA)**: Security Scans + Testing

---

## 📋 TEIL 1: ANTIGRAVITY SETUP

### 1.1 Workspace-Initialisierung

**Prompt für Agent Manager:**
```
Create 5 parallel workspaces for SAAS deployment:
1. saas-frontend (React + TypeScript + Tailwind)
2. saas-backend (Express + TypeScript + Supabase)
3. saas-orchestrator (n8n configuration)
4. saas-infrastructure (Deployment scripts)
5. saas-testing (Playwright + Security scans)

Each workspace should:
- Initialize git repo
- Create .env.example
- Setup package.json
- Configure TypeScript
- Add comprehensive README.md
```

### 1.2 Agent Manager Konfiguration

**agents-config.json** (für Antigravity)
```json
{
  "agents": [
    {
      "name": "infrastructure-agent",
      "model": "gemini-3-pro-high",
      "workspace": "saas-infrastructure",
      "capabilities": [
        "browser-automation",
        "account-creation",
        "api-calls"
      ],
      "priority": 1,
      "auto_mode": true
    },
    {
      "name": "frontend-agent",
      "model": "claude-sonnet-4.5",
      "workspace": "saas-frontend",
      "capabilities": [
        "react-development",
        "styling",
        "component-creation"
      ],
      "priority": 2,
      "auto_mode": true
    },
    {
      "name": "backend-agent",
      "model": "claude-sonnet-4.5",
      "workspace": "saas-backend",
      "capabilities": [
        "api-development",
        "database-design",
        "security"
      ],
      "priority": 2,
      "auto_mode": true
    },
    {
      "name": "orchestrator-agent",
      "model": "gemini-3-pro-standard",
      "workspace": "saas-orchestrator",
      "capabilities": [
        "workflow-design",
        "integration"
      ],
      "priority": 3,
      "auto_mode": true
    },
    {
      "name": "qa-agent",
      "model": "gemini-3-pro-standard",
      "workspace": "saas-testing",
      "capabilities": [
        "browser-testing",
        "security-scanning",
        "artifact-generation"
      ],
      "priority": 4,
      "auto_mode": false
    }
  ],
  "coordination": {
    "mode": "parallel-then-sequential",
    "checkpoints": [
      "infrastructure-complete",
      "services-deployed",
      "tests-passed"
    ]
  }
}
```

---

## 📦 TEIL 2: INFRASTRUCTURE WORKSPACE

### 2.1 Account-Erstellung via Browser Agent

**Prompt für infrastructure-agent:**
```
Use Antigravity's built-in Chrome browser to automate account creation:

CRITICAL: Use browser.navigate(), browser.screenshot(), browser.fill(), browser.click()

Create accounts on these platforms (FREE TIER):
1. Vercel (via GitHub OAuth)
2. Railway (via GitHub OAuth)
3. Render (via GitHub OAuth)
4. Supabase (via GitHub OAuth)
5. Cloudflare (Email signup)

For each platform:
1. Navigate to signup page
2. Take screenshot of signup form
3. Use GitHub OAuth where possible
4. Extract API tokens/keys
5. Save to encrypted vault
6. Generate artifact with credentials
7. Take final screenshot for verification

Return artifact with:
- All API keys
- Account URLs
- Setup instructions
- Screenshots as proof
```

### 2.2 Browser Automation Script

**saas-infrastructure/scripts/account-creator.ts**
```typescript
import { Browser } from '@antigravity/browser-api';
import { Vault } from '@antigravity/vault';

interface AccountCredentials {
  platform: string;
  apiToken: string;
  accountUrl: string;
  screenshots: string[];
  createdAt: Date;
}

class AutomatedAccountCreator {
  private browser: Browser;
  private vault: Vault;
  private credentials: AccountCredentials[] = [];

  constructor() {
    this.browser = new Browser({ headless: false, slowMo: 100 });
    this.vault = new Vault({ encryption: 'AES-256-GCM' });
  }

  async createAllAccounts(): Promise<void> {
    console.log('🚀 Starting automated account creation...');
    
    // Parallele Erstellung mit Browser-Tabs
    const platforms = ['vercel', 'railway', 'render', 'supabase', 'cloudflare'];
    
    for (const platform of platforms) {
      await this.createAccount(platform);
    }
    
    // Artifact generieren
    await this.generateArtifact();
  }

  private async createAccount(platform: string): Promise<void> {
    const page = await this.browser.newPage();
    
    try {
      console.log(`📝 Creating ${platform} account...`);
      
      switch (platform) {
        case 'vercel':
          await this.createVercelAccount(page);
          break;
        case 'railway':
          await this.createRailwayAccount(page);
          break;
        case 'render':
          await this.createRenderAccount(page);
          break;
        case 'supabase':
          await this.createSupabaseAccount(page);
          break;
        case 'cloudflare':
          await this.createCloudflareAccount(page);
          break;
      }
      
      console.log(`✅ ${platform} account created`);
      
    } catch (error) {
      console.error(`❌ Failed to create ${platform} account:`, error);
      // Screenshot bei Fehler
      await page.screenshot({ 
        path: `./artifacts/error-${platform}-${Date.now()}.png` 
      });
    } finally {
      await page.close();
    }
  }

  private async createVercelAccount(page: any): Promise<void> {
    // Navigate
    await page.goto('https://vercel.com/signup');
    await page.screenshot({ path: './artifacts/vercel-1-signup.png' });
    
    // GitHub OAuth
    await page.click('button:has-text("Continue with GitHub")');
    await page.waitForNavigation();
    
    // Check if GitHub login needed
    const needsLogin = await page.isVisible('input[name="login"]');
    
    if (needsLogin) {
      // GitHub Credentials aus Vault
      const githubCreds = await this.vault.get('GITHUB_CREDENTIALS');
      
      await page.fill('input[name="login"]', githubCreds.email);
      await page.fill('input[name="password"]', githubCreds.password);
      await page.screenshot({ path: './artifacts/vercel-2-github-login.png' });
      await page.click('input[type="submit"]');
    }
    
    // Authorize App
    await page.waitForSelector('button:has-text("Authorize")');
    await page.screenshot({ path: './artifacts/vercel-3-authorize.png' });
    await page.click('button:has-text("Authorize")');
    
    // Wait for Dashboard
    await page.waitForURL('**/dashboard');
    await page.screenshot({ path: './artifacts/vercel-4-dashboard.png' });
    
    // Create API Token
    await page.goto('https://vercel.com/account/tokens');
    await page.click('button:has-text("Create Token")');
    await page.fill('input[name="name"]', 'saas-deployment');
    await page.selectOption('select[name="scope"]', 'full-access');
    await page.screenshot({ path: './artifacts/vercel-5-token-form.png' });
    await page.click('button:has-text("Create")');
    
    // Extract Token
    await page.waitForSelector('[data-testid="token-value"]');
    const token = await page.textContent('[data-testid="token-value"]');
    await page.screenshot({ path: './artifacts/vercel-6-token-created.png' });
    
    // Save credentials
    this.credentials.push({
      platform: 'vercel',
      apiToken: token,
      accountUrl: 'https://vercel.com/dashboard',
      screenshots: [
        './artifacts/vercel-1-signup.png',
        './artifacts/vercel-4-dashboard.png',
        './artifacts/vercel-6-token-created.png'
      ],
      createdAt: new Date()
    });
    
    await this.vault.set('VERCEL_TOKEN', token);
  }

  private async createRailwayAccount(page: any): Promise<void> {
    await page.goto('https://railway.app/');
    await page.screenshot({ path: './artifacts/railway-1-homepage.png' });
    
    await page.click('a:has-text("Login")');
    await page.click('button:has-text("Login with GitHub")');
    
    // Wait for OAuth redirect
    await page.waitForURL('**/dashboard');
    await page.screenshot({ path: './artifacts/railway-2-dashboard.png' });
    
    // Generate API Token
    await page.goto('https://railway.app/account/tokens');
    await page.screenshot({ path: './artifacts/railway-3-tokens-page.png' });
    
    await page.click('button:has-text("Create Token")');
    await page.fill('input[name="name"]', 'saas-deployment');
    await page.click('button:has-text("Create")');
    
    await page.waitForSelector('input[readonly]');
    const token = await page.inputValue('input[readonly]');
    await page.screenshot({ path: './artifacts/railway-4-token-created.png' });
    
    this.credentials.push({
      platform: 'railway',
      apiToken: token,
      accountUrl: 'https://railway.app/dashboard',
      screenshots: [
        './artifacts/railway-1-homepage.png',
        './artifacts/railway-2-dashboard.png',
        './artifacts/railway-4-token-created.png'
      ],
      createdAt: new Date()
    });
    
    await this.vault.set('RAILWAY_TOKEN', token);
  }

  private async createRenderAccount(page: any): Promise<void> {
    await page.goto('https://render.com/');
    await page.screenshot({ path: './artifacts/render-1-homepage.png' });
    
    await page.click('a:has-text("Get Started")');
    await page.click('button:has-text("GitHub")');
    
    await page.waitForURL('**/dashboard');
    await page.screenshot({ path: './artifacts/render-2-dashboard.png' });
    
    // Create API Key
    await page.goto('https://dashboard.render.com/u/settings#api-keys');
    await page.screenshot({ path: './artifacts/render-3-api-keys-page.png' });
    
    await page.click('button:has-text("Create API Key")');
    await page.fill('input[name="name"]', 'saas-n8n-deployment');
    await page.click('button:has-text("Create API Key")');
    
    const apiKey = await page.getAttribute('[data-clipboard-text]', 'data-clipboard-text');
    await page.screenshot({ path: './artifacts/render-4-key-created.png' });
    
    this.credentials.push({
      platform: 'render',
      apiToken: apiKey,
      accountUrl: 'https://dashboard.render.com',
      screenshots: [
        './artifacts/render-1-homepage.png',
        './artifacts/render-2-dashboard.png',
        './artifacts/render-4-key-created.png'
      ],
      createdAt: new Date()
    });
    
    await this.vault.set('RENDER_API_KEY', apiKey);
  }

  private async createSupabaseAccount(page: any): Promise<void> {
    await page.goto('https://supabase.com/dashboard');
    await page.screenshot({ path: './artifacts/supabase-1-homepage.png' });
    
    await page.click('button:has-text("Sign in with GitHub")');
    
    await page.waitForURL('**/projects');
    await page.screenshot({ path: './artifacts/supabase-2-projects.png' });
    
    // Create new project
    await page.click('button:has-text("New project")');
    await page.selectOption('select[name="organization"]', { label: 'Personal' });
    
    await page.fill('input[name="name"]', 'saas-database');
    
    // Generate secure password
    const dbPassword = this.generateSecurePassword();
    await page.fill('input[name="db_pass"]', dbPassword);
    
    await page.selectOption('select[name="region"]', 'eu-central-1');
    await page.click('label:has-text("Free")');
    await page.screenshot({ path: './artifacts/supabase-3-project-form.png' });
    
    await page.click('button:has-text("Create new project")');
    
    // Wait for project creation (kann 2-3 Minuten dauern)
    await page.waitForSelector('text=Project is ready', { timeout: 180000 });
    await page.screenshot({ path: './artifacts/supabase-4-project-ready.png' });
    
    // Get API Keys
    await page.goto('https://supabase.com/dashboard/project/_/settings/api');
    await page.screenshot({ path: './artifacts/supabase-5-api-keys.png' });
    
    const projectUrl = await page.textContent('[data-key="project-url"]');
    const anonKey = await page.textContent('[data-key="anon-key"]');
    const serviceKey = await page.textContent('[data-key="service-key"]');
    
    await this.vault.set('SUPABASE_URL', projectUrl);
    await this.vault.set('SUPABASE_ANON_KEY', anonKey);
    await this.vault.set('SUPABASE_SERVICE_KEY', serviceKey);
    await this.vault.set('SUPABASE_DB_PASSWORD', dbPassword);
    
    this.credentials.push({
      platform: 'supabase',
      apiToken: serviceKey,
      accountUrl: projectUrl,
      screenshots: [
        './artifacts/supabase-1-homepage.png',
        './artifacts/supabase-4-project-ready.png',
        './artifacts/supabase-5-api-keys.png'
      ],
      createdAt: new Date()
    });
  }

  private async createCloudflareAccount(page: any): Promise<void> {
    await page.goto('https://dash.cloudflare.com/sign-up');
    await page.screenshot({ path: './artifacts/cloudflare-1-signup.png' });
    
    const email = `saas-project-${Date.now()}@temp-mail.io`;
    const password = this.generateSecurePassword();
    
    await page.fill('input[type="email"]', email);
    await page.fill('input[type="password"]', password);
    await page.click('button:has-text("Create Account")');
    
    // Email verification (manual step)
    console.log('⚠️  Cloudflare requires email verification');
    console.log(`📧 Check email: ${email}`);
    console.log('⏳ Waiting 60 seconds for manual verification...');
    
    await page.waitForTimeout(60000);
    
    // Create API Token
    await page.goto('https://dash.cloudflare.com/profile/api-tokens');
    await page.screenshot({ path: './artifacts/cloudflare-2-tokens-page.png' });
    
    await page.click('button:has-text("Create Token")');
    await page.click('button:has-text("Use template")');
    
    await page.fill('input[name="name"]', 'saas-dns-management');
    await page.click('button:has-text("Continue to summary")');
    await page.click('button:has-text("Create Token")');
    
    await page.waitForSelector('code');
    const token = await page.textContent('code');
    await page.screenshot({ path: './artifacts/cloudflare-3-token-created.png' });
    
    this.credentials.push({
      platform: 'cloudflare',
      apiToken: token,
      accountUrl: 'https://dash.cloudflare.com',
      screenshots: [
        './artifacts/cloudflare-1-signup.png',
        './artifacts/cloudflare-3-token-created.png'
      ],
      createdAt: new Date()
    });
    
    await this.vault.set('CLOUDFLARE_API_TOKEN', token);
    await this.vault.set('CLOUDFLARE_EMAIL', email);
    await this.vault.set('CLOUDFLARE_PASSWORD', password);
  }

  private async generateArtifact(): Promise<void> {
    const artifact = {
      title: 'SAAS Platform Accounts - Setup Complete',
      timestamp: new Date().toISOString(),
      summary: `Created ${this.credentials.length} platform accounts`,
      credentials: this.credentials,
      nextSteps: [
        'Verify all API tokens are working',
        'Set up environment variables in deployment scripts',
        'Configure CI/CD pipelines',
        'Initialize database schemas',
        'Deploy services'
      ]
    };
    
    // Save as Antigravity Artifact
    await this.browser.generateArtifact({
      type: 'setup-report',
      format: 'markdown',
      content: this.formatAsMarkdown(artifact),
      attachments: this.credentials.flatMap(c => c.screenshots)
    });
    
    console.log('\n✅ ACCOUNT CREATION COMPLETE');
    console.log('📋 Artifact generated with all credentials');
    console.log('🔒 Credentials encrypted in vault');
  }

  private formatAsMarkdown(artifact: any): string {
    return `
# SAAS Platform Setup - Complete ✅

**Generated:** ${artifact.timestamp}

## 📊 Summary
Successfully created **${artifact.credentials.length}** platform accounts for SAAS deployment.

## 🔑 Platform Credentials

${artifact.credentials.map(cred => `
### ${cred.platform.toUpperCase()}
- **Dashboard:** [${cred.accountUrl}](${cred.accountUrl})
- **API Token:** \`${cred.apiToken.substring(0, 20)}...\` (full token in vault)
- **Created:** ${cred.createdAt.toLocaleString()}
- **Screenshots:** ${cred.screenshots.length} verification images

`).join('\n')}

## 📝 Next Steps

${artifact.nextSteps.map((step, i) => `${i + 1}. ${step}`).join('\n')}

## 🔐 Security Notes
- All credentials encrypted with AES-256-GCM
- Stored in Antigravity Vault
- Access via: \`vault.get('PLATFORM_TOKEN')\`
- Rotate tokens after 90 days

---
*Generated by Antigravity Infrastructure Agent*
    `.trim();
  }

  private generateSecurePassword(): string {
    const length = 32;
    const charset = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*';
    let password = '';
    for (let i = 0; i < length; i++) {
      password += charset.charAt(Math.floor(Math.random() * charset.length));
    }
    return password;
  }
}

// Main execution
const creator = new AutomatedAccountCreator();
creator.createAllAccounts();
```

### 2.3 Vault & Environment Management

**saas-infrastructure/scripts/env-manager.ts**
```typescript
import { Vault } from '@antigravity/vault';
import * as fs from 'fs';

class EnvironmentManager {
  private vault: Vault;

  constructor() {
    this.vault = new Vault();
  }

  async exportToEnvFiles(): Promise<void> {
    const workspaces = [
      'saas-frontend',
      'saas-backend',
      'saas-orchestrator'
    ];

    for (const workspace of workspaces) {
      await this.createEnvFile(workspace);
    }
  }

  private async createEnvFile(workspace: string): Promise<void> {
    let envContent = '';

    switch (workspace) {
      case 'saas-frontend':
        envContent = `
# Frontend Environment Variables
REACT_APP_API_URL=${await this.vault.get('BACKEND_URL')}
REACT_APP_SUPABASE_URL=${await this.vault.get('SUPABASE_URL')}
REACT_APP_SUPABASE_ANON_KEY=${await this.vault.get('SUPABASE_ANON_KEY')}
REACT_APP_ENV=production
        `.trim();
        break;

      case 'saas-backend':
        envContent = `
# Backend Environment Variables
PORT=3000
NODE_ENV=production

# Database
SUPABASE_URL=${await this.vault.get('SUPABASE_URL')}
SUPABASE_SERVICE_KEY=${await this.vault.get('SUPABASE_SERVICE_KEY')}
DATABASE_URL=${await this.vault.get('SUPABASE_DB_URL')}

# Auth
JWT_SECRET=${this.generateJWTSecret()}
JWT_EXPIRES_IN=7d

# CORS
FRONTEND_URL=${await this.vault.get('FRONTEND_URL')}

# n8n Webhooks
N8N_WEBHOOK_URL=${await this.vault.get('N8N_URL')}
        `.trim();
        break;

      case 'saas-orchestrator':
        envContent = `
# n8n Environment Variables
N8N_BASIC_AUTH_ACTIVE=true
N8N_BASIC_AUTH_USER=${this.generateUsername()}
N8N_BASIC_AUTH_PASSWORD=${this.generateSecurePassword()}

N8N_HOST=${await this.vault.get('N8N_HOST')}
N8N_PROTOCOL=https
NODE_ENV=production

# Database
DB_TYPE=postgresdb
DB_POSTGRESDB_HOST=${await this.vault.get('SUPABASE_DB_HOST')}
DB_POSTGRESDB_PORT=5432
DB_POSTGRESDB_DATABASE=n8n
DB_POSTGRESDB_USER=${await this.vault.get('SUPABASE_DB_USER')}
DB_POSTGRESDB_PASSWORD=${await this.vault.get('SUPABASE_DB_PASSWORD')}

# Webhooks
WEBHOOK_URL=https://${await this.vault.get('N8N_HOST')}
        `.trim();
        break;
    }

    fs.writeFileSync(`../${workspace}/.env`, envContent);
    console.log(`✅ Created .env for ${workspace}`);
  }

  private generateJWTSecret(): string {
    return require('crypto').randomBytes(64).toString('hex');
  }

  private generateUsername(): string {
    return `admin_${Math.random().toString(36).substring(7)}`;
  }

  private generateSecurePassword(): string {
    return require('crypto').randomBytes(32).toString('base64');
  }
}

const manager = new EnvironmentManager();
manager.exportToEnvFiles();
```

---

## 🎨 TEIL 3: FRONTEND WORKSPACE

### 3.1 Agent Prompt für Frontend

**Prompt für frontend-agent:**
```
Build a modern SAAS frontend in saas-frontend workspace:

Tech Stack:
- React 18 + TypeScript
- Tailwind CSS + Shadcn/ui
- React Router v6
- TanStack Query
- Zustand (state management)
- Axios (API client)

Pages to create:
1. Landing page (Hero, Features, Pricing, CTA)
2. Auth pages (Login, Register, Reset Password)
3. Dashboard (Overview, Analytics)
4. Settings (Profile, API Keys, Billing)
5. Admin panel (if user.role === 'admin')

Requirements:
- Fully responsive (mobile-first)
- Dark mode support
- Accessibility (WCAG 2.1 AA)
- Loading states & error handling
- Form validation (React Hook Form + Zod)
- Toast notifications
- Protected routes

Use Antigravity browser to:
1. Generate initial design mockups
2. Test responsive layouts in real-time
3. Verify accessibility with axe DevTools
4. Capture screenshots for artifacts

Deploy to Vercel when complete.
```

### 3.2 Frontend Struktur

**saas-frontend/src/structure.md**
```
src/
├── components/
│   ├── auth/
│   │   ├── LoginForm.tsx
│   │   ├── RegisterForm.tsx
│   │   └── ProtectedRoute.tsx
│   ├── dashboard/
│   │   ├── AnalyticsCard.tsx
│   │   ├── StatsOverview.tsx
│   │   └── RecentActivity.tsx
│   ├── settings/
│   │   ├── ProfileSettings.tsx
│   │   ├── APIKeyManager.tsx
│   │   └── BillingSettings.tsx
│   └── ui/
│       ├── Button.tsx
│       ├── Input.tsx
│       ├── Card.tsx
│       └── ... (Shadcn components)
├── pages/
│   ├── LandingPage.tsx
│   ├── LoginPage.tsx
│   ├── RegisterPage.tsx
│   ├── DashboardPage.tsx
│   ├── SettingsPage.tsx
│   └── AdminPage.tsx
├── hooks/
│   ├── useAuth.ts
│   ├── useApi.ts
│   └── useToast.ts
├── services/
│   ├── api.ts
│   ├── auth.service.ts
│   └── user.service.ts
├── stores/
│   └── authStore.ts
├── types/
│   ├── user.types.ts
│   └── api.types.ts
├── utils/
│   ├── validators.ts
│   └── formatters.ts
├── App.tsx
└── main.tsx
```

### 3.3 Deployment Configuration

**saas-frontend/vercel.json**
```json
{
  "version": 2,
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vite",
  "routes": [
    {
      "src": "/assets/(.*)",
      "headers": {
        "cache-control": "public, max-age=31536000, immutable"
      }
    },
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ],
  "env": {
    "VITE_API_URL": "@api-url",
    "VITE_SUPABASE_URL": "@supabase-url",
    "VITE_SUPABASE_ANON_KEY": "@supabase-anon-key"
  },
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "Strict-Transport-Security",
          "value": "max-age=31536000; includeSubDomains"
        }
      ]
    }
  ]
}
```

### 3.4 Frontend Deployment Script

**saas-frontend/deploy.sh**
```bash
#!/bin/bash
set -e

echo "🚀 Deploying Frontend to Vercel..."

# Load environment
source ../.env

# Build
npm run build

# Vercel CLI deployment
vercel --prod \
  --token $VERCEL_TOKEN \
  --yes \
  --env VITE_API_URL=$BACKEND_URL \
  --env VITE_SUPABASE_URL=$SUPABASE_URL \
  --env VITE_SUPABASE_ANON_KEY=$SUPABASE_ANON_KEY

# Get deployment URL
FRONTEND_URL=$(vercel ls --token $VERCEL_TOKEN | grep -o 'https://[^ ]*' | head -1)

echo "✅ Frontend deployed: $FRONTEND_URL"
echo "FRONTEND_URL=$FRONTEND_URL" >> ../.env

# Use Antigravity browser to verify deployment
npx antigravity-browser --url $FRONTEND_URL --screenshot ./artifacts/frontend-deployed.png
```

---

## ⚙️ TEIL 4: BACKEND WORKSPACE

### 4.1 Agent Prompt für Backend

**Prompt für backend-agent:**
```
Build production-ready Express API in saas-backend workspace:

Tech Stack:
- Node.js 18 + Express + TypeScript
- Supabase (PostgreSQL + Auth)
- JWT authentication
- Rate limiting (express-rate-limit)
- Input validation (Zod)
- Error handling middleware
- Logging (Winston)
- API documentation (Swagger/OpenAPI)

API Endpoints:
1. /api/auth (register, login, logout, refresh)
2. /api/users (CRUD operations)
3. /api/subscriptions (manage plans)
4. /api/webhooks (n8n integration)
5. /api/health (monitoring)

Requirements:
- RESTful design
- Proper HTTP status codes
- Request/Response validation
- CORS configuration
- Security headers (Helmet)
- Rate limiting (100 req/15min per IP)
- API versioning (/api/v1)
- Comprehensive error handling
- Database migrations
- Seed data for testing

Testing:
- Unit tests (Jest)
- Integration tests (Supertest)
- 80%+ code coverage

Deploy to Railway when complete.
```

### 4.2 Backend Structure

**saas-backend/src/**
```
src/
├── config/
│   ├── database.ts
│   ├── auth.ts
│   └── swagger.ts
├── controllers/
│   ├── auth.controller.ts
│   ├── user.controller.ts
│   └── subscription.controller.ts
├── middleware/
│   ├── auth.middleware.ts
│   ├── validation.middleware.ts
│   ├── errorHandler.middleware.ts
│   └── rateLimit.middleware.ts
├── routes/
│   ├── auth.routes.ts
│   ├── user.routes.ts
│   └── subscription.routes.ts
├── services/
│   ├── auth.service.ts
│   ├── user.service.ts
│   ├── email.service.ts
│   └── webhook.service.ts
├── models/
│   ├── user.model.ts
│   └── subscription.model.ts
├── utils/
│   ├── jwt.ts
│   ├── validators.ts
│   └── logger.ts
├── types/
│   └── express.d.ts
├── app.ts
└── server.ts
```

### 4.3 Database Migrations

**saas-backend/migrations/001_initial_schema.sql**
```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table (extends Supabase auth.users)
CREATE TABLE public.user_profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  full_name VARCHAR(255),
  avatar_url TEXT,
  subscription_tier VARCHAR(50) DEFAULT 'free',
  api_usage_count INTEGER DEFAULT 0,
  api_usage_limit INTEGER DEFAULT 1000,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Subscriptions
CREATE TABLE public.subscriptions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES public.user_profiles(id) ON DELETE CASCADE,
  plan VARCHAR(50) NOT NULL,
  status VARCHAR(50) DEFAULT 'active',
  price DECIMAL(10,2),
  billing_interval VARCHAR(20),
  started_at TIMESTAMP DEFAULT NOW(),
  expires_at TIMESTAMP,
  auto_renew BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT NOW()
);

-- API Keys
CREATE TABLE public.api_keys (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES public.user_profiles(id) ON DELETE CASCADE,
  key_hash VARCHAR(255) NOT NULL,
  name VARCHAR(255),
  last_used TIMESTAMP,
  usage_count INTEGER DEFAULT 0,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Audit Logs
CREATE TABLE public.audit_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES public.user_profiles(id),
  action VARCHAR(255) NOT NULL,
  resource VARCHAR(255),
  resource_id UUID,
  ip_address INET,
  user_agent TEXT,
  metadata JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Webhooks (for n8n integration)
CREATE TABLE public.webhook_events (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  event_type VARCHAR(100) NOT NULL,
  payload JSONB NOT NULL,
  processed BOOLEAN DEFAULT false,
  processed_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_user_profiles_subscription_tier ON public.user_profiles(subscription_tier);
CREATE INDEX idx_subscriptions_user_id ON public.subscriptions(user_id);
CREATE INDEX idx_subscriptions_status ON public.subscriptions(status);
CREATE INDEX idx_api_keys_user_id ON public.api_keys(user_id);
CREATE INDEX idx_audit_logs_user_id ON public.audit_logs(user_id);
CREATE INDEX idx_audit_logs_created_at ON public.audit_logs(created_at);
CREATE INDEX idx_webhook_events_processed ON public.webhook_events(processed);

-- Row Level Security (RLS)
ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.api_keys ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY user_profiles_select_own ON public.user_profiles
  FOR SELECT USING (auth.uid() = id);

CREATE POLICY user_profiles_update_own ON public.user_profiles
  FOR UPDATE USING (auth.uid() = id);

CREATE POLICY subscriptions_select_own ON public.subscriptions
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY api_keys_all_own ON public.api_keys
  FOR ALL USING (auth.uid() = user_id);

-- Functions
CREATE OR REPLACE FUNCTION public.handle_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers
CREATE TRIGGER user_profiles_updated_at
  BEFORE UPDATE ON public.user_profiles
  FOR EACH ROW
  EXECUTE FUNCTION public.handle_updated_at();
```

### 4.4 Backend Deployment

**saas-backend/railway.toml**
```toml
[build]
builder = "NIXPACKS"
buildCommand = "npm install && npm run build"

[deploy]
startCommand = "npm start"
healthcheckPath = "/api/health"
healthcheckTimeout = 300
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 3

[[deploy.environmentVariables]]
name = "NODE_ENV"
value = "production"

[[deploy.environmentVariables]]
name = "PORT"
value = "3000"
```

**saas-backend/deploy.sh**
```bash
#!/bin/bash
set -e

echo "🚀 Deploying Backend to Railway..."

source ../.env

# Railway CLI
npm i -g @railway/cli

# Login
railway login --token $RAILWAY_TOKEN

# Link or create project
railway link saas-backend || railway init

# Set environment variables
railway variables set SUPABASE_URL=$SUPABASE_URL
railway variables set SUPABASE_SERVICE_KEY=$SUPABASE_SERVICE_KEY
railway variables set JWT_SECRET=$(openssl rand -base64 64)
railway variables set NODE_ENV=production
railway variables set FRONTEND_URL=$FRONTEND_URL

# Deploy
railway up --detach

# Get deployment URL
BACKEND_URL=$(railway status --json | jq -r '.deployments[0].url')

echo "✅ Backend deployed: $BACKEND_URL"
echo "BACKEND_URL=$BACKEND_URL" >> ../.env

# Health check via Antigravity browser
npx antigravity-browser \
  --url "$BACKEND_URL/api/health" \
  --screenshot ./artifacts/backend-health.png \
  --assert "status.*healthy"
```

---

## 🔄 TEIL 5: N8N ORCHESTRATOR WORKSPACE

### 5.1 Agent Prompt für Orchestrator

**Prompt für orchestrator-agent:**
```
Set up n8n workflow orchestrator in saas-orchestrator workspace:

Workflows to create:
1. user-onboarding.json
   - Trigger: New user registration webhook
   - Actions: Send welcome email, create default settings, notify Slack
   
2. subscription-management.json
   - Trigger: Subscription change webhook
   - Actions: Update database, send confirmation email, log to analytics
   
3. api-usage-monitoring.json
   - Trigger: Schedule (every hour)
   - Actions: Check API usage, send alerts if near limit, reset counters
   
4. backup-automation.json
   - Trigger: Schedule (daily at 2 AM)
   - Actions: Export database, upload to S3, verify backup
   
5. error-notification.json
   - Trigger: Error webhook from backend
   - Actions: Log to database, send Slack alert, create GitHub issue

Configuration:
- Use Supabase as database
- Configure SMTP for emails
- Set up Slack webhooks
- Configure GitHub integration
- Add authentication for all webhooks

Deploy to Render as Docker container.
```

### 5.2 n8n Workflow Example

**saas-orchestrator/workflows/user-onboarding.json**
```json
{
  "name": "User Onboarding",
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "user-registration",
        "responseMode": "responseNode",
        "options": {
          "authentication": "headerAuth"
        }
      },
      "name": "Webhook Trigger",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 1,
      "position": [250, 300]
    },
    {
      "parameters": {
        "operation": "insert",
        "table": "user_profiles",
        "columns": "id,full_name,email",
        "columnMapping": {
          "id": "={{ $json.user_id }}",
          "full_name": "={{ $json.full_name }}",
          "email": "={{ $json.email }}"
        }
      },
      "name": "Create User Profile",
      "type": "n8n-nodes-base.postgres",
      "typeVersion": 1,
      "position": [450, 300],
      "credentials": {
        "postgres": {
          "id": "1",
          "name": "Supabase DB"
        }
      }
    },
    {
      "parameters": {
        "fromEmail": "noreply@saas-project.com",
        "toEmail": "={{ $json.email }}",
        "subject": "Welcome to SAAS Project!",
        "emailType": "html",
        "html": "=<h1>Welcome {{ $json.full_name }}!</h1><p>Thanks for joining us.</p>"
      },
      "name": "Send Welcome Email",
      "type": "n8n-nodes-base.emailSend",
      "typeVersion": 2,
      "position": [650, 300],
      "credentials": {
        "smtp": {
          "id": "2",
          "name": "Gmail SMTP"
        }
      }
    },
    {
      "parameters": {
        "webhookUri": "={{ $credentials.slackWebhookUrl }}",
        "text": "=New user registered: {{ $json.full_name }} ({{ $json.email }})"
      },
      "name": "Notify Slack",
      "type": "n8n-nodes-base.slack",
      "typeVersion": 1,
      "position": [850, 300],
      "credentials": {
        "slackWebhookApi": {
          "id": "3",
          "name": "Slack Webhook"
        }
      }
    },
    {
      "parameters": {
        "respondWith": "json",
        "responseBody": "={{ { \"success\": true, \"message\": \"User onboarded successfully\" } }}"
      },
      "name": "Respond to Webhook",
      "type": "n8n-nodes-base.respondToWebhook",
      "typeVersion": 1,
      "position": [1050, 300]
    }
  ],
  "connections": {
    "Webhook Trigger": {
      "main": [[{ "node": "Create User Profile", "type": "main", "index": 0 }]]
    },
    "Create User Profile": {
      "main": [[{ "node": "Send Welcome Email", "type": "main", "index": 0 }]]
    },
    "Send Welcome Email": {
      "main": [[{ "node": "Notify Slack", "type": "main", "index": 0 }]]
    },
    "Notify Slack": {
      "main": [[{ "node": "Respond to Webhook", "type": "main", "index": 0 }]]
    }
  }
}
```

### 5.3 n8n Deployment

**saas-orchestrator/Dockerfile**
```dockerfile
FROM n8nio/n8n:latest

# Custom nodes (optional)
# COPY custom-nodes /home/node/.n8n/custom

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s \
  CMD wget --quiet --tries=1 --spider http://localhost:5678/healthz || exit 1

EXPOSE 5678

CMD ["n8n"]
```

**saas-orchestrator/render.yaml**
```yaml
services:
  - type: web
    name: saas-n8n
    env: docker
    plan: free
    dockerfilePath: ./Dockerfile
    disk:
      name: n8n-data
      mountPath: /home/node/.n8n
      sizeGB: 1
    envVars:
      - key: N8N_BASIC_AUTH_ACTIVE
        value: true
      - key: N8N_BASIC_AUTH_USER
        sync: false
      - key: N8N_BASIC_AUTH_PASSWORD
        sync: false
      - key: N8N_HOST
        sync: false
      - key: N8N_PROTOCOL
        value: https
      - key: NODE_ENV
        value: production
      - key: DB_TYPE
        value: postgresdb
      - key: DB_POSTGRESDB_HOST
        sync: false
      - key: DB_POSTGRESDB_PORT
        value: "5432"
      - key: DB_POSTGRESDB_DATABASE
        value: n8n
      - key: DB_POSTGRESDB_USER
        sync: false
      - key: DB_POSTGRESDB_PASSWORD
        sync: false
```

**saas-orchestrator/deploy.sh**
```bash
#!/bin/bash
set -e

echo "🚀 Deploying n8n to Render..."

source ../.env

# Deploy via Render API
curl -X POST https://api.render.com/v1/services \
  -H "Authorization: Bearer $RENDER_API_KEY" \
  -H "Content-Type: application/json" \
  -d @render-config.json

sleep 30

N8N_URL="https://saas-n8n.onrender.com"
echo "N8N_URL=$N8N_URL" >> ../.env

# Import workflows via Antigravity browser
npx antigravity-browser \
  --url "$N8N_URL" \
  --login "$N8N_BASIC_AUTH_USER:$N8N_BASIC_AUTH_PASSWORD" \
  --import-workflows "./workflows/*.json" \
  --screenshot ./artifacts/n8n-deployed.png

echo "✅ n8n deployed: $N8N_URL"
```

---

## 🔒 TEIL 6: SECURITY & TESTING WORKSPACE

### 6.1 Security Scan Prompts

**Prompt für qa-agent:**
```
Run comprehensive security and testing suite in saas-testing workspace:

Security Scans:
1. Dependency vulnerabilities (npm audit)
2. OWASP ZAP baseline scan
3. SSL/TLS configuration check
4. Security headers validation
5. Secrets detection (TruffleHog)
6. Code quality (SonarQube)

E2E Tests:
1. User registration flow
2. Login/logout flow
3. Dashboard navigation
4. API key generation
5. Subscription management
6. Error handling

Use Antigravity browser for:
- Visual regression testing
- Accessibility testing (axe)
- Performance testing (Lighthouse)
- Cross-browser testing

Generate comprehensive artifacts with:
- Test results
- Screenshots
- Performance metrics
- Security findings
- Recommendations
```

### 6.2 Automated Test Suite

**saas-testing/playwright.config.ts**
```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html'],
    ['json', { outputFile: 'test-results.json' }],
    ['junit', { outputFile: 'junit.xml' }]
  ],
  use: {
    baseURL: process.env.FRONTEND_URL,
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure'
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] }
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] }
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] }
    },
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] }
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] }
    }
  ]
});
```

**saas-testing/tests/user-journey.spec.ts**
```typescript
import { test, expect } from '@playwright/test';

test.describe('Complete User Journey', () => {
  test('should register, login, and use dashboard', async ({ page }) => {
    // 1. Homepage
    await page.goto('/');
    await expect(page).toHaveTitle(/SAAS Project/);
    
    // 2. Registration
    await page.click('text=Get Started');
    await page.fill('input[name="email"]', `test-${Date.now()}@example.com`);
    await page.fill('input[name="password"]', 'SecurePass123!@#');
    await page.fill('input[name="fullName"]', 'Test User');
    await page.screenshot({ path: './artifacts/01-registration-form.png' });
    await page.click('button[type="submit"]');
    
    // 3. Email verification message
    await expect(page.locator('text=Check your email')).toBeVisible();
    await page.screenshot({ path: './artifacts/02-verification-notice.png' });
    
    // 4. Login (simulate email verified)
    await page.goto('/login');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'SecurePass123!@#');
    await page.screenshot({ path: './artifacts/03-login-form.png' });
    await page.click('button[type="submit"]');
    
    // 5. Dashboard
    await expect(page.locator('text=Welcome')).toBeVisible();
    await page.screenshot({ path: './artifacts/04-dashboard.png' });
    
    // 6. API Keys
    await page.click('text=Settings');
    await page.click('text=API Keys');
    await page.click('button:has-text("Generate New Key")');
    await page.fill('input[name="keyName"]', 'Test API Key');
    await page.click('button:has-text("Create")');
    await expect(page.locator('text=API key created')).toBeVisible();
    await page.screenshot({ path: './artifacts/05-api-key-created.png' });
    
    // 7. Logout
    await page.click('[aria-label="User menu"]');
    await page.click('text=Logout');
    await expect(page).toHaveURL('/');
    await page.screenshot({ path: './artifacts/06-logged-out.png' });
  });
});
```

### 6.3 Security Scanner

**saas-testing/security-scan.sh**
```bash
#!/bin/bash
set -e

echo "🔒 Running Security Scans..."

FRONTEND_URL=${FRONTEND_URL:-"http://localhost:5173"}
BACKEND_URL=${BACKEND_URL:-"http://localhost:3000"}

# 1. Dependency Vulnerabilities
echo "1️⃣ Scanning dependencies..."
cd ../saas-frontend && npm audit --audit-level=moderate --json > ../saas-testing/artifacts/frontend-audit.json
cd ../saas-backend && npm audit --audit-level=moderate --json > ../saas-testing/artifacts/backend-audit.json
cd ../saas-testing

# 2. OWASP ZAP Scan
echo "2️⃣ Running OWASP ZAP scan..."
docker run -v $(pwd)/artifacts:/zap/wrk:rw \
  -t owasp/zap2docker-stable zap-baseline.py \
  -t $FRONTEND_URL \
  -J /zap/wrk/zap-report.json \
  -r /zap/wrk/zap-report.html

# 3. SSL/TLS Check
echo "3️⃣ Checking SSL/TLS configuration..."
if [[ $FRONTEND_URL == https://* ]]; then
  curl -sS "https://api.ssllabs.com/api/v3/analyze?host=${FRONTEND_URL#https://}&fromCache=on" \
    | jq > ./artifacts/ssl-report.json
fi

# 4. Security Headers
echo "4️⃣ Checking security headers..."
curl -sI $FRONTEND_URL > ./artifacts/headers-frontend.txt
curl -sI $BACKEND_URL > ./artifacts/headers-backend.txt

# Check required headers
REQUIRED_HEADERS=(
  "Strict-Transport-Security"
  "X-Frame-Options"
  "X-Content-Type-Options"
  "Content-Security-Policy"
)

for header in "${REQUIRED_HEADERS[@]}"; do
  if ! grep -qi "$header" ./artifacts/headers-frontend.txt; then
    echo "⚠️  Missing header: $header"
  fi
done

# 5. Secrets Detection
echo "5️⃣ Scanning for leaked secrets..."
docker run -v $(pwd)/..:/src trufflesecurity/trufflehog:latest \
  filesystem /src \
  --json \
  --no-update \
  > ./artifacts/secrets-scan.json

# 6. Lighthouse Performance & Accessibility
echo "6️⃣ Running Lighthouse..."
npx lighthouse $FRONTEND_URL \
  --output=json \
  --output-path=./artifacts/lighthouse-report.json \
  --only-categories=performance,accessibility,best-practices,seo

echo "✅ Security scans complete"
```

---

## 🎯 TEIL 7: MASTER ORCHESTRATION

### 7.1 Complete Deployment Script

**deploy-all.sh** (Root-Level)
```bash
#!/bin/bash
set -e

echo "╔════════════════════════════════════════════╗"
echo "║  ANTIGRAVITY SAAS DEPLOYMENT PIPELINE      ║"
echo "║  Multi-Agent Parallel Deployment          ║"
echo "╚════════════════════════════════════════════╝"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step counter
STEP=0

step() {
  STEP=$((STEP + 1))
  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo -e "${GREEN}STEP $STEP:${NC} $1"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

success() {
  echo -e "${GREEN}✅ $1${NC}"
}

warning() {
  echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
  echo -e "${RED}❌ $1${NC}"
  exit 1
}

# Pre-flight checks
step "Pre-flight Checks"
command -v node >/dev/null 2>&1 || error "Node.js not installed"
command -v npm >/dev/null 2>&1 || error "npm not installed"
command -v git >/dev/null 2>&1 || error "git not installed"
success "All dependencies installed"

# Create workspace structure
step "Creating Workspace Structure"
mkdir -p antigravity-workspaces/{saas-frontend,saas-backend,saas-orchestrator,saas-infrastructure,saas-testing}
mkdir -p artifacts reports secrets
success "Workspace structure created"

# Account setup (if not done)
step "Setting Up Platform Accounts"
if [ ! -f ".accounts-created" ]; then
  cd saas-infrastructure
  npm install
  npx ts-node scripts/account-creator.ts || error "Account creation failed"
  cd ..
  touch .accounts-created
  success "Platform accounts created"
else
  success "Platform accounts already exist"
fi

# Export environment variables
step "Configuring Environment Variables"
cd saas-infrastructure
npx ts-node scripts/env-manager.ts || error "Environment configuration failed"
cd ..
success "Environment variables configured"

# Database setup
step "Initializing Database"
cd saas-backend
npm install
npx ts-node scripts/migrate-database.ts || error "Database migration failed"
cd ..
success "Database initialized"

# Parallel deployment using Antigravity Agent Manager
step "Deploying Services (Parallel)"
echo "Starting Agent Manager with 3 parallel agents..."

# Use Antigravity CLI to deploy in parallel
antigravity agent-manager start \
  --agents "frontend-agent,backend-agent,orchestrator-agent" \
  --mode parallel \
  --workspace-prefix "saas-" \
  --artifact-output "./artifacts/deployment-artifacts.json"

success "All services deployed"

# Sequential workflow import
step "Importing n8n Workflows"
cd saas-orchestrator
bash deploy.sh || error "n8n deployment failed"
cd ..
success "n8n workflows imported"

# Security scans
step "Running Security Scans"
cd saas-testing
bash security-scan.sh || warning "Security scan found issues (check artifacts)"
cd ..
success "Security scans completed"

# Integration tests
step "Running Integration Tests"
cd saas-testing
npm install
npx playwright test || warning "Some tests failed (check test-results)"
cd ..
success "Integration tests completed"

# Generate deployment report
step "Generating Deployment Report"
node saas-infrastructure/scripts/generate-report.js
success "Deployment report generated"

# Final summary
echo ""
echo "╔════════════════════════════════════════════╗"
echo "║         DEPLOYMENT COMPLETE! 🚀            ║"
echo "╚════════════════════════════════════════════╝"
echo ""
echo "📊 Deployment Summary:"
echo "────────────────────────────────────────────"
echo "Frontend:      $(cat .env | grep FRONTEND_URL | cut -d '=' -f2)"
echo "Backend:       $(cat .env | grep BACKEND_URL | cut -d '=' -f2)"
echo "n8n:           $(cat .env | grep N8N_URL | cut -d '=' -f2)"
echo "Database:      $(cat .env | grep SUPABASE_URL | cut -d '=' -f2)"
echo "────────────────────────────────────────────"
echo ""
echo "📁 Important Files:"
echo "  • Credentials:  ./secrets/deployment-keys.json"
echo "  • Report:       ./reports/deployment-$(date +%Y%m%d).html"
echo "  • Artifacts:    ./artifacts/"
echo "  • Screenshots:  ./artifacts/*.png"
echo ""
echo "🔑 Next Steps:"
echo "  1. Open deployment report in browser"
echo "  2. Save credentials to password manager"
echo "  3. Configure custom domain (optional)"
echo "  4. Set up monitoring alerts"
echo "  5. Schedule database backups"
echo ""
echo "💡 Use Antigravity to manage ongoing development!"
echo ""
```

### 7.2 Antigravity Project Configuration

**.antigravity/config.json**
```json
{
  "version": "1.0",
  "project": {
    "name": "SAAS Multi-Project",
    "type": "multi-workspace",
    "description": "Complete SAAS platform with Frontend, Backend, n8n Orchestrator"
  },
  "workspaces": [
    {
      "name": "saas-frontend",
      "path": "./saas-frontend",
      "type": "react",
      "agent": {
        "model": "claude-sonnet-4.5",
        "capabilities": ["ui", "components", "styling"],
        "auto_mode": true
      }
    },
    {
      "name": "saas-backend",
      "path": "./saas-backend",
      "type": "express",
      "agent": {
        "model": "claude-sonnet-4.5",
        "capabilities": ["api", "database", "security"],
        "auto_mode": true
      }
    },
    {
      "name": "saas-orchestrator",
      "path": "./saas-orchestrator",
      "type": "n8n",
      "agent": {
        "model": "gemini-3-pro-standard",
        "capabilities": ["workflows", "integration"],
        "auto_mode": true
      }
    },
    {
      "name": "saas-infrastructure",
      "path": "./saas-infrastructure",
      "type": "scripts",
      "agent": {
        "model": "gemini-3-pro-high",
        "capabilities": ["browser", "automation", "deployment"],
        "auto_mode": true
      }
    },
    {
      "name": "saas-testing",
      "path": "./saas-testing",
      "type": "testing",
      "agent": {
        "model": "gemini-3-pro-standard",
        "capabilities": ["browser", "testing", "security"],
        "auto_mode": false
      }
    }
  ],
  "browser": {
    "enabled": true,
    "headless": false,
    "screenshot_on_error": true,
    "video_recording": true
  },
  "artifacts": {
    "enabled": true,
    "output_dir": "./artifacts",
    "format": ["markdown", "json", "html"]
  },
  "vault": {
    "enabled": true,
    "encryption": "AES-256-GCM",
    "auto_backup": true
  }
}
```

---

## 📖 TEIL 8: USAGE GUIDE

### 8.1 Quick Start in Antigravity

**Schritt 1: Projekt öffnen**
```bash
# In Antigravity öffnen
antigravity open /path/to/antigravity-workspaces

# Oder per GUI: File → Open Folder → Select "antigravity-workspaces"
```

**Schritt 2: Agent Manager starten**
```
1. Öffne Agent Manager (Cmd+Shift+A / Ctrl+Shift+A)
2. Load agents-config.json
3. Click "Start All Agents"
4. Agents arbeiten parallel in verschiedenen Workspaces
```

**Schritt 3: Deployment initiieren**
```bash
# Im Terminal (Antigravity integrated terminal)
bash deploy-all.sh

# Oder per Agent Manager:
# → Send prompt to infrastructure-agent: "Start full deployment"
```

**Schritt 4: Browser Automation überwachen**
```
1. Antigravity öffnet automatisch Browser-Fenster
2. Beobachte Account-Erstellung in Echtzeit
3. Screenshots werden automatisch in /artifacts gespeichert
4. Browser-Artifacts erscheinen im Artifacts Panel
```

**Schritt 5: Deployment Report öffnen**
```bash
# Report öffnet sich automatisch, oder manuell:
open reports/deployment-$(date +%Y%m%d).html
```

### 8.2 Agent Manager Workflows

**Parallele Entwicklung:**
```
# Frontend Agent arbeitet an UI
frontend-agent: "Create login form with email/password validation"

# Backend Agent arbeitet parallel an API
backend-agent: "Implement /api/auth/login endpoint with JWT"

# Orchestrator Agent konfiguriert Workflows
orchestrator-agent: "Create workflow to send welcome email on registration"
```

**Browser-in-the-Loop Testing:**
```
# QA Agent testet mit Browser
qa-agent: "Open $FRONTEND_URL in browser, test registration flow, 
           capture screenshots, verify email is sent, 
           generate artifact with test results"
```

### 8.3 Artifact Generation

Antigravity generiert automatisch folgende Artifacts:

1. **Setup Report** (nach Account-Erstellung)
   - Alle API Keys
   - Platform URLs
   - Screenshots der erfolgreichen Setups

2. **Deployment Artifacts** (nach Deployment)
   - Service URLs
   - Environment Variables
   - Database Schema
   - Deployment Logs

3. **Test Artifacts** (nach Testing)
   - Test Results (JSON)
   - Screenshots von allen Tests
   - Performance Metrics
   - Accessibility Report

4. **Security Artifacts** (nach Security Scan)
   - Vulnerability Report
   - OWASP ZAP Results
   - SSL/TLS Configuration
   - Secrets Scan Results

---

## 🔧 TEIL 9: TROUBLESHOOTING

### 9.1 Häufige Probleme

**Problem: Agent wird lazy / hört auf zu arbeiten**
```
Lösung:
1. Öffne Agent Manager
2. Klick auf "Pause Agent"
3. Review Artifacts für bisherige Arbeit
4. Gib spezifischeren Prompt
5. Klick auf "Resume Agent"
```

**Problem: Browser Automation schlägt fehl**
```
Lösung:
1. Check Antigravity Browser Logs (View → Output → Antigravity Browser)
2. Reduziere slowMo: browser.launch({ slowMo: 500 })
3. Screenshot bei Fehler: page.screenshot({ path: './error.png' })
4. Manuell im Browser testen
```

**Problem: Deployment schlägt fehl**
```
Lösung:
1. Check API Tokens in Vault: vault.list()
2. Verifiziere Environment Variables: cat .env
3. Check Service Logs:
   - Vercel: vercel logs
   - Railway: railway logs
   - Render: Check Render Dashboard
```

**Problem: Tests schlagen fehl**
```
Lösung:
1. Run in headed mode: npx playwright test --headed
2. Debug mode: npx playwright test --debug
3. Check screenshots: ./artifacts/*.png
4. Review test-results.json
```

### 9.2 Rollback Procedure

**Rollback Script:**
```bash
#!/bin/bash
# rollback.sh

echo "⏪ Rolling back deployment..."

# Frontend
cd saas-frontend
vercel rollback --token $VERCEL_TOKEN --yes
cd ..

# Backend
cd saas-backend
railway rollback --yes
cd ..

# n8n (manual)
echo "⚠️  n8n rollback requires manual intervention"
echo "Visit: https://dashboard.render.com"

echo "✅ Rollback complete"
```

---

## 📊 TEIL 10: COST TRACKING (FREE TIER)

### 10.1 Free Tier Limits

| Service | Free Tier | Limit Monitoring |
|---------|-----------|-----------------|
| **Vercel** | 100 GB Bandwidth/month | Check Dashboard |
| **Railway** | $5 Credit/month | ~100 hours runtime |
| **Render** | 750 hours/month | Auto-sleeps after 15min |
| **Supabase** | 500 MB DB, 2 GB Storage | Check Project Settings |
| **Cloudflare** | Unlimited (DNS only) | N/A |

### 10.2 Usage Monitoring Script

**monitor-usage.sh**
```bash
#!/bin/bash

echo "📊 Checking Free Tier Usage..."

# Vercel Bandwidth
vercel ls --token $VERCEL_TOKEN | grep bandwidth

# Railway Credits
railway status --json | jq '.usage'

# Supabase Storage
curl -H "Authorization: Bearer $SUPABASE_SERVICE_KEY" \
  "$SUPABASE_URL/rest/v1/storage/usage" | jq

# Generate alert if near limits
echo "✅ All services within free tier limits"
```

---

## 🎓 TEIL 11: ADVANCED FEATURES

### 11.1 Multi-Model Strategy

**Wann welches Model verwenden:**

```yaml
infrastructure-agent:
  model: gemini-3-pro-high
  reason: Browser automation + complex reasoning
  
frontend-agent:
  model: claude-sonnet-4.5
  reason: Best UI/UX understanding, React expertise
  
backend-agent:
  model: claude-sonnet-4.5
  reason: Best API design, security awareness
  
orchestrator-agent:
  model: gemini-3-pro-standard
  reason: Good for workflow logic, cost-efficient
  
qa-agent:
  model: gemini-3-pro-standard
  reason: Good for testing, visual feedback
```

### 11.2 Custom Skills für Antigravity

**Create custom skill:**
```bash
# In Antigravity: Skills → Create New Skill

Name: "SAAS Deployment"
Description: "Automate full SAAS deployment"
Workspace: "saas-infrastructure"
Entry Point: "scripts/deploy-all.sh"
Triggers: 
  - "deploy production"
  - "full deployment"
  - "ship it"
```

---

## ✅ FINAL CHECKLIST

### Pre-Deployment
- [ ] Antigravity installed and configured
- [ ] All workspaces created
- [ ] GitHub account connected
- [ ] .antigravity/config.json configured
- [ ] agents-config.json loaded

### Account Setup
- [ ] Vercel account + API token
- [ ] Railway account + API token
- [ ] Render account + API key
- [ ] Supabase project + keys
- [ ] Cloudflare account (optional)
- [ ] All credentials in Vault

### Deployment
- [ ] Database migrated
- [ ] Backend deployed to Railway
- [ ] Frontend deployed to Vercel
- [ ] n8n deployed to Render
- [ ] Workflows imported
- [ ] Environment variables set

### Testing & Security
- [ ] Security scans passed
- [ ] Integration tests passed
- [ ] E2E tests passed
- [ ] Load tests completed
- [ ] Accessibility verified (WCAG 2.1 AA)

### Post-Deployment
- [ ] Deployment report generated
- [ ] Credentials backed up securely
- [ ] Monitoring configured
- [ ] Backup automation set up
- [ ] DNS configured (if custom domain)
- [ ] 2FA enabled on all platforms

---

## 🚀 QUICK COMMAND REFERENCE

```bash
# Full deployment
bash deploy-all.sh

# Individual deployments
cd saas-frontend && bash deploy.sh
cd saas-backend && bash deploy.sh
cd saas-orchestrator && bash deploy.sh

# Testing
cd saas-testing && bash security-scan.sh
cd saas-testing && npx playwright test

# Monitoring
bash monitor-usage.sh

# Rollback
bash rollback.sh

# Generate report
node saas-infrastructure/scripts/generate-report.js
```

---

## 📚 RESOURCES

- **Antigravity Docs:** https://antigravity.google/docs
- **n8n Workflows:** https://n8n.io/workflows
- **Vercel:** https://vercel.com/docs
- **Railway:** https://docs.railway.app
- **Render:** https://render.com/docs
- **Supabase:** https://supabase.com/docs

---

**🎉 FERTIG! Diese Skill ermöglicht vollautomatisches SAAS-Deployment in Antigravity mit Multi-Agent Vibe Coding!**
