import './styles.css';
import { features, metrics, plans, testimonials, timeline } from './data';

const app = document.querySelector<HTMLDivElement>('#app');

if (!app) {
  throw new Error('App container missing');
}

app.innerHTML = `
  <div class="page">
    <header class="topbar">
      <div class="brand">Northwind Signal</div>
      <nav class="nav">
        <a href="#product">Product</a>
        <a href="#platform">Platform</a>
        <a href="#pricing">Pricing</a>
        <a href="#story">Story</a>
      </nav>
      <button class="button ghost">Request demo</button>
    </header>

    <section class="hero">
      <div class="hero-text">
        <p class="eyebrow">Signal Intelligence Platform</p>
        <h1>Turn operational noise into clear, actionable signals.</h1>
        <p class="lead">
          Northwind Signal connects product telemetry, revenue data, and incident response
          into a unified command center for modern SaaS teams.
        </p>
        <div class="hero-actions">
          <button class="button">Launch workspace</button>
          <button class="button ghost">See the platform</button>
        </div>
        <div class="metric-row">
          ${metrics
            .map(
              (metric) => `
            <div class="metric">
              <div class="metric-value">${metric.value}</div>
              <div class="metric-label">${metric.label}</div>
            </div>`
            )
            .join('')}
        </div>
      </div>
      <div class="hero-panel">
        <div class="panel">
          <div class="panel-header">
            <div>
              <p class="panel-title">Live Command Center</p>
              <p class="panel-subtitle">Last refreshed <span id="api-last-sync">moments ago</span></p>
            </div>
            <span class="pill">Stable</span>
          </div>
          <div class="panel-grid">
            ${timeline
              .map(
                (item) => `
              <div class="panel-card">
                <p class="panel-label">${item.label}</p>
                <p class="panel-value">${item.value}</p>
              </div>`
              )
              .join('')}
          </div>
          <div class="panel-footer">
            <div>
              <p class="panel-value" id="api-model-calls">120k</p>
              <p class="panel-label">Model calls this week</p>
            </div>
            <button class="button ghost">View workspace</button>
          </div>
        </div>
      </div>
    </section>

    <section id="report" class="section report-section">
      <div class="section-header">
        <p class="eyebrow">Company Briefing</p>
        <h2>Generate a compact report for last year.</h2>
        <p class="section-lead">Pulls live billing, usage, and project data from the backend.</p>
      </div>
      <div class="report-card">
        <div class="report-controls">
          <button class="button" id="report-generate">Generate report</button>
          <span class="pill" id="report-year">Last year</span>
        </div>
        <p class="muted" id="report-status">Click generate to load the report.</p>
        <div id="report-content" class="report-content"></div>
      </div>
    </section>

    <section id="product" class="section">
      <div class="section-header">
        <p class="eyebrow">Platform modules</p>
        <h2>Everything your ops team needs to stay ahead.</h2>
        <p class="section-lead">
          Unify data and decisioning across the org with playbooks, risk indexes, and human-first alerts.
        </p>
      </div>
      <div class="feature-grid">
        ${features
          .map(
            (feature) => `
          <div class="feature-card">
            <h3>${feature.title}</h3>
            <p>${feature.description}</p>
          </div>`
          )
          .join('')}
      </div>
    </section>

    <section id="platform" class="section split">
      <div class="split-copy">
        <p class="eyebrow">Unified workspace</p>
        <h2>Move from alert fire drills to calm, consistent execution.</h2>
        <p>
          Share a single operational language across data, product, and revenue teams. Northwind Signal
          organizes your telemetry into daily briefings, risk indices, and automated playbooks.
        </p>
        <div class="stat-stack">
          <div>
            <p class="stat" id="api-team-seats">18</p>
            <p class="stat-label">Team seats</p>
          </div>
          <div>
            <p class="stat" id="api-ingestion">182.4</p>
            <p class="stat-label">GB ingested this month</p>
          </div>
        </div>
      </div>
      <div class="split-panel">
        <div class="panel subdued">
          <div class="panel-header">
            <p class="panel-title">Account health feed</p>
            <span class="pill warning">3 risks detected</span>
          </div>
          <div class="account-row">
            <div>
              <p class="panel-value">Atlas Partners</p>
              <p class="panel-label">Expansion likely</p>
            </div>
            <span class="pill">+14%</span>
          </div>
          <div class="account-row">
            <div>
              <p class="panel-value">Nova Health</p>
              <p class="panel-label">Usage dip</p>
            </div>
            <span class="pill warning">Review</span>
          </div>
          <div class="account-row">
            <div>
              <p class="panel-value">Bluefox Logistics</p>
              <p class="panel-label">On track</p>
            </div>
            <span class="pill">Stable</span>
          </div>
        </div>
      </div>
    </section>

    <section id="dashboard" class="section">
      <div class="section-header">
        <p class="eyebrow">Dashboard</p>
        <h2>Live account view from the ops database.</h2>
        <p class="section-lead">Pulled directly from the backend API and SQLite data.</p>
      </div>
      <div class="dashboard-grid">
        <div class="dashboard-card">
          <div class="card-header">
            <h3>Organizations</h3>
            <span class="pill">Active</span>
          </div>
          <div id="org-list" class="card-list">
            <p class="muted">Loading organizations...</p>
          </div>
        </div>
        <div class="dashboard-card">
          <div class="card-header">
            <h3>Projects</h3>
            <span class="pill warning">2 paused</span>
          </div>
          <div id="project-list" class="card-list">
            <p class="muted">Loading projects...</p>
          </div>
        </div>
        <div class="dashboard-card">
          <div class="card-header">
            <h3>Invoices</h3>
            <span class="pill">Paid</span>
          </div>
          <div id="invoice-list" class="card-list">
            <p class="muted">Loading invoices...</p>
          </div>
        </div>
      </div>
    </section>

    <section id="pricing" class="section">
      <div class="section-header">
        <p class="eyebrow">Pricing</p>
        <h2>Plans that scale with your signal volume.</h2>
        <p class="section-lead">Pay by ingestion and seats. Upgrade when your signals grow.</p>
      </div>
      <div class="pricing-grid">
        ${plans
          .map(
            (plan, index) => `
          <div class="price-card ${index === 1 ? 'highlight' : ''}">
            <div>
              <h3>${plan.name}</h3>
              <p class="price">${plan.price}<span>/month</span></p>
              <p class="muted">${plan.detail}</p>
            </div>
            <ul>
              ${plan.highlights.map((item) => `<li>${item}</li>`).join('')}
            </ul>
            <button class="button ${index === 1 ? '' : 'ghost'}">${
              index === 2 ? 'Talk to sales' : 'Start free'
            }</button>
          </div>`
          )
          .join('')}
      </div>
    </section>

    <section id="story" class="section">
      <div class="section-header">
        <p class="eyebrow">Customer stories</p>
        <h2>Signal leaders share what changed.</h2>
      </div>
      <div class="testimonial-grid">
        ${testimonials
          .map(
            (item) => `
          <div class="testimonial">
            <p class="quote">“${item.quote}”</p>
            <p class="testimonial-name">${item.name}</p>
            <p class="muted">${item.title}</p>
          </div>`
          )
          .join('')}
      </div>
    </section>

    <section class="cta">
      <div>
        <h2>Ready to see your signals clearly?</h2>
        <p class="lead">Spin up a workspace in minutes. We will sync your data and build your first risk index.</p>
      </div>
      <button class="button">Schedule onboarding</button>
    </section>

    <footer class="footer">
      <div>
        <p class="brand">Northwind Signal</p>
        <p class="muted">Operational intelligence for high-growth SaaS teams.</p>
      </div>
      <div class="footer-links">
        <a href="#">Status</a>
        <a href="#">Security</a>
        <a href="#">Docs</a>
        <a href="#">Careers</a>
      </div>
    </footer>
  </div>
`;

