# Python Scripts, App and Tests

## Testing

Unittest is the chosen python test tool.

To run all the unit tests from the root folder use:

```
python3 -m unittest discover -s python -fv
```

To run an individual unit test use:

```

python3 -m unittest python/test/test_FILE.py
or
python3 -m unittest python.test.test_FILE

```

To import the tests into VS Code: Go into the settings `shift + command + p`, select `Python: Configure Tests`, select `unittest`, selelct `python` folder, select `test_.py`. This will create a `.vscode/settings.json` file. It will be possible to run and debug the test/s in the Testing tab.

## Debugging

VS Code Test debugging: Follow the steps above to debug the test code files.

VS Code normal debugging: for scripts and tests use the following `.vscode/launch.json` configuration:

```
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: App",
      "type": "python",
      "python": "${workspaceFolder}/venv/bin/python3",
      "request": "launch",
      "cwd": "${workspaceRoot}/python",
      "program": "${workspaceFolder}/python/scripts/FILE.py",
      // "program": "${workspaceFolder}/python/test/test_FILE.py",
      "console": "integratedTerminal",
      "env": {
        "PYTHONPATH": "${workspaceFolder}${pathSeparator}${env:PYTHONPATH}",
        "ADMIN_GITHUB_TOKEN": "TOKEN",
        "ORG_NAME": "ministryofjustice"
      }
    }
  ]
}
```

The env var in the above configuration `"PYTHONPATH": "${workspaceFolder}${pathSeparator}${env:PYTHONPATH}",` adds the python directory to PYTHONPATH which enables the debugger to see the directory as package and the files within it.
