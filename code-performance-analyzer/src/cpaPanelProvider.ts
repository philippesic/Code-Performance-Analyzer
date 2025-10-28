import * as vscode from 'vscode';


export class CpaPanelProvider implements vscode.WebviewViewProvider {
    public static readonly id = 'cpa-panel'; // must match id in package.json

    constructor (
        private readonly _extensionUri: vscode.Uri,
    ) { }

    public resolveWebviewView(
        webviewView: vscode.WebviewView,
        context: vscode.WebviewViewResolveContext,
        _token: vscode.CancellationToken,
    ) {
        webviewView.webview.options = {
            // allow scripts in webview
            enableScripts: true,
            localResourceRoots: [this._extensionUri]
        };
        // Set html content for webview
        webviewView.webview.html = this._getHtmlForWebview();
    }


    private _getHtmlForWebview(): string { // html is temporary, refine when we decide what to display.
        return `<!DOCTYPE html>
			<html lang="en">
			<head>
				<meta charset="UTF-8">
				<meta name="viewport" content="width=device-width, initial-scale=1.0">
				<title>Analysis Panel</title>
				<style>
					body { padding: 10px; }
					h1 { color: var(--vscode-editor-foreground); }
				</style>
			</head>
			<body>
				<h1>Code Performance Analyzer</h1>
				<p>Analysis features are currently under development!</p>
				
				<button id="example-button">Example button</button>

			</body>
			</html>`;
    }

}