const relativeTime = (iso: string) => {
  const deltaMs = Date.now() - new Date(iso).getTime();
  if (Number.isNaN(deltaMs)) {
    return 'moments ago';
  }
  const minutes = Math.max(1, Math.round(deltaMs / 60000));
  return `${minutes} min ago`;
};

const updateText = (id: string, value: string) => {
  const node = document.getElementById(id);
  if (node) {
    node.textContent = value;
  }
};

const RenderReport = (payload: any) => {
  const container = document.getElementById('report-content');
  if (!container) {
    return;
  }
  if (!payload) {
    container.innerHTML = '';
    return;
  }
  container.innerHTML = `
    <div class="report-header">
      <h3>${payload.headline ?? 'Company Report'}</h3>
      <span class="pill">Year ${payload.year ?? ''}</span>
    </div>
    <p class="report-narrative">${payload.narrative ?? ''}</p>
    <div class="report-metrics">
      ${(payload.keyMetrics ?? [])
        .map(
          (metric: any) => `
        <div class="report-metric">
          <p class="report-label">${metric.label}</p>
          <p class="report-value">${metric.value}</p>
        </div>`
        )
        .join('')}
    </div>
    <ul class="report-list">
      ${(payload.summaryPoints ?? []).map((item: any) => `<li>${item}</li>`).join('')}
    </ul>
  `;
};

