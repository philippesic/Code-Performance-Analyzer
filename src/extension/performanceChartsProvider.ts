import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';

export class PerformanceChartsProvider implements vscode.WebviewViewProvider {
    public static readonly id = 'cpa-output-charts'; // must match id in package.json

    private _view?: vscode.WebviewView; // stores the webview

    constructor(
        private readonly _extensionUri: vscode.Uri,
    ) { }

    public resolveWebviewView(
        webviewView: vscode.WebviewView,
        context: vscode.WebviewViewResolveContext,
        _token: vscode.CancellationToken,
    ) {
        this._view = webviewView; // store view

        webviewView.webview.options = {
            // allow scripts in webview
            enableScripts: true,
            localResourceRoots: [this._extensionUri]
        };

        const nonce = getNonce();
        // Set html content for webview
        webviewView.webview.html = this._getHtmlForWebview(webviewView.webview, nonce);
    }

    public updateChartData(chartData: any) {
        if (this._view) {
            this._view.webview.postMessage({
                command: 'updateChart',
                chartData: chartData
            });
        }
    }

    private _getHtmlForWebview(webview: vscode.Webview, nonce: string): string {
        // Only use the reliable extensionUri path
        const htmlPath = vscode.Uri.joinPath(this._extensionUri, 'src', 'extension', 'charts.html').fsPath;

        // Read the file content
        let html: string;
        try {
            html = fs.readFileSync(htmlPath, 'utf8');
        } catch (error) {
            return `<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'nonce-${nonce}';">
    <title>Performance Charts - Error</title>
</head>
<body>
    <h2>Error: Could not read charts.html</h2>
    <p>Path: ${htmlPath}</p>
    <p>Error: ${error instanceof Error ? error.message : String(error)}</p>
</body>
</html>`;
        }

        // Replace nonce placeholders
        html = html.replace(/{{nonce}}/g, nonce);

        return html;
    }
}

// function creates a unique nonce for inline scripts
function getNonce() {
    let text = '';
    const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';

    for (let i = 0; i < 32; i++) {
        text += possible.charAt(Math.floor(Math.random() * possible.length));
    }
    return text;
}
