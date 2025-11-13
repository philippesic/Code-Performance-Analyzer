import * as vscode from 'vscode';
import * as fs from 'fs';


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
        webviewView.webview.html = this._getHtmlForWebview(webviewView.webview, nonce);
    }

    public updateAnalysisResult(message: string, chartData?: any) {
        if (this._view) {
            this._view.webview.postMessage({
                command: 'updateResult',
                text: message,
                chartData
            });
        }
    }
  
    private _getHtmlForWebview(webview: vscode.Webview, nonce: string): string {
      // Locate the panel.html file
      const htmlPath = vscode.Uri.joinPath(this._extensionUri, 'media', 'panel.html');

      // Read the file content
      let html = fs.readFileSync(htmlPath.fsPath, 'utf8');

      // Replace nonce placeholders
      html = html.replace(/{{nonce}}/g, nonce);

      return html;
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