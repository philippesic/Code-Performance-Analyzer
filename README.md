# CPA

Test Model: `python src/complexity.py <code>`

Building Image:

PC (For Training): `docker build -t cpa .`

Mac: `docker build --platform=linux/amd64 -t cpa .`

--

Build Container:

PC: `run_container_win.bat`

Mac: `run_container_mac.sh`

--

Reenter Container:

`docker start -ai cpa-dev`

Models:

Complexity Model: starcoder2:3b

Teacher: deepseek-coder-v2:16b

Push: Run push_model
Pull: `cd models/student && git clone https://huggingface.co/philippesic/cpa`

## INTEGRATION (Juan):
For integration I created a stub server that serves the same response as the backend does, this way I avoid waiting times and downloading the whole fine-tuned model on my laptop. This is not to be used in reality. 
- To finish integrating, **update the `API_BASE_URL` constant in `./code-performance-analyzer/src/extension.ts` to the url of the backend server.**

## Running the frontend:
To run the frontend:
1. Setup and run the backend.
2. In the `./code-performance-analyzer` directory, run: `npm run compile`.
3. In visual studio open `./code-performance-analyzer/src/extension.ts`.
4. In visual studio, press F5 or trigger the "Debug: Start Debugging" while having the `extension.ts` file open. Visual studio will open a new window in the `test-code-performance-analyzer` directory, with the extension loaded in the environment.
5. Trigger the commands you want in the new debug window, there is a sample python function to quickly test the outputs.


# test-code-performance-analyzer README

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
