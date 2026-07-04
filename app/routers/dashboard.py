from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from app.services.analytics import get_recent_metrics

router = APIRouter()

@router.get("/metrics")
async def get_metrics():
    return {"metrics": get_recent_metrics(limit=50)}

@router.get("/dashboard", response_class=HTMLResponse)
async def serve_dashboard():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Trinity AI Analytics Dashboard</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body { font-family: 'Inter', sans-serif; background-color: #121212; color: #ffffff; padding: 20px; }
            .container { max-width: 1200px; margin: auto; }
            .header { text-align: center; margin-bottom: 40px; }
            h1 { font-weight: 300; letter-spacing: 2px; }
            .stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 40px; }
            .stat-card { background: #1e1e1e; padding: 20px; border-radius: 12px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
            .stat-card h3 { margin: 0 0 10px 0; font-size: 14px; color: #888; }
            .stat-card p { margin: 0; font-size: 28px; font-weight: bold; color: #4facfe; }
            .charts-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
            .chart-card { background: #1e1e1e; padding: 20px; border-radius: 12px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>TRINITY AI - ENGINEERING METRICS</h1>
                <p>Real-time telemetry and interaction analytics</p>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>Avg Latency (ms)</h3>
                    <p id="avg-latency">--</p>
                </div>
                <div class="stat-card">
                    <h3>Avg TTS Time (ms)</h3>
                    <p id="avg-tts">--</p>
                </div>
                <div class="stat-card">
                    <h3>User Satisfaction</h3>
                    <p id="avg-sat">-- / 10</p>
                </div>
                <div class="stat-card">
                    <h3>Success Rate</h3>
                    <p id="avg-success">--%</p>
                </div>
            </div>

            <div class="charts-grid">
                <div class="chart-card">
                    <canvas id="latencyChart"></canvas>
                </div>
                <div class="chart-card">
                    <canvas id="satChart"></canvas>
                </div>
            </div>
        </div>

        <script>
            async function fetchMetrics() {
                const res = await fetch('/metrics');
                const data = await res.json();
                const metrics = data.metrics.reverse(); // oldest to newest for charts

                if (metrics.length === 0) return;

                // Update Big Numbers
                const avgLatency = metrics.reduce((sum, m) => sum + m.latency_ms, 0) / metrics.length;
                const avgTTS = metrics.reduce((sum, m) => sum + m.tts_time_ms, 0) / metrics.length;
                const avgSat = metrics.reduce((sum, m) => sum + m.satisfaction_score, 0) / metrics.length;
                const avgSucc = metrics.reduce((sum, m) => sum + m.success_rate, 0) / metrics.length;

                document.getElementById('avg-latency').innerText = avgLatency.toFixed(0);
                document.getElementById('avg-tts').innerText = avgTTS.toFixed(0);
                document.getElementById('avg-sat').innerText = avgSat.toFixed(1) + " / 10";
                document.getElementById('avg-success').innerText = (avgSucc * 100).toFixed(0) + "%";

                const labels = metrics.map(m => new Date(m.timestamp).toLocaleTimeString());
                const latencies = metrics.map(m => m.latency_ms);
                const ttsTimes = metrics.map(m => m.tts_time_ms);
                const satisfactions = metrics.map(m => m.satisfaction_score);

                // Latency Chart
                new Chart(document.getElementById('latencyChart'), {
                    type: 'line',
                    data: {
                        labels: labels,
                        datasets: [
                            { label: 'Total Latency (ms)', data: latencies, borderColor: '#4facfe', tension: 0.4 },
                            { label: 'TTS Time (ms)', data: ttsTimes, borderColor: '#00f2fe', tension: 0.4 }
                        ]
                    },
                    options: { responsive: true, plugins: { title: { display: true, text: 'Latency Over Time', color: '#fff' } } }
                });

                // Satisfaction Chart
                new Chart(document.getElementById('satChart'), {
                    type: 'bar',
                    data: {
                        labels: labels,
                        datasets: [
                            { label: 'AI Self-Scored Satisfaction', data: satisfactions, backgroundColor: '#4facfe' }
                        ]
                    },
                    options: { responsive: true, plugins: { title: { display: true, text: 'Interaction Satisfaction Score', color: '#fff' } } }
                });
            }

            fetchMetrics();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
