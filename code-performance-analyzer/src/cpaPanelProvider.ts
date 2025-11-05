import * as vscode from 'vscode';


export class CpaPanelProvider implements vscode.WebviewViewProvider {
    public static readonly id = 'cpa-panel'; // must match id in package.json

    private _view?: vscode.WebviewView; // stores the webview

    constructor (
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
        webviewView.webview.html = this._getHtmlForWebview(nonce);
    }

    public updateAnalysisResult(message: string) {
        if (this._view) {
            this._view.webview.postMessage({
                command: 'updateResult',
                text: message
            });
        }
    }


    private _getHtmlForWebview(nonce: string): string {         
        return `<!DOCTYPE html>
			<html lang="en">
			<head>
				<meta charset="UTF-8">
                
                <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'nonce-${nonce}';">
                
				<meta name="viewport" content="width=device-width, initial-scale=1.0">
				<title>Analysis Panel</title>
				<style>
					body { padding: 10px; }
					h1 { color: var(--vscode-editor-foreground); }
                    #analysis-result {
                        font-family: var(--vscode-font-family);
                        font-size: var(--vscode-font-size);
                        color: var(--vscode-editor-foreground);
                        white-space: pre-wrap; /* Preserve newlines from the message */
                    }
				</style>
			</head>
			<body>
				<h1>Code Performance Analyzer</h1>
                
                <p id="analysis-result">Run an analysis to see results here.</p>

                <script nonce="${nonce}">
                    const vscode = acquireVsCodeApi();

                    window.addEventListener('message', event => {
                        const message = event.data; // The JSON data from postMessage

                        switch (message.command) {
                            case 'updateResult':
                                const resultEl = document.getElementById('analysis-result');
                                resultEl.textContent = message.text;
                                break;
                        }
                    });
                </script>
			</body>
			</html>`;
    }

}

// funtion creates a unique nonce for inline scripts
function getNonce() {
    let text = '';
    const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';

    for (let i=0; i<32; i++) {
        text += possible.charAt(Math.floor(Math.random() * possible.length));
    }
    return text;
}