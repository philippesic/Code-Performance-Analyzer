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
            vscode.window.registerWebviewViewProvider("cpa-panel", panel_provider)
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
		const lines = code.split(/\r?\n/);


		// Basic heuristics and metrics
		const loopRegex = /\b(for|while|foreach|do)\b/g;
		const recursiveCallRegex = /\b([A-Za-z_]\w*)\s*\((.*?)\)\s*{/;
		const functionRegex = /\b(function|def|class|\(|=>)\b/;
		const divideAndConquerHints = /\b(mid|merge|partition|divide|split)\b/;
		const searchOrSortHints = /\b(search|sort|binarySearch|mergeSort|quickSort)\b/;

		let loopCount = 0;
		let maxDepth = 0;
		let stackDepth = 0;
		let recursionDetected = false;

		for (const line of lines) {
			if (loopRegex.test(line)) {
				loopCount++;
				stackDepth++;
				maxDepth = Math.max(maxDepth, stackDepth);
			}
			if (/\b(return|end|})/.test(line)) {
				stackDepth = Math.max(0, stackDepth - 1);
			}
			if (recursiveCallRegex.test(line)) {
				recursionDetected = true;
			}
		}

		const funcCount = (code.match(functionRegex) || []).length;
		const divideConquer = divideAndConquerHints.test(code);
		const searchingSorting = searchOrSortHints.test(code);

		// Heuristic complexity estimation
		let complexity = 'O(1)';
		if (recursionDetected && divideConquer) {
			complexity = 'O(n log n)'; // merge sort–like
		} else if (recursionDetected) {
			complexity = 'O(2^n)'; // brute force recursion
		} else if (maxDepth >= 2) {
			complexity = 'O(n²)';
		} else if (loopCount === 1) {
			complexity = 'O(n)';
		} else if (searchingSorting) {
			complexity = 'O(n log n)';
		}

		// Prepare result message
		const message = `Estimated Complexity: ${complexity}
Detected Loops: ${loopCount}
Max Loop Depth: ${maxDepth}
Recursion: ${recursionDetected ? 'Yes' : 'No'}
Functions: ${funcCount}
`;

    	const decorationMessage = `Complexity: ${complexity}`;
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
		
		// Generate chart data for multiple complexities
		const n = Array.from({ length: 10 }, (_, i) => i + 1);
		const datasets = [
        { label: 'O(1)', data: n.map(() => 1) },
        { label: 'O(n)', data: n.map(x => x) },
        { label: 'O(n log n)', data: n.map(x => x * Math.log2(x + 1)) },
        { label: 'O(n²)', data: n.map(x => x * x) },
        { label: 'O(2^n)', data: n.map(x => Math.pow(2, Math.min(12, x))) },
    	];

		const chartData = {
			line: { labels: n.map(x => `n=${x}`), datasets, highlight: complexity },
		};

		panel_provider.updateAnalysisResult(message, chartData);
	});

	context.subscriptions.push(hello, analyze);
}

export function deactivate() {}
