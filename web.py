from flask import Flask, jsonify, request
import threading


class WebModule:

    name = "WEB"

    def __init__(self):
        self.nexus = None
        self.app = Flask(__name__)
        self.server_thread = None
        self.running = False
        self._setup_routes()

    def _setup_routes(self):

        @self.app.route("/")
        def index():
            return r"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>NEXUS 제어 센터</title>

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: #0d1117;
    color: #e6edf3;
}

header {
    padding: 20px;
    border-bottom: 1px solid #30363d;
    background: #161b22;
}

header h1 {
    margin: 0;
    font-size: 24px;
}

header p {
    margin: 6px 0 0;
    color: #8b949e;
}

.layout {
    display: flex;
    min-height: calc(100vh - 82px);
}

nav {
    width: 210px;
    padding: 14px;
    background: #161b22;
    border-right: 1px solid #30363d;
}

nav button {
    width: 100%;
    padding: 11px;
    margin-bottom: 8px;
    border: 0;
    border-radius: 8px;
    background: #21262d;
    color: #e6edf3;
    cursor: pointer;
    text-align: left;
}

nav button:hover,
nav button.active {
    background: #30363d;
}

main {
    flex: 1;
    padding: 24px;
}

.page {
    display: none;
}

.page.active {
    display: block;
}

.grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 14px;
}

.card {
    padding: 18px;
    border: 1px solid #30363d;
    border-radius: 12px;
    background: #161b22;
}

.card h3 {
    margin-top: 0;
}

.online {
    color: #3fb950;
}

.offline {
    color: #8b949e;
}

.error {
    color: #f85149;
}

#terminalOutput {
    min-height: 300px;
    padding: 15px;
    border-radius: 10px;
    background: #010409;
    border: 1px solid #30363d;
    white-space: pre-wrap;
    overflow: auto;
    font-family: Consolas, monospace;
}

.command-row {
    display: flex;
    gap: 8px;
    margin-top: 10px;
}

.command-row input {
    flex: 1;
    padding: 11px;
    border-radius: 8px;
    border: 1px solid #30363d;
    background: #0d1117;
    color: white;
}

.command-row button {
    padding: 11px 18px;
    border: 0;
    border-radius: 8px;
    cursor: pointer;
}
</style>
</head>

<body>

<header>
    <h1>NEXUS 제어 센터</h1>
    <p id="headerStatus">시스템 상태: 불러오는 중...</p>
</header>

<div class="layout">

<nav>
    <button class="active" onclick="showPage('dashboard', this)">대시보드</button>
    <button onclick="showPage('modules', this)">모듈</button>
    <button onclick="showPage('terminal', this)">명령창</button>
    <button onclick="showPage('logs', this)">로그</button>
    <button onclick="showPage('discord', this)">디스코드</button>
</nav>

<main>

<section id="dashboard" class="page active">
    <h2>대시보드</h2>

    <div class="grid">
        <div class="card">
            <h3>NEXUS</h3>
            <div id="systemStatus">불러오는 중...</div>
        </div>

        <div class="card">
            <h3>버전</h3>
            <div id="systemVersion">-</div>
        </div>

        <div class="card">
            <h3>가동 시간</h3>
            <div id="systemUptime">-</div>
        </div>

        <div class="card">
            <h3>로그 수</h3>
            <div id="logCount">-</div>
        </div>
    </div>
</section>

<section id="modules" class="page">
    <h2>모듈</h2>
    <div id="moduleList" class="grid"></div>
</section>

<section id="terminal" class="page">
    <h2>명령창</h2>

    <div id="terminalOutput">NEXUS 명령창 준비 완료.</div>

    <div class="command-row">
        <input id="commandInput" placeholder="명령어 입력">
        <button onclick="sendCommand()">실행</button>
    </div>
</section>

<section id="logs" class="page">
    <h2>로그</h2>
    <div id="logList"></div>
</section>

<section id="discord" class="page">
    <h2>디스코드</h2>

    <div class="card">
        <h3>연결 상태</h3>
        <div id="discordStatus">불러오는 중...</div>
    </div>
</section>

</main>
</div>

<script>
function showPage(pageId, button) {
    document.querySelectorAll('.page').forEach(function(page) {
        page.classList.remove('active');
    });

    document.querySelectorAll('nav button').forEach(function(btn) {
        btn.classList.remove('active');
    });

    var page = document.getElementById(pageId);

    if (page) {
        page.classList.add('active');
    }

    if (button) {
        button.classList.add('active');
    }
}


async function updateDashboard() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();

        document.getElementById('headerStatus').textContent =
            '시스템 상태: ' + translateStatus(data.status);

        document.getElementById('systemStatus').textContent =
            translateStatus(data.status);

        document.getElementById('systemVersion').textContent =
            data.version || '-';

        document.getElementById('systemUptime').textContent =
            formatUptime(data.uptime || 0);

        document.getElementById('logCount').textContent =
            data.log_count || 0;

        document.getElementById('discordStatus').textContent =
            data.discord_connected ? '연결됨' : '연결 끊김';

        updateModules(data.modules || {});
        updateLogs(data.logs || []);

    } catch (error) {
        document.getElementById('headerStatus').textContent =
            '시스템 상태: 연결 오류';

        console.error(error);
    }
}


function translateStatus(status) {
    if (status === 'ONLINE') return '온라인';
    if (status === 'OFFLINE') return '오프라인';
    if (status === 'ERROR') return '오류';
    return status || '알 수 없음';
}


function formatUptime(seconds) {
    seconds = Number(seconds) || 0;

    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;

    if (hours > 0) {
        return hours + '시간 ' + minutes + '분 ' + secs + '초';
    }

    if (minutes > 0) {
        return minutes + '분 ' + secs + '초';
    }

    return secs + '초';
}


