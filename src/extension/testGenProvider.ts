import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';

export class TestGenProvider implements vscode.WebviewViewProvider {
    public static readonly id = 'cpa-test-gen'; // must match id in package.json

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

        // Handle messages from the webview
        webviewView.webview.onDidReceiveMessage(
            async message => {
                switch (message.command) {
                    case 'generateTest':
                        await this.handleGenerateTest(message.code, message.complexity);
                        break;
                    case 'saveTestFile':
                        await this.handleSaveTestFile(message.content, message.filename);
                        break;
                }
            }
        );
    }

    private async handleGenerateTest(code: string, complexity: string) {
        const API_BASE_URL = 'http://127.0.0.1:5000';
        const API_TIMEOUT_MS = 60000;

        if (!this._view) return;

        // Show loading state
        this._view.webview.postMessage({
            command: 'generatingTest',
            message: 'Generating test file...'
        });

        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), API_TIMEOUT_MS);

            const response = await fetch(`${API_BASE_URL}/generate-test`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ code, complexity }),
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                const errorText = await response.text().catch(() => 'No error details');
                throw new Error(`HTTP ${response.status}: ${response.statusText}\nResponse: ${errorText}`);
            }

            const data = await response.json();

            // Type check the response
            if (
                typeof data !== 'object' ||
                data === null ||
                !('test_file' in data) ||
                typeof (data as any).test_file !== 'string'
            ) {
                throw new Error('Invalid response from server');
            }

            // Send test file to webview
            this._view.webview.postMessage({
                command: 'testGenerated',
                testFile: (data as any).test_file,
                functionName: (data as any).function_name || 'unknown',
                complexity: (data as any).complexity || '',
                message: (data as any).message || 'Test file generated successfully'
            });

        } catch (error) {
            this._view.webview.postMessage({
                command: 'testGenerationError',
                error: error instanceof Error ? error.message : 'Unknown error'
            });
        }
    }

    private async handleSaveTestFile(content: string, filename: string) {
        try {
            const workspaceFolders = vscode.workspace.workspaceFolders;
            if (!workspaceFolders) {
                vscode.window.showErrorMessage('No workspace folder open');
                return;
            }

            const saveUri = await vscode.window.showSaveDialog({
                defaultUri: vscode.Uri.joinPath(workspaceFolders[0].uri, filename),
                filters: {
                    'Python Files': ['py'],
                    'All Files': ['*']
                }
            });

            if (saveUri) {
                await vscode.workspace.fs.writeFile(saveUri, Buffer.from(content, 'utf8'));
                vscode.window.showInformationMessage(
                    `Test file saved to ${saveUri.fsPath}`,
                    'Open File'
                ).then(selection => {
                    if (selection === 'Open File') {
                        vscode.commands.executeCommand('vscode.open', saveUri);
                    }
                });
            }
        } catch (error) {
            vscode.window.showErrorMessage(
                `Failed to save test file: ${error instanceof Error ? error.message : 'Unknown error'}`
            );
        }
    }

    private _getHtmlForWebview(webview: vscode.Webview, nonce: string): string {
        // Only use the reliable extensionUri path
        const htmlPath = vscode.Uri.joinPath(this._extensionUri, 'src', 'extension', 'testgen.html').fsPath;

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
    <title>Test Generation - Error</title>
</head>
<body>
    <h2>Error: Could not read testgen.html</h2>
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
