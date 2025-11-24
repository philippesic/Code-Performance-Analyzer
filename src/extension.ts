import * as vscode from 'vscode';
import { CpaPanelProvider } from './cpaPanelProvider'; 

// ================== DEFINITIONS ================== 
// API configuration
const API_BASE_URL = 'http://localhost:5000'; // this is to be changed to the real server
const API_TIMEOUT_MS = 6000000; // 1 min

// define a type for the decoration for it to be displayed in the complexity
const complexityDecorationType = vscode.window.createTextEditorDecorationType({
    after: {
        margin: '0 0 0 3em',
        color: new vscode.ThemeColor('editorCodeLens.foreground'), //theme aware colors
        fontStyle: 'italic',
    },
    isWholeLine: true
});

// backend API response structure
interface AnalysisResponse {
	complexity: string;
	loops_detected: number;
	functions_detected: number;
	explanation?: string;
}


// ================== FUNCTIONS ================== 
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

	// Command: Analyze Code, now with async
	const analyze = vscode.commands.registerCommand('code-performance-analyzer.analyze', async () => {
		console.log('🔍 ANALYZE COMMAND STARTED - New version');
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

		// create unique output channel
		const output = vscode.window.createOutputChannel('Code Performance Analyzer');

		// handle wait time for api response
		await vscode.window.withProgress({
			location: vscode.ProgressLocation.Notification,
			title: "Analyzing code complexity...",
			cancellable: false
		}, async (progress) => {
			try {
				// await response
				const result = await fetchAnalysis(code);
				
				const decorationMessage = `Complexity: ${result.complexity}`;
				const message = `Estimated Time Complexity: ${result.complexity}\nDetected Loops: ${result.loops_detected}, Functions: ${result.functions_detected}`;

				// decoration
				const decoration = {
					range: new vscode.Range(selection.end, selection.end),
					renderOptions: {
						after: {
							contentText: ` // ${decorationMessage}`,
						},
					},
				};

				// apply decoration to editor
				editor.setDecorations(complexityDecorationType, [decoration]);

				// get output to vscode output panel
				output.appendLine('='.repeat(50));
				output.appendLine(`[${new Date().toLocaleTimeString()}] Code Analysis Results`);
				output.appendLine('='.repeat(50));
				output.appendLine(`Complexity: ${result.complexity}`);
				output.appendLine(`Loops detected: ${result.loops_detected}`);
				output.appendLine(`Functions detected: ${result.functions_detected}`);
				output.appendLine(message);
				
				//include optional explanation from backend result
				if (result.explanation) {
					output.appendLine(`Explanation: ${result.explanation}`);
				}
				output.appendLine('='.repeat(50));
				output.show(true);
				
				vscode.window.showInformationMessage(`Complexity: ${result.complexity}`);
				panel_provider.updateAnalysisResult(message);

			} catch (error) {
				// Error handling - fallback to local heuristics and log error
				output.clear();
				output.appendLine('='.repeat(50));
				output.appendLine('API ERROR: Falling back to local heuristics...');
				output.appendLine('='.repeat(50));
				output.appendLine(`[${new Date().toLocaleTimeString()}] API Error: ${error instanceof Error ? error.message : "Unknown error"}`);
				output.appendLine('='.repeat(50));
				
				const fallbackResult = localHeuristicAnalysis(code);
				
				const decorationMessage = `Complexity: ${fallbackResult.complexity}`;
				const message = `Estimated Time Complexity: ${fallbackResult.complexity}\nDetected Loops: ${fallbackResult.loops_detected}, Functions: ${fallbackResult.functions_detected}`;
								
				// create decoration
				const decoration = {
					range: new vscode.Range(selection.end, selection.end),
					renderOptions: {
						after: {
							contentText: ` // ${decorationMessage}`,
						},
					},
				};
				
				// apply decoration to editor:
				editor.setDecorations(complexityDecorationType, [decoration]);
				
				output.appendLine('');
				output.appendLine('LOCAL ANALYSIS RESULTS:');
				output.appendLine(message);
				output.appendLine('='.repeat(50));
				output.show(true);

				panel_provider.updateAnalysisResult(message + '\n(API unavailable - using local analysis)');

				vscode.window.showWarningMessage(
					`Backend unavailable - Using local analysis: ${fallbackResult.complexity}`,
					'View Details'
				).then(selection => {
					if (selection === 'View Details') {
						output.show(true);
					}
				});
			}
		});
	});
	context.subscriptions.push(hello, analyze);
}


// API fetch function
async function fetchAnalysis(code: string): Promise<AnalysisResponse> {
	// request timeout handler
	const controller = new AbortController();
	const timeoutId = setTimeout(() => controller.abort(), API_TIMEOUT_MS);

	try {
		const response = await fetch(`${API_BASE_URL}/analyze`, {
			method: 'POST', 
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({code}),
			signal: controller.signal // Connects timeout to request
		});

		clearTimeout(timeoutId);

		// check for http errors
		if (!response.ok) {
			throw new Error(`HTTP ${response.status}: ${response.statusText}`);
		}

		const data: unknown = await response.json();

		// type guard to validate response structure
		if (
			typeof data !== 'object' ||
			data === null ||
			!('complexity' in data) ||
			typeof (data as any).complexity !== 'string'
		) {
			throw new Error(`Invalid response: missing complexity field, got ${JSON.stringify(data)}`);
		}
		const typedData = data as AnalysisResponse;

		return {
			complexity: typedData.complexity,
			loops_detected: typedData.loops_detected || 0,
			functions_detected: typedData.functions_detected || 0,
			explanation: typedData.explanation
		};

	} catch (error) {
		clearTimeout(timeoutId);

		console.error("FULL FETCH ERROR:", error);

		// handle timeout
		if (error instanceof Error && error.name === 'AbortError') {
			throw new Error('Request timeout (1 minute exceeded)');
		}
		throw error;
	}
}

// Fallback function with local heuristics
function localHeuristicAnalysis(code: string): { complexity: string; loops_detected: number; functions_detected: number } {
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

	return {
		complexity, 
		loops_detected: loopCount,
		functions_detected: funcCount
	};
}

export function deactivate() {}
