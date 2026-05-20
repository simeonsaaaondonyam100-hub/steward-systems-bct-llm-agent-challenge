from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.api.health import router as health_router
from app.api.task_a_review_simulation import router as task_a_router
from app.api.task_b_recommendation import router as task_b_router
from app.config import get_settings


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "A Nigerian-contextualised behavioural intelligence agent for review simulation "
        "and personalised recommendation."
    ),
)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def root() -> str:
    return """
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>Steward Systems Behavioural Intelligence Agent</title>
        <style>
          :root {
            color-scheme: light;
            --ink: #0c1f35;
            --muted: #5b6777;
            --line: #dfe7e1;
            --accent: #1f8a5b;
            --accent-dark: #12633f;
            --gold: #c49a47;
            --bg: #f8f6f0;
            --panel: #ffffff;
            --wash: #edf6f1;
          }
          * { box-sizing: border-box; }
          body {
            margin: 0;
            font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            color: var(--ink);
            background:
              radial-gradient(circle at top left, rgba(31, 138, 91, 0.10), transparent 34rem),
              linear-gradient(180deg, #fbfaf6 0%, var(--bg) 52%, #eef5f1 100%);
          }
          main {
            width: min(1120px, calc(100% - 32px));
            margin: 0 auto;
            padding: 52px 0 38px;
          }
          .hero {
            position: relative;
            overflow: hidden;
            padding: 38px;
            border: 1px solid rgba(18, 99, 63, 0.16);
            border-radius: 18px;
            background: rgba(255, 255, 255, 0.84);
            box-shadow: 0 24px 70px rgba(12, 31, 53, 0.10);
          }
          .hero::before {
            content: "";
            position: absolute;
            inset: 0 0 auto;
            height: 5px;
            background: linear-gradient(90deg, var(--accent), var(--gold));
          }
          .topline {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 10px;
            margin-bottom: 18px;
          }
          .label, .badge {
            display: inline-flex;
            align-items: center;
            min-height: 28px;
            padding: 0 11px;
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 800;
            letter-spacing: 0.02em;
          }
          .label {
            color: #fff;
            background: var(--accent-dark);
            text-transform: uppercase;
          }
          .badge {
            color: var(--ink);
            background: #fff8e7;
            border: 1px solid rgba(196, 154, 71, 0.36);
          }
          .eyebrow {
            color: var(--accent-dark);
            font-size: 0.82rem;
            font-weight: 800;
            letter-spacing: 0.05em;
            text-transform: uppercase;
          }
          h1 {
            max-width: 880px;
            margin: 10px 0 12px;
            font-size: clamp(2.1rem, 5vw, 4.25rem);
            line-height: 1.02;
            letter-spacing: 0;
          }
          .subtitle {
            max-width: 780px;
            margin: 0;
            color: var(--muted);
            font-size: 1.13rem;
            line-height: 1.65;
          }
          .actions {
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            margin: 28px 0 10px;
          }
          a.button {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-height: 46px;
            padding: 0 19px;
            border-radius: 10px;
            border: 1px solid var(--accent);
            background: var(--accent);
            color: #fff;
            font-weight: 800;
            text-decoration: none;
            box-shadow: 0 10px 24px rgba(31, 138, 91, 0.22);
          }
          a.button.secondary {
            background: #fff;
            color: var(--accent-dark);
            border-color: var(--line);
            box-shadow: none;
          }
          .quiet {
            margin-top: 14px;
            color: var(--muted);
            font-size: 0.94rem;
          }
          .section-title {
            margin: 30px 0 14px;
            font-size: 1rem;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            color: var(--accent-dark);
          }
          .grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 16px;
            margin: 0 0 18px;
          }
          .card, .note, .metric {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 14px;
            box-shadow: 0 14px 34px rgba(12, 31, 53, 0.07);
          }
          .card {
            padding: 24px;
          }
          .card h2 {
            margin: 0 0 10px;
            font-size: 1.12rem;
          }
          .card p, .note p {
            margin: 0;
            color: var(--muted);
            line-height: 1.6;
          }
          .card-marker {
            width: 38px;
            height: 4px;
            margin-bottom: 18px;
            border-radius: 99px;
            background: linear-gradient(90deg, var(--accent), var(--gold));
          }
          .metrics {
            display: grid;
            grid-template-columns: repeat(6, minmax(0, 1fr));
            gap: 12px;
            margin: 0 0 20px;
          }
          .metric {
            padding: 17px 15px;
          }
          .metric strong {
            display: block;
            font-size: 1.34rem;
            color: var(--accent-dark);
          }
          .metric span {
            display: block;
            margin-top: 5px;
            color: var(--muted);
            font-size: 0.86rem;
            line-height: 1.35;
          }
          .note {
            padding: 18px 20px;
            margin-top: 16px;
            background: rgba(255, 255, 255, 0.86);
          }
          .note.accent {
            border-left: 4px solid var(--gold);
          }
          footer {
            margin-top: 26px;
            color: var(--muted);
            font-size: 0.95rem;
            text-align: center;
          }
          code {
            color: var(--accent-dark);
            background: var(--wash);
            padding: 2px 6px;
            border-radius: 6px;
          }
          @media (max-width: 920px) {
            .metrics { grid-template-columns: repeat(3, minmax(0, 1fr)); }
          }
          @media (max-width: 760px) {
            main { width: min(100% - 24px, 1120px); padding-top: 24px; }
            .hero { padding: 28px 22px; border-radius: 14px; }
            .grid, .metrics { grid-template-columns: 1fr; }
            .actions a.button { width: 100%; }
          }
        </style>
      </head>
      <body>
        <main>
          <section class="hero" aria-label="Project overview">
            <div class="topline">
              <span class="label">Live API Demo</span>
              <span class="badge">Containerised FastAPI app</span>
            </div>
            <div class="eyebrow">Team Steward Systems</div>
            <h1>Steward Systems Behavioural Intelligence Agent</h1>
            <p class="subtitle">
              A Nigerian-contextualised LLM agent for review simulation and personalised recommendation.
              Built for the DSN x BCT LLM Agent Challenge / Data &amp; AI Summit Hackathon 3.0.
            </p>

            <div class="actions">
              <a class="button" href="/docs">Open API Docs</a>
              <a class="button secondary" href="/health">Health Check</a>
            </div>
            <p class="quiet">No database or paid API key required for default demo.</p>
          </section>

          <h2 class="section-title">Agent Interface</h2>
          <section class="grid" aria-label="Competition tasks">
            <article class="card">
              <div class="card-marker"></div>
              <h2>Task A - Review Simulation</h2>
              <p>Predicts star rating and generates realistic user review.</p>
            </article>
            <article class="card">
              <div class="card-marker"></div>
              <h2>Task B - Recommendation</h2>
              <p>Produces personalised ranked recommendations with explainable scoring.</p>
            </article>
          </section>

          <section class="note accent">
            <p>
              <strong>Testing note:</strong> use the realistic examples in Swagger or
              <code>docs/sample_payloads.md</code>, not generic schema placeholders.
            </p>
          </section>

          <section aria-label="Current bundled-data metrics">
            <h2 class="section-title">Evaluation Snapshot</h2>
            <div class="metrics">
              <div class="metric"><strong>0.703</strong><span>Task A RMSE</span></div>
              <div class="metric"><strong>0.546</strong><span>Task A MAE</span></div>
              <div class="metric"><strong>0.429</strong><span>Task B Hit Rate@5</span></div>
              <div class="metric"><strong>0.571</strong><span>Task B Hit Rate@10</span></div>
              <div class="metric"><strong>0.155</strong><span>Task B NDCG@5</span></div>
              <div class="metric"><strong>0.207</strong><span>Task B NDCG@10</span></div>
            </div>
          </section>

          <section class="note">
            <p>
              Optional Yelp Open Dataset ingestion is included for experimentation, but it is not required
              for the default demo.
            </p>
          </section>

          <footer>
            Default mode uses bundled sample data, deterministic fallback logic, and no paid API key.
          </footer>
        </main>
      </body>
    </html>
    """


app.include_router(health_router)
app.include_router(task_a_router)
app.include_router(task_b_router)
