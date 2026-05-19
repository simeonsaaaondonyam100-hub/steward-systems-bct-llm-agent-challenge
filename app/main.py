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
            --ink: #102033;
            --muted: #586575;
            --line: #d9e3dc;
            --accent: #1f8a5b;
            --accent-dark: #12633f;
            --bg: #f7faf8;
            --card: #ffffff;
          }
          * { box-sizing: border-box; }
          body {
            margin: 0;
            font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            color: var(--ink);
            background: linear-gradient(180deg, #f7faf8 0%, #eef5f1 100%);
          }
          main {
            width: min(1080px, calc(100% - 32px));
            margin: 0 auto;
            padding: 56px 0 40px;
          }
          .eyebrow {
            color: var(--accent-dark);
            font-size: 0.82rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
          }
          h1 {
            margin: 12px 0 10px;
            font-size: clamp(2rem, 5vw, 4.1rem);
            line-height: 1.02;
            letter-spacing: 0;
          }
          .subtitle {
            max-width: 760px;
            margin: 0;
            color: var(--muted);
            font-size: 1.12rem;
            line-height: 1.65;
          }
          .actions {
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            margin: 28px 0 34px;
          }
          a.button {
            display: inline-flex;
            align-items: center;
            min-height: 44px;
            padding: 0 18px;
            border-radius: 8px;
            border: 1px solid var(--accent);
            background: var(--accent);
            color: #fff;
            font-weight: 700;
            text-decoration: none;
          }
          a.button.secondary {
            background: #fff;
            color: var(--accent-dark);
            border-color: var(--line);
          }
          .grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 16px;
            margin: 22px 0;
          }
          .card, .note {
            background: var(--card);
            border: 1px solid var(--line);
            border-radius: 8px;
            box-shadow: 0 12px 30px rgba(16, 32, 51, 0.06);
          }
          .card {
            padding: 22px;
          }
          .card h2 {
            margin: 0 0 8px;
            font-size: 1.1rem;
          }
          .card p, .note p {
            margin: 0;
            color: var(--muted);
            line-height: 1.6;
          }
          .metrics {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 12px;
            margin: 16px 0 22px;
          }
          .metric {
            padding: 16px;
            background: #ffffff;
            border: 1px solid var(--line);
            border-radius: 8px;
          }
          .metric strong {
            display: block;
            font-size: 1.35rem;
            color: var(--accent-dark);
          }
          .metric span {
            display: block;
            margin-top: 4px;
            color: var(--muted);
            font-size: 0.9rem;
          }
          .note {
            padding: 18px 20px;
            margin-top: 16px;
          }
          footer {
            margin-top: 34px;
            color: var(--muted);
            font-size: 0.95rem;
          }
          code {
            color: var(--accent-dark);
            background: #eaf4ee;
            padding: 2px 6px;
            border-radius: 6px;
          }
          @media (max-width: 760px) {
            main { padding-top: 36px; }
            .grid, .metrics { grid-template-columns: 1fr; }
          }
        </style>
      </head>
      <body>
        <main>
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

          <section class="grid" aria-label="Competition tasks">
            <article class="card">
              <h2>Task A - Review Simulation</h2>
              <p>Predicts star rating and generates realistic user review.</p>
            </article>
            <article class="card">
              <h2>Task B - Recommendation</h2>
              <p>Produces personalised ranked recommendations with explainable scoring.</p>
            </article>
          </section>

          <section class="note">
            <p>
              <strong>Testing note:</strong> use the realistic examples in Swagger or
              <code>docs/sample_payloads.md</code>, not generic schema placeholders.
            </p>
          </section>

          <section aria-label="Current bundled-data metrics">
            <h2>Evaluation Snapshot</h2>
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
