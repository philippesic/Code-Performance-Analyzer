import * as vscode from 'vscode';
import { CpaPanelProvider } from './cpaPanelProvider'; 

// define a type for the decoration for it to be displayed in the complexity
const complexityDecorationType = vscode.window.createTextEditorDecorationType({
    after: {
        margin: '0 0 0 3em',
        color: new vscode.ThemeColor('editorCodeLens.foreground'), //theme aware colors
        fontStyle: 'italic',
    },
    isWholeLine: true
});

export function activate(context: vscode.ExtensionContext) {
	console.log('Extension "Code Performance Analyzer" is now active!');
        
        // register the provider for the panel view
        const panel_provider = new CpaPanelProvider(context.extensionUri);
        
        context.subscriptions.push(
            vscode.window.registerWebviewViewProvider(CpaPanelProvider.id, panel_provider)
        );
	// Command: Hello World
	const hello = vscode.commands.registerCommand('code-performance-analyzer.helloWorld', () => {
		vscode.window.showInformationMessage('Hello from Code Performance Analyzer!');
	});

	// Command: Analyze Code
	const analyze = vscode.commands.registerCommand('code-performance-analyzer.analyze', () => {
		const editor = vscode.window.activeTextEditor;
		if (!editor) {
			vscode.window.showErrorMessage('No active editor found!');
			return;
		}
                
		// Trigger on selected code
		const selection = editor.selection;
		if (selection.isEmpty) {
			vscode.window.showInformationMessage('Please, select code to analyze and try again.');
			return;
		}

		const code = editor.document.getText(selection);

		// Basic heuristics
		const loopCount = (code.match(/\b(for|while)\b/g) || []).length;
		const funcCount = (code.match(/\bdef |function |=>/g) || []).length;
                
                let complexity = 'O(1)';
		if (loopCount > 0 && funcCount === 0) {
			complexity = 'O(n)';
		} else if (loopCount > 1) {
			complexity = 'O(n²)';
		} else if (funcCount > 2) {
			complexity = 'O(n log n)';
		}
		//let complexity = 'O(1)';
		//if (loopCount > 0 && funcCount === 0) complexity = 'O(n)';
		//else if (loopCount > 1) complexity = 'O(n²)';
		//else if (funcCount > 2) complexity = 'O(n log n)';

		const decorationMessage = `Complexity: ${complexity}`;
                const message = `Estimated Time Complexity: ${complexity}\nDetected Loops: ${loopCount}, Functions: ${funcCount}`;
                        
                // create decoration
                const decoration = {
                    range: new vscode.Range(selection.end, selection.end),
                    renderOptions: {
                        after: {
                            contentText: `// ${decorationMessage}`,
                        },
                    },
                };
                
                // apply decoration to editor:
                editor.setDecorations(complexityDecorationType, [decoration]);

		// Output to VS Code Output Panel
		const output = vscode.window.createOutputChannel('Code Performance Analyzer');
		output.appendLine(`[${new Date().toLocaleTimeString()}] Code Analysis Results`);
		output.appendLine(message);
		output.show(true);

		vscode.window.showInformationMessage(message);
		
		panel_provider.updateAnalysisResult(message);
	});

	context.subscriptions.push(hello, analyze);
}

export function deactivate() {}