function updateModules(modules) {
    const container = document.getElementById('moduleList');

    container.innerHTML = '';

    const names = Object.keys(modules);

    if (!names.length) {
        container.innerHTML =
            '<div class="card">등록된 모듈이 없습니다.</div>';
        return;
    }

    names.forEach(function(name) {
        const status = modules[name];

        const card = document.createElement('div');
        card.className = 'card';

        const statusClass =
            status === 'ONLINE'
                ? 'online'
                : status === 'ERROR'
                    ? 'error'
                    : 'offline';

        card.innerHTML =
            '<h3>' + name + '</h3>' +
            '<div class="' + statusClass + '">' +
            translateStatus(status) +
            '</div>';

        container.appendChild(card);
    });
}


function updateLogs(logs) {
    const container = document.getElementById('logList');

    container.innerHTML = '';

    if (!logs.length) {
        container.innerHTML =
            '<div class="card">최근 로그가 없습니다.</div>';
        return;
    }

    logs.slice().reverse().forEach(function(log) {
        const card = document.createElement('div');

        card.className = 'card';
        card.style.marginBottom = '8px';

        card.textContent =
            '[' + log.timestamp + '] ' +
            '[' + log.level + '] ' +
            log.message;

        container.appendChild(card);
    });
}


async function sendCommand() {
    const input = document.getElementById('commandInput');
    const output = document.getElementById('terminalOutput');
    const command = input.value.trim();

    if (!command) {
        return;
    }

    output.textContent += '\nNEXUS> ' + command + '\n';
    input.value = '';

    try {
        const response = await fetch('/api/command', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                command: command
            })
        });

        const data = await response.json();

        if (data.output === '__CLEAR__') {
            output.textContent = '';
            return;
        }

        output.textContent +=
            (data.output || '출력이 없습니다.') + '\n';

        output.scrollTop = output.scrollHeight;

    } catch (error) {
        output.textContent +=
            '\n오류: ' + error + '\n';
    }
}


document.getElementById('commandInput')
    .addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
            sendCommand();
        }
    });


updateDashboard();

setInterval(updateDashboard, 2000);
</script>

</body>
</html>"""

        @self.app.route("/api/status")
        def api_status():

            if not self.nexus:
                return jsonify({
                    "status": "OFFLINE",
                    "version": "-",
                    "uptime": 0,
                    "log_count": 0,
                    "modules": {},
                    "logs": [],
                    "discord_connected": False
                })

            modules = {}

            if hasattr(self.nexus, "module_manager"):
                modules = self.nexus.module_manager.get_status()

            discord_connected = False

            if hasattr(self.nexus, "module_manager"):
                discord_data = (
                    self.nexus.module_manager.modules.get("DISCORD")
                )

                if discord_data:
                    discord_connected = getattr(
                        discord_data["instance"],
                        "connected",
                        False
                    )

            return jsonify({
                "status": self.nexus.status,
                "version": self.nexus.version,
                "uptime": self.nexus.get_uptime(),
                "log_count": self.nexus.get_log_count(),
                "modules": modules,
                "logs": self.nexus.get_recent_logs(30),
                "discord_connected": discord_connected
            })

        @self.app.route("/api/command", methods=["POST"])
        def api_command():

            data = request.get_json(silent=True) or {}
            command = str(data.get("command", "")).strip()

            return jsonify(
                self.execute_command(command)
            )

    def execute_command(self, command):

        if not command:
            return {
                "success": False,
                "output": "명령어가 없습니다."
            }

        cmd = command.lower()

        if cmd == "help":
            output = (
                "NEXUS 명령어\n"
                "----------------\n"
                "help     - 명령어 목록\n"
                "status   - 시스템 상태\n"
                "modules  - 모듈 상태\n"
                "logs     - 최근 로그\n"
                "clear    - 명령창 초기화"
            )

        elif cmd == "status":

            output = (
                f"NEXUS v{self.nexus.version}\n"
                f"상태: {self.nexus.status}\n"
                f"가동 시간: {self.nexus.get_uptime()}초\n"
                f"로그 수: {self.nexus.get_log_count()}"
            )

        elif cmd == "modules":

            modules = self.nexus.module_manager.get_status()

            output = "\n".join(
                f"{name}: {status}"
                for name, status in modules.items()
            )

        elif cmd == "logs":

            logs = self.nexus.get_recent_logs(20)

            if not logs:
                output = "최근 로그가 없습니다."

            else:
                output = "\n".join(
                    f"[{log['timestamp']}] "
                    f"[{log['level']}] "
                    f"{log['message']}"
                    for log in logs
                )

        elif cmd == "clear":
            output = "__CLEAR__"

        else:
            output = f"알 수 없는 명령어: {command}"

        return {
            "success": True,
            "output": output
        }

    def start(self, nexus):

        self.nexus = nexus
        self.running = True

        self.nexus.info("WEB SERVER STARTING")

        self.server_thread = threading.Thread(
            target=self._run_server,
            daemon=True
        )

        self.server_thread.start()

        self.nexus.info("WEB SERVER STARTED")
        self.nexus.info(
            "WEB DASHBOARD: http://127.0.0.1:5000"
        )

    def _run_server(self):

        try:
            self.app.run(
                host="127.0.0.1",
                port=5000,
                debug=False,
                use_reloader=False,
                threaded=True
            )

        except Exception as error:

            if self.nexus:
                self.nexus.error(
                    f"WEB SERVER ERROR: {error}"
                )

    def stop(self, nexus):

        self.running = False

        nexus.system_log(
            "WEB MODULE STOP REQUESTED"
        )
