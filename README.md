# Code Performance Analyzer

## Containers:

Building Image:

PC (For Training): `docker build -t cpa .`

Mac: `docker build --platform=linux/amd64 -t cpa .`

--

Build Container:

PC: `build_container_win.bat`

Mac: `build_container_mac.sh`

--

Reenter Container:

`run_container.bat`

Or

`docker start -ai cpa-dev`

## Models:

Complexity Model: starcoder2:3b

Teacher: deepseek-coder-v2:16b

Push: Run `push_model.py`

Pull Safetensors: `cd src/model/models/student && git clone https://huggingface.co/philippesic/cpa`

## Hosting the model locally:

1. Run the command from `server.info` from the container root. Containers are setup to automatically port map. Note that the server may take a long time to start.

2. Test the server response via a curl: `curl -X POST http://127.0.0.1:5000/analyze -H "Content-Type: application/json" -d '{"code": "def loop(n):\n for i in range(n): pass"}'`

3. Running the model locally requires 11gb vram. Support for 8gb requires retraining a lighter model.

4. Currently, the only way to stop the server is via `kill <pid>` (`ps aux | grep python`)

## Running the extension environment:

1. Setup and run the backend

2. `npm run compile` in the `src` directory

3. In vscode open `.src/extension.ts`

4. Start debugging fith F5. If prompted, select `VSCode Extention Development` as your debugger

## Backend README

todo

## test-code-performance-analyzer README

This is the README for your extension "test-code-performance-analyzer". After writing up a brief description, we recommend including the following sections.

## Features

Describe specific features of your extension including screenshots of your extension in action. Image paths are relative to this README file.

For example if there is an image subfolder under your extension project workspace:

\!\[feature X\]\(images/feature-x.png\)

> Tip: Many popular extensions utilize animations. This is an excellent way to show off your extension! We recommend short, focused animations that are easy to follow.

## Requirements

If you have any requirements or dependencies, add a section describing those and how to install and configure them.

## Extension Settings

Include if your extension adds any VS Code settings through the `contributes.configuration` extension point.

For example:

This extension contributes the following settings:

* `myExtension.enable`: Enable/disable this extension.
* `myExtension.thing`: Set to `blah` to do something.

## Known Issues

Calling out known issues can help limit users opening duplicate issues against your extension.

## Release Notes

Users appreciate release notes as you update your extension.

### 1.0.0

Initial release of ...

### 1.0.1

Fixed issue #.

### 1.1.0

Added features X, Y, and Z.

---

## Following extension guidelines

Ensure that you've read through the extensions guidelines and follow the best practices for creating your extension.

* [Extension Guidelines](https://code.visualstudio.com/api/references/extension-guidelines)

## Working with Markdown

You can author your README using Visual Studio Code. Here are some useful editor keyboard shortcuts:

* Split the editor (`Cmd+\` on macOS or `Ctrl+\` on Windows and Linux).
* Toggle preview (`Shift+Cmd+V` on macOS or `Shift+Ctrl+V` on Windows and Linux).
* Press `Ctrl+Space` (Windows, Linux, macOS) to see a list of Markdown snippets.

## For more information

* [Visual Studio Code's Markdown Support](http://code.visualstudio.com/docs/languages/markdown)
* [Markdown Syntax Reference](https://help.github.com/articles/markdown-basics/)

**Enjoy!**