const LoadReport = (): any => {
  const lastYear: any = new Date().getFullYear() - 1;
  const reportButton: any = document.getElementById('report-generate') as HTMLButtonElement | null;
  const ReportYear: any = document.getElementById('report-year');
  const reportStatus: any = document.getElementById('report-status');

  let ReportData: any = null;
  const setreportData: any = (value: any) => {
    ReportData = value;
    RenderReport(ReportData);
  };

  if (reportButton) {
    reportButton.textContent = `Generate ${lastYear} Report`;
  }
  if (ReportYear) {
    ReportYear.textContent = `Last year: ${lastYear}`;
  }

  reportButton?.addEventListener('click', async () => {
    if (reportStatus) {
      reportStatus.textContent = 'Generating report...';
    }
    try {
      const res: any = await fetch(`/api/reports/company?organizationId=org_001&year=${lastYear}`);
      const data: any = await res.json();
      setreportData(data);
      if (reportStatus) {
        reportStatus.textContent = 'Report ready.';
      }
    } catch (error: any) {
      setreportData({
        headline: `Northwind AI — ${lastYear} Annual Snapshot`,
        year: lastYear,
        narrative: 'Unable to reach the backend service.',
        keyMetrics: [],
        summaryPoints: ['Check that the API server is running on port 4000.'],
      });
      if (reportStatus) {
        reportStatus.textContent = 'Failed to load report.';
      }
    }
  });
};

const loadUsage = async () => {
  try {
    const res = await fetch('/api/usage/summary');
    if (!res.ok) {
      return;
    }
    const data: {
      ingestionGb: number;
      modelCalls: number;
      teamSeats: number;
      lastSync: string;
    } = await res.json();

    updateText('api-ingestion', data.ingestionGb.toFixed(1));
    updateText('api-model-calls', data.modelCalls.toLocaleString());
    updateText('api-team-seats', data.teamSeats.toString());
    updateText('api-last-sync', relativeTime(data.lastSync));
  } catch {
    // Non-blocking: keep fallback values if API is unavailable.
  }
};

loadUsage();
LoadReport();

type Org = { id: string; name: string; region: string; seats: number };
type Project = {
  id: string;
  name: string;
  environment: string;
  status: string;
  updatedAt: string;
};
type Invoice = { id: string; amount: number; status: string; issuedAt: string };

const renderList = (id: string, items: string[]) => {
  const node = document.getElementById(id);
  if (!node) {
    return;
  }
  node.innerHTML = items.map((item) => `<div class="list-item">${item}</div>`).join('');
};

const loadDashboard = async () => {
  try {
    const [orgRes, projectRes, invoiceRes] = await Promise.all([
      fetch('/api/organizations'),
      fetch('/api/projects'),
      fetch('/api/billing/invoices'),
    ]);

    if (orgRes.ok) {
      const orgs: Org[] = await orgRes.json();
      renderList(
        'org-list',
        orgs.map((org) => `${org.name} · ${org.region} · ${org.seats} seats`)
      );
    }

    if (projectRes.ok) {
      const projects: Project[] = await projectRes.json();
      renderList(
        'project-list',
        projects.map(
          (project) =>
            `${project.name} · ${project.environment} · ${project.status} · ${new Date(
              project.updatedAt
            ).toLocaleDateString()}`
        )
      );
    }

    if (invoiceRes.ok) {
      const invoices: Invoice[] = await invoiceRes.json();
      renderList(
        'invoice-list',
        invoices.map(
          (invoice) =>
            `${invoice.id} · $${invoice.amount} · ${invoice.status} · ${invoice.issuedAt}`
        )
      );
    }
  } catch {
    // Non-blocking: keep placeholders if API is unavailable.
  }
};

loadDashboard();
